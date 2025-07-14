import zipfile
import os

from datetime import datetime

from .. import loader, utils


@loader.tds
class SMArchiver(loader.Module):
    """unloads all messages from Favorites"""

    strings = {
        "name": "SMArchiver",
        "archive_created": "🎉 Archive with messages has been successfully created: {filename}",
        "no_messages": "⚠️ There are no messages in Saved Messages.",
        "error": "❌ An error occurred: {error}",
        "processing": "🛠️ Processing messages... Please wait.\n\nP.S: Be careful, if you have a lot of messages, you may get flooding, and if you have a lot of heavy files, the download will be slower than usual.",
    }

    strings_ru = {
        "archive_created": "🎉 Архив с сообщениями успешно создан: {filename}",
        "no_messages": "⚠️ В Избранном нет сообщений.",
        "error": "❌ Произошла ошибка: {error}",
        "processing": "🛠️ Обработка сообщений... Пожалуйста, подождите.\n\nP.S: Будьте осторожны, если у вас много сообщений то вы можете получить флудвейт, и ещё если у вас много тяжёлых файлов то загрузка будет медленнее чем обычно.",
    }

    @loader.command(
        ru_doc="выгружает все сообщения из Избранного / Saved Messages и собирает их в одном архиве.",
        en_doc="downloads all messages from Favorites / Saved Messages and collects them in one archive.",
    )
    async def smdump(self, message):
        await utils.answer(message, self.strings["processing"])

        saved_messages = await message.client.get_messages("me", limit=None)

        if not saved_messages:
            await utils.answer(message, "Нет сообщений для выгрузки.")
            return

        current_month = datetime.now().strftime("%B %Y")
        archive_path = "saved_messages.zip"

        try:
            with zipfile.ZipFile(archive_path, "w") as archive:
                month_folder = f"{current_month}/"
                archive.writestr(month_folder, "")


                message_folders = {
                    "Text Messages": f"{month_folder}Text Messages/",
                    "Voice Messages": f"{month_folder}Voice Messages/",
                    "Video Messages": f"{month_folder}Video Messages/",
                    "Videos": f"{month_folder}Videos/",
                    "Audios": f"{month_folder}Audios/",
                    "GIFs": f"{month_folder}GIFs/",
                    "Files": f"{month_folder}Files/"
                }

                for folder in message_folders.values():
                    archive.writestr(folder, "")

                for msg in saved_messages:
                    await self.add_message_to_archive(msg, archive, message_folders)

            await message.client.send_file(
                message.chat_id,
                archive_path,
                caption=self.strings["archive_created"].format(filename=os.path.basename(archive_path)),
            )

        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))

        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)

    async def add_message_to_archive(self, msg, archive, folders):
        """Обрабатывает отдельное сообщение и добавляет его в архив."""
        if msg.message:
            timestamp = datetime.fromtimestamp(msg.date.timestamp()).strftime("%Y%m%d_%H%M%S")
            safe_name = f"message_{timestamp}.txt"
            archive.writestr(os.path.join(folders["Text Messages"], safe_name), msg.message)

        if msg.media:
            media_file = await msg.client.download_media(msg.media)
            if media_file:
                mime_type = msg.media.document.mime_type if hasattr(msg.media, "document") else None
                folder = folders["Files"]

                if mime_type:
                    if mime_type.startswith("audio/"):
                        folder = folders["Audios"]
                    elif mime_type.startswith("video/"):
                        folder = folders["Videos"]
                    elif mime_type.startswith("image/gif"):
                        folder = folders["GIFs"]

                archive.write(media_file, os.path.join(folder, os.path.basename(media_file)))