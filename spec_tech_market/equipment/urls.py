from . import views
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    EquipmentListView, EquipmentDetailView, EquipmentCreateView, 
    contact_seller, add_review, toggle_favorite, add_to_comparison, comparison_view, chat_view, 
    chat_view, toggle_sold_status, register, equipment_list, user_profile, SaveSearchView, ToggleNotificationView,
    DeleteSearchView, export_comparison_to_pdf, save_search 
)


app_name = 'equipment'

urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='equipment_list'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('add/', EquipmentCreateView.as_view(), name='equipment_create'),
    path('<int:equipment_id>/contact/', views.contact_seller, name='contact_seller'),
    path('<int:equipment_id>/toggle-sold/', toggle_sold_status, name='toggle_sold_status'),
    path('review/add/<int:equipment_id>/', add_review, name='add_review'),
    path('favorite/toggle/<int:equipment_id>/', toggle_favorite, name='toggle_favorite'),
    path('comparison/add/<int:equipment_id>/', add_to_comparison, name='add_to_comparison'),
    path('comparison/', comparison_view, name='comparison'),
    path('chat/equipment/<int:equipment_id>/', chat_view, name='chat_for_equipment'),
    path('chat/general/', chat_view, name='chat_general'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('list/', equipment_list, name='equipment_list'),
    path('list/', EquipmentListView.as_view(), name='equipment_list'),
    path('profile/', user_profile, name='user_profile'),
    path('api/save-search/', SaveSearchView.as_view(), name='save_search'),
    path('api/toggle-notification/<int:search_id>/', ToggleNotificationView.as_view(), name='toggle_notification'),
    path('api/delete-search/<int:search_id>/', DeleteSearchView.as_view(), name='delete_search'),
    path('export/pdf/<int:comparison_id>/', views.export_comparison_to_pdf, name='export_comparison_pdf'),
    path('accounts/', include('accounts.urls')),
    path('api/save-search/', save_search, name='save_search'),
    path('profile/', views.profile, name='user_profile'),
    path('api/add-to-comparison/<int:equipment_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('api/send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('api/verify-code/', views.verify_code, name='verify_code'),
]