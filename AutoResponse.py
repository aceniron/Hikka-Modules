from .. import loader, utils
import time

@loader.tds
class AutoResponse(loader.Module):
    """Модуль автоответчик."""

    strings = {
        "name": "AutoResponse",
        "module_enabled": "<emoji document_id=5264971795647184318>✅</emoji> <b>Автоответчик включен.</b>",
        "module_disabled": "<emoji document_id=5262642849630926308>❌</emoji> <b>Автоответчик выключен.</b>",
        "reset": "<emoji document_id=5345794417208861153>🔄</emoji> <b>Список пользователей с сработавшим автоответчиком сброшен.</b>",
        "message_cleared": "<emoji document_id=5345794417208861153>🔄</emoji> <b>Сообщение сброшено до начальных значений.</b>",
        "settings": "<b>Текущие настройки:</b>\n\n<b>Автоответчик включен:</b> {is_active}\n<b>Интервал повторного ответа:</b> {response_interval} часов\n<b>Количество отправок сообщения:</b> {numbs}\n<b>Отправка как ответ:</b> {reply}",
        "message_saved": "<b>Сообщение автоответчика сохранено.</b>"
    }

    def __init__(self):
        self.message = "Привет %name%! Это автоответчик. Я свяжусь с вами позже."
        self.urls = None
        self.reply = False
        self.numbs = "one"
        self.response_interval = 0
        self.is_active = False
        self.replied_users = {}
        self.allow_next_message = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.replied_users = self.db.get("AutoResponse", "replied_users", {})
        self.is_active = self.db.get("AutoResponse", "is_active", True)
        self.allow_next_message = self.db.get("AutoResponse", "allow_next_message", {})

    async def watcher(self, message):
        if not self.is_active:
            return
        if not message.is_private or message.out:
            return

        sender_id = message.sender_id
        sender = await self.client.get_entity(sender_id)
        
        # Проверка, чтобы автоответчик не действовал на ботов
        if sender.bot:
            return

        current_time = time.time()

        if self.numbs == "one" and sender_id in self.replied_users:
            last_response_time = self.replied_users[sender_id]
            response_interval = self.response_interval * 3600
            if response_interval == 0 or (current_time - last_response_time) < response_interval:
                return

        first_name = sender.first_name
        response_message = self.message.replace("%name%", first_name)

        if self.urls:
            if self.reply:
                await self.client.send_file(message.sender_id, self.urls, caption=response_message, reply_to=message.id)
            else:
                await self.client.send_file(message.sender_id, self.urls, caption=response_message)
        else:
            if self.reply:
                await self.client.send_message(message.sender_id, response_message, reply_to=message.id)
            else:
                await self.client.send_message(message.sender_id, response_message)

        self.replied_users[sender_id] = current_time
        self.allow_next_message[sender_id] = True
        self.db.set("AutoResponse", "replied_users", self.replied_users)
        self.db.set("AutoResponse", "allow_next_message", self.allow_next_message)

        if sender_id in self.allow_next_message and self.allow_next_message[sender_id]:
            self.allow_next_message[sender_id] = False
            self.db.set("AutoResponse", "allow_next_message", self.allow_next_message)
        else:
            async for msg in self.client.iter_messages(sender_id, from_user='me'):
                await msg.delete()
            async for msg in self.client.iter_messages(sender_id):
                await msg.delete()

    @loader.command()
    async def setmesse(self, message):
        """Установить сообщение автоответчика в ответ на сообщение или сообщения с медиафайлом."""
        reply = await message.get_reply_message()
        if reply:
            self.message = reply.text or ""
            self.urls = await self.client.download_media(reply, file=bytes)  # Загрузка файла
            await message.edit(self.strings["message_saved"])
        else:
            await message.edit("<b>Пожалуйста, используйте эту команду в ответ на сообщение или сообщение с медиафайлом.</b>")

    @loader.command()
    async def setreply(self, message):
        """Установить отправку сообщения как ответ (True/False)."""
        self.reply = utils.get_args_raw(message).lower() == "true"
        await message.edit(f"Отправка как ответ установлена: {self.reply}")

    @loader.command()
    async def setnumbes(self, message):
        """Установить количество отправок сообщения ('one' или 'all')."""
        self.numbs = utils.get_args_raw(message)
        await message.edit(f"Количество отправок сообщения установлено: {self.numbs}")

    @loader.command()
    async def setint(self, message):
        """Установить интервал повторного ответа в часах."""
        self.response_interval = int(utils.get_args_raw(message))
        await message.edit(f"Интервал повторного ответа установлен: {self.response_interval} часов")

    @loader.command()
    async def sendresponse(self, message):
        """Отправить ответное сообщение или сообщение с файлом."""
        sender_id = message.sender_id
        sender = await self.client.get_entity(sender_id)
        first_name = sender.first_name
        response_message = self.message.replace("%name%", first_name)
        
        if self.urls:
            await self.client.send_file(sender_id, self.urls, caption=response_message)
        else:
            await self.client.send_message(sender_id, response_message)

    @loader.command()
    async def enable(self, message):
        """Включить автоответчик."""
        self.is_active = True
        self.db.set("AutoResponse", "is_active", True)
        await message.edit(self.strings["module_enabled"])

    @loader.command()
    async def disable(self, message):
        """Выключить автоответчик."""
        self.is_active = False
        self.db.set("AutoResponse", "is_active", False)
        await message.edit(self.strings["module_disabled"])

    @loader.command()
    async def reset(self, message):
        """Сбросить список пользователей с сработавшим автоответчиком."""
        self.replied_users.clear()
        self.db.set("AutoResponse", "replied_users", {})
        await message.edit(self.strings["reset"])

    @loader.command()
    async def clearmessage(self, message):
        """Очистить сообщение автоответчика."""
        self.message = "Привет %name%! Это автоответчик. Я свяжусь с вами позже."
        self.urls = None
        await message.edit(self.strings["message_cleared"])

    @loader.command()
    async def showsettings(self, message):
        """Показать текущие настройки автоответчика."""
        settings = self.strings["settings"].format(
            is_active="Да" if self.is_active else "Нет",
            response_interval=self.response_interval,
            numbs=self.numbs,
            reply="Да" if self.reply else "Нет"
        )
        await message.edit(settings)