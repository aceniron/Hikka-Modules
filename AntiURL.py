from .. import loader
import re
import logging
from telethon.tl.patched import Message

logger = logging.getLogger(__name__)

class AntiURLMod(loader.Module):
    strings = {"name": "AntiURL"}

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client
        self.chats = self._db.get(self.strings["name"], "chats", [])

    async def linkcmd(self, message):
        """Turn link deletion mode on or off"""
        chat_id = message.chat.id
        if chat_id in self.chats:
            self.chats.remove(chat_id)
        else:
            self.chats.append(chat_id)
        self._db.set(self.strings["name"], "chats", self.chats)
        await message.delete()

    async def watcher(self, message):
        if getattr(message, "sender_id", None) != self._client._tg_id and bool(
            re.findall(
                r"""(?i)\b((?:https?://|t.me|rt|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))|(@\w+)""",
                message.text,
            )
            and message.chat.id in self.chats
        ):
            await message.delete()