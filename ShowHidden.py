from .. import loader, utils

@loader.tds
class ShowHidden(loader.Module):
    """Displays hidden modules"""

    strings = {
        "name": "ShowHidden",
        "no_hidden": "ℹ️ Нет скрытых модулей!",
        "hidden_modules_file": "Скрытые модули",
    }

    @loader.command(ru_doc="| Отображает скрытые модули")
    async def shiden(self, message):
        """| Display hidden modules"""
        # Удаляем команду мгновенно
        await message.delete()

        help_mod = next(
            (mod for mod in self.allmodules.modules if mod.strings["name"] == "Help"),
            None,
        )
        if not help_mod:
            await message.client.send_message(
                message.chat_id, "❌ Модуль Help не найден!"
            )
            return

        hidden = help_mod.get("hide", [])
        if not hidden:
            await message.client.send_message(
                message.chat_id, self.strings("no_hidden")
            )
            return

        # Создаем HTML таблицу
        table_rows = ""
        for i, mod in enumerate(hidden):
            if i % 5 == 0:
                table_rows += "<tr>"
            table_rows += f"<td>{mod}</td>"
            if (i + 1) % 5 == 0 or i == len(hidden) - 1:
                table_rows += "</tr>"

        html_content = f"""
        <html>
        <head><title>ShowHidden</title></head>
        <body>
        <table border="1">
        {table_rows}
        </table>
        </body>
        </html>
        """

        # Сохраняем в файл
        file_name = "ShowHidden.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Отправляем файл
        await message.client.send_file(
            message.chat_id,
            file_name,
            caption=self.strings("hidden_modules_file"),
        )