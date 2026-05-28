from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import SavedSearch, NewEquipmentNotification
from equipment.models import EquipmentType
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def check_saved_searches():
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

        if new_equipment.exists():
            for eq in new_equipment:
                NewEquipmentNotification.objects.create(
                    saved_search=subscription,
            equipment=eq
        )

            send_notification_email.delay(subscription.id, list(new_equipment.values_list('id', flat=True)))
            subscription.last_notified = now
            subscription.save()

@shared_task
def send_notification_email(subscription_id, equipment_ids):
    try:
        subscription = SavedSearch.objects.get(id=subscription_id)
        equipment_list = Equipment.objects.filter(id__in=equipment_ids)

        context = {
            'subscription': subscription,
            'equipment_list': equipment_list,
            'total_count': equipment_list.count(),
            'show_all_url': f"http://spectechmarket.ru/equipment/?{subscription.get_filter_params()}"
        }

        html_message = render_to_string('emails/new_equipment_notification.html', context)
        send_mail(
            subject=f"Новые объявления по поиску '{subscription.name}'",
            message="",
            from_email='noreply@spectechmarket.ru',
            recipient_list=[subscription.user.email],
            html_message=html_message
        )
    except SavedSearch.DoesNotExist:
        pass
