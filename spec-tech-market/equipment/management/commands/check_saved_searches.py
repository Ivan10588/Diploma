from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from .models import SavedSearch, NewEquipmentNotification
from equipment.models import Equipment
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        for subscription in SavedSearch.objects.filter(notify=True):
            if subscription.frequency == 'daily':
                period = timedelta(hours=24)
            else:
                period = timedelta(days=7)

            new_equipment = Equipment.objects.filter(
                created_at__gte=now - period
            ).filter(**subscription.filters)

            existing_notifications = NewEquipmentNotification.objects.filter(
                saved_search=subscription
            ).values_list('equipment_id', flat=True)
            new_equipment = new_equipment.exclude(id__in=existing_notifications)

            for eq in new_equipment:
                NewEquipmentNotification.objects.create(
                    saved_search=subscription,
            equipment=eq
        )

            if new_equipment.exists():
                self.send_notification_email(subscription, new_equipment)
                subscription.last_notified = now
                subscription.save()

    def send_notification_email(self, subscription, equipment_list):
        context = {
            'subscription': subscription,
            'equipment_list': equipment_list,
            'total_count': equipment_list.count(),
            'show_all_url': f"http://{self.get_domain()}{reverse('equipment_list')}?{subscription.get_filter_params()}"
        }

        html_message = render_to_string('emails/new_equipment_notification.html', context)
        plain_message = f"По вашему поиску '{subscription.name}' найдено {equipment_list.count()} новых объявлений."

        send_mail(
            subject=f"Новые объявления по поиску '{subscription.name}'",
            message=plain_message,
            from_email='noreply@spectechmarket.ru',
            recipient_list=[subscription.user.email],
            html_message=html_message
        )

    def get_domain(self):
        return 'spectechmarket.ru'
