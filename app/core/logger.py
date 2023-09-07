import logging
from datetime import datetime

from pythonjsonlogger import jsonlogger

from app.core.config import config


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


class MyLogger:
    def __init__(self):
        # Создаем логгер
        self.logger = logging.getLogger(config.project_name)
        self.logger.setLevel(config.log_level)

        # Создаем обработчик, который выводит сообщения в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.log_level)
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
        )
        console_handler.setFormatter(formatter)

        # Добавляем обработчик к логгеру
        self.logger.addHandler(console_handler)

    def error(self, message):
        self.logger.error(message, stacklevel=2)

    def warning(self, message):
        self.logger.warning(message, stacklevel=2)

    def info(self, message):
        self.logger.info(message, stacklevel=2)

    def debug(self, message):
        self.logger.debug(message, stacklevel=2)


logger = MyLogger()
