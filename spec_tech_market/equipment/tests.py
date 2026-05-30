from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import SavedSearch, NewEquipmentNotification
from equipment.models import Equipment
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase

class SavedSearchTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_save_search_api(self):
        response = self.client.post('/api/save-search/', {
            'name': 'Test Search',
            'filters': {'type': 'excavator', 'price_min': 50000},
            'notify': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'saved')

        saved_search = SavedSearch.objects.get(user=self.user, name='Test Search')
        self.assertEqual(saved_search.filters, {'type': 'excavator', 'price_min': 50000})

    def test_toggle_notification(self):
        search = SavedSearch.objects.create(
            user=self.user,
            name='Test Search',
            filters={},
            notify=True
        )

        response = self.client.post(f'/api/toggle-notification/{search.id}/', {
            'notify': False
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        updated_search = SavedSearch.objects.get(id=search.id)
        self.assertFalse(updated_search.notify)

    def test_get_new_count(self):
        search = SavedSearch.objects.create(
            user=self.user,
            name='Test Search',
            filters={'type': 'excavator'},
            notify=True
        )

        Equipment.objects.create(
            title='New Excavator',
            type='excavator',
            price=100000,
            created_at=timezone.now() - timedelta(days=3)
        )

        self.assertEqual(search.get_new_count(), 1)

    def test_delete_search(self):
        search = SavedSearch.objects.create(
            user=self.user,
            name='Test Search',
            filters={}
        )

        response = self.client.delete(f'/api/delete-search/{search.id}/')
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(SavedSearch.DoesNotExist):
            SavedSearch.objects.get(id=search.id)

    def test_notification_email_content(self):
        search = SavedSearch.objects.create(
            user=self.user,
            name='Heavy Equipment',
            filters={'weight_min': 20}
        )
        equipment = Equipment.objects.create(title='Heavy Loader', weight=25, price=200000)

        context = {
            'subscription': search,
            'equipment_list': [equipment],
            'total_count': 1,
            'show_all_url': 'http://spectechmarket.ru/equipment/?weight_min=20'
        }

        html_content = render_to_string('emails/new_equipment_notification.html', context)
        self.assertIn('Heavy Equipment', html_content)
        self.assertIn('Heavy Loader', html_content)

class SavedSearchesAPITest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='testpass')
    self.client.login(username='testuser', password='testpass')

  def test_save_search(self):
    data = {
      'name': 'Мой поиск',
      'filters': {'price_min': 1000, 'price_max': 5000},
      'notify': True,
      'frequency': 'daily'
    }
    response = self.client.post('/equipment/api/save-search/', data, format='json')
    self.assertEqual(response.status_code, 200)
    self.assertTrue(SavedSearch.objects.filter(name='Мой поиск').exists())