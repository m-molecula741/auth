from celery import Celery

from app.core.config import config

celery_app = Celery(config.project_name, include=["app.tasks.tasks"])
celery_app.conf.broker_url = config.celery_broker_url
