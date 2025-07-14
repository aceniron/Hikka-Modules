from telethon import types
from telethon.tl.functions.channels import LeaveChannelRequest
from .. import loader, utils
from telethon.tl.types import Message
from telethon.tl.functions.users import GetFullUserRequest

class ID(loader.Module):
    """Модуль для получения ID пользователей, чатов, каналов и ботов"""

    strings = {
        "name": "ID",
        "help": """
▫️ .userid Показывает список пользователей с их ID
▫️ .channelid Показывает список каналов с их ID
▫️ .botid Показывает список ботов с их ID
▫️ .groupid Показывает список групп/супергрупп с их ID
▫️ .id Получить ID пользователя и отправить его в избранное, а команду удалить
▫️ .leav [ID] -- Покинуть указанный чат или канал
▫️ .myid Показать собственный ID в любом чате, а команду удалить
▫️ .suid Получить реальный ID пользователя/чата/канала в личных сообщениях и отправить его в избранное, затем удалить команду (для каналов нужно иметь разрешение на публикацию постов)
▫️ .uid Показать ID пользователя, на сообщение которого был сделан ответ или по username в любом чате, а команду удалить
▫️ .cgid Получить ID группы/супергруппы в чате или по юзернейму
"""
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.owner
    async def idcmd(self, message):
        """Получить ID пользователя и отправить его в избранное, а команду удалить"""
        await message.delete()
        reply = await message.get_reply_message()
        if not reply:
            await message.client.send_message(message.to_id, "Пожалуйста, ответьте на сообщение пользователя.")
            return

        try:
            user = await message.client.get_entity(reply.sender_id)
            if isinstance(user, types.User):
                await message.client.send_message('me', f"ID пользователя: ⚜{user.id}⚜")
            else:
                await message.client.send_message(message.to_id, "Это не сообщение от пользователя.")
        except Exception as e:
            await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")

    async def myidcmd(self, message):
        """Показать собственный ID в любом чате, а команду удалить"""
        await message.delete()
        reply = await message.get_reply_message()
        if reply:
            await message.client.send_message(message.chat_id, f"Мой ID: ⚜{message.sender_id}⚜", reply_to=reply.id)
        else:
            await message.client.send_message(message.chat_id, f"Мой ID: ⚜{message.sender_id}⚜")

    async def uidcmd(self, message):
        """Показать ID пользователя, на сообщение которого был сделан ответ или по username в любом чате, а команду удалить"""
        await message.delete()
        args = utils.get_args_raw(message)
        
        if args:
            if not args.startswith("@"):
                await message.client.send_message(message.to_id, "Пожалуйста, укажите корректный @username.")
                return

            try:
                user = await message.client.get_entity(args)
                if isinstance(user, types.User):
                    await message.client.send_message(message.chat_id, f"ID пользователя {args}: ⚜{user.id}⚜")
                else:
                    await message.client.send_message(message.to_id, f"{args} не является пользователем.")
            except Exception as e:
                await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")
        else:
            reply = await message.get_reply_message()
            if not reply:
                await message.client.send_message(message.to_id, "❌ Пожалуйста, ответьте на сообщение пользователя.")
                return

            try:
                user = await message.client.get_entity(reply.sender_id)
                if isinstance(user, types.User):
                    await message.client.send_message(message.chat_id, f"Твой ID: ⚜{user.id}⚜", reply_to=reply.id)
                else:
                    await message.client.send_message(message.to_id, "Это не сообщение от пользователя.")
            except Exception as e:
                await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")

    async def suidcmd(self, message):
        """Получить реальный ID пользователя/чата/канала в личных сообщениях и отправить его в избранное, затем удалить команду (для каналов нужно иметь разрешение на публикацию постов)"""
        await message.delete()
        args = utils.get_args_raw(message)
        if args:
            if not args.startswith("@"):
                await message.client.send_message(message.to_id, "Пожалуйста, укажите корректный @username.")
                return

            try:
                user = await message.client.get_entity(args)
                await message.client.send_message('me', f"ID {args}: ⚜{user.id}⚜")
                # Убираем это сообщение
            except Exception as e:
                await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")
        else:
            try:
                user = await message.client.get_entity(message.chat_id)
                await message.client.send_message('me', f"ID: ⚜{user.id}⚜")
                # Убираем это сообщение
            except Exception as e:
                await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")

    async def useridcmd(self, message):
        """Показывает список пользователей с их ID"""
        await message.delete()
        users = []

        async for dialog in message.client.iter_dialogs():
            if isinstance(dialog.entity, types.User) and not dialog.entity.bot:
                if dialog.message:  # Проверка наличия активного диалога
                    users.append((dialog.name or "Без имени", dialog.entity.id))

        result = ""

        if users:
            users_list = "\n|\n".join([f"{name}\n⚜{user_id}⚜" for name, user_id in users])
            result += f"👤 <b>Пользователи:</b>\n{users_list}\n\n"
        else:
            result += "❌ <b>Пользователи не найдены.</b>\n\n"

        await message.client.send_message(message.to_id, result)

    async def channelidcmd(self, message):
        """Показывает список каналов с их ID"""
        await message.delete()
        channels = []

        async for dialog in message.client.iter_dialogs():
            if dialog.is_channel and not dialog.entity.megagroup:
                channels.append((dialog.name or "Без имени", dialog.entity.id, f"-100{abs(dialog.entity.id)}"))

        result = ""

        if channels:
            channels_list = "\n|\n".join([f"{name}\n⚜{channel_id}⚜\n⚜{channel_id_with_prefix}⚜" for name, channel_id, channel_id_with_prefix in channels])
            result += f"📡 <b>Каналы:</b>\n{channels_list}"
        else:
            result += "❌ <b>Каналы не найдены.</b>"

        await message.client.send_message(message.to_id, result)

    async def botidcmd(self, message):
        """Показывает список ботов с их ID"""
        await message.delete()
        bots = []

        async for dialog in message.client.iter_dialogs():
            if isinstance(dialog.entity, types.User) and dialog.entity.bot:
                bots.append((dialog.name or "Без имени", dialog.entity.id))

        result = ""

        if bots:
            bots_list = "\n|\n".join([f"{name}\n⚜{bot_id}⚜" for name, bot_id in bots])
            result += f"🤖 <b>Боты:</b>\n{bots_list}\n\n"
        else:
            result += "❌ <b>Боты не найдены.</b>\n\n"

        await message.client.send_message(message.to_id, result)

    async def groupidcmd(self, message):
        """Показывает список групп/супергрупп с их ID"""
        await message.delete()
        groups = []

        async for dialog in message.client.iter_dialogs():
            if dialog.is_group or (dialog.is_channel and dialog.entity.megagroup):
                groups.append((dialog.name or "Без имени", dialog.entity.id, f"-100{abs(dialog.entity.id)}"))

        result = ""

        if groups:
            groups_list = "\n|\n".join([f"{name}\n⚜{group_id}⚜\n⚜{group_id_with_prefix}⚜" for name, group_id, group_id_with_prefix in groups])
            result += f"📚 <b>Группы:</b>\n{groups_list}\n\n"
        else:
            result += "❌ <b>Группы не найдены.</b>\n\n"

        await message.client.send_message(message.to_id, result)

    async def leavcmd(self, message):
        """[ID] -- Покинуть указанный чат или канал"""
        await message.delete()
        args = utils.get_args_raw(message)
        if not args:
            await message.client.send_message(message.to_id, "<b>Пожалуйста, укажите ID чата или канала.</b>")
            return

        try:
            chat_id = int(args)
            await message.client(LeaveChannelRequest(chat_id))
            await message.client.send_message(message.to_id, f"<b>Успешно покинули чат или канал с ID:</b> ⚜{chat_id}⚜")
        except ValueError:
            await message.client.send_message(message.to_id, "<b>ID должен быть числом.</b>")
        except Exception as e:
            await message.client.send_message(message.to_id, f"<b>Ошибка при попытке покинуть чат или канал:</b> {e}")

    async def cgidcmd(self, message):
        """Получить ID группы/супергруппы в чате или по юзернейму"""
        await message.delete()
        args = utils.get_args_raw(message)

        if args:
            if not args.startswith("@"):
                await message.client.send_message(message.to_id, "Пожалуйста, укажите корректный @username группы.")
                return

            try:
                group = await message.client.get_entity(args)
                if isinstance(group, types.Chat) or (isinstance(group, types.Channel) and group.megagroup):
                    await message.client.send_message(message.to_id, f"ID группы/супергруппы: ⚜{group.id}⚜")
                else:
                    await message.client.send_message(message.to_id, "Это не группа или супергруппа.")
            except Exception as e:
                await message.client.send_message(message.to_id, f"Ошибка: {str(e)}")
        else:
            # Если аргумента нет, работаем с ответом на сообщение
            reply = await message.get_reply_message()

            if not reply or not (reply.is_group or (reply.is_channel and reply.entity.megagroup)):
                await message.client.send_message(message.to_id, "❌ Пожалуйста, ответьте на сообщение группы или супергруппы.")
                return

            group_id = reply.chat.id
            await message.client.send_message(message.to_id, f"ID группы: ⚜{group_id}⚜")