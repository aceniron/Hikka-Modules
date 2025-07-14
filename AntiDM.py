from .. import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import ReportSpamRequest, DeleteHistoryRequest
from telethon.errors import PeerIdInvalidError
from requests import post
import io
from telethon.errors import rpcerrorlist
import base64

class AntiDM(loader.Module):
    """AntiDM с дополнительными командами для очистки личных сообщений и удаления всех сообщений"""
    strings = {"name": "AntiDM"}

    def __init__(self):
        self.ad = False
        self.ubs_mode = False
        self.wi = []
        self.wu = []
        self.reply_message = None  # Сообщение по умолчанию
        self.reply_image = None    # Изображение по умолчанию
        self.antbo_mode = False    # Режим для удаления сообщений от ботов

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        # Восстановление состояния из базы данных
        self.ad = self.db.get("AntiDM", "ad", False)
        self.antbo_mode = self.db.get("AntiDM", "antbo_mode", False)
        self.ubs_mode = self.db.get("AntiDM", "ubs_mode", False)
        self.wi = self.db.get("AntiDM", "wi", [])
        self.wu = self.db.get("AntiDM", "wu", [])
        self.reply_message = self.db.get("AntiDM", "reply_message", None)
        self.reply_image = self.db.get("AntiDM", "reply_image", None)

    async def admsgcmd(self, message):
        """Сохраняет сообщение для отправки (использовать в ответ на сообщение или сообщение с изображением)"""
        reply = await message.get_reply_message()
        if not reply:
            self.reply_message = None
            self.reply_image = None
            self.db.set("AntiDM", "reply_message", None)
            self.db.set("AntiDM", "reply_image", None)
            await message.edit("<b>Сообщение и изображение удалены. Теперь ничего не будет отправляться пользователям.</b>")
            return

        if reply.media:
            self.reply_message = reply.text or ""
            image_data = await self.client.download_media(reply, bytes)
            self.reply_image = base64.b64encode(image_data).decode('utf-8')
            self.db.set("AntiDM", "reply_message", self.reply_message)
            self.db.set("AntiDM", "reply_image", self.reply_image)
            await message.edit(f"<b>Сообщение и изображение установлены:</b>\n<b>Текст:</b> {self.reply_message}\n<b>Изображение:</b> [сохранено]")
        else:
            self.reply_message = reply.text
            self.reply_image = None
            self.db.set("AntiDM", "reply_message", self.reply_message)
            self.db.set("AntiDM", "reply_image", None)
            await message.edit(f"<b>Сообщение изменено на:</b> {self.reply_message}")

    async def adoncmd(self, message):
        """Включает AntiDM"""
        self.ad = True
        self.db.set("AntiDM", "ad", True)
        await message.edit('<b>AntiDM включён.</b>')

    async def adoffcmd(self, message):
        """Выключает AntiDM"""
        self.ad = False
        self.db.set("AntiDM", "ad", False)
        await message.edit('<b>AntiDM выключён.</b>')

    async def ubscmd(self, message):
        """Переключает режим использования AntiDM"""
        self.ubs_mode = not self.ubs_mode
        self.db.set("AntiDM", "ubs_mode", self.ubs_mode)
        mode = "без репорта и блокировки" if self.ubs_mode else "с репортом и блокировкой"
        await message.edit(f'<b>Режим AntiDM переключен: {mode}.</b>')

    async def addwlcmd(self, message):
        """Добавляет пользователя или бота в белый список по username или в ответ на сообщение, или user ID
        Можно добавить несколько пользователей, разделяя их запятой"""
        args = utils.get_args_raw(message)

        if args:
            usernames_or_ids = [arg.strip() for arg in args.split(",")]
            added_users = []

            for username_or_id in usernames_or_ids:
                try:
                    if username_or_id.isdigit():
                        user_id = int(username_or_id)
                        user = await message.client.get_entity(user_id)
                    else:
                        user = await message.client.get_entity(username_or_id)

                    if str(user.id) not in self.wi:
                        self.wi.append(str(user.id))
                        self.wu.append(f'{user.first_name} -> @{user.username} -> {user.id}')
                        added_users.append(f'{user.first_name} -> @{user.username} -> {user.id}')
                except Exception as e:
                    await message.edit(f"<b>Ошибка при добавлении {username_or_id}:</b> {e}")
                    return

            self.db.set("AntiDM", "wi", self.wi)
            self.db.set("AntiDM", "wu", self.wu)
            await message.edit(f'<b>Добавлены:</b>\n' + "\n".join(added_users))
        else:
            try:
                reply = await message.get_reply_message()
                if not reply:
                    await message.edit("<b>Ошибка: укажите username, ID или сделайте реплай на сообщение.</b>")
                    return

                user = await message.client.get_entity(reply.sender_id)
                if str(user.id) not in self.wi:
                    self.wi.append(str(user.id))
                    self.wu.append(f'{user.first_name} -> @{user.username} -> {user.id}')
                    self.db.set("AntiDM", "wi", self.wi)
                    self.db.set("AntiDM", "wu", self.wu)
                    await message.edit(f'<b>Добавлен:</b>\n{user.first_name} -> @{user.username} -> {user.id}\n\n<b>Посмотреть белый список по команде</b><code>.wl</code>')
                else:
                    await message.edit("<b>Пользователь или бот уже в белом списке.</b>")
            except Exception as e:
                await message.edit(f"<b>Ошибка:</b> {e}")

    async def wlcmd(self, message):
        """Удаляет сообщение и отправляет список белого списка в формате"""
        await message.delete()  # Удаляет исходное сообщение команды
        formatted_wu = '\n'.join(self.wu)
        await message.respond(f'White List:\n{formatted_wu}')

    async def clswlcmd(self, message):
        """Очищает весь белый список"""
        self.wi.clear()
        self.wu.clear()
        self.db.set("AntiDM", "wi", self.wi)
        self.db.set("AntiDM", "wu", self.wu)
        await message.edit('<b>Белый список очищен.</b>')

    async def delwlidcmd(self, message):
        """Удаляет пользователей или ботов из белого списка по ID (несколько ID разделяются запятой)"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Укажите один или несколько ID для удаления, разделяя запятыми.</b>")
            return

        ids_to_remove = [arg.strip() for arg in args.split(",")]
        removed_users = []

        for user_id in ids_to_remove:
            if user_id in self.wi:
                self.wi.remove(user_id)
                user_info = next((info for info in self.wu if user_id in info), None)
                if user_info:
                    self.wu.remove(user_info)
                    removed_users.append(user_info)

        self.db.set("AntiDM", "wi", self.wi)
        self.db.set("AntiDM", "wu", self.wu)

        if removed_users:
            await message.edit(f'<b>Удалены из белого списка:</b>\n' + "\n".join(removed_users))
        else:
            await message.edit(f"<b>Указанные ID не найдены в белом списке.</b>")

    async def watcher(self, message):
        """Удаляет сообщения и блокирует пользователей, если они не в белом списке и не являются ботами"""
        me = (await message.client.get_me())
        if str(message.chat_id).startswith('-'):  # Исключение групповых чатов
            return
        if message.sender_id == me.id:  # Исключаем свои сообщения
            return
        if str(message.sender_id) in self.wi:  # Если пользователь или бот в белом списке
            return

        sender = await message.get_sender()
        if sender.bot:
            if str(sender.id) in self.wi:
                return  # Если бот в белом списке, то не удалять его сообщение
            if self.antbo_mode:
                await message.delete()
                try:
                    # Удаление переписки с ботом из списка чатов
                    entity = await self.client.get_input_entity(sender)
                    await self.client.delete_dialog(entity)
                except Exception as e:
                    await message.client.send_message(
                        me.id,
                        f"Ошибка при удалении переписки с ботом {message.chat_id}: {e}"
                    )
            return

        if self.ad:
            await message.delete()
            await self.send_saved_response(message.sender_id, message)

            try:
                # Удаление переписки из списка чатов
                entity = await self.client.get_input_entity(message.sender_id)
                await self.client.delete_dialog(entity)
            except Exception as e:
                await message.client.send_message(
                    me.id,
                    f"Ошибка при удалении переписки с {message.chat_id}: {e}"
                )

            if not self.ubs_mode:
                try:
                    await message.client(BlockRequest(message.sender_id))
                except Exception as e:
                    await message.client.send_message(
                        me.id,
                        f"Ошибка при блокировке пользователя {message.chat_id}: {e}"
                    )

                try:
                    await message.client(ReportSpamRequest(peer=message.sender_id))
                except Exception as e:
                    await message.client.send_message(
                        me.id,
                        f"Ошибка при отправке жалобы: {e}"
                    )

    @loader.sudo
    async def envscmd(self, message):
        """Показать сохраненное сообщение"""
        await self.send_saved_response(message.sender_id, message)

    async def send_saved_response(self, user_id, message):
        """Отправляет сохраненное сообщение или изображение пользователю"""
        if not self.reply_message and not self.reply_image:
            await message.edit("<b>Сообщение или изображение не установлено.</b>")
            return

        sender = await self.client.get_entity(user_id)
        first_name = sender.first_name
        response_message = self.reply_message.replace("%name%", first_name)

        if self.reply_image:
            image_data = base64.b64decode(self.reply_image)
            await self.client.send_file(user_id, image_data, caption=response_message)
        else:
            await self.client.send_message(user_id, response_message)

    @loader.sudo
    async def antbocmd(self, message):
        """Переключает режим удаления сообщений от ботов"""
        self.antbo_mode = not self.antbo_mode
        self.db.set("AntiDM", "antbo_mode", self.antbo_mode)
        mode = "включён" if self.antbo_mode else "выключён"
        await message.edit(f'<b>Режим удаления сообщений от ботов {mode}.</b>')

    @loader.sudo
    async def dmcmd(self, message):
        """Удаляет переписку в текущем чате (ЛС), как .delallpersonal"""
        if not message.is_private:
            await message.edit(self.strings["dm_not_private"])
            return

        await message.edit(self.strings["processing"])

        try:
            entity = await self._client.get_input_entity(message.chat_id)
            await self._client(DeleteHistoryRequest(
                peer=entity,
                max_id=0,
                just_clear=False,
                revoke=True
            ))
            await message.edit(self.strings["dm_done"])
        except rpcerrorlist.MessageIdInvalidError:
            await message.edit(self.strings["dm_invalid"])
        except Exception as e:
            await message.edit(self.strings["dm_error"].format(e))

    @loader.sudo
    async def delmecmd(self, message):
        """Удаляет все сообщения от тебя без вопросов"""
        chat = message.chat
        if chat:
            async for msg in message.client.iter_messages(chat, from_user="me"):
                await msg.delete()
            await message.delete()
        else:
            await message.edit("<b>В лс не чищу!</b>")

    async def delwlidcmd(self, message):
        """Удаляет пользователей или ботов из белого списка по ID (несколько ID разделяются запятой)"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Укажите один или несколько ID для удаления, разделяя запятыми.</b>")
            return

        ids_to_remove = [arg.strip() for arg in args.split(",")]
        removed_users = []

        for user_id in ids_to_remove:
            if user_id in self.wi:
                self.wi.remove(user_id)
                user_info = next((info for info in self.wu if user_id in info), None)
                if user_info:
                    self.wu.remove(user_info)
                    removed_users.append(user_info)

        self.db.set("AntiDM", "wi", self.wi)
        self.db.set("AntiDM", "wu", self.wu)

        if removed_users:
            await message.edit(f'<b>Удалены из белого списка:</b>\n' + "\n".join(removed_users))
        else:
            await message.edit(f"<b>Указанные ID не найдены в белом списке.</b>")