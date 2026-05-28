from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views import SendVerificationCodeView, VerifyCodeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('api/send-verification-code/', SendVerificationCodeView.as_view(), name='send_verification_code'),
    path('api/verify-code/', VerifyCodeView.as_view(), name='verify_code'),
]
