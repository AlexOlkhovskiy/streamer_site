import logging


class IgnoreSpecificDisallowedHost(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()

        # игнорируем только конкретный домен
        if (
            "Invalid HTTP_HOST header" in msg
            and "yaaya.by" in msg
        ):
            return False  # НЕ логировать

        return True  # логировать всё остальное
