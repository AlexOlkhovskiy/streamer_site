from django.db import models


class Roulette(models.Model):
    event_id = models.IntegerField(unique=True, verbose_name='id прокрута')
    datetime = models.DateTimeField(verbose_name='Дата и время прокрута')
    username = models.CharField(max_length=30, db_index=True, verbose_name='Кому выпало')
    result = models.CharField(max_length=50, verbose_name='Что выпало')
    order = models.TextField(default="", null=True, blank=True, verbose_name='Что заказал')
    ready = models.BooleanField(default=False, verbose_name='Выполнили')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    show = models.BooleanField(default=True, verbose_name='Показывать ли в публичном списке')

    def __str__(self):
        return f"{self.datetime} {self.username} {self.result}"

    class Meta:
        verbose_name_plural = 'Результаты рулетки'
        verbose_name = 'Прокрут рулетки'


class URL(models.Model):
    url_name = models.CharField(max_length=100, db_index=True, verbose_name='Название ссылки')
    url_link = models.TextField(verbose_name='Ссылка')
    description = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.url_name} {self.url_link}"

    class Meta:
        verbose_name_plural = 'Ссылки'
        verbose_name = 'Ссылка'


class TextSample(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название шаблона')
    text = models.TextField(null=True, blank=True, verbose_name='Текст')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Текстовые шаблоны'
        verbose_name = 'Текстовый шаблон'


class Film(models.Model):
    VIEW_TYPE_CHOICES = [
        ('аук', 'аук'),
        ('выкуп', 'выкуп'),
    ]
    AUCTION_TYPE_CHOICES = [
        ('балловый', 'балловый'),
        ('денежный', 'денежный'),
        ('смешанный', 'смешанный'),
        ('-', '-')
    ]

    film_name = models.TextField(verbose_name='Название фильма')
    film_year = models.CharField(max_length=20, verbose_name='Год фильма')
    top_on_auction = models.CharField(default='-', blank=True, null=True, max_length=10, verbose_name='Топ на ауке')
    chance_to_win = models.CharField(default='-', blank=True, null=True, max_length=10, verbose_name='Шанс на выигрыш')
    winners_nicknames = models.TextField(default='-', blank=True, verbose_name='Чей фильм победил')
    auction_date = models.DateField(verbose_name='Дата аукциона')
    view_type = models.CharField(max_length=10, choices=VIEW_TYPE_CHOICES, default='Аук', verbose_name='Аук или выкуп')
    kinopoisk_id = models.CharField(max_length=10, verbose_name='id фильма на кинопоиске')
    rating_kinopoisk = models.FloatField(null=True, blank=True, verbose_name='Оценка фильма на кинопоиске')
    rating_imdb = models.FloatField(null=True, blank=True, verbose_name='Оценка фильма на IMDb')
    auction_type = models.CharField(max_length=10, choices=AUCTION_TYPE_CHOICES, default='Аук', verbose_name='Тип аука')
    comments = models.TextField(blank=True, verbose_name='Комментарии')
    show = models.BooleanField(default=True, verbose_name='Показывать ли в публичном списке')

    def __str__(self):
        return f'{self.auction_date} {self.film_name}'

    class Meta:
        verbose_name_plural = 'Фильмы'
        verbose_name = 'Фильм'
        ordering = ['auction_date']


class FilmForWatching(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время добавления')
    kinopoisk_id = models.IntegerField(verbose_name='id фильма на кинопоиске')
    name = models.CharField(default="Новый фильм", null=True, blank=True, max_length=255, db_index=True, verbose_name='Название фильма')
    poster_url_preview = models.CharField(null=True, blank=True, max_length=512, verbose_name='Ссылка на постер фильма')
    rating_kinopoisk = models.FloatField(null=True, blank=True, max_length=10, verbose_name='Рейтинг на кинопоиске')
    rating_imdb = models.FloatField(null=True, blank=True, max_length=10, verbose_name='Рейтинг на IMDb')
    film_length = models.CharField(null=True, blank=True, max_length=10, verbose_name='Длительность фильма')
    film_year = models.IntegerField(null=True, blank=True, verbose_name='Год фильма')
    film_genres = models.CharField(null=True, blank=True, max_length=255, verbose_name='Список жанров')
    description = models.CharField(null=True, blank=True, max_length=2048, verbose_name='Описание фильма')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Фильмы на просмотр'
        verbose_name = 'Фильм на просмотр'


class MessagesFromBot(models.Model):
    timestamp = models.DateTimeField(verbose_name='Время сообщения')
    chat_id = models.BigIntegerField(verbose_name='id чата')
    author_id = models.BigIntegerField(verbose_name='id автора', db_index=True)
    full_name = models.CharField(max_length=255, verbose_name='Имя автора')
    username = models.CharField(null=True, blank=True, max_length=255, verbose_name='username автора')
    is_bot = models.BooleanField(default=False, verbose_name='Это бот')
    message_text = models.TextField(blank=True, verbose_name='Текст сообщения')
    message_id = models.BigIntegerField(verbose_name='id сообщения')
    message_type = models.CharField(max_length=50, verbose_name='Тип сообщения')
    reply_to = models.IntegerField(null=True, blank=True, verbose_name='id сообщения на ответ')
    stickerpack_name = models.CharField(null=True, blank=True, max_length=100, verbose_name='Название стикерпака')

    def __str__(self):
        return f"{self.timestamp} {self.full_name} {self.message_id}"

    class Meta:
        verbose_name_plural = 'Сообщения из чата тг'
        verbose_name = 'Сообщение из чата тг'
        unique_together = [['chat_id', 'message_id']]
        indexes = [
            models.Index(fields=['chat_id', 'timestamp']),
            models.Index(fields=['chat_id', 'author_id']),
        ]