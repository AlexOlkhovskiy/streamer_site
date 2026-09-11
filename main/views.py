from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from main.models import (
    Roulette, URL, QuestionAndAnswer, TextSample, Film, FilmForWatching, 
    MessagesFromBot, MediaLimit, Love, Flag, TwitchStream, TwitchSubscription, 
    TwitchChatMessage, Donate, Follower, TwitchAppToken
)
from dateutil.relativedelta import relativedelta
from .utils import *
import random
import locale
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import statistics
import re
import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import date, datetime, timedelta
from datetime import timezone as datetime_timezone
from django.db.models import Sum, Min, Max, Count, Q, Case, When, Value, CharField, IntegerField, OuterRef, Subquery
from django.db.models.functions import TruncDate
from urllib.parse import quote_plus
import hmac
import hashlib
import time


#os.environ['LC_ALL'] = 'ru_RU.UTF-8'
log_path = "/var/www/roulette/print.log"
subs_events_log_path = "/var/www/Twitch/twitch_subscriptions_events.log"
my_secret_code = 'sk*Fu+qm4Cka0P1'


def custom_print(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")


def log_twitch_request(request) -> None:
    try:
        with open(subs_events_log_path, "a", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"time: {datetime.utcnow().isoformat()} UTC\n")
            f.write(f"method: {request.method}\n")
            f.write(f"path: {request.path}\n")

            f.write("headers:\n")
            for k, v in request.headers.items():
                f.write(f"  {k}: {v}\n")

            f.write("body:\n")
            try:
                f.write(request.body.decode("utf-8"))
            except UnicodeDecodeError:
                f.write(str(request.body))

            f.write("\n\n")
    except Exception as e:
        print("Log write error:", e)

def serve_sitemap(request):
    sitemap_file_path = os.path.join(settings.STATIC_ROOT, 'sitemap.xml')

    try:
        with open(sitemap_file_path, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        return HttpResponse("Error: file not found.", status=404)

    response = HttpResponse(data, content_type='application/xml')
    return response


def health_check(request):
    return HttpResponse("ok", content_type="text/plain")


def plural(n, forms):
    """
    Склонение слов:
    forms = ("месяц", "месяца", "месяцев")
    """
    if 11 <= n % 100 <= 14:
        return forms[2]
    if n % 10 == 1:
        return forms[0]
    if 2 <= n % 10 <= 4:
        return forms[1]
    return forms[2]


def format_time_difference(start_date):
    start_date = start_date.date()
    today = timezone.localdate()

    delta = relativedelta(today, start_date)

    parts = []

    if delta.years:
        parts.append(f"{delta.years} {plural(delta.years, ('год', 'года', 'лет'))}")
    if delta.months:
        parts.append(f"{delta.months} {plural(delta.months, ('месяц', 'месяца', 'месяцев'))}")
    if delta.days or not parts:
        parts.append(f"{delta.days} {plural(delta.days, ('день', 'дня', 'дней'))}")

    return ' '.join(parts)


def driving_experience():
    start_date = date(2025, 7, 1)
    today = date.today()

    delta = relativedelta(today, start_date)

    parts = []

    if delta.years:
        parts.append(f"{delta.years} {plural(delta.years, ('год', 'года', 'лет'))}")
    if delta.months:
        parts.append(f"{delta.months} {plural(delta.months, ('месяц', 'месяца', 'месяцев'))}")
    if delta.days or not parts:
        parts.append(f"{delta.days} {plural(delta.days, ('день', 'дня', 'дней'))}")

    return f"Стаж вождения розовой гонщицы: {' '.join(parts)}   🏎  🏁"


def get_top_users_text():
    # ====== КУЛДАУН ======
    flag = Flag.objects.filter(name="тг !топ кулдаун").first()
    if flag and flag.is_active:
        return "⏳ Команду сегодня уже использовали, попробуйте завтра 🙄"

    if flag:
        flag.is_active = True
        flag.save()

    # ====== НАСТРОЙКИ ======
    RAMA_IDS = [777000, 1259302177, -1001259302177]  # актуальные id Рамы
    CHAT_ID = -1001359449994

    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    periods = {
        "all": None,
        "year": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        "month": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        "week": week_start,
    }

    titles = {
        "all": "🏆 ТОП-5 за всё время",
        "year": "📅 ТОП-5 за год",
        "month": "🗓 ТОП-5 за месяц",
        "week": "📆 ТОП-5 за неделю",
    }

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    decorative_line = "─" * 30

    result_text = []

    for key, since in periods.items():
        qs = MessagesFromBot.objects.filter(chat_id=CHAT_ID)
        if since:
            qs = qs.filter(timestamp__gte=since)

        # --- Группировка по author_id, объединяем Раму ---
        top_users = (
            qs.annotate(
                grouped_id=Case(
                    When(author_id__in=RAMA_IDS, then=Value(-999)),  # объединяем Раму
                    default='author_id',
                    output_field=IntegerField()
                )
            )
            .values("grouped_id")
            .annotate(
                msg_count=Count("id"),
                last_name=Max("full_name")  # для остальных пользователей берём последнее имя
            )
            .order_by("-msg_count")[:5]
        )

        result_text.append(titles[key])
        result_text.append(decorative_line)

        if not top_users:
            result_text.append("_Нет данных_")
            result_text.append("")
            continue

        for i, user in enumerate(top_users):
            if user["grouped_id"] == -999:
                display_name = "Рама"
            else:
                display_name = user["last_name"]

            result_text.append(
                f"{medals[i]} {display_name} — {user['msg_count']} "
                f"{plural(user['msg_count'], ('сообщение', 'сообщения', 'сообщений'))}"
            )

        result_text.append("")

    return "\n".join(result_text)
'''
def get_top_users_text():
    # ====== КУЛДАУН ======
    flag = Flag.objects.filter(name="тг !топ кулдаун").first()
    if flag and flag.is_active:
        return "⏳ Команду сегодня уже использовали, попробуйте завтра 🙄"

    if flag:
        flag.is_active= True
        flag.save()

    # ====== НАСТРОЙКИ ======
    RAMA_IDS = [777000, 1259302177, -1001259302177]
    CHAT_ID = -1001359449994

    now = timezone.now()

    # Начало недели (понедельник)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    periods = {
        "all": None,
        "year": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        "month": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        "week": week_start,
    }

    titles = {
        "all": "🏆 ТОП-5 за всё время",
        "year": "📅 ТОП-5 за год",
        "month": "🗓 ТОП-5 за месяц",
        "week": "📆 ТОП-5 за неделю",
    }

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    decorative_line = "─" * 30

    result_text = []

    for key, since in periods.items():
        qs = MessagesFromBot.objects.filter(chat_id=CHAT_ID)

        if since:
            qs = qs.filter(timestamp__gte=since)

        top_users = (
            qs.annotate(
                display_name=Case(
                    When(author_id__in=RAMA_IDS, then=Value("Рама")),
                    default="full_name",
                    output_field=CharField(),
                )
            )
            .values("display_name")
            .annotate(msg_count=Count("id"))
            .order_by("-msg_count")[:5]
        )

        result_text.append(titles[key])
        result_text.append(decorative_line)

        if not top_users:
            result_text.append("_Нет данных_")
            result_text.append("")
            continue

        for i, user in enumerate(top_users):
            result_text.append(
                f"{medals[i]} {user['display_name']} — {user['msg_count']} {plural(user['msg_count'], ('сообщение', 'сообщения', 'сообщений'))}"
            )

        result_text.append("")

    return "\n".join(result_text)
'''
'''
def format_time_difference(total_seconds):
    """ Переводит количество секунд в удобный формат с указанием лет, месяцев и дней. Результат формируется в форме, отвечающей на вопрос "сколько времени прошло?" :param total_seconds: количество секунд :return: строковое представление длительности в годах, месяцах и днях """
    total_seconds = int(total_seconds)
    seconds_per_year = 365 * 24 * 60 * 60
    years = int(total_seconds // seconds_per_year)
    remaining_seconds = total_seconds % seconds_per_year

    seconds_per_month = 30 * 24 * 60 * 60
    months = int(remaining_seconds // seconds_per_month)
    remaining_seconds %= seconds_per_month

    days = int(remaining_seconds / (24 * 60 * 60))

    parts = []

    def plural_form(n, forms):
        """Возвращает правильную форму множественного числа."""
        n = abs(n)
        if n % 10 == 1 and n % 100 != 11:
            return forms[0]
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return forms[1]
        else:
            return forms[2]

    if years > 0:
        parts.append(f'{years} {plural_form(years, ["год", "года", "лет"])}')
    if months > 0:
        parts.append(f'{months} {plural_form(months, ["месяц", "месяца", "месяцев"])}')
    if days > 0:
        parts.append(f'{days} {plural_form(days, ["день", "дня", "дней"])}')

    return ' '.join(parts)
'''


def get_median_in_range(top_range):
    numbers = [int(x) for x in top_range.split('-')]
    median = str((numbers[0] + numbers[1]) // 2)

    return median


def get_tops_frequency(streamer_films):
    tops = {
        '1': {'count': 0, 'percent': 0},
        '2': {'count': 0, 'percent': 0},
        '3': {'count': 0, 'percent': 0},
        '4': {'count': 0, 'percent': 0},
        '5': {'count': 0, 'percent': 0},
        'others': {'count': 0, 'percent': 0},
    }

    streamer_films = [film for film in streamer_films if film['view_type'] == 'аук']
    counter = 0
    for film in streamer_films:
        top = get_median_in_range(film['top_on_auction']) if '-' in film['top_on_auction'] and film['top_on_auction'] != '-' else film['top_on_auction']
        if film['top_on_auction'] != '-':
            counter += 1
        if top in tops:
            tops[top]['count'] += 1
        elif film['top_on_auction'] != '-':
            tops['others']['count'] += 1
    for top in tops:
        tops[top]['percent'] = round(tops[top]['count'] / counter * 100, 1) if counter else 0
    return tops


def get_imdb_rating_frequency(streamer_films):
    imdb_data = {
        '8': {'count': 0, 'percent': 0},
        '7': {'count': 0, 'percent': 0},
        '6': {'count': 0, 'percent': 0},
        '5': {'count': 0, 'percent': 0},
        '4': {'count': 0, 'percent': 0},
    }
    streamer_films = [film for film in streamer_films if film['rating_imdb'] != '-']
    counter = len(streamer_films)
    for film in streamer_films:
        rating = float(film['rating_imdb'])
        if rating >= 8:
            imdb_data['8']['count'] += 1
        elif 7 <= rating < 8:
            imdb_data['7']['count'] += 1
        elif 6 <= rating < 7:
            imdb_data['6']['count'] += 1
        elif 5 <= rating < 6:
            imdb_data['5']['count'] += 1
        else:
            imdb_data['4']['count'] += 1
    for imdb in imdb_data:
        imdb_data[imdb]['percent'] = round(imdb_data[imdb]['count'] / counter * 100, 1)

    return imdb_data


def get_years_frequency(streamer_films):
    years = {
        '2020': {'count': 0, 'percent': 0},
        '2010': {'count': 0, 'percent': 0},
        '2000': {'count': 0, 'percent': 0},
        '1990': {'count': 0, 'percent': 0},
        '1980': {'count': 0, 'percent': 0},
        'others': {'count': 0, 'percent': 0},
    }

    counter = len(streamer_films)
    for film in streamer_films:
        year = int(film['film_year'][:4])
        if year >= 2020:
            years['2020']['count'] += 1
        elif 2010 <= year < 2020:
            years['2010']['count'] += 1
        elif 2000 <= year < 2010:
            years['2000']['count'] += 1
        elif 1990 <= year < 2000:
            years['1990']['count'] += 1
        elif 1980 <= year < 1990:
            years['1980']['count'] += 1
        else:
            years['others']['count'] += 1
    for year in years:
        years[year]['percent'] = round(years[year]['count'] / counter * 100, 1)
    return years


def remove_non_unicode_backslashes(input_string):
    """
    Удаляет из строки все обратные слеши, за которыми не следует символ 'u'.
    """
    return re.sub(r'\\(?!u)', '', input_string)


def replace_double_quotes_in_message(input_string):
    """
    Находит подстроку "message":"какой-то текст" и заменяет двойные кавычки на одинарные внутри значения message.
    """

    start_string = '"message":"'
    end_string = '","'

    start_index = input_string.find(start_string)
    if start_index == -1:
        return input_string  # "message" не найдено

    end_index = input_string.find(end_string, start_index + len(start_string))
    if end_index == -1:
        return input_string  # Конец не найден

    start_value_index = start_index + len(start_string)
    message_value = input_string[start_value_index:end_index]

    modified_message_value = message_value.replace('"', "'")

    updated_input_string = (
        input_string[:start_value_index] + modified_message_value + input_string[end_index:]
    )

    return updated_input_string


def update_roulette_results():
    url = URL.objects.get(pk=1).url_link
    data = {}
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script')

    for script_tag in script_tags:
        # 1. Получаем содержимое (если есть)
        script_content = script_tag.text.strip()  # Убираем пробелы в начале и конце
        if script_content:
            if "addEvent" in script_content:
                ready_match = re.search(r'\$\(document\).ready\(function\s*\(\)\s*\{([\s\S]*?)\}\)\;', script_content)

                if ready_match:
                    ready_content = ready_match.group(1)
                    add_event_matches = re.findall(r"addEvent\s*\((.*?)\)\;", ready_content)
                    for match in add_event_matches:
                        match = remove_non_unicode_backslashes(match)
                        match = match.replace('"{', '{').replace('}"', '}')
                        match = replace_double_quotes_in_message(match)
                        try:
                            my_dict = json.loads(match[1:-1])
                        except:
                            print(match)
                        event_id = my_dict['id']
                        datetime = my_dict['date_created']
                        index = my_dict['header'].index('Рулетка:') + 9
                        username = my_dict['header'][index:].strip()
                        if username == "null":
                            username = 'Аноним'
                        index = my_dict['message'].index('Результат:') + 10
                        result = my_dict['message'][index:].strip()
                        try:
                            new_event = Roulette(
                                event_id=event_id,
                                datetime=datetime,
                                username=username,
                                result=result,
                                ready=False,
                                comment="",
                                show=True
                            )
                            new_event.save()
                        except IntegrityError:
                            print(f"Запись с id {event_id} уже существует. Пропускаем.")  # Сообщение об ошибке
                            continue  # Переходим к следующей итерации цикла
                else:
                    print("$(document).ready не найден.")
                break


def roulette(request):
    #locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    #locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    #start_date = timezone.make_aware(datetime(2025, 1, 1))
    #results = Roulette.objects.filter(datetime__gte=start_date).exclude(result='Ничего').order_by('-datetime')
    results = Roulette.objects.filter(show=True).order_by('-datetime')
    info_text = TextSample.objects.get(pk=2).text
    percent_text = TextSample.objects.get(pk=3).text
    data = {}
    nickname_list = set()
    results_list = set()
    MONTHS_RU = {
        1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май', 6: 'июнь',
        7: 'июль', 8: 'август', 9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
    }
    month_map = {
        "январь": 1,
        "февраль": 2,
        "март": 3,
        "апрель": 4,
        "май": 5,
        "июнь": 6,
        "июль": 7,
        "август": 8,
        "сентябрь": 9,
        "октябрь": 10,
        "ноябрь": 11,
        "декабрь": 12
    }


    NAMES = {
        'Андрей': 'anko', # 16
        'Жил был камаро': 'CAMARO' # 6
    }

    for result in results:
        username = result.username if result.username not in NAMES else NAMES[result.username]
        result_str = result.result.strip()
        data[result.id] = {
            'datetime': result.datetime,
            'username': username,
            'result': result_str,
            'ready': 'ДА' if result.ready else 'НЕТ',
            'ready_class': 'ready' if result.ready else 'not-ready',
            'order': result.order,
        }

        nickname_list.add(username)
        results_list.add(result_str)

    unique_month_years = set((r.datetime.month, r.datetime.year) for r in results)

    months_list = [f"{MONTHS_RU[m]} {y}" for m, y in unique_month_years]

    months_list = sorted(months_list, key=lambda x: (-int(x.split()[1]), month_map[x.split()[0]]), reverse=True)

    results_count = len(results)
    nickname_list = sorted(nickname_list, key=str.lower)
    results_list = sorted(results_list, key=str.lower)

    return render(request, 'main/roulette.html', {'data': data, 'months_list': months_list, 'info_text': info_text,
                                                  'percent_text': percent_text, 'nickname_list': nickname_list,
                                                  'results_list': results_list, 'results_count': results_count})
    #else:
        #return render(request, 'main/unauthorized_user.html')


def main_page(request):
    twitch_link = URL.objects.get(pk=2).url_link
    telegram_link = URL.objects.get(pk=4).url_link
    donate = URL.objects.get(pk=22)
    feedback_link = URL.objects.get(pk=23).url_link
    page_description = TextSample.objects.get(pk=5).text
    page_name = TextSample.objects.get(pk=6).text
    data = {
        'twitch_link': twitch_link,
        'telegram_link': telegram_link,
        'donate': donate,
        'feedback_link': feedback_link,
        'page_description': page_description,
        'page_name': page_name
    }

    return render(request, 'main/main.html', {'data': data})


def about(request):
    data = TextSample.objects.get(pk=1).text

    return render(request, 'main/about.html', {'data': data})


def links(request):
    #links = URL.objects.all()
    #data = {}

    #for link in links:
        #data[link.id] = {'name': link.url_name, 'link': link.url_link, 'text': link.description}

    links = URL.objects.filter(id__in=[2, 4, 22, 25])

    data = {
        link.id: {
            "name": link.url_name,
            "link": link.url_link,
            "text": link.description,
        }
        for link in links
    }

    return render(request, 'main/links.html', {'data': data})


def links_others(request):
    links = URL.objects.all()
    data = {}

    for link in links:
        data[link.id] = {'name': link.url_name, 'link': link.url_link, 'text': link.description}

    return render(request, 'main/links_others.html', {'data': data})


def clips(request):
    return render(request, 'main/clips.html')


def twitch(request):
    return render(request, 'main/twitch.html')


def telegram(request):
    return render(request, 'main/telegram.html')


def faq(request):
    if request.user.is_staff:
        data = list(QuestionAndAnswer.objects.values())

        return render(request, 'main/faq.html', {'data': data})
    else:
        return render(request, 'main/unauthorized_user.html')


def change_list(request):
    return render(request, 'main/change_list.html')


@staff_member_required
def update_roulette(request):
    if request.method == 'POST':
        try:
            update_roulette_results()
            result = {'status': 'success', 'message': 'Функция выполнена успешно!'}
        except Exception as e:
            result = {'status': 'error', 'message': str(e)}
        return JsonResponse(result)
    else:
        return JsonResponse({'status': 'error', 'message': 'Недопустимый метод запроса'})


@staff_member_required
def instruction(request):
    return render(request, 'main/instruction.html')


@staff_member_required
def custom_admin_page(request):
    channel_type = {
        '': 'обычный аккаунт',
        'affiliate': 'компаньонка',
        'partner': 'партнёрка'
    }
    stream_category = {
        '509658': 'Just Chatting',
        '116747788': 'Pools, Hot Tubs, and Beaches',
        '509672': 'IRL',
        '21779': 'League of Legends',
        '491487': 'Dead by Daylight',
        '32399': 'Counter-Strike'
    }
    options = ['get_clips', 'week_clips', 'month_clips', 'last_year_clips',
               'current_year_clips', 'all_time_clips']
    if request.method == 'POST':
        # Получаем действие (какая кнопка нажата)
        action = request.POST.get('action')

        if action == 'get_info_by_name':
            input_value = request.POST.get('get_info_by_name')
            try:
                result = get_info_by_name(input_value)
                if result != 'нет такого пользователя':
                    created_at = datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    data = {
                        'result': {
                            'id': result['id'],
                            'login': result['login'],
                            'display_name': result['display_name'],
                            'description': result['description'],
                            'profile_image_url': result['profile_image_url'],
                            'broadcaster_type': channel_type[result['broadcaster_type']],
                            'created_at': created_at,
                            'followers_count': get_followers_count_by_id(result['id'])
                        },
                        'rate_limit_remaining': result['rate_limit_remaining'],
                        'rate_limit_reset': result['rate_limit_reset'],
                        'show_limits': 'yes',
                        'ok': 'yes',
                        'endpoint': 'get_info_by_name'
                    }
                else:
                    data = {
                        'result': result,
                        'ok': 'no',
                        'endpoint': 'get_info_by_name'
                    }
            except Exception as e:
                data = {
                    'result': f"Произошла ошибка: {e}",
                    'ok': 'no',
                    'endpoint': 'get_info_by_name'
                }
        elif action == 'get_info_by_id':
            input_value = request.POST.get('get_info_by_id')

            try:
                result = get_user_by_id(input_value)
                if result != 'Нет такого пользователя':
                    created_at = datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    data = {
                        'result': {
                            'id': result['id'],
                            'login': result['login'],
                            'display_name': result['display_name'],
                            'description': result['description'],
                            'profile_image_url': result['profile_image_url'],
                            'broadcaster_type': channel_type[result['broadcaster_type']],
                            'created_at': created_at,
                            'followers_count': get_followers_count_by_id(result['id'])
                        },
                        'rate_limit_remaining': result['rate_limit_remaining'],
                        'rate_limit_reset': result['rate_limit_reset'],
                        'show_limits': 'yes',
                        'ok': 'yes',
                        'endpoint': 'get_info_by_id'
                    }
                else:
                    data = {
                        'result': result,
                        'ok': 'no',
                        'endpoint': 'get_info_by_name'
                    }
            except Exception as e:
                data = {
                    'result': f"Произошла ошибка: {e}",
                    'ok': 'no',
                    'endpoint': 'get_info_by_name'
                }
        elif action == 'get_clips':
            nickname = request.POST.get('get_clips_nickname')
            category = request.POST.get('get_clips_category')
            try:
                result, info = get_clips_by_category(nickname, category)

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'get_clips',
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'get_clips'
                }
        elif action == 'week_clips':
            try:
                result, info = get_clips_period('yrarami', 'week')

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'week_clips'
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'week_clips'
                }
        elif action == 'month_clips':
            try:
                result, info = get_clips_period('yrarami', 'month')

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'month_clips'
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'month_clips'
                }
        elif action == 'current_year_clips':
            try:
                result, info = get_clips_period('yrarami', 'current_year_clips')

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'current_year_clips'
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'current_year_clips'
                }
        elif action == 'last_year_clips':
            try:
                result, info = get_clips_period('yrarami', 'last_year_clips')

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'last_year_clips'
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'last_year_clips'
                }
        elif action == 'all_time_clips':
            try:
                result, info = get_clips_period('yrarami', 'all_time_clips')

                for clip in result:
                    clip['created_at'] = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M:%S')
                    if clip['game_id'] in stream_category:
                        clip['category'] = stream_category[clip['game_id']]
                    else:
                        clip['category'] = get_category_by_id(clip['game_id'])
                data = {
                    'result': result,
                    'rate_limit_remaining': info['rate_limit_remaining'],
                    'rate_limit_reset': info['rate_limit_reset'],
                    'show_limits': 'yes',
                    'ok': 'yes',
                    'endpoint': 'all_time_clips'
                }
            except Exception as e:
                result = f"Произошла ошибка: {e}"
                data = {
                    'result': result,
                    'ok': 'no',
                    'endpoint': 'all_time_clips'
                }
        else:
            data = {
                'result': None,
                'ok': 'no'
            }

        return render(request, 'main/admin_page.html', {'data': data, 'options': options})
    else:
        target = request.GET.get('target')

        if target == 'viewers_leaderboard':
            # 116650500 - yrarami
            # 52268235 - wizebot
            # 1392419334 - yraramibot
            # 1564983 - moobot
            excluded_user_ids = [116650500, 52268235, 1392419334, 1564983]
        
            base_qs = TwitchChatMessage.objects.filter(
                channel_name='yrarami'
            ).exclude(
                user_id__in=excluded_user_ids
            )
        
            # 1️⃣ Общее количество сообщений
            total_messages = base_qs.count()
        
            # 2️⃣ Дата самого первого сообщения
            first_message = base_qs.aggregate(
                first_date=Min("created_at")
            )["first_date"]
            first_message_date = first_message.strftime("%d.%m.%Y") if first_message else None
        
            # 3️⃣ Агрегаты по пользователям
            leaderboard_qs = list(
                base_qs
                .values("user_id")
                .annotate(
                    message_count=Count("id"),
                    days_count=Count(TruncDate("created_at"), distinct=True),
                    last_ts=Max("created_at"),  # ← важно: timestamp, не date
                )
                .order_by("-message_count")
            )
        
            # 4️⃣ Получаем последние имена (БЕЗ Q!)
            user_ids = [row["user_id"] for row in leaderboard_qs]
        
            latest_messages = (
                TwitchChatMessage.objects
                .filter(user_id__in=user_ids, channel_name='yrarami')
                .order_by("user_id", "-created_at")
                .values("user_id", "display_name")
            )
        
            latest_names = {}
            for msg in latest_messages:
                if msg["user_id"] not in latest_names:
                    latest_names[msg["user_id"]] = msg["display_name"]
        
            # 5️⃣ Собираем итоговый лидерборд
            leaderboard = []
            for row in leaderboard_qs:
                percent = round((row["message_count"] / total_messages) * 100, 2) if total_messages else 0
                leaderboard.append({
                    "display_name": latest_names.get(row["user_id"]),
                    "message_count": row["message_count"],
                    "percent": percent,
                    "days_count": row["days_count"],
                })
        
            return render(request, 'main/admin_page.html', {
                "data": {
                    "leaderboard": leaderboard,
                    "total_messages": total_messages,
                    "viewer_leaderboard_date": first_message_date,
                }
            })
    return render(request, 'main/admin_page.html', {})


def films(request):
    films = Film.objects.all().order_by('-auction_date')
    want_to_watch = FilmForWatching.objects.all()
    rules = TextSample.objects.get(pk=4).text
    want_watch_text = TextSample.objects.get(pk=8).text
    for film in want_to_watch:
        total_minutes = film.film_length
        if total_minutes and total_minutes.isdigit():
            hours = int(total_minutes) // 60 #
            minutes = int(total_minutes) % 60
            if hours:
                film.film_length_str = f"{hours} ч {minutes} мин"
            else:
                film.film_length_str = f"{minutes} мин"
        else:
            film.film_length_str = "-"

    data = {}
    nickname_list = set()
    MONTHS_RU = {
        1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май', 6: 'июнь',
        7: 'июль', 8: 'август', 9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
    }

    month_map = {
        "январь": 1,
        "февраль": 2,
        "март": 3,
        "апрель": 4,
        "май": 5,
        "июнь": 6,
        "июль": 7,
        "август": 8,
        "сентябрь": 9,
        "октябрь": 10,
        "ноябрь": 11,
        "декабрь": 12
    }

    for film in films:
        data[film.pk] = {
            'datetime': film.auction_date,
            'winners_nicknames': film.winners_nicknames,
            'film_name': film.film_name,
            'film_year': film.film_year,
            'top_on_auction': film.top_on_auction,
            'chance_to_win': film.chance_to_win,
            'kinopoisk_id': film.kinopoisk_id,
            'kinopoisk_rating': film.rating_kinopoisk,
            'imdb_rating': film.rating_imdb,
            'view_type': film.view_type,
            'auction_type': film.auction_type,
            'film_class': 'auc' if film.view_type == 'аук' else 'buy',
        }
        nickname_list.update(tuple(film.winners_nicknames.split(', ')))

    unique_month_years = set((r.auction_date.month, r.auction_date.year) for r in films)

    months_list = [f"{MONTHS_RU[m]} {y}" for m, y in unique_month_years]
    months_list = sorted(months_list, key=lambda x: (-int(x.split()[1]), month_map[x.split()[0]]))
    results_count = len(films)
    nickname_list = sorted(nickname_list, key=str.lower)

    statistics = {
        'tops': get_tops_frequency(films.values()),
        'imdb': get_imdb_rating_frequency(films.values()),
        'years': get_years_frequency(films.values())
    }

    return render(request, 'main/films.html', {'data': data, 'months_list': months_list, 'nickname_list': nickname_list,
                                               'results_count': results_count, 'want_to_watch': want_to_watch,
                                               'want_watch_text': want_watch_text, 'statistics': statistics, 'rules': rules})


def schedule(request):
    schedule_data = TextSample.objects.get(pk=9).text.split("\r\n")
    question_text = TextSample.objects.get(pk=10).text
    data = {
        'monday': schedule_data[0],
        'tuesday': schedule_data[1],
        'wednesday': schedule_data[2],
        'thursday': schedule_data[3],
        'friday': schedule_data[4],
        'saturday': schedule_data[5],
        'sunday': schedule_data[6],
    }
    return render(request, 'main/schedule.html', {'data': data, 'question_text': question_text})


# проверка является ли чатерс олдом
def check_tg_user(request):
    if request.GET.get('code') == my_secret_code:
        '''
        1) Ищем по id юзера его самое первое сообщение
        2) Если у него нет сообщений или с его даты прошло меньше 3 дней - возвращаем False, иначе возвращаем True
        '''
        user_id = request.GET.get('user_id')
        oldest_message = MessagesFromBot.objects.filter(author_id=user_id).aggregate(Min('timestamp'))
        min_timestamp = oldest_message['timestamp__min']
        print(min_timestamp)

        if min_timestamp:
            min_timestamp = min_timestamp.timestamp()
            now = datetime.now().timestamp()
            # Разница между текущей датой и временем и самой первой записью
            delta = now - min_timestamp
            min_period = 86400 * 3  # 3 дня
            print(delta)
            if delta > min_period:
                message = True
            else:
                message = False
        else:
            message = False
        print(message)
        return JsonResponse({'message': message})
    else:
        return JsonResponse({'message': 'Ошибка доступа'})


# запрос подробной статы по чатерсу
def get_tg_user_info(request):
    if request.GET.get('code') == my_secret_code:
        yrarami_ids = [777000, -1001259302177, 1259302177]
        videohostings = ['instagram.com/reel', 'tiktok.com/', 'youtube.com/', 'youtu.be', 'vk.com/clip', 'vk.com/video']
        user_id = int(request.GET.get('user_id'))
        if user_id not in yrarami_ids:
            messages = MessagesFromBot.objects.filter(author_id=user_id, chat_id=-1001359449994)
        else:
            messages = MessagesFromBot.objects.filter(author_id__in=yrarami_ids, chat_id=-1001359449994)

        message_types = {
            'video': 0,
            'photo': 0,
            'gif': 0,
            'sticker': 0
        }

        for msg in messages:
            if 'photo' in msg.message_type:
                message_types['photo'] += 1
            elif 'gif' in msg.message_type:
                message_types['gif'] += 1
            elif 'sticker' in msg.message_type:
                message_types['sticker'] += 1
            elif 'video' in msg.message_type or any(host in msg.message_text for host in videohostings):
                message_types['video'] += 1

        first_message = min(messages, key=lambda m: m.timestamp)
        formatted_first_date = first_message.timestamp.strftime('%H:%M:%S %d.%m.%Y')
        current_time = datetime.now()
        # Вычисляем разницу во времени между первым сообщением и текущим временем
        #time_difference = current_time.timestamp() - first_message.timestamp.timestamp()
        #time_difference = format_time_difference(time_difference)
        try:
            time_difference = format_time_difference(first_message.timestamp)
        except Exception as e:
            time_difference = '---'
            custom_print(e)
        total_messages_count = len(messages)
        response = {
            'first_message_date': formatted_first_date,
            'time_in_chat': time_difference,
            'total_messages_count': total_messages_count,
            'video': message_types['video'],
            'photo': message_types['photo'],
            'gif': message_types['gif'],
            'sticker': message_types['sticker']
        }

        return JsonResponse({'response': response})
    else:
        return JsonResponse({'response': 'Ошибка доступа'})


# проверка суточных лимитов телеграм чатерса по медиафайлам
@csrf_exempt
def check_tg_limits(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # Проверка на секретный код доступа
    if data.get('code') != my_secret_code:
        return JsonResponse({'error': 'Access denied'}, status=403)

    flag = Flag.objects.filter(name='лимиты на медиа в тг').first()
    if not flag.is_active:
        response = {'limits_status': 'off'}
        return JsonResponse(response)

    author_id = int(data.get('author_id'))
    nickname = data.get('nickname', '')
    media_type = data.get('media_type', '')

    if not author_id or not media_type:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    moderators = [1068939591, 7300865444, 921120420]
    # Создаём запись при необходимости (без явных defaults, Django сам подставит)
    obj, created = MediaLimit.objects.get_or_create(
        author_id=author_id,
        defaults={'is_moderator': author_id in moderators} 
    )

    obj.author_name = nickname

    # Увеличиваем счётчик в зависимости от media_type
    if media_type == 'image':
        obj.image_count += 1
    elif media_type == 'video':
        obj.video_count += 1
    elif media_type == 'gif':
        obj.gif_count += 1
    elif media_type == 'yrarami_clip':
        obj.yrarami_clips_count += 1
    elif media_type == 'other_clip':
        obj.other_clips_count += 1
    elif media_type == 'repost':
        # получаем время отправки последних двух сообщений пользователя
        last_two = list(
            MessagesFromBot.objects
            .filter(author_id=author_id)
            .order_by('-timestamp')
            .values_list('timestamp', flat=True)[:2]
        )
        if len(last_two) == 2:
            # защита от нескольких картинок в одном репосте, если с последнего сообщения
            # пользователя прошло меньше 2 сек, то считаем это за один репост
            delta = last_two[0] - last_two[1]

            if delta > timedelta(seconds=2):
                custom_print('if delta > timedelta(seconds=2):')
                obj.repost_count += 1
    else:
        return JsonResponse({'error': 'Unknown media_type'}, status=400)

    obj.save()

    # если только добавили пользователя, то лимиты не могут быть исчерпаны
    if created:
        return JsonResponse({
            'limit_exceeded': False,
            'exceeded_field': None,
            'limits_status': 'on'
        })
    else:
        # Определяем лимиты
        limits = (
            {'image_count': 20, 'video_count': 10, 'yrarami_clips_count': 10, 'other_clips_count': 3, 'repost_count': 3, 'gif_count': 5}
            if obj.is_moderator
            else {'image_count': 10, 'video_count': 3, 'yrarami_clips_count': 5, 'other_clips_count': 2, 'repost_count': 1, 'gif_count': 5}
        )

        # Проверка превышения лимита
        media_type_text = ''

        if media_type == 'image' and obj.image_count > limits['image_count']:
            media_type_text = 'изображения'
        elif media_type == 'video' and obj.video_count > limits['video_count']:
            media_type_text = 'видео'
        elif media_type == 'gif' and obj.gif_count > limits['gif_count']:
            media_type_text = 'gif'
        elif media_type == 'yrarami_clip' and obj.yrarami_clips_count > limits['yrarami_clips_count']:
            media_type_text = 'клипы с канала Рамы'
        elif media_type == 'other_clip' and obj.other_clips_count > limits['other_clips_count']:
            media_type_text = 'клипы с чужих каналов'
        elif media_type == 'repost' and obj.repost_count > limits['repost_count']:
            media_type_text = 'репосты'

        response = {
            'limit_exceeded': bool(media_type_text),
            'media_type_text': media_type_text,
            'limits_status': 'on'
        }
        if media_type_text:
            image_count_remainder = max(limits['image_count'] - obj.image_count, 0)  # чтобы отсечь отрицательные значения
            video_count_remainder = max(limits['video_count'] - obj.video_count, 0)
            gif_count_remainder = max(limits['gif_count'] - obj.gif_count, 0)
            yrarami_clips_count_remainder = max(limits['yrarami_clips_count'] - obj.yrarami_clips_count, 0)
            other_clips_count_remainder = max(limits['other_clips_count'] - obj.other_clips_count, 0)
            repost_count_remainder = max(limits['repost_count'] - obj.repost_count, 0)
            response['user_data'] = {
                'image_count_remainder': f"{image_count_remainder}/{limits['image_count']}",
                'video_count_remainder': f"{video_count_remainder}/{limits['video_count']}",
                'gif_count_remainder': f"{gif_count_remainder}/{limits['gif_count']}",
                'yrarami_clips_count_remainder': f"{yrarami_clips_count_remainder}/{limits['yrarami_clips_count']}",
                'other_clips_count_remainder': f"{other_clips_count_remainder}/{limits['other_clips_count']}",
                'repost_count_remainder': f"{repost_count_remainder}/{limits['repost_count']}"
            }

        return JsonResponse(response)


def check_tg_limits_for_command(request):
    if request.GET.get('code') == my_secret_code:
        user_id = int(request.GET.get('user_id'))
        user = MediaLimit.objects.filter(author_id=user_id).first()
        response = {'limits': ''}
        moderators = [1068939591, 7300865444, 921120420]
        limits = (
            {'image_count': 20, 'video_count': 10, 'yrarami_clips_count': 10, 'other_clips_count': 3, 'repost_count': 3, 'gif_count': 5}
            if user_id in moderators
            else {'image_count': 10, 'video_count': 3, 'yrarami_clips_count': 5, 'other_clips_count': 2, 'repost_count': 1, 'gif_count': 5}        )
        if user is None:
            response['limits'] = (
                f"Ваши оставшиеся лимиты на сегодня:\n"
                f"Видео: {limits['video_count']}/{limits['video_count']}\n"
                f"Изображения: {limits['image_count']}/{limits['image_count']}\n"
                f"GIF: {limits['gif_count']}/{limits['gif_count']}\n"
                f"Клипы с канала Рамы: {limits['yrarami_clips_count']}/{limits['yrarami_clips_count']}\n"
                f"Клипы с других каналов: {limits['other_clips_count']}/{limits['other_clips_count']}\n"
                f"Репосты: {limits['repost_count']}/{limits['repost_count']}"
            )
        else:
            image_count_remainder = max(limits['image_count'] - user.image_count, 0)  # чтобы отсечь отрицательные значения
            video_count_remainder = max(limits['video_count'] - user.video_count, 0)
            gif_count_remainder = max(limits['gif_count'] - user.gif_count, 0)
            yrarami_clips_count_remainder = max(limits['yrarami_clips_count'] - user.yrarami_clips_count, 0)
            other_clips_count_remainder = max(limits['other_clips_count'] - user.other_clips_count, 0)
            repost_count_remainder = max(limits['repost_count'] - user.repost_count, 0)
            response['limits'] = (
                f"Ваши оставшиеся лимиты на сегодня:\n"
                f"Видео: {video_count_remainder}/{limits['video_count']}\n"
                f"Изображения: {image_count_remainder}/{limits['image_count']}\n"
                f"GIF: {gif_count_remainder}/{limits['gif_count']}\n"
                f"Клипы с канала Рамы: {yrarami_clips_count_remainder}/{limits['yrarami_clips_count']}\n"
                f"Клипы с других каналов: {other_clips_count_remainder}/{limits['other_clips_count']}\n"
                f"Репосты: {repost_count_remainder}/{limits['repost_count']}"
            )

        return JsonResponse(response)
    else:
        return JsonResponse({'error': 'Access denied'}, status=403)


love_variants = {
    "0": [
        "Это я - твой единственный зритель. Я на протяжении многих лет создавал иллюзию того, что тебя смотрят много "
        "людей, но это был я. А ты вот так вот поступила со мной, после всего что между нами было? Вот так вот, да? "
        "Ну хорошо. Ладно. Я всё понял. Я больше не буду писать тебе сообщения со всех своих аккаунтов. Прощай...🙄 "
    ],
    "1-40": [
        "Весьма прискорбно, наша любимая стримерша совсем забыла про своих зрителей, она больше не хочет радовать нас своими "
        "чудесными образами, улыбкой и хорошим настроением. После такого предательства мне ничего не остаётся кроме как пойти "
        "бомжевать на вокзал и горько плакать, провожая людей покрасневшими мокрыми глазами, тех самых людей, которые "
        "спешат на поезд, чтобы встретиться с ТЕМИ КОМУ ОНИ НУЖНЫ 😩",
        "Сколько сколько?! Больше 3 дней...Чувствую себя как брошенный щенок, которого хозяйка привязала к дереву в парке "
        "и оставила навсегда 🥺",
        "Рамыч наверно заболела или депрессует, может творческий кризис или ещё что...Мы тебя очень любим, возвращайся скорее!"
    ],
    "41-60": [
        "Блять, Ирина, ёб твою мать, чё за пылесос такой? Его никто нахуй не купит, блять! Его даже выебать в трубку невозможно..."
        "Ты ебанутая совсем просто...просто ебанутая! 🗿",
        "2 дня без стримов...вы понимаете, что это уже не шутки? Ирина, пожалуйста, задумайся, услышь нас - дело набирает "
        "серьёзный оборот. А дальше что? 3 дня без стримов? 4 дня? А может быть неделя?! 🤯 Это просто неслыхано! "
        "На первый раз прощаем, но ты должна прямо сейчас завести стрим! 😤",
        "Сколько?! 2 дня? Да ты шо ахуэл блять...Ребят, всё, идём искать другую стримерку 😢",
        "Стрима не было вчера и стрима не было позавчера. Вам может показаться, что тут всё ясно, но, ребята, не стоит "
        "вскрывать эту тему. Вы молодые, шутливые, вам все легко. Это не то. Это не Папа Конь и даже не лолерская стримхата. "
        "Сюда лучше не лезть. Серьезно, любой из вас будет жалеть, что не оформил подписку на приватку t.me/yrarami/2174. "
        "В остальном же лучше закройте тему и забудьте что тут писалось. Я вполне понимаю что данным сообщением вызову "
        "дополнительный интерес где же стримы, но хочу сразу предостеречь пытливых - стоп. Остальных просто не найдут.",
        "Рамыч наверно заболела или депрессует, может творческий кризис или ещё что...Мы тебя очень любим, возвращайся скорее!"
    ],
    "61-80": [
        "С последнего поточка вообще то больше суток прошло так то...Не то чтобы я на что-то намекаю, но я на что-то намекаю 😏",
        "А куда делся стример? Вроде вчера не было подруба, сегодня тоже тишина, нам уже начинать волноваться? 🙄\n"
        "Пока что ещё люблю, но беру тебя на карандашик...",
        "Хороший вчера был стрим, отдыхай милашка...А, погоди, вчера его не было 🤔 Как же так? Нууу ты же подрубишь сегодня, "
        "не бросишь своих зрителей, ведь правда, да? 🥺"
    ],
    "81-99": [
        "Так приятно, когда твой стример регулярно стримит 🥰 \nИря, мы тебя очень любим ❤️",
        "Фууух, вышла из душа, так приятно 🙂 Обернула 50кг тело и грудь 3го размера полотенчиком, вся мокренькая...жаль слетела подписочка "
        "на любимую стримершу clck.ru/3RkPSk, ой слетеелааа... Мальсики, купите пж 🥺",
        "Иря стримит регулярно и очень бодро! У неё вайбовые стримы! Жаль, что далеко не все поймут в чём же дело)))) "
        "Действительно тонко))))) Не так уж много и образованных в наше время, кто знает, почему её стримы так интересны и необычны)))) 😏",
        "Охуенный был стрим! После такого можно и отдохнуть хорошенько 😌 \nМы тебя очень любим (пока что)."
    ],
    "100": "Арарамушка зайка солнышко на стриме сказала, что любит меня, думая, что любит меня! Да она не может любить меня! А я люблю тебя!",
    "146": "Ребята, Арарамушка сейчас стримит twitch.tv/yrarami\n"
           "Самая красивая девочка на свете! ❤️❤️❤️ Самая лучшая, самая добрая! Ребята, вот Арарамушка, это дружественный канал. "
           "Дай Бог здоровья и успехов нашей красотульке!❤️❤️❤️\n"
           "Обязательно заходите на стримчик twitch.tv/yrarami"
}

@csrf_exempt
def get_love(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # Проверка на секретный код доступа
    if data.get('code') != my_secret_code:
        return JsonResponse({'error': 'Access denied'}, status=403)

    author_id = int(data.get('author_id'))
    nickname = data.get('nickname', '')
    response = ''

    obj, created = Love.objects.get_or_create(
        author_id=author_id,
        defaults={
            "author_name": nickname,
            "updated_at": timezone.now(),
        }
    )

    # проверяем дату последнего успешного выполнения команды !love, если дата не совпадает с датой вызова, тогда
    # выполняем и обновляем дату выполнения команды
    if created or obj.updated_at.date() != timezone.now().date():
        last_stream = (
            TwitchStream.objects
            .order_by("-started_at")
            .first()
        )
        # Если стрим идёт
        if last_stream.ended_at is None:
            obj.counter = 1 if created else obj.counter + 1
            obj.updated_at = timezone.now()
            obj.save()

            return JsonResponse({"response": love_variants['146']})

        # считаем сколько времени прошло с последнего стрима
        time_since_end = timezone.now() - last_stream.ended_at

        total_hours = int(time_since_end.total_seconds() // 3600)
        days = total_hours // 24
        hours = total_hours % 24

        if total_hours < 24:
            random_integer = random.randint(81, 100)
            if random_integer == 100:
                response = love_variants["100"]
            else:
                response = random.choice(love_variants["81-99"])
        elif 24 <= total_hours < 48:
            random_integer = random.randint(61, 80)
            response = random.choice(love_variants["61-80"])
        elif 48 <= total_hours < 72:
            random_integer = random.randint(41, 60)
            response = random.choice(love_variants["41-60"])
        else:
            random_integer = random.randint(0, 40)
            if random_integer == 0:
                response = love_variants["0"]
            else:
                response = random.choice(love_variants["1-40"])

        # Формируем человекочитаемое время
        parts = []

        if days > 0:
            parts.append(f"{days} {plural(days, ('день', 'дня', 'дней'))}")
        if hours > 0 or days == 0:
            parts.append(f"{hours} {plural(hours, ('час', 'часа', 'часов'))}")

        time_text = " ".join(parts)

        response = f"С последнего стрима {"прошёл" if days == 1 else "прошло"} {time_text}, сегодня любишь yrarami на {random_integer}%.\n\n" \
                   f"{response}"

        obj.counter = 1 if created else obj.counter + 1
        obj.save()
    else:
        response = "Вы уже спрашивали сегодня, лимит на любовь исчерпан, приходите завтра 😉"
        return JsonResponse({"response": response})

    return JsonResponse({"response": response})


@csrf_exempt
def tg_admin(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # Проверка на секретный код доступа
    if data.get('code') != my_secret_code:
        return JsonResponse({'error': 'Access denied'}, status=403)

    option = data.get('option')
    response = ''
    flag = Flag.objects.filter(name='лимиты на медиа в тг').first()
    if option == 'status':
        if flag.is_active:
            response = 'Лимиты на медиа включены ✅'
        else:
            response = 'Лимиты на медиа выключены ❌'
    elif option == 'on':
        flag.is_active = True
        flag.save()
        response = 'Лимиты на медиа снова отслеживаются 🎉'
    elif option == 'off':
        flag.is_active = False
        flag.save()
        response = 'Лимиты на медиа больше не отслеживаются 😒'

    return JsonResponse({"response": response})


def get_tg_rules(request):
    if request.GET.get('code') == my_secret_code:
        rules = TextSample.objects.get(pk=12).text
        return JsonResponse({"response": rules})

    return JsonResponse({"response": "Ошибка доступа"})


def get_last_donate(request):
    if request.GET.get('code') == my_secret_code:
        last_donate = Donate.objects.order_by('-datetime').first()

        if not last_donate:
            return JsonResponse({"response": None})

        return JsonResponse({
            "response": {
                "username": last_donate.username,
                "message": last_donate.message,
                "is_commission_covered": last_donate.is_commission_covered,
                "amount": round(last_donate.amount),
                "amount_main": round(last_donate.amount_main),
                "currency": last_donate.currency,
            }
        })

    return JsonResponse({"response": "Ошибка доступа"})


def get_driving_experience(request):
    if request.GET.get('code') == my_secret_code:
        drive = driving_experience()
        return JsonResponse({"response": drive})

    return JsonResponse({"response": "Ошибка доступа"})


def get_tg_top_users(request):
    if request.GET.get('code') == my_secret_code:
        top_users = get_top_users_text()
        return JsonResponse({"response": top_users})

    return JsonResponse({"response": "Ошибка доступа"})


######### ОТСЛЕЖИВАНИЕ НАЧАЛА И КОНЦА СТРИМА #########
TWITCH_WEBHOOK_SECRET = "h9T1m0vK8s2fH7Yl3aerPz5sD36bNpX7"
TWITCH_BROADCASTER_ID = "116650500"
TELEGRAM_BOT_TOKEN = "7875706157:AAEqgxA84MFdS3L9hxthHuaHYNCTNXjYa5E"
TELEGRAM_CHAT_ID = "-1001359449994" #"-1002511000091" - тестовый чат, "-1001359449994" - чат Рамы
STREAMER_ID = 116650500
TWITCH_CALLBACK_URL = "https://yrarami.ru/twitch_webhook/"


# функция, что расшифровывает secret что пришёл в запросе и
# проверяет совпадает ли он с нашим исходным secret (контроль доступа
# с нашей стороны, чтобы не было левых запросов на этот url)
def verify_twitch_signature(secret: str, request) -> bool:
    signature = request.headers.get("Twitch-Eventsub-Message-Signature", "")
    message_id = request.headers.get("Twitch-Eventsub-Message-Id", "")
    timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp", "")

    if not signature or not message_id or not timestamp:
        return False

    message = message_id.encode('utf-8') + timestamp.encode('utf-8') + request.body

    expected_hash = hmac.new(
        key=secret.encode('utf-8'),
        msg=message,
        digestmod=hashlib.sha256
    ).hexdigest()
    expected = f"sha256={expected_hash}"

    return hmac.compare_digest(expected, signature)


def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("Telegram error:", e)


def create_subscription(event_type: str) -> None:
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_APP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "type": event_type,
        "version": "1",
        "condition": {
            "broadcaster_user_id": TWITCH_BROADCASTER_ID
        },
        "transport": {
            "method": "webhook",
            "callback": TWITCH_CALLBACK_URL,
            "secret": TWITCH_WEBHOOK_SECRET
        }
    }

    response = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        json=payload,
        headers=headers,
        timeout=10
    )

    if response.status_code != 202:
        print(
            f"[Twitch] Failed to create subscription "
            f"{event_type}: {response.status_code} {response.text}"
        )
        return

    data = response.json()["data"][0]

    TwitchSubscription.objects.update_or_create(
        event_type=event_type,
        defaults={
            "subscription_id": data["id"],
        }
    )


@csrf_exempt
def twitch_webhook(request):
    if not verify_twitch_signature(
        TWITCH_WEBHOOK_SECRET,
        request
    ):
        return HttpResponse(status=403)

    log_twitch_request(request)
    payload = json.loads(request.body)

    # --- Twitch challenge ---
    if "challenge" in payload:
        return HttpResponse(
            payload["challenge"],
            content_type="text/plain"
        )

    subscription = payload.get("subscription", {})
    event_type = subscription.get("type")
    status = subscription.get("status")
    event = payload.get("event", {})

    # --- Подписка не активна ---
    if status != "enabled":
        custom_print(f"[Twitch] Subscription {event_type} status={status}, recreating")
        create_subscription(event_type)
        return HttpResponse(status=200)

    # --- STREAM ONLINE ---
    if event_type == "stream.online":
        # даём время Helix создать стрим, потому что EventSub всегда спешит
        for _ in range(6):
            stream_info = get_stream_info(STREAMER_ID)
            if stream_info:
                break
            time.sleep(10)

        if not stream_info:
            # стрим не найден (race condition)
            custom_print("stream_info не найден")
            return HttpResponse(status=200)

        started_at = parse_datetime(stream_info["started_at"])

        stream = TwitchStream.objects.create(
            stream_id=stream_info["id"],
            title=stream_info["title"],
            started_at=started_at
        )
        custom_print("стрим начался")
        send_telegram_message(
            f"🔴 Стрим начался!\n"
            f"Название: {stream.title}\n"
            f"twitch.tv/yrarami"
        )

    # --- STREAM OFFLINE ---
    elif event_type == "stream.offline":
        custom_print("стрим закончился")

        stream = (
            TwitchStream.objects
            .filter(ended_at__isnull=True)
            .order_by("-started_at")
            .first()
        )

        if not stream:
            return HttpResponse(status=200)

        stream.ended_at = timezone.now()
        stream.save()

        # --- сообщения стрима ---
        messages = TwitchChatMessage.objects.filter(
            created_at__gte=stream.started_at,
            created_at__lte=stream.ended_at
        )

        total_messages = messages.count()

        unique_chatters_count = (
            messages
            .values('display_name')
            .distinct()
            .count()
        )

        # --- сообщения по минутам ---
        # решил считать именно медианную скорость (а не просто среднюю) и без учёта пустых минут, так как например 
        # на ИРЛ стримах могут быть лаги и в это время простой в чате или например первые минуты стрима заставка
        per_minute = {}
        for msg in messages.only("created_at"):
            minute = msg.created_at.replace(second=0, microsecond=0)
            per_minute[minute] = per_minute.get(minute, 0) + 1

        median_speed = (
            statistics.median(per_minute.values())
            if per_minute else 0
        )

        # --- ТОП-5 ---
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        top_chatters = (
            messages
            .values('display_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        top_chatters_with_percent = []
        for c in top_chatters:
            percent = round(c['count'] / total_messages * 100) if total_messages else 0
            top_chatters_with_percent.append({
                **c,
                "percent": percent
            })

        top5_percent = sum(c["percent"] for c in top_chatters_with_percent)

        top_chatters_text = "\n".join(
            f"{medals[i]} {c['display_name']} - {c['count']} ({c['percent']}%)"
            for i, c in enumerate(top_chatters_with_percent)
        )

        send_telegram_message(
            f"⚫️ Стрим завершён\n"
            f"Длительность: {stream.duration}\n"
            f"Всего сообщений: {total_messages} (топ-5: {top5_percent}%)\n"
            f"Уникальных чаттерсов: {unique_chatters_count}\n"
            f"Средняя скорость чата: {median_speed} сообщ/мин\n"
            f"Топ 5 чаттерсов:\n"
            f"{top_chatters_text}"
        )
    elif event_type == "channel.ban":    
        user_login = event.get("user_login")
        user_id = event.get("user_id")
    
        moderator_login = event.get("moderator_user_login")
        moderator_id = event.get("moderator_user_id")
    
        reason = event.get("reason")
        ends_at = event.get("ends_at")  # null = перманентный бан
    
        if ends_at:
            action = "TIMEOUT"
        else:
            action = "BAN"
    
        custom_print(
            f"[Twitch] {action} | "
            f"user={user_login} ({user_id}) | "
            f"moderator={moderator_login} ({moderator_id}) | "
            f"ends_at={ends_at} | "
            f"reason={reason} | "
            f"raw_event={event}"
        )
    elif event_type == "channel.unban":
        user_login = event.get("user_login")
        user_id = event.get("user_id")
    
        moderator_login = event.get("moderator_user_login")
        moderator_id = event.get("moderator_user_id")
    
        custom_print(
            f"[Twitch] UNBAN_OR_UNTIMEOUT | "
            f"user={user_login} ({user_id}) | "
            f"moderator={moderator_login} ({moderator_id}) | "
            f"raw_event={event}"
        )
    else:
        custom_print("Это другой эвент")

    return HttpResponse(status=200)


#################### КОНЕЦ БЛОКА ####################


def humanize_timedelta(td):
    total_seconds = int(td.total_seconds())
    if total_seconds < 60:
        return "меньше минуты назад"

    minutes = total_seconds // 60
    hours = minutes // 60
    days = hours // 24

    hours %= 24
    minutes %= 60

    parts = []

    if days:
        parts.append(f"{days} дн.")
    if hours:
        parts.append(f"{hours} ч.")
    if not parts and minutes:
        parts.append(f"{minutes} мин.")

    return " ".join(parts) + " назад"


@csrf_exempt
def get_last_stream(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # Проверка на секретный код доступа
    if data.get('code') != my_secret_code:
        return JsonResponse({'error': 'Access denied'}, status=403)

    last_stream = (
        TwitchStream.objects
        .order_by('-started_at')
        .first()
    )

    if not last_stream:
        return JsonResponse({"response": "Стримов ещё не было"})

    # Если стрим ещё идёт
    if last_stream.ended_at is None:
        now_time = timezone.now()
        duration = now_time - last_stream.started_at

        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        response = (
            f"Стрим ещё идёт!\n\n"
            f"Начался {last_stream.started_at:%d.%m.%Y} в {last_stream.started_at:%H:%M}\n"
            f"Идёт уже {hours:02}:{minutes:02}:{seconds:02}\n"
            f"Заглядывай на стримчик twitch.tv/yrarami"
        )
        return JsonResponse({"response": response})

    # Сколько времени прошло после окончания
    time_ago = timezone.now() - last_stream.ended_at

    # Сообщения стрима (фильтрация по времени)
    # Приводим к локальному времени
    local_started = timezone.localtime(last_stream.started_at)
    local_ended = timezone.localtime(last_stream.ended_at)
    messages = TwitchChatMessage.objects.filter(
        created_at__gte=last_stream.started_at,
        created_at__lte=last_stream.ended_at
    ).order_by('created_at')

    total_messages = messages.count()

    unique_chatters_count = (
        messages
        .values('display_name')
        .distinct()
        .count()
    )

    # Сообщения по минутам для медианы
    per_minute = {}

    for msg in messages.only("created_at"):
        minute = msg.created_at.replace(second=0, microsecond=0)
        per_minute[minute] = per_minute.get(minute, 0) + 1

    median_speed = (
        statistics.median(per_minute.values())
        if per_minute else 0
    )
    '''
    # Топ-5 чаттеров
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    top_chatters = (
        messages
        .values('display_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    top_chatters_text = "\n".join(
        f"{medals[i]} {c['display_name']} - {c['count']}"
        for i, c in enumerate(top_chatters, start=0)
    )

    response = (
        f"Последний стрим был {humanize_timedelta(time_ago)}\n"
        f"Название: {last_stream.title}\n"
        f"Начало: {local_started:%d.%m.%Y} в {local_started:%H:%M}\n"
        f"Конец: {local_ended:%d.%m.%Y} в {local_ended:%H:%M}\n"
        f"Время стрима: {last_stream.duration}\n"
        f"Всего сообщений: {total_messages}\n"
        f"Уникальных чаттерсов: {unique_chatters_count}\n"
        f"Средняя скорость чата: {median_speed} сообщ/мин\n"
        f"Топ 5 чаттерсов:\n"
        f"{top_chatters_text}"
    )
    return JsonResponse({"response": response})
    '''

    # Топ-5 чаттеров с процентами
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    top_chatters = (
        messages
        .values('display_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    top_chatters_with_percent = []
    for c in top_chatters:
        percent = round(c['count'] / total_messages * 100) if total_messages else 0
        top_chatters_with_percent.append({
            **c,
            "percent": percent
        })

    top5_percent = sum(c["percent"] for c in top_chatters_with_percent)

    top_chatters_text = "\n".join(
        f"{medals[i]} {c['display_name']} - {c['count']} ({c['percent']}%)"
        for i, c in enumerate(top_chatters_with_percent)
    )

    response = (
        f"Последний стрим был {humanize_timedelta(time_ago)}\n"
        f"Название: {last_stream.title}\n"
        f"Начало: {local_started:%d.%m.%Y} в {local_started:%H:%M}\n"
        f"Конец: {local_ended:%d.%m.%Y} в {local_ended:%H:%M}\n"
        f"Время стрима: {last_stream.duration}\n"
        f"Всего сообщений: {total_messages} (топ-5: {top5_percent}%)\n"
        f"Уникальных чаттерсов: {unique_chatters_count}\n"
        f"Средняя скорость чата: {median_speed} сообщ/мин\n"
        f"Топ 5 чаттерсов:\n"
        f"{top_chatters_text}"
    )
    return JsonResponse({"response": response})


def tg_rules(request):
    rules = TextSample.objects.get(pk=13).text

    return render(request, 'main/tg_rules.html', {'rules': rules})


@csrf_exempt
def get_last_tg_message(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if data.get('code') != my_secret_code:
        return JsonResponse({"response": "Ошибка доступа"})

    user_id = data.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id parameter is required'}, status=400)

    last_timestamp = (
        MessagesFromBot.objects
        .filter(author_id=user_id)
        .values_list('timestamp', flat=True)
        .order_by('-timestamp')
        .first()
    )

    return JsonResponse({
        'timestamp': last_timestamp.isoformat() if last_timestamp else None
    })


def save_followers(request):
    if not (request.user.is_superuser):
        return HttpResponseForbidden("Нет доступа")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = int(data.get("user_id"))
            login = data.get("login", "")
            chat_name = data.get("chat_name", "")
            account_date_str = data.get("account_date", "")

            # Конвертируем дату из формата "DD.MM.YYYY HH:MM:SS"
            account_date = datetime.strptime(account_date_str, "%d.%m.%Y %H:%M:%S")

            # Сохраняем в базу
            obj = Follower.objects.create(
                twitch_id=user_id,
                login=login,
                nickname=chat_name,
                creation_date=account_date
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)}, status=400)

    return JsonResponse({"status": "error", "msg": "POST required"}, status=400)


def twitch_auth(request):
    TWITCH_CLIENT_ID = "y0o2xnuac24iphenirsxizknz9tjgw"
    TWITCH_CLIENT_SECRET = "e4kjrrugta7lg38r1b3yw6edicfakx"
    scopes = "channel:moderate"


    auth_url = (
        "https://id.twitch.tv/oauth2/authorize"
        f"?client_id={TWITCH_CLIENT_ID}"
        f"&redirect_uri={request.build_absolute_uri('/twitch/callback/')}"
        "&response_type=code"
        f"&scope={scopes}"
    )

    return redirect(auth_url)


def twitch_callback(request):
    TWITCH_CLIENT_ID = "y0o2xnuac24iphenirsxizknz9tjgw"
    TWITCH_CLIENT_SECRET = "e4kjrrugta7lg38r1b3yw6edicfakx"

    code = request.GET.get("code")
    if not code:
        return HttpResponseBadRequest("No code provided")

    token_url = "https://id.twitch.tv/oauth2/token"

    data = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": request.build_absolute_uri("/twitch/callback/"),
    }

    resp = requests.post(token_url, data=data)
    resp.raise_for_status()

    tokens = resp.json()

    with open("twitch_tokens.json", "a") as f:
        f.write(json.dumps(tokens) + "\n")

    return HttpResponse("Access token сохранён")


@csrf_exempt
def get_twitch_app_token(request):
    """
    Возвращает валидный токен для данного имени.
    Если токен просрочен, можно вызвать refresh.
    """

    name="twitch_app_main"

    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if data.get('code') != my_secret_code:
        return JsonResponse({"response": "Ошибка доступа"})

    try:
        token_obj = TwitchAppToken.objects.get(name=name)
    except TwitchAppToken.DoesNotExist:
        raise RuntimeError(f"Twitch token '{name}' не найден в базе")

    # Проверяем, не истёк ли токен
    if token_obj.expires_at <= timezone.now():
        raise RuntimeError(f"Twitch token '{name}' просрочен")

    return JsonResponse({"access_token": token_obj.access_token})
