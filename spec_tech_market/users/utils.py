import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import VerificationCode

def send_verification_code(user, method='email'):
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = timezone.now() + timedelta(minutes=10)

    VerificationCode.objects.create(
        user=user,
        code=code,
        type=method,
        expires_at=expires_at
    )

    if method == 'email':
        send_mail(
            'Код подтверждения',
            f'Ваш код: {code}',
            'noreply@spectechmarket.ru',
            [user.email]
        )
    elif method == 'phone':
        # Здесь должна быть реализация отправки SMS через API провайдера
        # Пример для Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        # client.messages.create(
        #     body=f'Ваш код подтверждения: {code}',
        #     from_=settings.TWILIO_PHONE,
        #     to=user.profile.phone
        # )
        pass
