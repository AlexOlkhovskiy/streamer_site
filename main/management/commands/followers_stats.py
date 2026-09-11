from django.core.management.base import BaseCommand
from main.models import Follower


class Command(BaseCommand):
    help = "Выводит списки подписчиков по различным категориям"

    def print_list(self, title, queryset):
        self.stdout.write(self.style.SUCCESS(f"\n=== {title} (всего: {queryset.count()}) ==="))
        for i, user in enumerate(queryset.order_by('nickname'), start=1):
            self.stdout.write(f"{i}. {user.nickname}")

    def handle(self, *args, **kwargs):

        # 1. Классный чатерс
        good_chatters = Follower.objects.filter(color='good')

        # 2. Все забаненные (по полю ban, кроме "без бана")
        banned_users = Follower.objects.exclude(ban='без бана')

        # 3. Подозрительные
        suspicious_users = Follower.objects.filter(color='suspicious')

        # 4. Опасный/Забанен
        danger_users = Follower.objects.filter(color='danger')

        # 5. Бывшие модераторы (prev_moderator_yrarami не пустое)
        ex_moderators = Follower.objects.exclude(prev_moderator_yrarami='')

        # 6. Стримеры
        streamers = Follower.objects.filter(streamer=True)

        # Вывод
        self.print_list("Классный чатерс", good_chatters)
        self.print_list("Забаненные пользователи", banned_users)
        self.print_list("Подозрительные", suspicious_users)
        self.print_list("Опасный/Забанен", danger_users)
        self.print_list("Бывшие модераторы yrarami", ex_moderators)
        self.print_list("Стримеры", streamers)