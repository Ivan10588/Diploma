from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review, SellerRating

@receiver(post_save, sender=Review)
def update_seller_rating(sender, instance, created, **kwargs):
    if created:
        seller = instance.seller
        reviews = Review.objects.filter(seller=seller)
        avg_score = reviews.aggregate(Avg('rating'))['rating__avg']

        if avg_score is None:
            avg_score = 0.0

        review_count = reviews.count()

        total_equipment = seller.equipment_set.count()
        if total_equipment > 0:
            completion_rate = (
                seller.equipment_set.filter(is_sold=True).count() / total_equipment * 100
            )
        else:
            completion_rate = 0.0

        SellerRating.objects.update_or_create(
            seller=seller,
            defaults={
                'average_score': avg_score,
                'review_count': review_count,
                'completion_rate': completion_rate
            }
        )