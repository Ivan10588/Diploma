from django.contrib.auth.models import User

def create_notification(other_user: User, message: str, url: str, user: User = None):
    """
    Создаёт уведомление для указанного пользователя.
    user — опциональный параметр: кто отправил уведомление.
    """
    print(f"Уведомление для {other_user.username}: {message} -> {url}")
    if user:
        print(f"Отправлено пользователем: {user.username}")
    return True
