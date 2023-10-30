"""A module to schedule tasks"""

import os
from celery import Celery
from celery.schedules import crontab

app = Celery(__name__)
app.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379/0"
)

# Define the schedule for your tasks
app.conf.beat_schedule = {
    "generate_daily_verse": {
        "task": "daily_verse",
        "schedule": crontab(minute="*"),  # Every minute
    },
}
