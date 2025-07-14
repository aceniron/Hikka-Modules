import io
import random
import string
from .. import loader, utils
from PIL import Image, ImageDraw, ImageFilter

@loader.tds
class Frip(loader.Module):
    """Всеразличные рамки для вашего фото!\nОснова для первого аргумента: #000000 - черный #ffffff - белый"""
    strings = {
        "name": "Frip",
        }
    
    @loader.command()
    async def frip(self, message):
        """[ Цвет рамки на англ, либо HEX ] [ Цвет подсветки на англ, либо HEX ] - создать рамку\nПример: .frip #000000 red\n"""
        args = utils.get_args_raw(message)
        args1 = (args.split(' ', 2)[0])
        args2 = (args.split(' ', 2)[1])
        
        
        
        R = False
        Q = "image"
        P = "/"
        L = "RGBA"
        K = "<b>Ответьте на фото/стикер</b>"
        A = message
        C = await A.get_reply_message()
        B = io.BytesIO()
        M = None
        if A.file:
            if A.file.mime_type.split(P)[0] == Q:
                await A.download_media(B)
            elif C:
                if C.file:
                    if C.file.mime_type.split(P)[0] == Q:
                        M = R
                        await C.download_media(B)
                else:
                    await A.edit(K)
                    return
            else:
                await A.edit(K)
                return
        elif C:
            if C.file:
                if C.file.mime_type.split(P)[0] == Q:
                    M = R
                    await C.download_media(B)
            else:
                await A.edit(K)
                return
        else:
            await A.edit(K)
            return
        try:
            I = Image.open(B) 
        except:
            await A.edit(K)
            return
        await A.edit("<b>В процессе...</b>")
        F, G = I.size
        B = Image.new(L, (F, G))
        J = min(F // 100, G // 100)
        D = Image.new(L, (F + J * 40, G + J * 40), f"{args1}")
        if I.mode == L:
            B.paste(I, (0, 0), I)
            E = Image.new(L, (F, G))
            for N in range(F):
                for O in range(G):
                    if B.getpixel((N, O)) != (0, 0, 0, 0):
                        E.putpixel((N, O), (0, 0, 0))
        else:
            B.paste(I, (0, 0))
            E = Image.new(L, (F, G), f"{args2}")
        E = E.resize((F + J * 5, G + J * 5))
        D.paste(E, ((D.width - E.width) // 2, (D.height - E.height) // 2), E)
        D = D.filter(ImageFilter.GaussianBlur(J * 5))
        D.paste(B, ((D.width - B.width) // 2, (D.height - B.height) // 2), B)
        H = io.BytesIO()
        H.name = (
            "-".join(
                [
                    "".join([random.choice(string.hexdigits) for B in range(A)])
                    for A in [5, 4, 3, 2, 1]
                ]
            )
            + ".png"
        )
        D.save(H, "PNG")
        H.seek(0)
        if utils.get_args_raw(A):
            await A.client.send_file(A.to_id, H, force_document=R)
            await A.delete()
        elif M:
            await C.reply(file=H)
            await A.delete()
        else:
            await A.edit(file=H, text="")
            
   
    @loader.command()
    async def ffrip(self, message):
        """[ Цвет рамки на англ, либо HEX ] [ Цвет подсветки на англ, либо HEX ] - создать рамку в виде файла\nПример: .ffrip #000000 red\n"""
        args = utils.get_args_raw(message)
        args1 = (args.split(' ', 2)[0])
        args2 = (args.split(' ', 2)[1])
        
        
        
        R = True
        Q = "image"
        P = "/"
        L = "RGBA"
        K = "<b>Ответьте на фото/стикер</b>"
        A = message
        C = await A.get_reply_message()
        B = io.BytesIO()
        M = None
        if A.file:
            if A.file.mime_type.split(P)[0] == Q:
                await A.download_media(B)
            elif C:
                if C.file:
                    if C.file.mime_type.split(P)[0] == Q:
                        M = R
                        await C.download_media(B)
                else:
                    await A.edit(K)
                    return
            else:
                await A.edit(K)
                return
        elif C:
            if C.file:
                if C.file.mime_type.split(P)[0] == Q:
                    M = R
                    await C.download_media(B)
            else:
                await A.edit(K)
                return
        else:
            await A.edit(K)
            return
        try:
            I = Image.open(B) 
        except:
            await A.edit(K)
            return
        await A.edit("<b>В процессе...</b>")
        F, G = I.size
        B = Image.new(L, (F, G))
        J = min(F // 100, G // 100)
        D = Image.new(L, (F + J * 40, G + J * 40), f"{args1}")
        if I.mode == L:
            B.paste(I, (0, 0), I)
            E = Image.new(L, (F, G))
            for N in range(F):
                for O in range(G):
                    if B.getpixel((N, O)) != (0, 0, 0, 0):
                        E.putpixel((N, O), (0, 0, 0))
        else:
            B.paste(I, (0, 0))
            E = Image.new(L, (F, G), f"{args2}")
        E = E.resize((F + J * 5, G + J * 5))
        D.paste(E, ((D.width - E.width) // 2, (D.height - E.height) // 2), E)
        D = D.filter(ImageFilter.GaussianBlur(J * 5))
        D.paste(B, ((D.width - B.width) // 2, (D.height - B.height) // 2), B)
        H = io.BytesIO()
        H.name = (
            "-".join(
                [
                    "".join([random.choice(string.hexdigits) for B in range(A)])
                    for A in [5, 4, 3, 2, 1]
                ]
            )
            + ".png"
        )
        D.save(H, "PNG")
        H.seek(0)
        if utils.get_args_raw(A):
            await A.client.send_file(A.to_id, H, force_document=R)
            await A.delete()
        elif M:
            await C.reply(file=H)
            await A.delete()
        else:
            await A.edit(file=H, text="")

    @loader.command()
    async def krug(self, message):
        """[ Цвет рамки на англ, либо HEX ] - создать изображение с круглой рамкой и неоновой подсветкой на прозрачном фоне\nПример: .krug #34c3eb\n"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Укажите цвет рамки (на англ или HEX)</b>")
            return

        frame_color = args

        # Размер изображения
        size = 450
        inner_radius = 150  # Внутренний радиус рамки
        outer_radius = 170  # Внешний радиус рамки

        # Создание прозрачного изображения
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Создание маски для круглой рамки
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((size//2 - outer_radius, size//2 - outer_radius, size//2 + outer_radius, size//2 + outer_radius), fill=255)
        draw.ellipse((size//2 - inner_radius, size//2 - inner_radius, size//2 + inner_radius, size//2 + inner_radius), fill=0)

        # Создание изображения рамки
        frame_image = Image.new("RGBA", (size, size), frame_color)
        frame_image.putalpha(mask)

        # Наложение рамки на прозрачное изображение
        image.paste(frame_image, (0, 0), frame_image)

        # Добавление неоновой подсветки
        neon_image = frame_image.filter(ImageFilter.GaussianBlur(10))
        image.paste(neon_image, (0, 0), neon_image)

        # Сохранение изображения
        output_image = io.BytesIO()
        output_image.name = f"{''.join(random.choices(string.hexdigits, k=10))}.png"
        image.save(output_image, "PNG")
        output_image.seek(0)

        # Отправка изображения
        await message.client.send_file(message.to_id, output_image, force_document=True)
        await message.delete()