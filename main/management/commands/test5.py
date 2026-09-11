from django.core.management.base import BaseCommand
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = "Удалить все сообщения, где full_name = 'Perplexity'"

    def handle(self, *args, **options):
        qs = MessagesFromBot.objects.filter(full_name='Perplexity')
        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("Сообщений с автором 'Perplexity' не найдено."))
            return

        confirm = input(f"Найдено {count} сообщений от 'Perplexity'. Удалить их? (y/N): ").strip().lower()
        if confirm != "y":
            self.stdout.write(self.style.WARNING("Удаление отменено."))
            return

        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Удалено {deleted} сообщений от 'Perplexity'."))
