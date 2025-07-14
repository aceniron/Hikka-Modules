from .. import loader, utils
from ..utils import answer
from telethon.tl.types import Message


@loader.tds
class SpamBanCheckMod(loader.Module):
    """Check spam ban for your account."""

    strings = {
        "name": "CheckSpamBan",
        "svo": "Your account is free from any restrictions.",
        "good": "<b>Everything is fine!You don't have a spam ban.</b>",
        "spamban": "<b>Unfortunately, your account has received a spam ban...\n\n{kk}\n\n{ll}</b>",
    }

    strings_ru = {
        "svo": "Ваш аккаунт свободен от каких-либо ограничений.",
        "good": "<b>Все прекрасно!\nУ вас нет спам бана.</b>",
        "spamban": "<b>К сожалению ваш аккаунт получил спам-бан...\n\n{kk}\n\n{ll}</b>",
    }

    async def spambancmd(self, message: Message):
        """- checks your account for spam ban via @SpamBot bot."""
        async with self._client.conversation("@SpamBot") as conv:
            msg = await conv.send_message("/start")
            r = await conv.get_response()
            if r.text == self.strings("svo"):
                text = self.strings("good")
            else:
                response_lines = r.text.split("\n")
                kk = response_lines[2]
                ll = response_lines[4]
                text = self.strings("spamban").format(kk=kk, ll=ll)
            await msg.delete()
            await r.delete()
            await answer(message, text)