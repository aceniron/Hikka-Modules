import os
from .. import loader, utils
from asyncio import sleep

@loader.tds
class Forade(loader.Module):
    """Модуль для копирования сообщений там, где стоит запрет на это и отправки в избранное."""

    strings = {"name": "Forade"}

    async def xcmd(self, message):
        """Скачивает все с чатов/каналов по ссылке на сообщение (для приватных чатов/каналов нужно, чтобы вы были подписаны на тот или иной чат/канал)."""
        try:
            args = utils.get_args_raw(message)
            if not args:
                return

            args = args.split()
            if len(args) < 1:
                return

            link = args[0]

            if not link.startswith("https://t.me/"):
                return

            await message.delete()

            if link.startswith("https://t.me/c/"):
                parts = link.split('/')
                channel_id = int(parts[4])
                message_id = int(parts[5])
            else:
                parts = link.split('/')
                channel_id = parts[3]
                message_id = int(parts[4])

            q = await message.client.get_messages(channel_id, ids=message_id)

            if q.media:
                f = await message.client.download_media(q.media)

                if q.message:
                    await message.client.send_file('me', f, caption=q.text)
                else:
                    await message.client.send_file('me', f)
            else:
                await message.client.send_message('me', q.text)

        except Exception as e:
            print(f"Ошибка: {e}")

    async def xxcmd(self, message):
        """Скачивает все с чатов/каналов в ответ на сообщение."""
        await message.delete()
        name = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if reply:
            caption = reply.text if reply.text else ''

            if reply.media:
                ext = reply.file.ext
                media_fname = f'{name or message.id + reply.id}{ext}'

                await message.client.download_media(reply, media_fname)
                await message.client.send_file('me', media_fname, caption=caption)
            else:
                if reply.text:
                    await message.client.send_message('me', reply.text)