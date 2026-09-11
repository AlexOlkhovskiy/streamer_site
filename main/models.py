from django.db import models
from datetime import timedelta
from django.utils import timezone


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


class Vip(models.Model):
    event_id = models.IntegerField(unique=True, verbose_name='id покупки')
    datetime = models.DateTimeField(verbose_name='Дата и время покупки')
    username = models.CharField(max_length=30, db_index=True, verbose_name='Кто купил')
    user_id = models.IntegerField(null=True, blank=True, verbose_name='id фолловера')
    ready = models.BooleanField(default=False, verbose_name='Выполнили')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.datetime} {self.username}"

    class Meta:
        verbose_name_plural = 'Заказы випок'
        verbose_name = 'Заказ випки'


class URL(models.Model):
    url_name = models.CharField(max_length=100, db_index=True, verbose_name='Название ссылки')
    url_link = models.TextField(verbose_name='Ссылка')
    description = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.url_name} {self.url_link}"

    class Meta:
        verbose_name_plural = 'Ссылки'
        verbose_name = 'Ссылка'


class QuestionAndAnswer(models.Model):
    question = models.TextField(verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    question_number = models.IntegerField(unique=True, verbose_name='Номер вопроса')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = 'Вопросы и ответы'
        verbose_name = 'Вопрос и ответ'
        ordering = ['question_number']


class TextSample(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название шаблона')
    text = models.TextField(null=True, blank=True, verbose_name='Текст')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Текстовые шаблоны'
        verbose_name = 'Текстовый шаблон'


class MessagesFromBot(models.Model):
    timestamp = models.DateTimeField(verbose_name='Время сообщения')
    chat_id = models.BigIntegerField(verbose_name='id чата')
    author_id = models.BigIntegerField(verbose_name='id автора', db_index=True)
    full_name = models.CharField(verbose_name='Имя автора')
    username = models.CharField(null=True, blank=True, verbose_name='username автора')
    is_bot = models.BooleanField(default=False, verbose_name='Это бот')
    message_text = models.TextField(blank=True, verbose_name='Текст сообщения')
    message_id = models.BigIntegerField(verbose_name='id сообщения')
    message_type = models.CharField(verbose_name='Тип сообщения')
    reply_to = models.IntegerField(null=True, blank=True, verbose_name='id сообщения на ответ')
    stickerpack_name = models.CharField(null=True, blank=True, verbose_name='Название стикерпака')

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


class MediaLimit(models.Model):
    author_id = models.IntegerField(unique=True, verbose_name='id автора')
    author_name = models.CharField(verbose_name='Имя автора')
    image_count = models.IntegerField(default=0, verbose_name='фото')
    video_count = models.IntegerField(default=0, verbose_name='видео')
    yrarami_clips_count = models.IntegerField(default=0, verbose_name='клипы урарами')
    other_clips_count = models.IntegerField(default=0, verbose_name='прочие клипы')
    repost_count = models.IntegerField(default=0, verbose_name='репосты')
    is_moderator = models.BooleanField(default=False, verbose_name='Это модератор')
    gif_count = models.IntegerField(default=0, verbose_name='gif')

    class Meta:
        verbose_name_plural = 'Лимиты по чату тг'
        verbose_name = 'Лимит по чату тг'


class Flag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название флага")
    is_active = models.BooleanField(default=False, verbose_name="Состояние флага")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения флага")

    class Meta:
        verbose_name = 'Флаг'
        verbose_name_plural = 'Флаги'

    def __str__(self):
        return f"{self.name} ({'Вкл' if self.is_active else 'Выкл'})"


class Love(models.Model):
    author_id = models.IntegerField(unique=True, verbose_name='id автора')
    author_name = models.CharField(verbose_name='Имя автора')
    updated_at = models.DateTimeField(verbose_name="Дата выполнения команды")
    counter = models.IntegerField(default=0, verbose_name='Количество вызовов команды')

    class Meta:
        verbose_name = 'Команда Love'
        verbose_name_plural = 'Команды Love'

    def __str__(self):
        return f"{self.author_id} {self.author_name}"


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
    name = models.CharField(default="Новый фильм", null=True, blank=True, db_index=True, verbose_name='Название фильма')
    poster_url_preview = models.CharField(null=True, blank=True, verbose_name='Ссылка на постер фильма')
    rating_kinopoisk = models.FloatField(null=True, blank=True, max_length=10, verbose_name='Рейтинг на кинопоиске')
    rating_imdb = models.FloatField(null=True, blank=True, max_length=10, verbose_name='Рейтинг на IMDb')
    film_length = models.CharField(null=True, blank=True, max_length=10, verbose_name='Длительность фильма')
    film_year = models.IntegerField(null=True, blank=True, verbose_name='Год фильма')
    film_genres = models.CharField(null=True, blank=True, verbose_name='Список жанров')
    description = models.CharField(null=True, blank=True, verbose_name='Описание фильма')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Фильмы на просмотр'
        verbose_name = 'Фильм на просмотр'


class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время добавления')
    info = models.TextField(verbose_name='Информация')

    class Meta:
        verbose_name_plural = 'Логи'
        verbose_name = 'Лог'


class BannedUser(models.Model):
    timestamp = models.DateTimeField(verbose_name='Время бана')
    author_id = models.BigIntegerField(unique=True, verbose_name='id автора')
    full_name = models.CharField(verbose_name='Имя автора')
    username = models.CharField(null=True, blank=True, verbose_name='username автора')
    message_text = models.TextField(blank=True, verbose_name='Текст сообщения')
    message_id = models.BigIntegerField(verbose_name='id сообщения')
    spam_patterns = models.TextField(blank=True, verbose_name='Спам паттерны')

    class Meta:
        verbose_name_plural = 'Забаненные пользователи тг'
        verbose_name = 'Забаненный пользователь тг'

    def __str__(self):
        return f"{self.timestamp} {self.full_name}"


class TwitchAppToken(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Название токена")
    access_token = models.TextField(verbose_name="Access token")
    refreshed_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время обновления токена")
    expires_at = models.DateTimeField(verbose_name="Дата и время истечения токена")

    class Meta:
        verbose_name = "Twitch app token"
        verbose_name_plural = "Twitch app tokens"

    def __str__(self):
        return self.name


class TwitchSubscription(models.Model):
    EVENT_TYPES = (
        ("stream.online", "Stream online"),
        ("stream.offline", "Stream offline"),
        ("channel.ban", "Channel ban"),
        ("channel.unban", "Channel unban"),
    )

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    subscription_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("event_type",)
        verbose_name = "Twitch subscription"
        verbose_name_plural = "Twitch subscriptions"

    def __str__(self):
        return f"{self.event_type}"


class TwitchStream(models.Model):
    stream_id = models.CharField(max_length=100, unique=True, verbose_name='ID стрима')
    title = models.CharField(max_length=200, verbose_name='Название стрима')
    started_at = models.DateTimeField(verbose_name='Время начала')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    duration = models.DurationField(null=True, blank=True, verbose_name='Продолжительность')

    def save(self, *args, **kwargs):
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            # ОБРЕЗАЕМ микросекунды
            self.duration = timedelta(seconds=int(delta.total_seconds()))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.started_at} - {self.title}"

    class Meta:
        verbose_name_plural = 'Twitch стримы'
        verbose_name = 'Twitch стрим'


class TwitchBotToken(models.Model):
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.access_token:
            return f"Access token …{self.access_token[-6:]} (expires {self.expires_at})"
        return "No token"


class TwitchChatMessage(models.Model):
    channel_name = models.CharField(max_length=100, verbose_name='Название канала')
    message_id = models.CharField(max_length=100, verbose_name='id сообщения')
    reply_to_message_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='id сообщения на ответ')
    user_id = models.BigIntegerField(verbose_name='id автора')
    username = models.CharField(max_length=100, verbose_name='username автора')
    display_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Имя в чате')
    message = models.TextField(verbose_name='Текст сообщения')

    is_mod = models.BooleanField(default=False, verbose_name='Это модер')
    is_subscriber = models.BooleanField(default=False, verbose_name='Это подписчик')
    is_vip = models.BooleanField(default=False, verbose_name='Это вип')
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name='Цвет ника')
    first_message = models.BooleanField(default=False, verbose_name='Это первое сообщение')

    created_at = models.DateTimeField(verbose_name='Время сообщения')

    class Meta:
        verbose_name_plural = 'Сообщения с твича'
        verbose_name = 'Сообщение с твича'

        indexes = [
            models.Index(fields=["channel_name", "user_id", "-created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["channel_name", "message_id"],
                name="uniq_channel_message"
            )
        ]

    def __str__(self):
        return f"{self.created_at} {self.message_id} {self.username}"


class Donate(models.Model):
    donate_id = models.IntegerField(unique=True, verbose_name='id доната')
    datetime = models.DateTimeField(verbose_name='Дата и время доната')
    username = models.CharField(max_length=30, db_index=True, verbose_name='Никнейм донатера')
    amount_main = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма доната в рублях')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма доната')
    currency = models.CharField(max_length=10, verbose_name='Валюта')
    is_commission_covered = models.BooleanField(verbose_name='Покрыта ли комиссия')
    message = models.TextField(verbose_name='Сообщение')
    media_data = models.TextField(blank=True, verbose_name='Дополнительные данные')
    test_donate = models.BooleanField(default=False, verbose_name='Тестовый донат')

    def __str__(self):
        return f"{self.datetime} {self.username} {self.amount_main}"

    class Meta:
        verbose_name_plural = 'Донаты'
        verbose_name = 'Донат'


class Follower(models.Model):
    BAN_CHOICES = [
        ('без бана', 'без бана'),
        ('бан у yrarami', 'бан у yrarami'),
        ('бан на твиче', 'бан на твиче')
    ]
    STATUS_CHOICES = [
        ('danger', 'Опасный'),
        ('suspicious', 'Подозрительный'),
        ('neutral', 'Нейтральный'),
        ('good', 'Классный чатерс'),
    ]
    login = models.CharField(max_length=50, db_index=True, verbose_name='Логин', unique=True)
    nickname = models.CharField(max_length=50, db_index=True, verbose_name='Никнейм')
    old_nicknames = models.JSONField(default=list, blank=True, verbose_name='Старые ники')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    creation_date = models.DateField(verbose_name='Дата регистрации')
    view_date = models.DateField(db_index=True, null=True, blank=True, verbose_name='Дата отслеживания yrarami')
    twitch_id = models.IntegerField(verbose_name='twitch id', unique=True)

    # шаблон для json словаря {"<twitch_id>": ["nickname"]}
    fakes = models.JSONField(default=dict, blank=True, verbose_name='Фэйковые аккаунты')

    telegram_id = models.IntegerField(null=True, blank=True, verbose_name='telegram id', unique=True)
    telegram_nickname = models.CharField(max_length=50, default='', blank=True, verbose_name='Телеграм никнейм')
    telegram_tag = models.CharField(max_length=50, default='', blank=True, verbose_name='Телеграм тэг')

    vip_channel = models.JSONField(default=list, blank=True, verbose_name='Где является випом')
    moderator_channel = models.JSONField(default=list, blank=True, verbose_name='Где является модером')
    streamer = models.BooleanField(default=False, verbose_name='Является ли стримером')
    contentmaker = models.BooleanField(default=False, verbose_name='Является ли контентмейкером')
    top_donater = models.BooleanField(default=False, verbose_name='Является ли топ донатером')
    # если поле пустое, значит не был модером, а если был, то указываем период модерства
    prev_moderator_yrarami = models.CharField(max_length=25, default='', blank=True, verbose_name='Был модером у yrarami')
    prev_moderator = models.JSONField(default=list, blank=True, verbose_name='Где был модером')
    ban = models.CharField(max_length=20, choices=BAN_CHOICES, default='без бана', verbose_name='Бан')
    color = models.CharField(max_length=20, choices=STATUS_CHOICES, default='neutral', verbose_name='Цвет карточки')
    show = models.BooleanField(default=True, verbose_name='Показывать ли юзера в публичном списке')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name_plural = 'Подписчики'
        verbose_name = 'Подписчик'
        ordering = ['nickname']


class ModerationEvent(models.Model):

    class ActionType(models.TextChoices):
        BAN = "BAN", "Ban"
        TIMEOUT = "TIMEOUT", "Timeout"
        UNBAN = "UNBAN", "Unban"
        UNTIMEOUT = "UNTIMEOUT", "Untimeout"

    event_id = models.UUIDField(unique=True, verbose_name='id события')

    action_type = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        db_index=True, verbose_name='тип события'
    )

    # Пользователь
    user_id = models.CharField(max_length=50, db_index=True, verbose_name='id юзера')
    user_login = models.CharField(max_length=255, verbose_name='login юзера')
    user_name = models.CharField(max_length=255, verbose_name='имя юзера')

    # Канал
    broadcaster_user_id = models.CharField(max_length=50, db_index=True, verbose_name='id стримера')
    broadcaster_user_login = models.CharField(max_length=255, verbose_name='login стримера')
    broadcaster_user_name = models.CharField(max_length=255, verbose_name='имя стримера')

    # Модератор
    moderator_user_id = models.CharField(max_length=50, verbose_name='id модератора')
    moderator_user_login = models.CharField(max_length=255, verbose_name='login модератора')
    moderator_user_name = models.CharField(max_length=255, verbose_name='имя модератора')

    # Детали для BAN / TIMEOUT
    reason = models.TextField(blank=True, null=True, verbose_name='причина бана/мута')
    ends_at = models.DateTimeField(blank=True, null=True, verbose_name='дата окончания мута')
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, verbose_name='срок мута')

    # Время события от Twitch
    event_datetime = models.DateTimeField(db_index=True, verbose_name='время события')

    # Когда записали в БД
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='время записи в базу')

    # погашено ли наказание
    resolved = models.BooleanField(default=False)

    # ссылка на событие которое это завершило
    resolved_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_events"
    )

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["broadcaster_user_id"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["resolved"]),
        ]

    def __str__(self):
        return f"{self.action_type} {self.user_login} ({self.event_datetime})"