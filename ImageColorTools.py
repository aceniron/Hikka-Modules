import io
import random
from telethon.tl.types import Message
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputMediaUploadedPhoto
from PIL import Image, ImageDraw
import requests

from .. import loader, utils


@loader.tds
class ImageColorToolsMod(loader.Module):
    """Модуль для работы с изображениями и цветами"""
    
    strings = {"name": "ImageColorTools"}
    IMAGE_SIZE = (512, 512)  # Установим размер изображения по умолчанию

    async def colorhexcmd(self, message: Message):
        """Определить HEX-код цвета из изображения (ответ на фото)"""
        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            await message.edit("Ответьте на изображение.")
            return
        
        img = await reply.download_media(bytes)
        image = Image.open(io.BytesIO(img)).convert("RGB")
        pixels = list(image.getdata())
        color = random.choice(pixels)
        hex_code = "#{:02x}{:02x}{:02x}".format(*color)

        await message.edit(f"Определённый HEX-код цвета: {hex_code}")

    async def colorimagecmd(self, message: Message):
        """Сгенерировать изображение по HEX-коду. Пример: .colorimage #ff0000"""
        args = utils.get_args_raw(message)
        if not args.startswith("#") or len(args) != 7:
            await message.edit("Используйте HEX-код формата #RRGGBB")
            return

        try:
            img = Image.new("RGB", self.IMAGE_SIZE, args)
            bio = io.BytesIO()
            bio.name = "color.jpg"
            img.save(bio, "JPEG")
            bio.seek(0)

            await message.client(SendMediaRequest(
                peer=message.to_id,
                media=InputMediaUploadedPhoto(file=await message.client.upload_file(bio)),
                message="Изображение с цветом " + args
            ))

        except Exception as e:
            await message.edit(f"Ошибка: {str(e)}")

    async def gradientcmd(self, message: Message):
        """Создать градиентное изображение. Пример: .gradient #000000 | #0f1537"""
        args = utils.get_args_raw(message)
        if " | " not in args:
            await message.edit("Используйте формат: .gradient #RRGGBB | #RRGGBB")
            return
        
        try:
            color1, color2 = args.split(" | ")
            if not (color1.startswith("#") and len(color1) == 7 and color2.startswith("#") and len(color2) == 7):
                await message.edit("Цвета должны быть в формате #RRGGBB")
                return

            img = Image.new("RGB", self.IMAGE_SIZE, color1)
            draw = ImageDraw.Draw(img)

            width, height = self.IMAGE_SIZE
            for i in range(width):
                for j in range(height):
                    ratio = ((i + j) / (width + height)) * 2  # 50%/50% распределение
                    ratio = min(1, max(0, ratio))  # Обрезаем в диапазоне [0,1]

                    r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
                    g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
                    b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)

                    draw.point((i, height - j - 1), (r, g, b))  # Меняем направление: снизу слева → вверх справа

            bio = io.BytesIO()
            bio.name = "gradient.jpg"
            img.save(bio, "JPEG")
            bio.seek(0)

            await message.client(SendMediaRequest(
                peer=message.to_id,
                media=InputMediaUploadedPhoto(file=await message.client.upload_file(bio)),
                message=f"Градиент от {color1} к {color2}"
            ))

        except Exception as e:
            await message.edit(f"Ошибка: {str(e)}")

    async def imagesizecmd(self, message: Message):
        """Установить размер изображения. Пример: .imagesize 640x360"""
        args = utils.get_args_raw(message)
        if "x" not in args:
            await message.edit("Используйте формат ширинаxвысота, например 640x360")
            return
        
        try:
            width, height = map(int, args.split("x"))
            self.IMAGE_SIZE = (width, height)
            await message.edit(f"Размер изображения установлен: {width}x{height}")

        except ValueError:
            await message.edit("Неверный формат, используйте числа.")

    async def imagesettingscmd(self, message: Message):
        """Отобразить текущие настройки размера изображения"""
        size = self.IMAGE_SIZE
        await message.edit(f"Текущий размер изображения: {size[0]}x{size[1]}")