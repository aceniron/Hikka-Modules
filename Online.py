from asyncio import sleep

from .. import loader


@loader.tds
class EternalOnlineMod(loader.Module):
    """Вечный онлайн, который будет читать сообщения в чатах."""

    strings = {"name": "Online"}

    async def client_ready(self, client, db):
        self.db = db

    async def onlinecmd(self, message):
        """Включить вечный онлайн"""
        await message.delete()  # Удаляем команду из чата
        if not self.db.get("Eternal Online", "status"):
            self.db.set("Eternal Online", "status", True)
            while self.db.get("Eternal Online", "status"):
                msg = await message.client.send_message(
                    "me", "Telegram best messenger! 🤩"
                )
                await msg.delete()
                await sleep(1000)

        else:
            self.db.set("Eternal Online", "status", False)

    async def watcher(self, message):
        if self.db.get("Eternal Online", "status"):
            await message.client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )