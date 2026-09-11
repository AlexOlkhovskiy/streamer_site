from django.core.management.base import BaseCommand
from django.db.models import Count
from collections import defaultdict

from main.models import MessagesFromBot


class Command(BaseCommand):
    help = 'Лидерборд стикерпаков по количеству использований'

    def handle(self, *args, **options):
        # Все сообщения со стикерами и непустым стикерпаком
        stickers = (
            MessagesFromBot.objects
            .filter(
                message_type='sticker',
                stickerpack_name__isnull=False
            )
            .exclude(stickerpack_name='')
        )

        # --- считаем общее количество использований ---
        pack_stats = (
            stickers
            .values('stickerpack_name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        if not pack_stats:
            self.stdout.write('Стикеры не найдены')
            return

        self.stdout.write(
            f"{'#':<3} {'Стикерпак':<40} {'Использований':<15} Кто использовал чаще всех"
        )
        self.stdout.write('-' * 90)

        for i, pack in enumerate(pack_stats, start=1):
            pack_name = pack['stickerpack_name']

            # --- кто использовал этот стикерпак чаще всех ---
            top_user = (
                stickers
                .filter(stickerpack_name=pack_name)
                .values('full_name')
                .annotate(cnt=Count('id'))
                .order_by('-cnt')
                .first()
            )

            top_user_name = top_user['full_name'] if top_user else '—'

            self.stdout.write(
                f"{i:<3} {pack_name:<40} {pack['total']:<15} {top_user_name}"
            )
