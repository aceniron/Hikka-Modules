from .. import loader, utils
import logging
from telethon.tl.functions.messages import CreateChatRequest, ExportChatInviteRequest, DeleteChatUserRequest
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.errors import UserRestrictedError
from telethon import events, TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

def register(cb):
    cb(TGCreateMod())

class tgcreate(loader.Module):
    """Создать группу, супергруппу, канал или бот"""
    strings = {'name': 'tgcreate'}

    async def ctgcmd(self, message):
        """Используй .ctg <g|s|c> <название>, чтобы создать группу, супергруппу или канал."""
        args = utils.get_args_raw(message).split(' ')
        try:
            title = utils.get_args_raw(message).split(" ", 1)[1]
            if 'g' in args[0]:
                r = await message.client(CreateChatRequest(users=['missrose_bot'], title=title))
                created_chat = r.chats[0].id
                await message.client(DeleteChatUserRequest(chat_id=created_chat, user_id='@missrose_bot'))
            elif 's' in args[0]:
                r = await message.client(CreateChannelRequest(title=title, about='', megagroup=True))
            elif 'c' in args[0]:
                r = await message.client(CreateChannelRequest(title=title, about='', megagroup=False))
            created_chat = r.chats[0].id
            result = await message.client(ExportChatInviteRequest(peer=created_chat))
            await message.edit(f'<b>Группа \"{title}\" создана.\nЛинк: {result.link}.</b>')
        except IndexError:
            return await message.edit('<b>Неверно указаны аргументы.</b>')
        except UnboundLocalError:
            return await message.edit('<b>Неверно указаны аргументы.</b>')
        except UserRestrictedError:
            return await message.edit('<b>У вас спамбан, вы не можете создавать каналы или группы.</b>')

    async def btgcmd(self, message):
        """Используй .btg <username>, чтобы создать бота."""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit('<b>Не указан username бота.</b>')
            return
        username = args.split(' ')[0]
        valid_endings = ('bot', 'Bot', '_bot', '_Bot')
        if not username.endswith(valid_endings):
            await message.edit('<b>Username должен оканчиваться на "bot", "Bot", "_bot", или "_Bot".</b>')
            return

        # Взаимодействие с @BotFather для создания бота
        async with message.client.conversation('@BotFather') as conv:
            await conv.send_message('/newbot')
            response = await conv.get_response()
            if 'Alright, a new bot. How are we going to call it?' in response.text:
                await conv.send_message(username)
                response = await conv.get_response()
                if 'Good. Now let\'s choose a username for your bot.' in response.text:
                    await conv.send_message(username)
                    response = await conv.get_response()
                    if 'Done! Congratulations on your new bot.' in response.text:
                        bot_details = response.text
                        await message.delete()  # Удаление сообщения с командой .btg
                        await message.respond(bot_details)  # Отправка деталей бота в чат
                    elif 'Sorry, this username is already taken.' in response.text:
                        await message.delete()  # Удаление сообщения с командой .btg
                        await message.respond(response.text)  # Отправка сообщения об ошибке в чат
                    elif 'Sorry, too many attempts.' in response.text:
                        await message.delete()  # Удаление сообщения с командой .btg
                        await message.respond(response.text)  # Отправка сообщения о временной блокировке в чат
                    else:
                        await message.respond(response.text)
                else:
                    await message.respond(response.text)
            elif 'Sorry, too many attempts.' in response.text:
                await message.delete()  # Удаление сообщения с командой .btg
                await message.respond(response.text)  # Отправка сообщения о временной блокировке в чат
            else:
                await message.respond(response.text)

    @events.register(events.NewMessage(incoming=True, pattern='\\.ctg'))
    async def _(self, event):
        # Ваш код для обработки события здесь
        pass

    @events.register(events.NewMessage(incoming=True, pattern='\\.btg'))
    async def _(self, event):
        # Ваш код для обработки события здесь
        pass