import time
from datetime import datetime
import requests
from django.http import HttpResponse
import locale
import pymorphy3
from dateutil.relativedelta import relativedelta
from main.models import TwitchAppToken
from django.utils import timezone

#locale.setlocale(
#    category=locale.LC_ALL,
#    locale="ru_RU.UTF-8"  # Note: do not use "de_DE" as it doesn't work
#)

TWITCH_CLIENT_ID = 'y0o2xnuac24iphenirsxizknz9tjgw'
clientSecret = 'e4kjrrugta7lg38r1b3yw6edicfakx'


'''
Раньше запрашивали токен один раз при запуске джанго сервера и он хранился в памяти
Теперь токен хранится в БД и обновляется по расписанию скриптом вне джанго

def get_token():
    url = 'https://id.twitch.tv/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': clientSecret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()['access_token']


token = get_token()
'''


def get_app_token(name="twitch_app_main"):
    """
    Возвращает валидный токен для данного имени.
    Если токен просрочен, можно вызвать refresh.
    """
    try:
        token_obj = TwitchAppToken.objects.get(name=name)
    except TwitchAppToken.DoesNotExist:
        raise RuntimeError(f"Twitch token '{name}' не найден в базе")

    # Проверяем, не истёк ли токен
    if token_obj.expires_at <= timezone.now():
        raise RuntimeError(f"Twitch token '{name}' просрочен")

    return token_obj.access_token


def get_id_by_name(username):
    url = f'https://api.twitch.tv/helix/users?login={username}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    if not response.json()['data']:
        return 'нет такого пользователя'
    else:
        return response.json()['data'][0]['id']


def get_info_by_name(username):
    url = f'https://api.twitch.tv/helix/users?login={username}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    response_json = response.json()
    if str(response_json.get('status')) == '400':
        print(f'пользователь с ником {username} не найден')
        info = 'нет такого пользователя'
    elif response_json.get('data'):
        if 'id' in response_json.get('data')[0]:
            info = response.json()['data'][0]
            print('всё ок')
        else:
            print('нет такого пользователя 1')
            info = 'нет такого пользователя'
        rate_limit = response.headers.get('RateLimit-Limit')
        rate_limit_remaining = response.headers.get('RateLimit-Remaining')
        rate_limit_reset = response.headers.get('RateLimit-Reset')
        reset_ts = int(rate_limit_reset)
        now = int(time.time())
        seconds_until_reset = max(0, reset_ts - now)
        info['rate_limit_remaining'] = f'{rate_limit_remaining}/{rate_limit}'
        info['rate_limit_reset'] = seconds_until_reset
    else:
        print(response_json)
        print('нет такого пользователя 2')
        rate_limit_remaining = response.headers.get('RateLimit-Remaining')
        print(f"Осталось запросов: {rate_limit_remaining}")
        info = 'нет такого пользователя'

    return info


def get_user_by_id(id):
    url = f'https://api.twitch.tv/helix/users?id={id}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    response_json = response.json()

    if str(response_json.get('status')) == '400':
        print(f'пользователь с id {id} не найден')
        info = 'нет такого пользователя'
    elif response_json.get('data'):
        info = response.json()['data'][0]

        rate_limit = response.headers.get('RateLimit-Limit')
        rate_limit_remaining = response.headers.get('RateLimit-Remaining')
        rate_limit_reset = response.headers.get('RateLimit-Reset')
        reset_ts = int(rate_limit_reset)
        now = int(time.time())
        seconds_until_reset = max(0, reset_ts - now)
        info['rate_limit_remaining'] = f'{rate_limit_remaining}/{rate_limit}'
        info['rate_limit_reset'] = seconds_until_reset
    else:
        info = 'нет такого пользователя'

    return info


def get_user_by_id_full_data(id):
    url = f'https://api.twitch.tv/helix/users?id={id}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)

    return response.json()


def get_followers_count_by_name(nickname):
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={get_id_by_name(nickname)}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    followers = response.json()['total']

    return followers


# ПОЛУЧИТЬ КОЛИЧЕСТВО ФОЛЛОВЕРОВ ПО ID КАНАЛА
def get_followers_count_by_id(user_id):
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={user_id}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    return response.json()['total']


def get_clips(nickname):
    url = f'https://api.twitch.tv/helix/clips?broadcaster_id={get_id_by_name(nickname)}'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }

    response = requests.get(url, headers=headers)

    return response


def get_category_by_id(category_id):
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }
    response = requests.get(
        f'https://api.twitch.tv/helix/games?id={category_id}',
        headers=headers
    )

    if response.status_code == 200:
        game_data = response.json()['data'][0]
        category_name = game_data['name']
    else:
        category_name = 'неизвестная категория'
        print('Ошибка:', response.status_code)

    return category_name


def get_clips_by_category(nickname, category_id):
    start_time = time.time()
    # сколько клипов нужно получить
    limit = 20
    url_base = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }
    broadcaster_id = get_id_by_name(nickname)
    collected_clips = []
    unique_clips_ids = set()
    clips_ids = []
    cursor = None
    first_cursor = None
    iterations = 0
    counter = 0
    info = {
        'rate_limit_remaining': None,
        'rate_limit_reset': None,
    }

    while len(collected_clips) < limit:
        # Определяем параметры для следующего запроса
        params = {
            'broadcaster_id': broadcaster_id,
            'first': 100,  # Берём максимум 100 клипов за раз
        }
        if cursor:
            params['after'] = cursor

        # Делаем запрос
        response = requests.get(url_base, headers=headers, params=params)
        iterations += 1
        # ====== ДОБАВЛЕНО: обработка лимитов ======
        rate_limit = response.headers.get('RateLimit-Limit')
        rate_limit_remaining = response.headers.get('RateLimit-Remaining')
        rate_limit_reset = response.headers.get('RateLimit-Reset')

        if rate_limit_reset:
            reset_ts = int(rate_limit_reset)
            now = int(time.time())
            seconds_until_reset = max(0, reset_ts - now)
        else:
            seconds_until_reset = None

        info['rate_limit_remaining'] = f'{rate_limit_remaining}/{rate_limit}'
        info['rate_limit_reset'] = seconds_until_reset
        # =========================================
        if response.status_code != 200:
            print(response.status_code)
            break  # Выходим, если произошла ошибка

        data = response.json()
        unique_clips_ids.update(clip['id'] for clip in data['data'])
        if category_id != 'all':
            clips_for_extend = []
            for clip in data['data']:
                if clip['game_id'] == category_id and clip['id'] not in clips_ids:
                    clips_for_extend.append(clip)
                    clips_ids.append(clip['id'])
            collected_clips.extend(clips_for_extend)
        else:
            clips_for_extend = []
            for clip in data['data']:
                if clip['id'] not in clips_ids:
                    clips_for_extend.append(clip)
                    clips_ids.append(clip['id'])
            collected_clips.extend(clips_for_extend)

        counter += len(data['data'])
        print(f"{data['data'][0]['view_count']} {counter} {len(unique_clips_ids)} {iterations}")
        # Выходим, если собрали достаточно клипов
        if len(collected_clips) >= limit:
            break
        # Обновляем курсор для следующей итерации
        cursor = data.get('pagination', {}).get('cursor')
        # Выходим, если уже пошли перебирать клипы по второму кругу
        if cursor == first_cursor:
            print('курсоры совпали')
            end_time = time.time()
            print(f"Время выполнения: {end_time - start_time} секунд")
            break
        if counter <= 100:
            first_cursor = cursor
    collected_clips = sorted(collected_clips, key=lambda x: x['view_count'], reverse=True)

    return collected_clips[:limit], info


# получить клипы за указанный период
def get_clips_period(nickname, period):
    url = f'https://api.twitch.tv/helix/clips'
    headers = {
        'Authorization': 'Bearer ' + get_app_token(),
        'Client-Id': TWITCH_CLIENT_ID
    }
    broadcaster_id = get_id_by_name(nickname)
    current_date = datetime.now()
    ended_at = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    if period == 'all_time_clips':
        started_at = datetime(2019, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif period == 'last_year_clips':
        started_at = (current_date - relativedelta(years=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif period == 'current_year_clips':
        started_at = datetime(2026, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
    elif period == 'month':
        started_at = (current_date - relativedelta(months=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    # week_clips
    else:
        started_at = (current_date - relativedelta(weeks=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f"Период поиска: {started_at} - {ended_at}")
    params = {
        'broadcaster_id': broadcaster_id,
        'first': 100,
        'started_at': started_at,
        'ended_at': ended_at
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if response.status_code != 200:
        data = "Клипы не найдены"
    else:
        data = data['data']

    rate_limit = response.headers.get('RateLimit-Limit')
    rate_limit_remaining = response.headers.get('RateLimit-Remaining')
    rate_limit_reset = response.headers.get('RateLimit-Reset')
    reset_ts = int(rate_limit_reset)
    now = int(time.time())
    seconds_until_reset = max(0, reset_ts - now)
    info = {
        'rate_limit_remaining': f'{rate_limit_remaining}/{rate_limit}',
        'rate_limit_reset': seconds_until_reset
    }

    return data[:20], info

'''
функция работает следующим образом: итерируемся по очереди по каждому месяцу в обратную сторону начиная
с текущего месяца и до декабря 2018. Собираем все клипы нужной категории, в конце возвращаем топ 20 клипов.

'''
def get_clips_by_category2(nickname, category_id):
    start_time = time.time()
    limit = 20
    url_base = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Authorization': f'Bearer {get_app_token()}',
        'Client-Id': TWITCH_CLIENT_ID
    }
    broadcaster_id = get_id_by_name(nickname)
    # наши целевые клипы
    target_clips = []
    target_clips_ids = set()
    # общее кол-во клипов даже с дублями
    all_clips_counter = 0
    # общее кол-во клипов без дублей
    all_clips_counter_unique = 0
    unique_clips = []
    unique_clips_ids = set()
    # кол-во пройденных месяцев
    iterations = 0
    current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_date = '2018-12-01 00:00:00'

    # Внешний цикл по месяцам
    while True:
        # Получаем первый день текущего месяца и последнего дня предыдущего месяца
        ended_at = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        started_at = (current_date - relativedelta(months=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        iterations += 1
        cursor = None
        # общее кол-во клипов за месяц
        month_clips_counter = 0
        # общее кол-во клипов за месяц без дублей
        #month_clips_counter_unique = 0
        #month_unique_clips_ids = set()

        # Внутренний цикл по страницам (каждый месяц)
        while True:
            params = {
                'broadcaster_id': broadcaster_id,
                'first': 100,  # Максимальное число клипов за раз
                'started_at': started_at,
                'ended_at': ended_at
            }

            if cursor:
                params['after'] = cursor

            response = requests.get(url_base, headers=headers, params=params)

            if response.status_code != 200:
                print(f'Ошибка при получении клипов: {response.status_code}')
                break

            data = response.json()

            # обновляем общие данные
            # all_clips_counter += len(data['data'])
            # обновляем данные за месяц
            # month_clips_counter += len(data['data'])

            # for clip in data['data']:
            #     if clip['id'] not in unique_clips_ids:
            #         unique_clips.append(clip)
            #         unique_clips_ids.add(clip['id'])
            #         all_clips_counter_unique += 1
            #     if clip['id'] not in month_unique_clips_ids:
            #         month_unique_clips_ids.add(clip['id'])
            #         month_clips_counter_unique += 1

            for clip in data['data']:
                if clip['game_id'] not in target_clips_ids:
                    if category_id == 'all':
                            target_clips.append(clip)
                            target_clips_ids.add(clip['id'])
                    else:
                        if clip['game_id'] == category_id:
                            target_clips.append(clip)
                            target_clips_ids.add(clip['id'])

            # Проверка выхода внутреннего цикла
            # если твич больше не возвращает клипов
            if len(data['data']) == 0:
                break

            # Следующая страница
            cursor = data.get('pagination', {}).get('cursor')
            if not cursor:
                break

        #print(f'Итераций: {iterations}')
        #print(f'Клипов all: {all_clips_counter} Клипов all unique: {all_clips_counter_unique}')
        #print(f'Клипов month all: {month_clips_counter} Клипов month unique: {month_clips_counter_unique}')
        #print(f'Целевых клипов: {len(target_clips)}')
        #print(f'{started_at}')
        #print()

        # Смещаемся на предыдущий месяц
        current_date -= relativedelta(months=1)

        if str(current_date) == last_date:
            break

    # Сортируем финальный набор клипов по количеству просмотров
    target_clips = list(target_clips)
    target_clips.sort(key=lambda x: x['view_count'], reverse=True)
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f'Пройденных месяцев: {iterations}')
    return target_clips[:limit]


# преобразуем дату из '2023-06-21T10:11:05Z' в 6 июня 2023г
def get_normal_datetime(date_text):
    month_with_number = datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ").strftime("%m %B").lower()
    year = datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y")

    # Склоняем месяц в родительном падеже
    morph = pymorphy3.MorphAnalyzer()
    create_date = morph.parse(month_with_number)[0].inflect({'gent'}).word
    return f"{create_date} {year}г"


def get_stream_info(user_id):
    """
    Возвращает информацию о текущем стриме или None, если стрим оффлайн
    """
    url = f"https://api.twitch.tv/helix/streams?user_id={user_id}"
    headers = {
        "Authorization": f'Bearer {get_app_token()}',
        "Client-Id": TWITCH_CLIENT_ID,
    }

    response = requests.get(url, headers=headers)
    data = response.json().get("data", [])

    if not data:
        return None  # стрим не запущен

    stream = data[0]

    return {
        "id": stream.get("id"),
        "title": stream.get("title"),
        "started_at": stream.get("started_at"),
    }