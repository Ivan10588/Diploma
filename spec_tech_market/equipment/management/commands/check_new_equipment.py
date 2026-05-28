from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        for subscription in NotificationSubscription.objects.all():
            new_equipment = Equipment.objects.filter(
                created_at__gte=now - timedelta(hours=24)
            ).filter(**subscription.filters)

            if new_equipment.exists():
                self.send_notification(subscription, new_equipment)

    def send_notification(self, subscription, equipment_list):
        send_mail(
            subject=f"Новые объявления по вашему поиску: {subscription.name}",
            message=render_to_string('emails/new_equipment_notification.html', {
                'subscription': subscription,
                'equipment_list': equipment_list
            }),
            from_email='noreply@spectechmarket.ru',
            recipient_list=[subscription.user.email]
        )
