from rest_framework import serializers
from .models import SavedSearch

class SavedSearchSerializer(serializers.ModelSerializer):
  class Meta:
    model = SavedSearch
    fields = ['id', 'name', 'filters', 'notify', 'frequency', 'last_notified', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at', 'user']
