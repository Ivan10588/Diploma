from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    return HttpResponse("Страница логина")

def logout_view(request):
    return HttpResponse("Страница выхода")

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # замените 'home' на имя вашего главного маршрута
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})