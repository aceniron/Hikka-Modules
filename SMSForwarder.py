from telethon import events
from .. import loader

class SMSForwarderMod(loader.Module):
    """Модуль для копирования сообщений из @fakemailbot в Избранное, без подписей"""

    strings = {"name": "SMSForwarder"}
    is_enabled = False

    async def smsoncmd(self, message):
        """Включить копирование сообщений из @fakemailbot в Избранное"""
        self.is_enabled = True
        await message.edit("✅ Копирование сообщений из @fakemailbot в Избранное включено!")

    async def smsoffcmd(self, message):
        """Отключить копирование сообщений из @fakemailbot в Избранное"""
        self.is_enabled = False
        await message.edit("❌ Копирование сообщений из @fakemailbot в Избранное отключено!")

    async def watcher(self, message):
        """Отслеживает сообщения от @fakemailbot и пересылает их в Избранное"""
        if self.is_enabled and message.sender_id == (await message.client.get_entity("fakemailbot")).id:
            try:
                # Проверяем, содержит ли сообщение медиа
                if message.media:
                    # Отправка медиа без подписи
                    await message.client.send_file("me", message.media)
                else:
                    # Отправка текста
                    await message.client.send_message("me", message.raw_text)
            except Exception as e:
                await message.respond(f"⚠ Ошибка при отправке сообщения в Избранное: {e}")