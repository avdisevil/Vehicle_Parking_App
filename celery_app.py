# Celery app configuration for background tasks and scheduling
from celery import Celery
from celery.schedules import crontab
from backend import flask_app


# Factory function to create and configure the Celery app
def make_celery(app):
    # Create Celery instance with Redis as broker and backend
    celery_app = Celery(
        'vehicle_parking',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['tasks.reminder_tasks']  # Import tasks for scheduling
    )

    # Set timezone and UTC handling
    celery_app.conf.timezone = 'Asia/Kolkata'   # Set timezone to IST
    celery_app.conf.enable_utc = True           # Let Celery handle UTC internally

    # Define scheduled tasks (Celery Beat)
    celery_app.conf.beat_schedule = {
        'send-daily-reminder': {
            'task': 'tasks.reminder_tasks.send_daily_reminder',
            'schedule': crontab(hour=20, minute=9)  # Daily at 20:09 IST
            # 'schedule': crontab(minute = '*')     # For testing: every minute
        },

        'monthly-user-report': {
            'task': 'tasks.reminder_tasks.send_monthly_user_report',
            'schedule': crontab(hour=20, minute=1, day_of_month=27)  # Monthly on 27th
            # 'schedule': crontab(minute = '*')     # For testing: every minute
        },
    }

    # Attach Flask app context to Celery for DB and config access
    celery_app.flask_app = app

    return celery_app

# Create the global Celery app instance
celery_app = make_celery(flask_app)