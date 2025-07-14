from telethon.tl.types import Message
import asyncio
from .. import loader, utils

@loader.tds
class Copilot(loader.Module):
    """
    Бесплатный ChatGPT.
    Сначала запустите бота @CopilotOfficialBot.
    """

    strings = {
        "name": "Copilot",
        "no_args": "🚫 Не указан текст для обработки!",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.gpt_free = "@CopilotOfficialBot"

    async def message_q(self, text: str, user_id: int):
        """Отправляет сообщение и возвращает все ответы (включая текст и медиа)"""
        async with self.client.conversation(user_id) as conv:
            msg = await conv.send_message(text)
            responses = []

            while True:
                response = await conv.get_response()
                if "✅ Запрос отправлен" in response.text or "Ожидание ответа" in response.text:
                    continue

                responses.append(response)

                # Завершаем, если мы не получаем медиа и текст, после чего можно прекратить цикл
                if not response.media and response.text and not response.text.startswith('Ожидание'):
                    break

            return responses

    async def handle_response(self, response: Message, chat_id: int, reply_to: int = None):
        """Пересылает все медиа и текст от бота @CopilotOfficialBot в указанный чат"""
        if response.media:
            # Если медиа (изображение, видео, файл и т.д.), отправляем его в указанный чат
            await self.client.send_file(chat_id, response.media, reply_to=reply_to)
        elif response.text:
            # Если текстовое сообщение, отправляем его в указанный чат
            await self.client.send_message(chat_id, response.text, reply_to=reply_to)

    async def tcmd(self, message: Message):
        """
        {text} - обработать текст через ChatGPT
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if args:
            query = args
        elif reply:
            query = reply.text
        else:
            await message.edit(self.strings["no_args"])
            return

        reply_to = message.reply_to_msg_id if message.is_reply else None  # Получаем ID сообщения, на которое дан ответ, если есть
        chat_id = message.chat_id

        await message.delete()  # Удаляем командное сообщение

        responses = await self.message_q(query, self.gpt_free)

        # Обрабатываем все ответы от бота @CopilotOfficialBot
        for response in responses:
            await self.handle_response(response, chat_id, reply_to)

    async def dgptcmd(self, message: Message):
        """
        - сбросить диалог и начать новый
        """
        await self.message_q("/clear", self.gpt_free)
        await message.delete()  # Удаляем командное сообщение

    async def cimgcmd(self, message: Message):
        """
        {text} - создать изображение через бот и переслать в текущий чат
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if args:
            query = "создай " + args
        elif reply:
            query = "создай " + reply.text
        else:
            await message.edit(self.strings["no_args"])
            return

        bot = self.gpt_free
        reply_to = message.reply_to_msg_id if message.is_reply else None  # Получаем ID сообщения, на которое дан ответ, если есть
        chat_id = message.chat_id

        await message.delete()  # Удаляем командное сообщение

        async with self.client.conversation(bot) as conv:
            await conv.send_message(query)
            response_text = await conv.get_response()
            response_img = await conv.get_response()

            # Пропускаем текст и ждем изображение
            if response_img.media:
                await self.client.send_file(chat_id, response_img.media, reply_to=reply_to)
            else:
                await self.client.send_message(chat_id, "Failed to get image from bot.", reply_to=reply_to)