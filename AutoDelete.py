from telethon import events
from .. import loader, utils

class AutoDeleteMod(loader.Module):
    """Модуль для автоматического удаления сообщений"""
    strings = {"name": "AutoDelete"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.auto_delete_modes = self.db.get(self.strings["name"], "modes", {})

    @loader.command()
    async def autodeletecmd(self, message):
        """Включает/выключает режим автоматического удаления"""
        chat_id = str(message.chat_id)
        current_mode = self.auto_delete_modes.get(chat_id, False)
        self.auto_delete_modes[chat_id] = not current_mode
        self.db.set(self.strings["name"], "modes", self.auto_delete_modes)
        await message.delete()

    @loader.watcher()
    async def watcher(self, message):
        chat_id = str(message.chat_id)
        if self.auto_delete_modes.get(chat_id, False) and message.is_channel and not message.out:
            chat = await message.get_chat()
            if chat.megagroup:
                await self.client.delete_messages(chat.id, [message.id])