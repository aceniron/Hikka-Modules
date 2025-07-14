from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import GetForumTopicsRequest  # ВАЖНО: правильный импорт
from .. import loader, utils


@loader.tds
class MyMessagesCleanerMod(loader.Module):
    """🧹 Удаляет все ваши сообщения из всех чатов, включая группы с темами (форумы), не выходя из них"""

    strings = {
        "name": "MyMessagesCleaner",
        "processing": "⏳ Удаляю ваши сообщения...",
        "done": "✅ Удалено {} сообщений",
    }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command(desc="Удаляет все ваши сообщения из всех чатов, включая группы с темами (форумы), не выходя из них")
    async def delmymsgs(self, message):
        """Удаляет все ваши сообщения из всех чатов (включая темы в форумах)"""
        await utils.answer(message, self.strings["processing"])
        count = 0

        async for dialog in self._client.iter_dialogs():
            entity = dialog.entity

            # Пропустить новостные каналы (не мегагруппы)
            if isinstance(entity, Channel) and not entity.megagroup:
                continue

            # Удаление сообщений в обычных чатах и ЛС
            try:
                async for msg in self._client.iter_messages(dialog.id, from_user="me"):
                    try:
                        await msg.delete()
                        count += 1
                    except:
                        continue
            except:
                continue

            # Удаление сообщений в форумах (группах с темами)
            if isinstance(entity, Channel) and getattr(entity, "megagroup", False) and getattr(entity, "forum", False):
                try:
                    result = await self._client(GetForumTopicsRequest(
                        channel=entity,
                        offset_date=0,
                        offset_id=0,
                        offset_topic=0,
                        limit=100
                    ))
                    for topic in result.topics:
                        try:
                            async for msg in self._client.iter_messages(
                                entity,
                                from_user="me",
                                thread_id=topic.id
                            ):
                                try:
                                    await msg.delete()
                                    count += 1
                                except:
                                    continue
                        except:
                            continue
                except:
                    continue

        await utils.answer(message, self.strings["done"].format(count))