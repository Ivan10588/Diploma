import schedule
import time
import threading
from django.utils import timezone

def send_daily_notifications():
    """Отправка ежедневных уведомлений о новых объявлениях"""
    from .models import Equipment
    from django.contrib.auth.models import User
    from .models import Notification

    today = timezone.now().date()
    new_equipment = Equipment.objects.filter(
        created_at__date=today,
        is_sold=False
    )

    if new_equipment.exists():
        users = User.objects.all()
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Добавлено {new_equipment.count()} новых объявлений за сегодня!",
                link="/equipment/",
                is_read=False
            )
        print(f"Отправлено {users.count()} уведомлений о новых объявлениях")

def clean_old_notifications():
    """Очистка уведомлений старше 30 дней"""
    from .models import Notification

    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    old_notifications = Notification.objects.filter(
        created_at__lt=thirty_days_ago
    )
    count = old_notifications.count()
    old_notifications.delete()
    print(f"Удалено {count} старых уведомлений")

def reset_views_count():
    """Сброс счётчика просмотров для популярных объявлений"""
    from .models import Equipment

    popular_equipment = Equipment.objects.filter(views_count__gt=1000)
    for eq in popular_equipment:
        eq.views_count = 0
        eq.save()
    print(f"Сброс просмотров для {popular_equipment.count()} объявлений")

def start_scheduler():
    """Запуск планировщика в отдельном потоке"""
    def run_scheduler():
        schedule.every().day.at("09:00").do(send_daily_notifications)
        schedule.every().day.at("02:00").do(clean_old_notifications)
        schedule.every().monday.at("10:00").do(reset_views_count)
        schedule.every(15).minutes.do(lambda: print("Планировщик работает..."))

        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
