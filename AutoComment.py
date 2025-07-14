import logging

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class AutoCommentMod(loader.Module):
    """Automatically comments under any channels you want"""

    strings = {
        "name": "AutoComment",
        "disabled": "❌ Disabled",
        "enabled": "✅ Enabled",
        "status_now": "👌 AutoComment was <b>{}</b>!",
        "status_toggle": "Комментим ли мы? <b>{}</b>!",
        "message_set": "Сообщение установлено: <b>{}</b>",
        "channels_set": "Каналы установлены: <b>{}</b>",
        "current_settings": "Текущие настройки:\nСтатус: <b>{}</b>\nСообщение: <b>{}</b>\nКаналы: <b>{}</b>",
    }

    def __init__(self):
        self.status = True
        self.message = "I'm the first! 😎"
        self.channels = []

    @loader.watcher(only_messages=True, only_channels=True)
    async def watcher(self, message):
        if not self.status:
            return
        chat = utils.get_chat_id(message)

        if chat not in self.channels:
            return
        await self.client.send_message(
            entity=chat, message=self.message, comment_to=message
        )
        logger.debug(f"commented on {message.id} in {chat}")

    async def commentcmd(self, message):
        """Toggle Module <on/off>"""
        self.status = not self.status
        status = self.strings["enabled"] if self.status else self.strings["disabled"]
        await utils.answer(message, self.strings["status_now"].format(status))

    async def setcommentcmd(self, message):
        """Set the comment message"""
        new_message = utils.get_args_raw(message)
        self.message = new_message
        await utils.answer(message, self.strings["message_set"].format(new_message))

    async def setchcocmd(self, message):
        """Set the channels (ids)"""
        new_channels = list(map(int, utils.get_args_raw(message).split()))
        self.channels = new_channels
        await utils.answer(message, self.strings["channels_set"].format(new_channels))

    async def showconfigcmd(self, message):
        """Show current configuration"""
        status = self.strings["enabled"] if self.status else self.strings["disabled"]
        await utils.answer(message, self.strings["current_settings"].format(status, self.message, self.channels))