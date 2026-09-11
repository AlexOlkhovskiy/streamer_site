from django.core.management.base import BaseCommand
import csv
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse as dt_parse

from main.models import MessagesFromBot


class Command(BaseCommand):
    file_path = 'MessagesFromBot.csv'

    def handle(self, *args, **options):
        self.stdout.write(f'Start import from {self.file_path}')
        
        if not Path(self.file_path).is_file():
            raise FileNotFoundError("File not found")
            
        with open(self.file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp = dt_parse(row['timestamp'])
                    
                    obj = MessagesFromBot(
                        id=row.get('id'),
                        timestamp=timestamp,
                        chat_id=int(row['chat_id']),
                        author_id=int(row['author_id']),
                        full_name=row['full_name'],
                        username=row.get('username'),
                        is_bot=(row['is_bot'].lower() == 'true'),
                        message_text=row.get('message_text'),
                        message_id=int(row['message_id']),
                        message_type=row['message_type'],
                        reply_to=row.get('reply_to') or None,
                        stickerpack_name=row.get('stickerpack_name') or None
                    )
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f'Load id={row.get('id')}'))
                
                except Exception as e:
                    self.stderr.write(f"Error from row {row}: {e}")
        
        self.stdout.write(self.style.SUCCESS('Messages successfully loaded!'))