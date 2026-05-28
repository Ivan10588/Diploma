from django.contrib.auth.models import User

def create_notification(other_user, message, url):
    """
    Создаёт уведомление для указанного пользователя
    """
    print(f"Уведомление для {other_user.username}: {message} -> {url}")
    return True
