from .. import loader, utils
import os

@loader.tds
class Calc(loader.Module):
    """Калькулятор"""

    strings = {"name": "Calc"}

    async def ciccmd(self, message):
        """– рассчитать сложный процент"""
        try:
            args = utils.get_args(message)
            if len(args) != 3:
                await utils.answer(message, "Пожалуйста, введите параметры в формате: .cic <начальная сумма> <процент> <количество дней>")
                return

            try:
                sum_money = float(args[0])
                proc = float(args[1])
                days = int(args[2])
            except ValueError:
                await utils.answer(message, "Пожалуйста, убедитесь, что вы ввели числа в правильном формате.")
                return

            daily_rate = proc / 100
            result = []

            for day in range(1, days + 1):
                interest = sum_money * daily_rate
                sum_money += interest
                result.append((day, round(sum_money - interest, 2), proc, round(sum_money, 2)))

            html_content = """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Сложный процент</title>
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        border: 1px solid black;
                        padding: 8px;
                        text-align: center;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                </style>
            </head>
            <body>
                <h2>Расчет сложных процентов</h2>
                <table>
                    <tr>
                        <th>День</th>
                        <th>Начальная сумма</th>
                        <th>Процент</th>
                        <th>Конечная сумма</th>
                    </tr>
            """

            for day, start_sum, proc, end_sum in result:
                html_content += f"""
                    <tr>
                        <td>{day}</td>
                        <td>{start_sum}$</td>
                        <td>{proc}%</td>
                        <td>{end_sum}$</td>
                    </tr>
                """

            html_content += """
                </table>
            </body>
            </html>
            """

            with open('procent.html', 'w', encoding='utf-8') as f:
                f.write(html_content)

            await message.client.send_file(message.chat_id, 'procent.html')
            os.remove('procent.html')

        except Exception as e:
            await utils.answer(message, f"Произошла ошибка: {str(e)}")

    async def ctmcmd(self, message):
        """1y/1mon/1w/1d/1h/1min/1s – конвертирует годы, месяцы, недели, дни, часы, минуты и секунды"""
        try:
            args = utils.get_args_raw(message).strip().lower()
            if not args:
                await utils.answer(message, "Пожалуйста, введите значение и обозначение (например, 1y или 12mon).")
                return

            value = int(''.join(filter(str.isdigit, args)))
            unit = ''.join(filter(str.isalpha, args))

            if unit == 'y':
                years = value
                months = years * 12
                weeks = years * 52.1429
                days = years * 365
                hours = days * 24
                minutes = hours * 60
                seconds = minutes * 60
                header = "Years"
            elif unit == 'mon':
                months = value
                years = months / 12
                weeks = years * 52.1429
                days = years * 365
                hours = days * 24
                minutes = hours * 60
                seconds = minutes * 60
                header = "Months"
            elif unit == 'w':
                weeks = value
                years = weeks / 52.1429
                months = years * 12
                days = years * 365
                hours = days * 24
                minutes = hours * 60
                seconds = minutes * 60
                header = "Weeks"
            elif unit == 'd':
                days = value
                years = days / 365
                months = years * 12
                weeks = years * 52.1429
                hours = days * 24
                minutes = hours * 60
                seconds = minutes * 60
                header = "Days"
            elif unit == 'h':
                hours = value
                days = hours / 24
                years = days / 365
                months = years * 12
                weeks = years * 52.1429
                minutes = hours * 60
                seconds = minutes * 60
                header = "Hours"
            elif unit == 'min':
                minutes = value
                hours = minutes / 60
                days = hours / 24
                years = days / 365
                months = years * 12
                weeks = years * 52.1429
                seconds = minutes * 60
                header = "Minutes"
            elif unit == 's':
                seconds = value
                minutes = seconds / 60
                hours = minutes / 60
                days = hours / 24
                years = days / 365
                months = years * 12
                weeks = years * 52.1429
                header = "Seconds"
            else:
                await utils.answer(message, "Неверное обозначение. Используйте y, mon, w, d, h, min или s.")
                return

            result_message = f"""
{header}: {value:.2f}

Годы
{years:.8f}
|
Месяцев
{months:.8f}
|
Недель
{weeks:.8f}
|
Дней
{days:.8f}
|
Часов
{hours:.8f}
|
Минут
{minutes:.8f}
|
Секунд
{seconds:.8f}
"""

            await message.respond(result_message)
            await message.delete()
        except ValueError:
            await utils.answer(message, "Пожалуйста, введите значение в правильном формате (например, 1y или 12mon).")

    async def calccmd(self, message):
        """– решает математическую задачу. Пример: 2*2-2/2"""
        try:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, "Пожалуйста, используйте команду в ответ на сообщение с математической задачей.")
                return

            expression = reply.message

            expression = expression.replace('x', '*').replace('/', '/').replace('+', '+').replace('-', '-')

            result = eval(expression)

            await reply.reply(f"{expression} = {result}")

            await message.delete()
        except Exception as e:
            await utils.answer(message, f"Произошла ошибка при вычислении: {str(e)}")