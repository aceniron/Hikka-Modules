from .. import loader, utils
import logging
import base64
import requests
import json
from requests.exceptions import MissingSchema, ChunkedEncodingError
import os

logger = logging.getLogger(__name__)

def register(cb):
    cb(GitHubMod())

@loader.tds
class GitHub(loader.Module):
    """Управление файлами в репозитории GitHub"""

    strings = {
        "name": "GitHub",
        "reply_to_file": "<b>Ответьте на файл</b>",
        "error_file": "Формат не поддерживается",
        "connection_error": "<i>Ошибка соединения</i>",
        "repo_error": "<i>Ошибка репозитория</i>",
        "token_error": "<i>Ошибка токена</i>",
        "exist_422": "<b>Не удалось загрузить файл. Возможная причина: файл с таким названием уже существует в репозитории.</b>",
        "token_not_found": "Токен не найден",
        "username_not_found": "Имя пользователя GitHub не указано",
        "repo_not_found": "Репозиторий не указан",
        "list_files_error": "<i>Не удалось получить список файлов репозитория</i>",
        "delete_success": "<b>Файл {} успешно удален</b>",
        "delete_fail": "<b>Не удалось удалить файл. Возможно, он не существует</b>",
        "create_repo_success_public": "<b>Публичный репозиторий {} успешно создан</b>",
        "create_repo_success_private": "<b>Приватный репозиторий {} успешно создан</b>",
        "repo_create_fail": "<b>Не удалось создать репозиторий</b>",
        "current_settings": "Текущие настройки:\nТокен: <b>{}</b>\nИмя пользователя: <b>{}</b>\nРепозиторий: <b>{}</b>",
    }

    def __init__(self):
        self.GH_TOKEN = "TOKEN"
        self.GH_USERNAME = "USERNAME"
        self.GH_REPO = "REPOSITORY"
        self.load_settings()

    async def client_ready(self, client, db):
        self.client = client

    async def settokencmd(self, message):
        """Установить GitHub токен"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["token_not_found"])
            return
        self.GH_TOKEN = args
        await utils.answer(message, f"Токен установлен: {args}")
        self.save_settings()

    async def setusernamecmd(self, message):
        """Установить GitHub имя пользователя"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["username_not_found"])
            return
        self.GH_USERNAME = args
        await utils.answer(message, f"Имя пользователя установлено: {args}")
        self.save_settings()

    async def setrepocmd(self, message):
        """Установить GitHub репозиторий"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["repo_not_found"])
            return
        self.GH_REPO = args
        await utils.answer(message, f"Репозиторий установлен: {args}")
        self.save_settings()

    async def showcfgcmd(self, message):
        """Показать текущие настройки"""
        await utils.answer(message, self.strings["current_settings"].format(self.GH_TOKEN, self.GH_USERNAME, self.GH_REPO))

    @loader.owner
    async def gitcmd(self, message):
        """Загрузить файл в репозиторий (с уведомлением в Избранное)"""
        reply = await message.get_reply_message()
        if not reply:
            await message.reply(self.strings["reply_to_file"])
            return
        media = reply.media
        if not media:
            await message.reply(self.strings["error_file"])
            return

        await message.delete()  # Удаляем сообщение до выполнения функционала

        try:
            fname = (reply.media.document.attributes[0]).file_name
        except AttributeError:
            await message.reply(self.strings["error_file"])
            return

        try:
            file = await message.client.download_file(media)
            encoded_string = base64.b64encode(file)
            stout = encoded_string.decode("utf-8")
            TOKEN = self.GH_TOKEN
            USERNAME = self.GH_USERNAME
            REPO = self.GH_REPO
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{fname}"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            git_data = '{"message": "Upload file", "content":' + '"' + stout + '"' + "}"
            r = requests.put(url, headers=head, data=git_data)
            if int(r.status_code) == 201:
                file_name_without_ext = fname.replace(".py", "")
                await self.client.send_message(
                    message.chat_id,
                    f"Файл {file_name_without_ext} успешно загружен на GitHub",
                    reply_to=reply.id
                )
            else:
                await message.reply(self.strings["repo_error"])
        except (ConnectionError, MissingSchema, ChunkedEncodingError):
            await message.reply(self.strings["connection_error"])
        except Exception:
            await message.reply(self.strings["error_file"])

    @loader.owner
    async def lilescmd(self, message):
        """Получить список файлов в html формате (без аргумениов) с репозитория или ссылку на указанный (с аргументом к примеру .liles GitHub"""
        args = utils.get_args_raw(message).strip()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        try:
            TOKEN = self.GH_TOKEN
            USERNAME = self.GH_USERNAME
            REPO = self.GH_REPO
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(url, headers=head)
            if r.status_code == 200:
                files = json.loads(r.text)
                if args:  # Если указан аргумент
                    file_name = f"{args}.py"  # Добавляем расширение .py
                    for file in files:
                        if file["type"] == "file" and file["name"] == file_name:
                            await self.client.send_message(
                                message.chat_id,
                                f"{args}\n{file['download_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')}",
                                reply_to=message.id
                            )
                            return
                    await self.client.send_message(message.chat_id, f"Файл {file_name} не найден.", reply_to=message.id)
                else:  # Если аргумент не указан
                    file_list = [
                        {"index": idx + 1, "name": file["name"].replace(".py", ""), "link": file["download_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")}
                        for idx, file in enumerate(files)
                        if file["type"] == "file"
                    ]
                    # Создаем HTML таблицу
                    html_content = """
                    <html>
                    <head>
                        <title>Список файлов в репозитории</title>
                    </head>
                    <body>
                        <table border="1">
                            <tr>
                                <th>№</th>
                                <th>Name</th>
                                <th>Link</th>
                            </tr>
                    """
                    for file in file_list:
                        html_content += f"""
                            <tr>
                                <td>{file['index']}</td>
                                <td>{file['name']}</td>
                                <td><a href="{file['link']}">{file['link']}</a></td>
                            </tr>
                        """
                    html_content += """
                        </table>
                    </body>
                    </html>
                    """
                    # Сохраняем HTML в файл
                    file_path = "repository.html"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    # Отправляем HTML файл
                    await self.client.send_file(message.chat_id, file_path, reply_to=message.id)
                    os.remove(file_path)  # Удаляем файл после отправки
            else:
                await self.client.send_message(
                    message.chat_id, self.strings["list_files_error"], reply_to=message.id
                )
        except Exception as e:
            logger.exception(e)
            await self.client.send_message(
                message.chat_id, self.strings["list_files_error"], reply_to=message.id
            )

    @loader.owner
    async def delecmd(self, message):
        """Удалить файл из репозитория по названию"""
        args = utils.get_args_raw(message).strip()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        if not args:
            await self.client.send_message(message.chat_id, "<b>Укажите имя файла для удаления!</b>", reply_to=message.id)
            return

        try:
            TOKEN = self.GH_TOKEN
            USERNAME = self.GH_USERNAME
            REPO = self.GH_REPO
            fname = f"{args}.py"  # Автоматически добавляем расширение .py
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{fname}"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(url, headers=head)
            if r.status_code == 200:
                file_info = json.loads(r.text)
                sha = file_info["sha"]
                delete_data = json.dumps({"message": "Delete file", "sha": sha})
                delete_req = requests.delete(url, headers=head, data=delete_data)
                if delete_req.status_code == 200:
                    file_name_without_ext = fname.replace(".py", "")
                    await self.client.send_message(
                        message.chat_id, self.strings["delete_success"].format(file_name_without_ext), reply_to=message.id
                    )
                else:
                    await self.client.send_message(message.chat_id, self.strings["delete_fail"], reply_to=message.id)
            else:
                await self.client.send_message(message.chat_id, self.strings["delete_fail"], reply_to=message.id)
        except Exception as e:
            logger.exception(e)
            await self.client.send_message(message.chat_id, self.strings["delete_fail"], reply_to=message.id)

    @loader.owner
    async def publrecmd(self, message):
        """Создать публичный репозиторий"""
        args = utils.get_args_raw(message).strip().split()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        if len(args) < 1:  # Изменяем условие на < 1 для простоты использования команды
            await self.client.send_message(message.chat_id, "<b>Укажите имя репозитория!</b>", reply_to=message.id)
            return

        repo_name = args[0]
        TOKEN = self.GH_TOKEN
        USERNAME = self.GH_USERNAME
        head = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = "https://api.github.com/user/repos"
        data = json.dumps({"name": repo_name, "private": False})
        response = requests.post(url, headers=head, data=data)
        if response.status_code == 201:
            await self.client.send_message(
                message.chat_id, self.strings["create_repo_success_public"].format(repo_name), reply_to=message.id
            )
        else:
            await self.client.send_message(message.chat_id, self.strings["repo_create_fail"], reply_to=message.id)

    @loader.owner
    async def privrecmd(self, message):
        """Создать приватный репозиторий"""
        args = utils.get_args_raw(message).strip().split()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        if len(args) < 1:  # Изменяем условие на < 1 для простоты использования команды
            await self.client.send_message(message.chat_id, "<b>Укажите имя репозитория!</b>", reply_to=message.id)
            return

        repo_name = args[0]
        TOKEN = self.GH_TOKEN
        USERNAME = self.GH_USERNAME
        head = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = "https://api.github.com/user/repos"
        data = json.dumps({"name": repo_name, "private": True})
        response = requests.post(url, headers=head, data=data)
        if response.status_code == 201:
            await self.client.send_message(
                message.chat_id, self.strings["create_repo_success_private"].format(repo_name), reply_to=message.id
            )
        else:
            await self.client.send_message(message.chat_id, self.strings["repo_create_fail"], reply_to=message.id)

    @loader.owner
    async def fgitcmd(self, message):
        """Скачать файл с GitHub репозитория"""
        args = utils.get_args_raw(message).strip()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        if not args:
            await self.client.send_message(message.chat_id, "<b>Укажите имя файла для скачивания!</b>", reply_to=message.id)
            return

        try:
            TOKEN = self.GH_TOKEN
            USERNAME = self.GH_USERNAME
            REPO = self.GH_REPO
            fname = f"{args}.py"  # Автоматически добавляем расширение .py
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{fname}"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(url, headers=head)
            if r.status_code == 200:
                file_info = json.loads(r.text)
                content = base64.b64decode(file_info["content"])
                # Сохраняем файл
                with open(fname, "wb") as file:
                    file.write(content)
                # Отправляем файл в чат
                await self.client.send_file(message.chat_id, fname, reply_to=message.id)
                # Удаляем файл после отправки
                os.remove(fname)
            else:
                await self.client.send_message(message.chat_id, self.strings["list_files_error"], reply_to=message.id)
        except Exception as e:
            logger.exception(e)
            await self.client.send_message(message.chat_id, self.strings["list_files_error"], reply_to=message.id)

    @loader.owner
    async def lcmd(self, message):
        """Тоже самое что и liles только без html файла и с dlm ссылкой (перед dlm ставим свой префикс)"""
        args = utils.get_args_raw(message).strip()
        await message.delete()  # Удаляем сообщение до выполнения функционала

        try:
            TOKEN = self.GH_TOKEN
            USERNAME = self.GH_USERNAME
            REPO = self.GH_REPO
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(url, headers=head)
            if r.status_code == 200:
                files = json.loads(r.text)
                if args:  # Если указан аргумент
                    file_name = f"{args}.py"  # Добавляем расширение .py
                    for file in files:
                        if file["type"] == "file" and file["name"] == file_name:
                            await self.client.send_message(
                                message.chat_id,
                                f".dlm {file['download_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')}",
                                reply_to=message.id
                            )
                            return
                    await self.client.send_message(message.chat_id, f"Файл {file_name} не найден.", reply_to=message.id)
                else:  # Если аргумент не указан
                    file_list = "\n".join(
                        file["name"].replace(".py", "") for file in files if file["type"] == "file"
                    )
                    await self.client.send_message(message.chat_id, file_list, reply_to=message.id)
            else:
                await self.client.send_message(
                    message.chat_id, self.strings["list_files_error"], reply_to=message.id
                )
        except Exception as e:
            logger.exception(e)
            await self.client.send_message(
                message.chat_id, self.strings["list_files_error"], reply_to=message.id
            )

    def save_settings(self):
        settings = {
            "GH_TOKEN": self.GH_TOKEN,
            "GH_USERNAME": self.GH_USERNAME,
            "GH_REPO": self.GH_REPO,
        }
        with open("github_settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open("github_settings.json", "r") as f:
                settings = json.load(f)
                self.GH_TOKEN = settings.get("GH_TOKEN", "TOKEN")
                self.GH_USERNAME = settings.get("GH_USERNAME", "USERNAME")
                self.GH_REPO = settings.get("GH_REPO", "REPOSITORY")
        except FileNotFoundError:
            pass