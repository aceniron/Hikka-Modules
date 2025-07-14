from telethon.types import Message
from .. import loader, utils

@loader.tds
class ForwardMessage(loader.Module):
    """Пересылка сообщений из чатов и каналов в выбранные чаты и каналы с возможностью настройки режима пересылки и логированием"""
    strings = {"name": "ForwardMessage"}

    async def client_ready(self, client, db):
        self._client = client
        self.db = db
        # Храним правила пересылки в формате словаря
        self.forwarding_rules = self.db.get(self.strings["name"], "forwarding_rules", {})
        self.log_chat_id = self.db.get(self.strings["name"], "log_chat_id", None)

    @loader.command(
        ru_doc="Добавить правило пересылки.\nИспользуй: .addforward <ID исходного чата/канала> <ID целевого чата/канала> <режим>\nРежим: 0 - без текста, 1 - с текстом"
    )
    async def addforward(self, message: Message):
        """Добавить правило пересылки сообщений"""
        args = utils.get_args_raw(message)
        if not args or len(args.split()) != 3:
            await utils.answer(
                message,
                "❌ Используй: .addforward <ID исходного чата/канала> <ID целевого чата/канала> <режим>\nРежим: 0 - без текста, 1 - с текстом"
            )
            return

        try:
            source_chat_id, target_chat_id, forward_mode = map(int, args.split())
            source_chat_id_str = str(source_chat_id)
            if source_chat_id_str not in self.forwarding_rules:
                self.forwarding_rules[source_chat_id_str] = []
            self.forwarding_rules[source_chat_id_str].append((target_chat_id, forward_mode))
            self.db.set(self.strings["name"], "forwarding_rules", self.forwarding_rules)
            await utils.answer(
                message,
                f"✅ Правило добавлено:\nИз чата/канала {source_chat_id} в чат/канал {target_chat_id}, режим: {forward_mode}"
            )
        except ValueError:
            await utils.answer(
                message,
                "❌ Неверный формат ID чатов/каналов или режима. Используй: .addforward <ID исходного чата/канала> <ID целевого чата/канала> <режим>"
            )

    @loader.command(
        ru_doc="Сбросить все правила пересылки.\nИспользуй: .clearforward"
    )
    async def clearforward(self, message: Message):
        """Сбросить все правила пересылки"""
        self.forwarding_rules = {}
        self.db.set(self.strings["name"], "forwarding_rules", {})
        await utils.answer(message, "✅ Все правила пересылки сброшены.")

    @loader.command(
        ru_doc="Показать текущие правила пересылки.\nИспользуй: .showforwards"
    )
    async def showforwards(self, message: Message):
        """Показать текущие правила пересылки"""
        if not self.forwarding_rules:
            await utils.answer(message, "ℹ️ Нет установленных правил пересылки.")
            return

        rules = ""
        idx = 1
        for source_chat_id, targets in self.forwarding_rules.items():
            for target_chat_id, forward_mode in targets:
                rules += f"{idx}. Из чата/канала {source_chat_id} в чат/канал {target_chat_id}, режим: {forward_mode}\n"
                idx += 1
        await utils.answer(message, f"📋 Текущие правила пересылки:\n{rules}")

    @loader.command(
        ru_doc="Удалить конкретное правило пересылки.\nИспользуй: .delforward <номер_правила>"
    )
    async def delforward(self, message: Message):
        """Удалить конкретное правило пересылки"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await utils.answer(
                message,
                "❌ Укажите номер правила для удаления. Используй: .delforward <номер_правила>"
            )
            return

        rule_number = int(args)
        current = 0
        found = False
        for source_chat_id in list(self.forwarding_rules.keys()):
            targets = self.forwarding_rules[source_chat_id]
            for i in range(len(targets)):
                current += 1
                if current == rule_number:
                    del targets[i]
                    if not targets:
                        del self.forwarding_rules[source_chat_id]
                    found = True
                    break
            if found:
                break

        if found:
            self.db.set(self.strings["name"], "forwarding_rules", self.forwarding_rules)
            await utils.answer(message, f"✅ Правило пересылки №{rule_number} удалено.")
        else:
            await utils.answer(message, "❌ Правило с таким номером не найдено.")

    @loader.command(
        ru_doc="Установить ID чата для логирования.\nИспользуй: .setlogchat <ID чата/канала>"
    )
    async def setlogchat(self, message: Message):
        """Установить чат для логирования пересылок"""
        args = utils.get_args_raw(message)
        if not args or not args.lstrip("-").isdigit():
            await utils.answer(
                message,
                "❌ Укажите корректный ID чата или канала. Используй: .setlogchat <ID чата/канала>"
            )
            return

        self.log_chat_id = int(args)
        self.db.set(self.strings["name"], "log_chat_id", self.log_chat_id)
        await utils.answer(message, f"✅ Чат для логирования установлен: {self.log_chat_id}")

    @loader.command(
        ru_doc="Показать текущий ID чата для логирования.\nИспользуй: .showlogchat"
    )
    async def showlogchat(self, message: Message):
        """Показать текущий чат для логирования"""
        if self.log_chat_id:
            await utils.answer(message, f"📝 Чат для логирования: {self.log_chat_id}")
        else:
            await utils.answer(message, "ℹ️ Чат для логирования не установлен.")

    @loader.watcher(out=False)
    async def watcher(self, message: Message):
        """Отслеживать сообщения и пересылать их согласно правилам"""
        if not isinstance(message, Message):
            return

        source_chat_id = str(message.chat_id)
        if source_chat_id in self.forwarding_rules:
            for target_chat_id, forward_mode in self.forwarding_rules[source_chat_id]:
                try:
                    if forward_mode == 0:
                        # Пересылка без текста
                        await self._client.send_message(
                            int(target_chat_id),
                            file=message.media or None
                        )
                    elif forward_mode == 1:
                        # Пересылка с текстом
                        await self._client.send_message(
                            int(target_chat_id),
                            message.text or '',
                            file=message.media or None
                        )
                    # Логирование пересылки
                    if self.log_chat_id:
                        log_entry = (
                            f"Переслано сообщение из {source_chat_id} "
                            f"в {target_chat_id}, режим: {forward_mode}"
                        )
                        await self._client.send_message(self.log_chat_id, log_entry)
                except Exception as e:
                    # Логирование ошибки в лог-чат
                    if self.log_chat_id:
                        error_entry = (
                            f"Ошибка при пересылке сообщения из {source_chat_id} "
                            f"в {target_chat_id}: {e}"
                        )
                        await self._client.send_message(self.log_chat_id, error_entry)
                    # Вывод ошибки в консоль для отладки
                    print(f"Ошибка при пересылке сообщения из {source_chat_id} в {target_chat_id}: {e}")