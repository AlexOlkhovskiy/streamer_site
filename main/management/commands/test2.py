from django.core.management.base import BaseCommand
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = 'Выводит количество сообщений пользователя с author_id=106893959 за всё время'

    def handle(self, *args, **options):
        author_id = 113218226

        count = MessagesFromBot.objects.filter(author_id=author_id).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Пользователь с author_id={author_id} имеет {count} сообщений за всё время.'
            )
        )
