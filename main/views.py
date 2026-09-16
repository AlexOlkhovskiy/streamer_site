from django.shortcuts import render
from main.models import (
    Roulette, URL, TextSample, Film, FilmForWatching,
)


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


def roulette(request):
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
        'Андрей': 'anko',
        'Жил был камаро': 'CAMARO'
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


def change_list(request):
    return render(request, 'main/change_list.html')


def films(request):
    films = Film.objects.all().order_by('-auction_date')
    want_to_watch = FilmForWatching.objects.all()
    rules = TextSample.objects.get(pk=4).text
    want_watch_text = TextSample.objects.get(pk=8).text
    for film in want_to_watch:
        total_minutes = film.film_length
        if total_minutes and total_minutes.isdigit():
            hours = int(total_minutes) // 60
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