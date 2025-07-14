from .. import loader, utils
from telethon import events, types
import asyncio

@loader.tds
class Cleaner(loader.Module):
    """Автоматическая очистка чата и канала от стикеров, войсов, медиа и других типов сообщений"""

    strings = {
        "name": "Cleaner",
        "cleaned": "🧹 Удалено {} сообщений",
        "no_permission": "⚠️ Недостаточно прав для удаления сообщений",
        "total_messages": "Всего {} публикаций"
    }

    def __init__(self):
        self.active_chats = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.active_chats = self.db.get(__name__, "active_chats", {})

        async def cleaner_handler(event):
            chat_id = str(event.chat_id)
            if chat_id not in self.active_chats:
                return

            try:
                participant = await event.client.get_permissions(event.chat_id)
                if not participant.delete_messages:
                    print(f"Недостаточно прав для удаления сообщений в чате {chat_id}")
                    return
            except Exception as e:
                print(f"Ошибка получения прав для чата {chat_id}: {e}")
                return

            should_delete = False

            if event.message.sticker:
                should_delete = True
            elif event.message.voice:
                should_delete = True
            elif event.message.media:
                should_delete = True
            elif event.message.forward:
                should_delete = True

            if should_delete:
                await asyncio.sleep(60)
                try:
                    await event.message.delete()
                except:
                    pass

        self.handler = cleaner_handler
        client.add_event_handler(self.handler, events.NewMessage())

    @loader.command()
    async def cleanum(self, message):
        """Очистить последние сообщения в чате или канале: .cleanum <количество>"""
        if not message.is_reply and not utils.get_args_raw(message):
            await utils.answer(message, "⚠️ Укажите количество сообщений для удаления")
            return

        try:
            count = int(utils.get_args_raw(message)) if utils.get_args_raw(message) else 100
        except:
            count = 100

        try:
            deleted = 0
            async for msg in message.client.iter_messages(message.chat_id, limit=count):
                try:
                    await msg.delete()
                    deleted += 1
                except:
                    continue

            await utils.answer(message, self.strings["cleaned"].format(deleted))
        except:
            await utils.answer(message, self.strings["no_permission"])

    @loader.command()
    async def cleansms(self, message):
        """Отобразить количество всех сообщений в канале или группе"""
        chat_id = message.chat_id

        try:
            total_messages = 0
            async for _ in message.client.iter_messages(chat_id):
                total_messages += 1
            total_messages_text = self.strings["total_messages"].format(total_messages)

            # Отправить сообщение в избранное
            await message.client.send_message('me', total_messages_text)

            # Удалить команду из чата
            await message.delete()

        except Exception as e:
            await utils.answer(message, f"Ошибка при подсчете сообщений: {e}")