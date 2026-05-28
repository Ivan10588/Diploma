from django.contrib import admin
from .models import Equipment, EquipmentType, Region, Review, Favorite, ComparisonList, ComparisonItem, ChatMessage, Notification

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_sold', 'created_at', 'views_count')
    list_filter = ('is_sold', 'equipment_type', 'region', 'created_at')
    search_fields = ('title', 'model', 'description')
    readonly_fields = ('created_at', 'views_count')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('equipment__title',)

@admin.register(ComparisonList)
class ComparisonListAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(ComparisonItem)
class ComparisonItemAdmin(admin.ModelAdmin):
    list_display = ('comparison_list', 'equipment')
    search_fields = ('equipment__title',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'equipment', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('message',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message',)
