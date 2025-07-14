from .. import loader, utils
import io
import requests
import os
import logging
import random
import json  # Добавил импорт json
from telethon.tl.types import Message
from telethon.tl.functions.channels import JoinChannelRequest

logger = logging.getLogger(__name__)

@loader.tds
class Uploader(loader.Module):
    """Module for uploading files to various file hosting services"""

    strings = {
        "name": """Uploader""",
        "uploading": "⚡ <b>Uploading file...</b>",
        "reply_to_file": "❌ <b>Reply to file!</b>",
        "uploaded": "❤️ <b>File uploaded!</b>\n\n🔥 <b>URL:</b> <code>{link_to_file}</code>",
        "error": "❌ <b>Error while uploading: {}</b>",
        "noargs": "<emoji document_id=5208434048753484584>⛔</emoji> <b>No file specified</b>",
        "err": "<emoji document_id=5208434048753484584>⛔</emoji> <b>Upload error</b>"
    }

    strings_ru = {
        "name": """Uploader""", 
        "uploading": "⚡ <b>Загружаю файл...</b>",
        "reply_to_file": "❌ <b>Ответьте на файл!</b>", 
        "uploaded": "❤️ <b>Файл загружен!</b>\n\n🔥 <b>URL:</b> <code>{link_to_file}</code>",
        "error": "❌ <b>Ошибка при загрузке: {}</b>",
        "noargs": "<emoji document_id=5208434048753484584>⛔</emoji> <b>Файл не указан</b>",
        "err": "<emoji document_id=5208434048753484584>⛔</emoji> <b>Ошибка загрузки</b>"
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def _get_file(self, message):
        """Helper to get file from message"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings["reply_to_file"])
            return None
            
        if reply.media:
            file = io.BytesIO(await self.client.download_media(reply.media, bytes))
            if hasattr(reply.media, "document"):
                file.name = reply.file.name or f"file_{reply.file.id}"
            else:
                file.name = f"file_{reply.id}.jpg"
        else:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            file.name = "text.txt"
            
        return file

    async def get_media(self, message: Message):
        reply = await message.get_reply_message()
        m = None
        if reply and reply.media:
            m = reply
        elif message.media:
            m = message
        elif not reply:
            await utils.answer(message, self.strings["noargs"])
            return False

        if not m:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            file.name = "file.txt"
        else:
            file = io.BytesIO(await self.client.download_media(m, bytes))
            file.name = (
                m.file.name
                or (
                    "".join(
                        [
                            random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                            for _ in range(16)
                        ]
                    )
                )
                + m.file.ext
            )

        return file

    async def cbcmd(self, message):
        """Upload file to catbox.moe"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return
        
        try:
            response = requests.post(
                "https://catbox.moe/user/api.php",
                files={"fileToUpload": file},
                data={"reqtype": "fileupload"}
            )
            if response.ok:
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=response.text))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def encmd(self, message):
        """Upload file to envs.sh"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return
            
        try:
            response = requests.post("https://envs.sh", files={"file": file})
            if response.ok:
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=response.text))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def kapcmd(self, message): 
        """Upload file to kappa.lol"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return
            
        try:
            response = requests.post("https://kappa.lol/api/upload", files={"file": file})
            if response.ok:
                data = response.json()
                url = f"https://kappa.lol/{data['id']}"
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=url))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def oxcmd(self, message):
        """Upload file to 0x0.st"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return
            
        try:
            response = requests.post(
                "https://0x0.st",
                files={"file": file}
            )
            if response.ok:
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=response.text))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def x0cmd(self, message):
        """Upload file to x0.at"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return
            
        try:
            response = requests.post("https://x0.at", files={"file": file})
            if response.ok:
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=response.text))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.sudo
    @loader.command(en_doc="Upload file", ru_doc="Upload file to http://ndpropave5.temp.swtest.ru", ua_doc="Upload file to http://ndpropave5.temp.swtest.ru")
    async def ndp(self, message: Message):
        """Upload file"""
        file = await self.get_media(message)
        if not file:
            return
        
        await utils.answer(message, self.strings["uploading"])
        
        try:
            devup = requests.post("http://ndpropave5.temp.swtest.ru", files={"file": file})
        except ConnectionError as e:
            logger.error(f"File uploading error: {e}", exc_info=True)
            await utils.answer(message, self.strings["err"])
            return
        
        link = devup.text
 
        await utils.answer(message, self.strings["uploaded"].format(link_to_file=link))

    async def tmpfilescmd(self, message):
        """Upload file to tmpfiles.org"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return

        try:
            response = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": file}
            )
            if response.ok:
                data = json.loads(response.text)
                url = data["data"]["url"]
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=url))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def pomfcmd(self, message):
        """Upload file to pomf.lain.la"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return

        try:
            response = requests.post(
                "https://pomf.lain.la/upload.php",
                files={"files[]": file}
            )
            if response.ok:
                data = json.loads(response.text)
                url = data["files"][0]["url"]
                await utils.answer(message, self.strings["uploaded"].format(link_to_file=url))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))

    async def bashcmd(self, message):
        """Upload file to bashupload.com"""
        await utils.answer(message, self.strings["uploading"])
        file = await self._get_file(message)
        if not file:
            return

        try:
            response = requests.put(
                "https://bashupload.com",
                data=file.read()
            )
            if response.ok:
                urls = [line for line in response.text.split("\n") if "wget" in line]
                if urls:
                    url = urls[0].split()[-1]
                    await utils.answer(message, self.strings["uploaded"].format(link_to_file=url))
                else:
                    await utils.answer(message, self.strings["error"].format("Could not find URL"))
            else:
                await utils.answer(message, self.strings["error"].format(response.status_code))
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))