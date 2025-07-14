from telethon.tl.types import (
    InputMessagesFilterPhotos,
    InputMessagesFilterVideo,
    InputMessagesFilterVoice,
    InputMessagesFilterMusic,
    InputMessagesFilterDocument,
    InputMessagesFilterContacts,
    InputMessagesFilterGeo,
    InputMessagesFilterRoundVideo,
    InputMessagesFilterUrl,
    InputMessagesFilterGif,
)

from .. import loader  # type: ignore


@loader.tds
class ChatStatisticMod(loader.Module):
    "Статистика чата"
    strings = {"name": "ChatStatistic"}

    @loader.owner
    async def statacmd(self, m):
        await m.edit("<b>Считаем...</b>")
        al = str((await m.client.get_messages(m.to_id, limit=0)).total)
        ph = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterPhotos()
                )
            ).total
        )
        vi = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterVideo()
                )
            ).total
        )
        mu = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterMusic()
                )
            ).total
        )
        vo = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterVoice()
                )
            ).total
        )
        vv = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterRoundVideo()
                )
            ).total
        )
        do = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterDocument()
                )
            ).total
        )
        urls = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterUrl()
                )
            ).total
        )
        gifs = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterGif()
                )
            ).total
        )
        geos = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterGeo()
                )
            ).total
        )
        cont = str(
            (
                await m.client.get_messages(
                    m.to_id, limit=0, filter=InputMessagesFilterContacts()
                )
            ).total
        )
        await m.edit(
            (
                "<emoji document_id=5256230583717079814>📝</emoji> <b>Всего сoообщений</b> {}\n"
                + "<emoji document_id=5775949822993371030>🖼</emoji> <b>Фоток:</b> {}\n"
                + "<emoji document_id=6005986106703613755>📷</emoji> <b>Видосов:</b> {}\n"
                + "<emoji document_id=5255944749348562622>🎵</emoji> <b>Попсы:</b> {}\n"
                + "<emoji document_id=5256054356913957552>🎙</emoji> <b>Голосовых:</b> {}\n"
                + "<emoji document_id=5249019346512008974>▶️</emoji> <b>Кругляшков:</b> {}\n"
                + "<emoji document_id=5253526631221307799>📂</emoji> <b>Файлов:</b> {}\n"
                + "<emoji document_id=5253490441826870592>🔗</emoji> <b>Ссылок:</b> {}\n"
                + "<emoji document_id=5255917867148257511>🖼</emoji> <b>Гифок:</b> {}\n"
                + "<emoji document_id=5253713110111365241>📍</emoji> <b>Координат:</b> {}\n"
                + "<emoji document_id=5255835635704408236>👤</emoji> <b>Контактов:</b> {}"
            ).format(al, ph, vi, mu, vo, vv, do, urls, gifs, geos, cont)
        )