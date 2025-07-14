import asyncio

from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class FuckChatMod(loader.Module):
    """Auto-read tags and messages in selected chats"""

    strings = {
        "name": "FuckChat",
        "args": "🚫 <b>Incorrect args specified</b>",
        "on": "✅ <b>Now I ignore tags and auto-read messages in this chat</b>",
        "off": "✅ <b>Now I don't ignore tags and auto-read messages in this chat</b>",
    }

    strings_ru = {
        "args": "🚫 <b>Указаны неверные аргументы</b>",
        "on": "✅ <b>Теперь я буду игнорировать теги и автоматически читать сообщения в этом чате</b>",
        "off": "✅ <b>Теперь я не буду игнорировать теги и автоматически читать сообщения в этом чате</b>",
    }

    async def client_ready(self, client, db):
        self._ratelimit = []

    async def fuckallcmd(self, message: Message):
        """[chat_id,...] - Toggle notags and autoread for specified chat IDs"""
        args = utils.get_args_raw(message)
        chat_ids = [int(cid.strip()) for cid in args.split(",")]

        for cid in chat_ids:
            self._ratelimit = list(set(self._ratelimit) - set([cid]))

            if cid not in self.get("tags", []):
                self.set("tags", self.get("tags", []) + [cid])
                self.set("strict", self.get("strict", []) + [cid])
            else:
                self.set(
                    "tags",
                    list(set(self.get("tags", [])) - set([cid])),
                )
                self.set(
                    "strict",
                    list(set(self.get("strict", [])) - set([cid])),
                )

        await message.delete()

    async def fuckclearcmd(self, message: Message):
        """Очистить список чатов и отключить функционал fuckall"""
        self.set("tags", [])
        self.set("strict", [])
        await utils.answer(message, "✅ <b>Список чатов очищен, функционал отключен.</b>")

    async def fuckchatscmd(self, message: Message):
        """Показать активные авточтения в чатах"""
        res = "<b>== Active Chats ==</b>\n"
        for chat in self.get("tags", []):
            res += f"{chat}\n"

        await utils.answer(message, res)

    async def watcher(self, message: Message):
        if not hasattr(message, "text") or not isinstance(message, Message):
            return

        chat_id = utils.get_chat_id(message)
        if hasattr(message.peer_id, "channel_id"):
            chat_id = message.peer_id.channel_id

        if chat_id in self.get("tags", []) and message.mentioned:
            await self._client.send_read_acknowledge(
                message.peer_id,
                message,
                clear_mentions=True,
            )

        elif chat_id in self.get("strict", []):
            await self._client.send_read_acknowledge(message.peer_id, message)

    @loader.command()
    async def fuckid(self, message: Message):
        """Показывает список всех групп, на которые подписаны"""
        groups = []

        async for dialog in message.client.iter_dialogs():
            if dialog.is_group or (dialog.is_channel and dialog.entity.megagroup):
                groups.append((dialog.name or "Без имени", dialog.entity.id))

        result = ""

        if groups:
            groups_list = "\n".join([f"{name} - ⚜{group_id}⚜" for name, group_id in groups])
            result += f"📚 <b>Группы:</b>\n{groups_list}"
        else:
            result += "❌ <b>Группы не найдены.</b>"

        await message.edit(result)