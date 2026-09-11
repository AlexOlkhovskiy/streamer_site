from django.core.management.base import BaseCommand
from main.models import TwitchStream


class Command(BaseCommand):
    help = 'Проверяет, являются ли поля started_at и ended_at aware-объектами в первой записи TwitchStream'

    def handle(self, *args, **kwargs):
        try:
            obj = TwitchStream.objects.order_by('-id').first()
            if obj is None:
                self.stdout.write(self.style.ERROR('В базе нет записей TwitchStream.'))
                return

            # started_at
            if obj.started_at is not None:
                is_aware_started = obj.started_at.tzinfo is not None
                tzinfo_started = obj.started_at.tzinfo
            else:
                is_aware_started = None
                tzinfo_started = None

            # ended_at
            if obj.ended_at is not None:
                is_aware_ended = obj.ended_at.tzinfo is not None
                tzinfo_ended = obj.ended_at.tzinfo
            else:
                is_aware_ended = None
                tzinfo_ended = None

            self.stdout.write(f'Запись ID: {obj.id}')
            self.stdout.write(f'started_at: {obj.started_at}')
            self.stdout.write(f'  aware: {is_aware_started}')
            self.stdout.write(f'  tzinfo: {tzinfo_started}')
            self.stdout.write(f'ended_at: {obj.ended_at}')
            self.stdout.write(f'  aware: {is_aware_ended}')
            self.stdout.write(f'  tzinfo: {tzinfo_ended}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))