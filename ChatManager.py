from typing import List, Union
from telethon.tl.types import Dialog, User, Channel, Chat
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest

from .. import loader, utils


@loader.tds
class ChatManagerMod(loader.Module):
    """📃Модуль для управления чатами на аккаунте"""

    strings = {
        "name": "ChatManager",
        "description": (
            """📃Модуль для управления чатами на аккаунте."""
        ),
        "processing": "⏳ Обработка...",
        "deleted_personal": "✅ Удалено {} личных чатов с удаленными аккаунтами",
        "deleted_all_personal": "✅ Удалено {} личных чатов",
        "left_all_groups": "✅ Вышел из {} групп",
        "left_groups_less": "✅ Вышел из {} групп с количеством участников меньше {}",
        "whitelist_added": "✅ Добавлено в вайтлист: {}",
        "left_groups_not_whitelist": "✅ Вышел из {} групп, не находящихся в вайтлисте",
        "left_channels_not_whitelist": "✅ Вышел из {} каналов, не находящихся в вайтлисте",
        "left_all_channels": "✅ Вышел из {} каналов",
        "whitelist_cleared": "✅ Вайтлист очищен",
        "whitelist_empty": "ℹ️ Вайтлист пуст",
        "whitelist_content": "📋 Содержимое вайтлиста:\n{}",
    }

    def __init__(self):
        self.whitelist: List[int] = []

    async def client_ready(self, client, db):
        self._client = client

    @loader.command(desc="Удалить все личные чаты от удаленных аккаунтов")
    async def deldeleted(self, message):
        """Удаляет все личные чаты с удаленными аккаунтами"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if not isinstance(dialog.entity, User):
                continue

            if dialog.entity.deleted:
                await self._client(DeleteHistoryRequest(
                    peer=dialog.entity,
                    max_id=0,
                    revoke=True
                ))
                count += 1

        await utils.answer(
            message,
            self.strings["deleted_personal"].format(count)
        )

    @loader.command(desc="Удалить все личные чаты")
    async def delallpersonal(self, message):
        """Удаляет все личные чаты (диалоги с пользователями)"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, User):
                await self._client(DeleteHistoryRequest(
                    peer=dialog.entity,
                    max_id=0,
                    revoke=True
                ))
                count += 1

        await utils.answer(
            message,
            self.strings["deleted_all_personal"].format(count)
        )

    @loader.command(desc="Выйти из всех групп")
    async def leaveallgroups(self, message):
        """Выходит из всех групп (не каналов)"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, Chat):
                await self._client(LeaveChannelRequest(dialog.entity))
                count += 1

        await utils.answer(
            message,
            self.strings["left_all_groups"].format(count)
        )

    @loader.command(desc="Выйти из групп с числом участников меньше указанного")
    async def leavegroupsless(self, message):
        """Выходит из групп с числом участников меньше указанного"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await utils.answer(message, "❌ Укажите число участников")
            return

        min_members = int(args)
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, Chat):
                try:
                    participants = await self._client.get_participants(dialog.entity)
                    if len(participants) < min_members:
                        await self._client(LeaveChannelRequest(dialog.entity))
                        count += 1
                except:
                    continue

        await utils.answer(
            message,
            self.strings["left_groups_less"].format(count, min_members)
        )

    @loader.command(desc="Добавить чат в вайтлист (например: -10012345678)")
    async def whitelistadd(self, message):
        """Добавляет чат в вайтлист (из него не будут выходить)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажите ID чата (например: -10012345678)")
            return

        try:
            chat_id = int(args)
            if chat_id not in self.whitelist:
                self.whitelist.append(chat_id)
            await utils.answer(
                message,
                self.strings["whitelist_added"].format(chat_id)
            )
        except ValueError:
            await utils.answer(message, "❌ Неверный ID чата")

    @loader.command(desc="Выйти из групп не из вайтлиста")
    async def leavegroupsnotwl(self, message):
        """Выходит из всех групп, кроме находящихся в вайтлисте"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, Chat):
                if dialog.entity.id not in self.whitelist:
                    await self._client(LeaveChannelRequest(dialog.entity))
                    count += 1

        await utils.answer(
            message,
            self.strings["left_groups_not_whitelist"].format(count)
        )

    @loader.command(desc="Выйти из каналов не из вайтлиста")
    async def leavechannelsnotwl(self, message):
        """Выходит из всех каналов, кроме находящихся в вайтлисте"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, Channel) and not dialog.entity.megagroup:
                if dialog.entity.id not in self.whitelist:
                    await self._client(LeaveChannelRequest(dialog.entity))
                    count += 1

        await utils.answer(
            message,
            self.strings["left_channels_not_whitelist"].format(count)
        )

    @loader.command(desc="Выйти из всех каналов")
    async def leaveallchannels(self, message):
        """Выходит из всех каналов"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            if isinstance(dialog.entity, Channel) and not dialog.entity.megagroup:
                await self._client(LeaveChannelRequest(dialog.entity))
                count += 1

        await utils.answer(
            message,
            self.strings["left_all_channels"].format(count)
        )

    @loader.command(desc="Показать вайтлист")
    async def whitelistshow(self, message):
        """Показывает содержимое вайтлиста"""
        if not self.whitelist:
            await utils.answer(message, self.strings["whitelist_empty"])
            return

        text = "\n".join(str(chat_id) for chat_id in self.whitelist)
        await utils.answer(
            message,
            self.strings["whitelist_content"].format(text)
        )

    @loader.command(desc="Очистить вайтлист")
    async def whitelistclear(self, message):
        """Очищает вайтлист"""
        self.whitelist = []
        await utils.answer(message, self.strings["whitelist_cleared"])

    def __repr__(self):
        return (
            f"<ChatManagerMod whitelist={len(self.whitelist)} items>\n"
        )