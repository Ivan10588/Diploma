from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlencode

class EquipmentType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    hours_worked = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_equipment')
    is_sold = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('equipment', 'author')

    def __str__(self):
        return f'Review by {self.author.username} for {self.equipment.title}'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'equipment')

class ComparisonList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

class ComparisonItem(models.Model):
    comparison_list = models.ForeignKey(ComparisonList, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages')
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='equipment_profile')
    phone = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, verbose_name='Название поиска')
    filters = models.JSONField(verbose_name='Параметры поиска')
    notify = models.BooleanField(default=True, verbose_name='Получать уведомления')
    frequency = models.CharField(
        max_length=20,
        choices=[('daily', 'Ежедневно'), ('weekly', 'Еженедельно')],
        default='daily',
        verbose_name='Частота уведомлений'
    )
    last_notified = models.DateTimeField(null=True, blank=True, verbose_name='Последнее уведомление')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name']


    def get_new_count(self):
        """Возвращает количество новых объявлений по этому поиску за последнюю неделю"""
        week_ago = timezone.now() - timedelta(days=7)
        new_equipment = Equipment.objects.filter(
            created_at__gte=week_ago
        ).filter(**self.filters)
        return new_equipment.count()

    def get_filter_params(self):
        """Преобразует фильтры в строку параметров URL"""
        return urlencode(self.filters)


class NewEquipmentNotification(models.Model):
    saved_search = models.ForeignKey(SavedSearch, on_delete=models.CASCADE)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SellerRating(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rating')
    average_score = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Рейтинг продавца'
        verbose_name_plural = 'Рейтинги продавцов'


    def __str__(self):
        return f'{self.seller.username} — {self.average_score:.1f} ({self.review_count} отзывов)'
