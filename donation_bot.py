import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Any
import socketio
import sqlite3
import os

DEFAULT_URL = "https://www.donationalerts.com/oauth/"
DEFAULT_API_LINK = "https://www.donationalerts.com/api/v1/"
processed_ids = set()
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'db.sqlite3')

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()


@dataclass
class Event:

    id: int
    alert_type: str
    is_shown: str
    additional_data: dict
    billing_system: str
    billing_system_type: str
    username: str
    amount: str
    amount_formatted: str
    amount_main: int
    currency: str
    message: str
    date_created: Any
    emotes: str
    ap_id: str
    _is_test_alert: bool
    message_type: str
    preset_id: int


sio = socketio.Client()


class Alert:

    def __init__(self, token):
        self.token = token

    def event(self):
        def wrapper(function):
            @sio.on("connect")
            def on_connect():
                sio.emit("add-user", {"token": self.token, "type": "alert_widget"})

            @sio.on("donation")
            def on_message(data):
                global processed_ids
                data = json.loads(data)
                if data['id'] not in processed_ids:
                    processed_ids.add(data['id'])
                    function(data)
                else:
                    processed_ids.remove(data['id'])

            sio.connect("wss://socket.donationalerts.ru:443", transports="websocket")

        return wrapper


token = "CcM9gL1OT4eAdR7qgoDj"
alert = Alert(token)


@alert.event()
def new_donation(event):
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_datetime)

    if int(event.get('alert_type')) == 19 and event.get('message') == 'Вип04ка':
        data = {
            'event_id': event.get('id'),
            'datetime': event.get('date_created'),
            'username': event.get('username'),
            'user_id': None,
            'ready': False,
            'comment': ""
        }
        cursor.execute(''' INSERT INTO main_vip (event_id, datetime, username, user_id, ready, comment) VALUES \
                       (:event_id, :datetime, :username, :user_id, :ready, :comment) ''', data)

        conn.commit()
    elif int(event.get('alert_type')) == 12:
        username = event.get('header').split(":", 1)[1][1:]
        result = event.get('message').split(":", 1)[1][1:]
        show = True
        if not username:
            username = "Аноним"
        if result == 'Ничего' or username == "Аноним":
            show = False
        data = {
            'event_id': event.get('id'),
            'datetime': event.get('date_created'),
            'username': username,
            'result': result,
            'order': "",
            'ready': False,
            'comment': "",
            'show': show
        }

        cursor.execute(''' INSERT INTO main_roulette (event_id, datetime, username, result, "order", ready, comment, show) VALUES \
                       (:event_id, :datetime, :username, :result, :order, :ready, :comment, :show) ''', data)

        conn.commit()
    elif int(event.get('alert_type')) == 1:
        # Донат
        additional_data_raw = event.get('additional_data') or "{}"
        try:
            additional_data = json.loads(additional_data_raw)
        except json.JSONDecodeError:
            additional_data = {}

        data = {
            'donate_id': event.get('id'),
            'datetime': event.get('date_created'),
            'username': event.get('username') or "Аноним",
            'amount_main': event.get('amount_main'),
            'amount': event.get('amount'),
            'currency': event.get('currency'),
            'is_commission_covered': bool(additional_data.get('is_commission_covered', 0)),
            'test_donate': event.get('billing_system') in ('fake', 'test'),
            'message': event.get('message') or "",
            'media_data': json.dumps({
                'billing_system': event.get('billing_system'),
                'billing_system_type': event.get('billing_system_type'),
                'tts_url': event.get('tts_url'),
                'ap_id': event.get('ap_id'),
                'emotes': event.get('emotes'),
                'message_type': event.get('message_type'),
                'preset_id': event.get('preset_id'),
                'asr_text': event.get('asr_text'),
            }, ensure_ascii=False),
        }

        cursor.execute(
            '''
            INSERT OR IGNORE INTO main_donate
            (donate_id, datetime, username, amount_main, amount, currency, is_commission_covered, message, media_data, test_donate)
            VALUES
            (:donate_id, :datetime, :username, :amount_main, :amount, :currency, :is_commission_covered, :message, :media_data, :test_donate)
            ''',
            data
        )

        conn.commit()


    filename = 'da_nohup_stdout.out'

    try:
        with open(filename, 'a', encoding='utf-8') as file:
            if file.tell() > 0:  # Проверяем, не пустой ли файл
                file.write('\n')  # Пропускаем строку если файл уже содержит данные

            file.write(str(event) + '\n')  # Записываем как текст
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

while True:
    time.sleep(1)
