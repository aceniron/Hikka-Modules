
from .. import loader, utils
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateEmojiStatusRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError, ImageProcessFailedError
from telethon import types, functions
import io
import requests
import os
from telethon.tl.functions.channels import JoinChannelRequest

@loader.tds
class ProfileToolsModule(loader.Module):
    strings = {"name": "CopyUser"}

    def init(self):
        self.name = self.strings["name"]
        self._backup_data = None

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def upload_to_0x0(self, photo_bytes):
        try:
            files = {'file': ('photo.png', photo_bytes)}
            response = requests.post(
                'https://0x0.st',
                files=files,
                data={'secret': True}
            )
            return response.text.strip()
        except Exception as e:
            return f"Ошибка: {str(e)}"

    @loader.command()
    async def copyuser(self, message):
        """Скопировать профиль пользователя (работает по reply/@username/ID)"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        try:
            if args:
                try:
                    if args.isdigit():
                        user = await message.client.get_entity(int(args))
                    else:
                        user = await message.client.get_entity(args)
                except ValueError:
                    await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b>Не удалось найти пользователя!</b>")
                    return
            elif reply:
                user = await reply.get_sender()
            else:
                await utils.answer(message, "<emoji document_id=5832251986635920010>➡️</emoji><b>Укажите пользователя (reply/@username/ID)!</b>")
                return

            full = await message.client(GetFullUserRequest(user.id))
            user_info = full.users[0]
            
            if full.full_user.profile_photo:
                try:
                    photos = await message.client.get_profile_photos(user.id)
                    if photos:
                        await message.client(DeletePhotosRequest(
                            await message.client.get_profile_photos("me")
                        ))
                        
                        photo = await message.client.download_media(photos[0])
                        await message.client(UploadProfilePhotoRequest(
                            file=await message.client.upload_file(photo)
                        ))
                        os.remove(photo)
                        await utils.answer(message, "<emoji document_id=5879770735999717115>👤</emoji><b>Аватар изменен.</b>")
                    else:
                        await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Ошибка при изменении аватара.</b>")
                except ImageProcessFailedError:
                    await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Ошибка при обработке аватара.</b>")
            else:
                await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>У пользователя нет аватара!</b>")
            
            await message.client(UpdateProfileRequest(
                first_name=user_info.first_name if user_info.first_name is not None else "",
                last_name=user_info.last_name if user_info.last_name is not None else "",
                about=full.full_user.about[:70] if full.full_user.about is not None else "",
            ))

            if hasattr(user_info, 'emoji_status') and user_info.emoji_status:
                await message.client(
                    UpdateEmojiStatusRequest(
                        emoji_status=user_info.emoji_status
                    )
                )
            
            await utils.answer(message, "<emoji document_id=5397916757333654639>➕</emoji> <b>Профиль пользователя скопирован!</b>")
        except UsernameNotOccupiedError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Пользователь не найден!</b>")
        except UsernameInvalidError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Неверный формат юзернейма/ID.</b>")
        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command()
    async def backupme(self, message):
        """Сделать резервную копию профиля"""
        try:
            user = await self.client.get_me()
            full = await self.client(GetFullUserRequest(user.id))
            user_info = full.users[0]
            
            avatar_url = None
            photos = await self.client.get_profile_photos(user.id)
            if photos:
                photo = await self.client.download_media(photos[0], bytes)
                avatar_url = await self.upload_to_0x0(photo)

            emoji_status_id = None
            if hasattr(user_info, 'emoji_status') and user_info.emoji_status:
                emoji_status_id = user_info.emoji_status.document_id

            backup_data = {
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "about": full.full_user.about,
                "avatar_url": avatar_url,
                "emoji_status_id": emoji_status_id
            }
            
            self.db.set("BackupProfile", "backup_data", backup_data)
            
            await utils.answer(
                message,
                f"<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш данный профиль сохранен. Вы можете вернуть его используя</b> <code>restoreme</code>\n\n<b>⚙️ URL данной Аватарки: {avatar_url}</b>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command()
    async def restoreme(self, message):
        """Восстановить профиль из резервной копии"""
        try:
            backup_data = self.db.get("BackupProfile", "backup_data")
            
            if not backup_data:
                await utils.answer(message, "❌ <b>Резервная копия не найдена!</b>")
                return

            if backup_data.get("avatar_url"):
                try:
                    photos = await self.client.get_profile_photos('me')
                    await self.client(DeletePhotosRequest(photos))
                    
                    response = requests.get(backup_data["avatar_url"])
                    avatar_bytes = io.BytesIO(response.content)
                    
                    await self.client(UploadProfilePhotoRequest(
                        file=await self.client.upload_file(avatar_bytes)
                    ))
                except ImageProcessFailedError:
                    await utils.answer(message, "❌ <b>Не удалось восстановить аватар</b>")

            await self.client(UpdateProfileRequest(
                first_name=backup_data.get("first_name", ""),
                last_name=backup_data.get("last_name", "") or "",
                about=backup_data.get("about", "")
            ))

            if backup_data.get("emoji_status_id"):
                await self.client(
                    UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                            document_id=backup_data["emoji_status_id"]
                        )
                    )
                )

            await utils.answer(
                message,
                "<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш прошлый профиль возвращен.</b>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")