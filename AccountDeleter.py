from .. import loader, utils
import os
import asyncio
import aiohttp
from io import BytesIO
from telethon import functions
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import DeletePhotosRequest
import re

PHOTO_FILE = "delacc_photo.txt"
DEFAULT_PHOTO = "https://envs.sh/ar_.jpg"  # Стандартная аватарка

@loader.tds
class AccountDeleter(loader.Module):
    strings = {"name": "AccountDeleter"}

    @loader.command()
    async def delacc(self, m):
        """Удаляет аккаунт (меняет аватарку, ник и удаляет username)"""
        text = "Удаление аккаунта через..."
        await utils.answer(m, f"{text} <b>10</b> <emoji document_id=5296432770392791386>✈️</emoji>")
        await asyncio.sleep(0.5)
        await utils.answer(m, f"{text} <b>6</b> <emoji document_id=5296432770392791386>✈️</emoji>")
        await asyncio.sleep(0.7)
        await utils.answer(m, f"{text} <b>3</b> <emoji document_id=5296432770392791386>✈️</emoji>")
        await asyncio.sleep(1)
        await utils.answer(m, f"{text} <b>1</b> <emoji document_id=5296432770392791386>✈️</emoji>")
        await asyncio.sleep(0.8)

        # Удаление всех предыдущих фотографий профиля
        profile_photos = await self.client.get_profile_photos('me')
        await self.client(DeletePhotosRequest(profile_photos))

        # Получаем ссылку на фото
        photo_url = self.get_saved_photo()
        if not self.is_valid_url(photo_url):
            await utils.answer(m, "<b>Ошибка: сохранённая ссылка недействительна. Установите новую через .setdelphoto <ссылка></b>")
            return
        
        await self.set_photo(photo_url, m)

        # Меняем имя и удаляем username
        await self._client(UpdateProfileRequest(
            first_name='Deleted Account',
            last_name='',
            about='Аккаунт удалён. Вся информация на https://telegram.org/faq'
        ))
        await self._client(UpdateUsernameRequest(""))  # Удаляем username

        await utils.answer(m, "<b>Ваш аккаунт полностью удалён. <emoji document_id=6325592348529003273>😦</emoji></b>")

    @loader.command()
    async def setdelphoto(self, m):
        """Устанавливает фото для .delacc (без ссылки - сброс на стандартное)"""
        args = utils.get_args_raw(m)

        if args:  # Если передана ссылка
            if not self.is_valid_url(args):
                await utils.answer(m, "<b>Укажите корректную ссылку на изображение!</b>")
                return
            photo_url = args
        else:  # Если вызвали без аргументов, сбрасываем на стандартную
            photo_url = DEFAULT_PHOTO

        with open(PHOTO_FILE, "w") as f:
            f.write(photo_url)

        await self.set_photo(photo_url, m)  # Сразу же меняем фото
        await utils.answer(m, "<b>Ссылка на фото обновлена! Теперь .delacc будет использовать новое изображение.</b>")

    def get_saved_photo(self):
        """Получает сохранённую ссылку на фото или использует стандартную"""
        if os.path.exists(PHOTO_FILE):
            with open(PHOTO_FILE, "r") as f:
                link = f.read().strip()
                return link if link else DEFAULT_PHOTO
        return DEFAULT_PHOTO  # Стандартная ссылка

    def is_valid_url(self, url):
        """Проверяет, является ли строка корректной ссылкой"""
        regex = re.compile(
            r'^(https?:\/\/)?'  # http:// или https://
            r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}|'  # доменное имя
            r'(\d{1,3}\.){3}\d{1,3})'  # или IP
            r'(:\d+)?(\/.*)?$', re.IGNORECASE)
        return re.match(regex, url) is not None

    async def set_photo(self, photo_url, m):
        """Устанавливает аватарку из указанной ссылки"""
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    avatar = await self.client.upload_file(BytesIO(image_data))
                    await self.client(functions.photos.UploadProfilePhotoRequest(file=avatar))
                    await utils.answer(m, "<b>Фото профиля успешно обновлено!</b>")
                else:
                    await utils.answer(m, "<b>Не удалось загрузить изображение. Проверьте ссылку и попробуйте снова.</b>")

    @loader.command()
    async def gethex(self, m):
        """Определяет HEX код цвета из изображения (в центре изображения)"""
        if not m.is_reply:
            await utils.answer(m, "<b>Ответьте на изображение!</b>")
            return
        
        replied_msg = await m.get_reply_message()
        if not replied_msg.photo:
            await utils.answer(m, "<b>Ответьте на изображение!</b>")
            return

        photo = replied_msg.photo
        photo_path = await self.client.download_media(photo)
        
        from PIL import Image
        
        image = Image.open(photo_path)
        width, height = image.size
        central_pixel = image.getpixel((int(width / 2), int(height / 2)))
        
        hex_color = '#{:02x}{:02x}{:02x}'.format(*central_pixel[:3])
        await utils.answer(m, f"<b>HEX код цвета:</b> {hex_color}")
        
        os.remove(photo_path)