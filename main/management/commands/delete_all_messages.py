# your_app/management/commands/delete_all_messages.py

from django.core.management.base import BaseCommand
from main.models import MessagesFromBot

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        count_deleted = MessagesFromBot.objects.all().count()
        MessagesFromBot.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Success deleted {count_deleted} messages."))