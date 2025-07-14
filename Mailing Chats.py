from .. import loader, utils
import asyncio
import logging

@loader.tds
class MailingChatsMod(loader.Module):
    """🪐 Модуль для параллельной рассылки сохранённых сообщений по чатам и топикам"""

    strings = {
        "name": "Mailing Chats",
        "chat_added": "✅ Чат {} добавлен",
        "chat_removed": "❌ Чат {} удалён",
        "no_chats": "📋 Список чатов пуст",
        "chats_list": "📝 Чаты:\n{}",
        "saved": "💾 Сохранено сообщений: {}",
        "no_saved": "📂 Нет сохранённых сообщений",
        "cleared": "🧹 Сообщения очищены",
        "broadcast_started": "📡 Рассылка запущена",
        "broadcast_stopped": "🛑 Рассылка остановлена",
        "tag_status": "🏷️ Статус тегов: {}"
    }

    def __init__(self):
        self.broadcasting = False

    def _get_chats(self): return self.db.get(self.strings["name"], "chats", [])
    def _save_chats(self, chats): self.db.set(self.strings["name"], "chats", chats)
    def _get_saved_msgs(self): return self.db.get(self.strings["name"], "saved_msgs", [])
    def _save_msgs(self, msgs): self.db.set(self.strings["name"], "saved_msgs", msgs)
    def _get_delay(self): return self.db.get(self.strings["name"], "delay_seconds", 2)
    def _get_tags_enabled(self): return self.db.get(self.strings["name"], "tags_enabled", False)
    def _set_tags_enabled(self, value): self.db.set(self.strings["name"], "tags_enabled", value)
    def _get_usertag_filter(self): return self.db.get(self.strings["name"], "usertag_filter", "0")
    def _set_usertag_filter(self, value): self.db.set(self.strings["name"], "usertag_filter", value)

    def _normalize_chat(self, chat_raw):
        try:
            if chat_raw.startswith("@"): return chat_raw
            chat_id = int(chat_raw)
            if chat_id > 1000000000000: return chat_id
            if not str(chat_id).startswith("-100"): return int("-100" + str(chat_id))
            return chat_id
        except Exception: return chat_raw

    @loader.command()
    async def addchatr(self, message):
        """Добавить чаты для рассылки: @user, 2847..., -100..."""
        raw = utils.get_args_raw(message)
        if not raw: return await message.edit("❌ Укажи чаты через запятую")
        chats = [self._normalize_chat(c.strip()) for c in raw.split(",")]
        current = self._get_chats()
        added = [str(c) for c in chats if c not in current]
        self._save_chats(current + chats)
        await message.edit(f"{self.strings['chat_added'].format(', '.join(added))}")

    @loader.command()
    async def delchatr(self, message):
        """Удалить указанные чаты из списка"""
        raw = utils.get_args_raw(message)
        if not raw: return await message.edit("❌ Укажи чаты через запятую")
        chats = [self._normalize_chat(c.strip()) for c in raw.split(",")]
        current = self._get_chats()
        remaining = [c for c in current if c not in chats]
        removed = [str(c) for c in chats if c in current]
        self._save_chats(remaining)
        await message.edit(f"{self.strings['chat_removed'].format(', '.join(removed))}")

    @loader.command()
    async def listchatr(self, message):
        """Показать список добавленных чатов"""
        chats = self._get_chats()
        if not chats: return await message.edit(self.strings["no_chats"])
        await message.edit(self.strings["chats_list"].format("\n".join([str(c) for c in chats])))

    @loader.command()
    async def clearchatr(self, message):
        """Очистить список всех чатов"""
        self._save_chats([])
        await message.edit("🧹 Список чатов очищен")

    @loader.command()
    async def savemail(self, message):
        """Сохраняет сообщение, на которое ты ответил"""
        if not message.reply_to: return await message.edit("❌ Ответь на сообщение для сохранения")
        msg = await message.get_reply_message()
        saved = self._get_saved_msgs()
        saved.append((message.chat_id, msg.id))
        self._save_msgs(saved)
        await message.edit(self.strings["saved"].format(len(saved)))

    @loader.command()
    async def showmail(self, message):
        """Показать все сохранённые сообщения"""
        saved = self._get_saved_msgs()
        if not saved: return await message.edit(self.strings["no_saved"])
        for chat_id, msg_id in saved:
            try:
                msg = await message.client.get_messages(chat_id, ids=msg_id)
                if msg.media:
                    await message.client.send_file(message.chat_id, msg.media, caption=msg.message or "")
                else:
                    await message.client.send_message(message.chat_id, msg.message or "")
                await asyncio.sleep(0.5)
            except Exception as e:
                logging.error(f"Ошибка получения {msg_id} из {chat_id}: {e}")

    @loader.command()
    async def clearmail(self, message):
        """Удалить все сохранённые сообщения"""
        self._save_msgs([])
        await message.edit(self.strings["cleared"])

    @loader.command()
    async def setdelay(self, message):
        """Установить задержку между отправками"""
        raw = utils.get_args_raw(message)
        try:
            sec = float(raw)
            if sec < 0: raise ValueError
            self.db.set(self.strings["name"], "delay_seconds", sec)
            await message.edit(f"⚙️ Задержка установлена: {sec} сек")
        except Exception: await message.edit("❌ Введите число >= 0")

    @loader.command()
    async def settags(self, message):
        """Включить или отключить тегание участников"""
        raw = utils.get_args_raw(message).lower()
        if raw not in ["true", "false"]: return await message.edit("❌ Укажите true или false")
        self._set_tags_enabled(raw == "true")
        await message.edit(f"🏷️ Теги включены: {raw == 'true'}")

    @loader.command()
    async def tagsstatus(self, message):
        """Показать, включены ли теги"""
        status = self._get_tags_enabled()
        await message.edit(self.strings["tag_status"].format(status))

    @loader.command()
    async def usertag(self, message):
        """Установить фильтр usertag: ID или @username через запятую"""
        raw = utils.get_args_raw(message)
        if not raw: return await message.edit("❌ Укажи хотя бы один ID или @username через запятую")
        self._set_usertag_filter(raw)
        await message.edit(f"✅ usertag установлен: {raw}")

    @loader.command()
    async def usertaglist(self, message):
        """Показать текущий список usertag"""
        taglist = self._get_usertag_filter()
        await message.edit(f"📋 Текущий usertag: {taglist}")

    @loader.command()
    async def clearusertag(self, message):
        """Сбросить usertag — теперь тегаются все"""
        self._set_usertag_filter("0")
        await message.edit("🧹 usertag сброшен до 0 — теперь тегаются все")

    @loader.command()
    async def mailall(self, message):
        """Запустить рассылку по всем чатам"""
        chats_raw = self._get_chats()
        msgs = self._get_saved_msgs()
        delay = self._get_delay()
        tags_enabled = self._get_tags_enabled()
        usertag = self._get_usertag_filter()
        if not chats_raw: return await message.edit(self.strings["no_chats"])
        if not msgs: return await message.edit(self.strings["no_saved"])
        self.broadcasting = True
        await message.edit(self.strings["broadcast_started"])

        entities = []
        for raw in chats_raw:
            try:
                entity = await message.client.get_input_entity(self._normalize_chat(str(raw)))
                entities.append(entity)
            except Exception as e:
                logging.error(f"Не удалось получить {raw}: {e}")

        tag_targets = [i.strip().lstrip("@").lower() for i in usertag.split(",")] if usertag != "0" else []

        while self.broadcasting:
            for chat_id, msg_id in msgs:
                if not self.broadcasting: break
                try:
                    original = await message.client.get_messages(chat_id, ids=msg_id)
                except Exception as e:
                    logging.error(f"Ошибка получения {msg_id} из {chat_id}: {e}")
                    continue

                for entity in entities:
                    if not self.broadcasting: break
                    final_text = original.message or ""

                    if tags_enabled:
                        try:
                            users = []
                            async for user in message.client.iter_participants(entity):
                                if user.bot: continue
                                uid = str(user.id)
                                uname = (user.username or "").lower()
                                if usertag == "0" or uid in tag_targets or uname in tag_targets:
                                    users.append(f'<a href="tg://user?id={user.id}">\u200B</a>')
                            final_text += " " + "".join(users)
                        except Exception as e:
                            logging.error(f"Ошибка тегания в {entity}: {e}")

                    try:
                        if not self.broadcasting: break
                        if original.media:
                            await message.client.send_file(entity, original.media, caption=final_text)
                        else:
                            await message.client.send_message(entity, final_text)
                    except Exception as e:
                        logging.error(f"Ошибка отправки в {entity}: {e}")
                if not self.broadcasting: break
                await asyncio.sleep(delay)

    @loader.command()
    async def stopbroadcast(self, message):
        """Остановить рассылку немедленно"""
        self.broadcasting = False
        await message.edit(self.strings["broadcast_stopped"])

    @loader.command()
    async def top(self, message):
        """Отправить последнее сохранённое сообщение в текущую тему супергруппы"""
        saved = self._get_saved_msgs()
        tags_enabled = self._get_tags_enabled()
        usertag = self._get_usertag_filter()
        tag_targets = [i.strip().lstrip("@").lower() for i in usertag.split(",")] if usertag != "0" else []

        if not saved:
            return await message.edit("❌ Нет сохранённого сообщения")

        chat_id, msg_id = saved[-1]
        try:
            original = await message.client.get_messages(chat_id, ids=msg_id)
        except Exception as e:
            return await message.edit(f"❌ Ошибка получения сообщения: {e}")

        final_text = original.message or ""
        if tags_enabled:
            try:
                users = []
                async for user in message.client.iter_participants(message.chat_id):
                    if user.bot: continue
                    uid = str(user.id)
                    uname = (user.username or "").lower()
                    if usertag == "0" or uid in tag_targets or uname in tag_targets:
                        users.append(f'<a href="tg://user?id={user.id}">\u200B</a>')
                final_text += " " + "".join(users)
            except Exception as e:
                logging.error(f"Ошибка тегания в .top: {e}")

        try:
            reply_id = message.reply_to_msg_id
            if original.media:
                await message.client.send_file(message.chat_id, original.media, caption=final_text, reply_to=reply_id)
            else:
                await message.client.send_message(message.chat_id, final_text, reply_to=reply_id)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Ошибка отправки: {e}")