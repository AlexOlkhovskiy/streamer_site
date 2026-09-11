from django.core.management.base import BaseCommand
from pathlib import Path
import json
from main.models import MessagesFromBot  # заменить your_app на название вашего приложения


class Command(BaseCommand):
    ''' Команда для создания в базе записей из вручную импортированной истории сообщений из телеграмма '''

    def handle(self, *args, **options):
        json_file_path = './telegram_messages_16_18_october.json'
        self.stdout.write(f"Считывание данных из файла {json_file_path}.")

        try:
            with open(json_file_path, encoding="utf-8") as f:
                messages = json.load(f)['messages']
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Файл {json_file_path} не найден."))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Неверный формат JSON в файле {json_file_path}."))
            return

        created_count = 0

        for message in messages:
            try:
                if message.get('type') != 'service':
                    # 1259302177 Урарами лайф
                    # 1359449994 Чат Рами,
                    # timestamp = datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                    is_bot = False
                    chat_id = -1001359449994
                    author_id = message.get('from_id')
                    full_name = message.get('from')
                    if full_name == None:
                        full_name = author_id
                    if "channel" in author_id:
                        author_id = author_id[7:]
                        is_bot = True
                    else:
                        author_id = author_id[4:]
                    message_text = message.get('text')
                    stickerpack_name = message.get('stickerpack_name', "")
                    reply_to = message.get('reply_to_message_id', None)
                    message_type = ""
                    if message_text:
                        message_type += "text, "
                    if "media_type" in message:
                        media_type = message.get('media_type')
                        if media_type == "video_file":
                            message_type += "video, "
                        elif media_type == "sticker":
                            message_type += "sticker, "
                        elif media_type == "animation":
                            message_type += "gif, "
                        elif media_type == "audio_file":
                            message_type += "audio, "
                        elif media_type == "voice_message":
                            message_type += "voice, "
                    elif "photo" in message:
                        message_type += "photo, "
                    elif "file" in message:
                        message_type += "file, "
                    if "forwarded_from" in message:
                        message_text = f"Сообщение переслано от {message.get('forwarded_from')}: {message_text}"
                    # Попытаемся создать запись в БД
                    obj = MessagesFromBot(
                        timestamp=message.get('date'),  #
                        chat_id=chat_id,  #
                        author_id=author_id,  #
                        full_name=full_name,  #
                        username="",  #
                        is_bot=is_bot,  #
                        message_text=message_text,  #
                        message_id=message.get('id'),  #
                        message_type=message_type[:-2],  #
                        stickerpack_name=stickerpack_name,  #
                        reply_to=reply_to  #
                    )
                    obj.save()
                    created_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Ошибка при создании записи: {message}, причина: {e}"))
                # break # Завершаем цикл при первой ошибке

        self.stdout.write(self.style.SUCCESS(f"Успешно создано записей: {created_count}."))
