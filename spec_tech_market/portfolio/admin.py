from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'completion_date', 'project_url']
    list_filter = ['status', 'completion_date']
    search_fields = ['title', 'description', 'technologies']
    date_hierarchy = 'completion_date'
