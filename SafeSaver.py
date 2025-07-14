from .. import loader, utils
from telethon.tl.types import Message
from telethon.tl.functions.messages import ForwardMessagesRequest
import logging
import time

logger = logging.getLogger(__name__)

@loader.tds
class SafeMessageSaverMod(loader.Module):
    """Безопасный сохранятель сообщений"""

    strings = {
        "name": "SafeSaver",
        "saved": "💾 Сохранено как: <code>{}</code>",
        "not_found": "🔍 Не найдено: <code>{}</code>",
        "restored": "",
        "deleted": "🗑 Удалено сохранение: <code>{}</code>",
        "list": "📋 Сохранённые сообщения:\n{}",
        "empty": "📭 Нет сохранённых сообщений",
        "help": (
            "ℹ <b>Команды:</b>\n"
            "<code>.ssave название</code> - сохранить (ответом)\n"
            "<code>.sget название</code> - восстановить\n"
            "<code>.sdel название</code> - удалить\n"
            "<code>.slist</code> - показать всё\n"
            "<code>.shelp</code> - справка"
        ),
    }

    def __init__(self):
        self.storage = {}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.storage = self._db.get("SafeSaver", "storage", {})

    def save_db(self):
        self._db.set("SafeSaver", "storage", self.storage)

    @loader.unrestricted
    async def ssavecmd(self, message: Message):
        """Сохранить сообщение"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["help"])

        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "❌ Ответьте на сообщение")

        self.storage[args.lower()] = {
            "text": reply.text,
            "raw_text": reply.raw_text,
            "date": int(time.time()),
            "chat_id": utils.get_chat_id(message),
            "msg_id": reply.id,
            "is_media": bool(reply.media),
        }

        self.save_db()
        await utils.answer(
            message,
            self.strings["saved"].format(args)
        )

    @loader.unrestricted
    async def sgetcmd(self, message: Message):
        """Восстановить сообщение"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["help"])

        key = args.lower()
        if key not in self.storage:
            return await utils.answer(
                message,
                self.strings["not_found"].format(key)
            )

        saved = self.storage[key]
        try:
            await self._client(ForwardMessagesRequest(
                from_peer=saved["chat_id"],
                id=[saved["msg_id"]],
                to_peer=utils.get_chat_id(message),
                drop_author=True,
                noforwards=False
            ))
            await message.delete() # Удаляем команду после успешного выполнения

        except Exception as e:
            logger.error(f"Ошибка пересылки: {e}")
            await utils.answer(
                message,
                f"Произошла ошибка при восстановлении."
            )

    @loader.unrestricted
    async def sdelcmd(self, message: Message):
        """Удалить сохранение"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["help"])

        key = args.lower()
        if key in self.storage:
            del self.storage[key]
            self.save_db()
            await utils.answer(
                message,
                self.strings["deleted"].format(key)
            )
        else:
            await utils.answer(
                message,
                self.strings["not_found"].format(key)
            )

    @loader.unrestricted
    async def slistcmd(self, message: Message):
        """Показать список"""
        if not self.storage:
            return await utils.answer(message, self.strings["empty"])

        items = [
            f"• <code>{name}</code> - {data['text'][:30]}..."
            for name, data in self.storage.items()
        ]
        await utils.answer(
            message,
            self.strings["list"].format("\n".join(items))
        )

    @loader.unrestricted
    async def shelpcmd(self, message: Message):
        """Показать справку"""
        await utils.answer(message, self.strings["help"])