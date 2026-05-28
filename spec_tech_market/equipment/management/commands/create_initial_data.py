from django.core.management.base import BaseCommand
from equipment.models import EquipmentType, Region

class Command(BaseCommand):
    help = 'Создаёт начальные данные для типов техники и регионов'

    def handle(self, *args, **options):
        types = ['Экскаватор', 'Бульдозер', 'Сочленённый самосвал', 'Погрузчик', 'Автогрейдер']
        for type_name in types:
            EquipmentType.objects.get_or_create(name=type_name)

        regions = ['Москва', 'Санкт‑Петербург', 'Екатеринбург', 'Новосибирск', 'Казань']
        for region_name in regions:
            Region.objects.get_or_create(name=region_name)

        self.stdout.write(
            self.style.SUCCESS('Успешно созданы начальные данные')
        )
