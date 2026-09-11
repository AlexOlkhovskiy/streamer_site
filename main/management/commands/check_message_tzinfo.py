from django.core.management.base import BaseCommand
from main.models import TwitchChatMessage


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            obj = TwitchChatMessage.objects.order_by('-id').first()
            if obj is None:
                self.stdout.write(self.style.ERROR('В базе нет записей TwitchChatMessage.'))
                return

            # created_at
            if obj.created_at is not None:
                is_aware_started = obj.created_at.tzinfo is not None
                tzinfo_started = obj.created_at.tzinfo
            else:
                is_aware_started = None
                tzinfo_started = None

            self.stdout.write(f'Запись ID: {obj.message_id}')
            self.stdout.write(f'started_at: {obj.created_at}')
            self.stdout.write(f'  aware: {is_aware_started}')
            self.stdout.write(f'  tzinfo: {tzinfo_started}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))