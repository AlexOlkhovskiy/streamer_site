from django.core.management.base import BaseCommand
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = "Подсчитать количество сообщений, где full_name = 'Perplexity'"

    def handle(self, *args, **options):
        count = MessagesFromBot.objects.filter(full_name='Perplexity').count()
        self.stdout.write(self.style.SUCCESS(f'Количество сообщений от Perplexity: {count}'))
