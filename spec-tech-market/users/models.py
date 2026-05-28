from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    type = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('phone', 'Phone')]
    )
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Код верификации'
        verbose_name_plural = 'Коды верификации'

    def __str__(self):
        return f'{self.user.username} - {self.code} ({self.type})'
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'