from .. import loader, utils
from asyncio import sleep, gather
from telethon.tl.functions.channels import JoinChannelRequest

def register(cb):
    cb(SpamMod())

class SpamMod(loader.Module):
    """Спам модуль с поддержкой топиков"""
    strings = {'name': 'Spam'}

    def __init__(self):
        self.saved_message = None
        self.saved_media = None

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def spamcmd(self, message):
        """Обычный спам. Используй .spam <кол-во:int> <текст или ничего для сохраненного сообщения>."""

        try:
            await message.delete()
            args = utils.get_args(message)
            if len(args) < 1:
                raise ValueError("Недостаточно аргументов")
            
            count = int(args[0].strip())  # Количество повторений
            spam_text = " ".join(args[1:]).strip() if len(args) > 1 else None  # Текст для спама

            # Используем сохранённое сообщение, если текст не указан
            text_to_spam = spam_text or self.saved_message
            media_to_spam = self.saved_media if not spam_text else None

            if not text_to_spam and not media_to_spam:
                raise ValueError("Нет текста или сохраненного сообщения для спама. Используй .adspm для сохранения сообщения.")

            # Проверяем, работает ли команда в чатах с топиками
            if hasattr(message.peer_id, "channel_id") and hasattr(message, "reply_to_top_id"):
                reply_to = message.reply_to_top_id  # Для топиков
            else:
                reply_to = None

            # Отправляем спам
            for _ in range(count):
                if media_to_spam:
                    await message.client.send_file(
                        message.to_id, media_to_spam, caption=text_to_spam, reply_to=reply_to
                    )
                else:
                    await message.client.send_message(
                        message.to_id, text_to_spam, reply_to=reply_to
                    )

        except Exception as e:
            await message.client.send_message(message.to_id, f'Ошибка: {str(e)}\nИспользуй: .spam <кол-во:int> <текст или ничего для сохраненного сообщения>.')

    async def adspmcmd(self, message):
        """Сохранить сообщение или сообщение с медиа. Используй .adspm <текст> или ответ на медиа."""
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        if reply and reply.media:
            self.saved_media = reply.media
            self.saved_message = reply.message or None
        else:
            self.saved_message = args
            self.saved_media = None

        await message.edit("Сообщение сохранено для спама.")

    async def clspmcmd(self, message):
        """Очистить сохраненное сообщение для спама."""
        
        self.saved_message = None
        self.saved_media = None

        await message.edit("Сохраненное сообщение для спама очищено.")

    async def lispmcmd(self, message):
        """Показать сохраненное сообщение для спама."""

        if self.saved_message or self.saved_media:
            if self.saved_media:
                await message.client.send_file(message.to_id, self.saved_media, caption=self.saved_message)
            else:
                await message.edit(self.saved_message)
        else:
            await message.edit("Нет сохраненного сообщения для спама.")