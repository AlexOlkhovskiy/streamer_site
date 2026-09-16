import time
from datetime import datetime, timedelta
from django.contrib import messages
import requests
from django.contrib import admin
from .models import (
    Roulette, URL, MessagesFromBot, TextSample, Film, FilmForWatching
)
import openpyxl
import csv
from django.http import HttpResponse


class ExportCsvMixin:
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="data.csv"'

        writer = csv.writer(response)
        fields = [field.name for field in self.model._meta.fields]
        writer.writerow(fields)

        for obj in queryset:
            row = [getattr(obj, field) for field in fields]
            writer.writerow(row)

        response['Content-Disposition'] = f'attachment; filename="{self.model.__name__}.csv"'
        return response
    export_csv.short_description = "Импорт в CSV"


class ExportExcelMixin:
    def export_excel(self, request, queryset):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Data"

        fields = [field.name for field in self.model._meta.fields]
        ws.append(fields)

        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field)
                # Удаляем информацию о временной зоне и добавляем 3 часа, если это datetime
                if isinstance(value, datetime):
                    value = value.replace(tzinfo=None) + timedelta(hours=3)
                row.append(value)
            ws.append(row)

        wb.save(response)
        response['Content-Disposition'] = f'attachment; filename="{self.model.__name__}.xlsx"'
        return response

    export_excel.short_description = "Импорт в Excel"


class UpdateFromKinopoiskMixin:
    """ Mixin для добавления возможности обновления данных фильмов из Кинопоиска. """

    def update_films_from_kinopoisk(self, request, queryset):
        """ Обновление полей фильмов на основании данных с сайта Кинопоиск. """
        updated_count = 0  # Количество успешно обновленных фильмов
        failed_count = 0  # Количество ошибок
        kp_api_key = '<тут нужно вставить токен>'

        for film in queryset:
            try:
                # Получаем данные о фильме по кинопроиску ID
                url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film.kinopoisk_id}'
                headers = {'X-API-KEY': kp_api_key, 'Content-Type': 'application/json'}

                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Проверяем успешность запроса

                data = response.json()

                # Обновляем поля фильма
                film.name = str(data.get('nameRu', ''))
                film.poster_url_preview = str(data.get('posterUrlPreview', ''))
                film.rating_kinopoisk = float(data.get('ratingKinopoisk', ''))
                film.rating_imdb = float(data.get('ratingImdb', ''))
                film.film_length = int(data.get('filmLength', ''))
                film.film_year = int(data.get('year', ''))
                film.film_genres = ", ".join([genre['genre'] for genre in data.get('genres', '')])
                film.description = data.get('description', '')

                # Сохраняем изменения
                film.save()
                updated_count += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Ошибка при обработке фильма '{film.name}' ({film.pk}): {e}",
                    level=messages.ERROR
                )
                failed_count += 1

            # небольшая задержка, так как у кинопоиска ограничение в 20 запросов в секунду
            time.sleep(0.1)

        if updated_count > 0:
            success_message = f"{updated_count} запись(-и) успешно обновлена."
            self.message_user(request, success_message, level=messages.SUCCESS)

        if failed_count > 0:
            error_message = f"{failed_count} ошибка(-и) произошла во время обработки."
            self.message_user(request, error_message, level=messages.WARNING)

    update_films_from_kinopoisk.short_description = "Заполнить инфу с Кинопоиска"


class RouletteAdmin(ExportCsvMixin, ExportExcelMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel"]
    list_display = ('event_id', 'datetime', 'ready', 'username', 'result', 'order', 'comment', 'show',)
    search_fields = ['event_id', 'username', 'result', 'order', 'comment']
    ordering = ['-datetime']


class URLAdmin(ExportCsvMixin, ExportExcelMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel"]
    list_display = ('id', 'url_name', 'url_link',)
    ordering = ['id']
    list_display_links = ('url_name',)


class TextSampleAdmin(ExportCsvMixin, ExportExcelMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel"]
    list_display = ('pk', 'name', 'text',)
    search_fields = ['name', 'text']
    list_display_links = ('name',)


class MessagesFromBotAdmin(ExportCsvMixin, ExportExcelMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel"]
    list_display = ('timestamp', 'chat_id', 'author_id', 'full_name', 'username', 'message_type',
                    'message_id', 'reply_to', 'message_text', 'stickerpack_name', 'is_bot',)
    search_fields = ['message_text', 'full_name', 'username', 'message_id', 'author_id', 'chat_id', 'message_type', 'stickerpack_name']
    ordering = ['-timestamp']


class FilmAdmin(ExportCsvMixin, ExportExcelMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel"]
    list_display = ('auction_date', 'film_name', 'film_year', 'rating_kinopoisk', 'rating_imdb', 'top_on_auction',
                    'chance_to_win', 'winners_nicknames', 'view_type', 'kinopoisk_id', 'auction_type', 'show')
    search_fields = ['film_name', 'film_year', 'winners_nicknames']
    ordering = ['-auction_date']


class FilmForWatchingAdmin(ExportCsvMixin, ExportExcelMixin, UpdateFromKinopoiskMixin, admin.ModelAdmin):
    actions = ["export_csv", "export_excel", "update_films_from_kinopoisk"]
    list_display = ('created_at', 'name', 'film_year', 'film_length', 'film_genres', 'kinopoisk_id', 'rating_kinopoisk', 'rating_imdb')


admin.site.register(Roulette, RouletteAdmin)
admin.site.register(URL, URLAdmin)
admin.site.register(MessagesFromBot, MessagesFromBotAdmin)
admin.site.register(TextSample, TextSampleAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(FilmForWatching, FilmForWatchingAdmin)