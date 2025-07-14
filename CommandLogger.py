from telethon import events, functions, types
from .. import loader, utils
import datetime
from PIL import Image, ImageDraw, ImageFont
import io

class CommandLoggerMod(loader.Module):
    """Логирование использованных команд в выбранный канал или группу"""
    strings = {"name": "CommandLogger"}

    def __init__(self):
        self.client = None
        self.logging_enabled = False  # Логирование по умолчанию выключено
        self.log_chat = None  # Хранит ID или username канала для логов

    async def client_ready(self, client, db):
        """Этот метод выполняется, когда бот готов к работе."""
        self.client = client
        await self.ensure_log_group()

    async def ensure_log_group(self):
        """Проверка существования группы с названием 'Command Logger' и создание новой при необходимости"""
        async for dialog in self.client.iter_dialogs():
            if dialog.name == "Command Logger" and isinstance(dialog.entity, types.Chat):
                self.log_chat = dialog.entity.id
                print(f"Существующая группа 'Command Logger' найдена с ID: {self.log_chat}")
                return

        try:
            result = await self.client(functions.messages.CreateChatRequest(
                users=[],
                title="Command Logger"
            ))
            self.log_chat = result.chats[0].id
            print(f"Приватная группа 'Command Logger' создана с ID: {self.log_chat}")
        except Exception as e:
            print(f"Ошибка при создании приватной группы: {e}")

    async def log_command(self, event):
        """Логирование команды в выбранный канал/чат"""
        if not self.logging_enabled or not self.log_chat:
            return

        try:
            message = event.raw_text
            command = message.split()[0] if message else "Неизвестно"

            # Пропуск команды .cmdlog
            if command == ".cmdlog":
                return

            args = " ".join(message.split()[1:]) if len(message.split()) > 1 else "Нет аргументов"
            timestamp = datetime.datetime.now()
            time_str = timestamp.strftime("%H:%M")  # Время
            date_str = timestamp.strftime("%d.%m.%y")  # Дата

            log_text = f"Время: {time_str}\n|\nДата: {date_str}\n|\nКоманда: {command}\n|\nАргументы: {args}"

            await self.client.send_message(self.log_chat, log_text)
        except Exception as e:
            # Логирование ошибки, если не удалось отправить сообщение
            print(f"Ошибка при попытке отправить лог: {e}")

    async def watcher(self, event):
        """Отслеживание команд в любом чате, где начинается с точки"""
        if not event.text.startswith("."):
            return

        # Если логирование включено, отправляем логи в выбранный чат
        if self.logging_enabled:
            # Проверяем, что команда не была вызвана в чате для логирования
            if event.chat and event.chat.id != self.log_chat:
                await self.log_command(event)

    async def cmdlogcmd(self, message):
        """Команда для включения/выключения логирования команд"""
        self.logging_enabled = not self.logging_enabled

        if self.logging_enabled:
            await message.edit(f"📋 Логирование команд включено. Логи будут отправляться в группу 'Command Logger'.")
        else:
            await message.edit(f"📋 Логирование команд выключено для группы 'Command Logger'.")