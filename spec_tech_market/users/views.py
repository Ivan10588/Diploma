from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from .utils import send_verification_code
from .models import VerificationCode

@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeView(View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        method = request.POST.get('method')

        try:
            verification = VerificationCode.objects.get(
                user=request.user,
                code=code,
                type=method,
                expires_at__gt=timezone.now(),
                is_used=False
            )
            verification.is_used = True
            verification.save()

            if method == 'email':
                request.user.profile.email_verified = True
                request.user.profile.save()
                messages.success(request, 'Email успешно подтверждён!')
            elif method == 'phone':
                request.user.profile.phone_verified = True
                request.user.profile.save()
                messages.success(request, 'Телефон успешно подтверждён!')

            return JsonResponse({'status': 'success'})
        except VerificationCode.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Неверный или просроченный код'
            })

@method_decorator(csrf_exempt, name='dispatch')
class SendVerificationCodeView(View):
    def post(self, request, *args, **kwargs):
        method = request.POST.get('method', 'email')
        send_verification_code(request.user, method)
        return JsonResponse({'status': 'success'})
