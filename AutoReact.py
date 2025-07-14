from telethon import events, types
from .. import loader, utils
import logging

@loader.tds
class AutoReactMod(loader.Module):
    strings = {
        "name": "AutoReact",
        "enabled": "✅ Автореакции включены в группе с ID: {}",
        "disabled": "🚫 Автореакции выключены в группе с ID: {}",
        "reaction_set": "✅ Установлена реакция: {}",
        "no_reaction": "⚠️ Укажите эмодзи или его ID для реакции",
        "group_list": "📄 Список групп с автореакциями: {}",
        "user_added": "✅ Пользователь с ID {} добавлен в список",
        "user_list": "📄 Список пользователей с автореакциями: {}",
        "groups_cleared": "🗑️ Список групп очищен",
        "users_cleared": "🗑️ Список пользователей очищен",
        "subscribed_groups": "📄 Список подписанных групп:\n{}",
        "current_reaction": "Текущая реакция: {}"
    }

    def __init__(self):
        self.current_reaction = "👍"
        self.active_chats = {}
        self.user_list = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.active_chats = self.get("active_chats", {})
        self.user_list = self.get("user_list", [])

    def save_active_chats(self):
        self.set("active_chats", self.active_chats)

    def save_user_list(self):
        self.set("user_list", self.user_list)

    @loader.command(ru_doc="Включить/выключить автореакции в указанной группе")
    async def addg(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_reaction"])
            return

        chat_id = args.strip()
        
        if chat_id in self.active_chats:
            del self.active_chats[chat_id]
            status = False
        else:
            self.active_chats[chat_id] = True
            status = True
            
        self.save_active_chats()
        
        await utils.answer(
            message,
            self.strings["enabled"].format(chat_id) if status else self.strings["disabled"].format(chat_id)
        )

    @loader.command(ru_doc="Показать список групп с автореакциями")
    async def showg(self, message):
        await utils.answer(message, self.strings["group_list"].format(", ".join(self.active_chats.keys())))

    @loader.command(ru_doc="Добавить пользователя по его ID")
    async def addu(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_reaction"])
            return

        user_id = args.strip()
        if user_id not in self.user_list:
            self.user_list.append(user_id)
            self.save_user_list()
            await utils.answer(message, self.strings["user_added"].format(user_id))
        else:
            await utils.answer(message, f"⚠️ Пользователь с ID {user_id} уже в списке.")

    @loader.command(ru_doc="Показать список пользователей с автореакциями")
    async def showu(self, message):
        await utils.answer(message, self.strings["user_list"].format(", ".join(self.user_list)))

    @loader.command(ru_doc="Очистить список групп с автореакциями")
    async def clup(self, message):
        self.active_chats.clear()
        self.save_active_chats()
        await utils.answer(message, self.strings["groups_cleared"])

    @loader.command(ru_doc="Очистить список пользователей с автореакциями")
    async def cles(self, message):
        self.user_list.clear()
        self.save_user_list()
        await utils.answer(message, self.strings["users_cleared"])

    @loader.command(ru_doc="Установить реакцию (обычный эмодзи или ID)")
    async def semo(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_reaction"])
            return
        
        self.current_reaction = args
        await utils.answer(message, self.strings["reaction_set"].format(args))

    @loader.command(ru_doc="Показать текущую реакцию")
    async def showr(self, message):
        await utils.answer(message, self.strings["current_reaction"].format(self.current_reaction))

    @loader.watcher()
    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return
            
        chat_id = str(message.chat_id)
        
        if chat_id not in self.active_chats or str(message.sender_id) not in self.user_list:
            return

        try:
            await message.react(self.current_reaction)
        except Exception as e:
            logging.error(f"Ошибка при установке реакции: {str(e)}")

    @loader.command(ru_doc="Показать список групп, на которые вы подписаны")
    async def mygroups(self, message):
        groups = []
        async for dialog in self._client.iter_dialogs():
            if dialog.is_group:
                groups.append(f"{dialog.name}\n{dialog.id}")

        await utils.answer(message, self.strings["subscribed_groups"].format("\n|\n".join(groups)))