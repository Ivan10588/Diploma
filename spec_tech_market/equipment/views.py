from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import (
    Equipment, EquipmentType, Region, Notification,
    Favorite, ComparisonList, ComparisonItem, ChatMessage, SavedSearch
)
from .forms import EquipmentForm, ContactSellerForm, ReviewForm
from .notifications import create_notification
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('equipment_type', 'region')
        equipment_type_id = self.request.GET.get('equipment_type')
        if equipment_type_id:
            queryset = queryset.filter(equipment_type_id=equipment_type_id)
        region_id = self.request.GET.get('region')
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(model__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'year_new':
            queryset = queryset.order_by('-year')
        elif sort_by == 'views':
            queryset = queryset.order_by('-views_count')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment_types'] = EquipmentType.objects.all()
        context['regions'] = Region.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context

class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

class EquipmentCreateView(CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment/equipment_form.html'
    success_url = reverse_lazy('equipment:equipment_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.object:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                equipment=self.object
            ).exists()
        return context

def contact_seller(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        messages.success(request, f'Сообщение для продавца {equipment.owner.username} отправлено!')
        return redirect('equipment:equipment_detail', pk=equipment_id)

    return render(request, 'equipment/equipment_detail.html', {
        'equipment': equipment,
    })

def toggle_sold_status(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.user != equipment.owner:
        messages.error(request, 'У вас нет прав для изменения статуса этого объявления.')
        return redirect('equipment:equipment_detail', equipment.pk)

    equipment.is_sold = not equipment.is_sold
    equipment.save()

    status_text = 'продана' if equipment.is_sold else 'не продана'
    messages.success(request, f'Объявление успешно отмечено как {status_text}.')

    return redirect('equipment:equipment_detail', equipment.pk)

def add_review(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.equipment = equipment
            review.author = request.user
            try:
                review.save()
                messages.success(request, 'Отзыв успешно добавлен!')
            except IntegrityError:
                messages.error(request, 'Вы уже оставляли отзыв на это объявление.')
            return redirect('equipment:equipment_detail', equipment.pk)
    else:
        form = ReviewForm()

    return render(request, 'equipment/add_review.html', {
        'form': form,
        'equipment': equipment
    })

@login_required
def toggle_favorite(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        equipment=equipment
    )
    if not created:
        favorite.delete()
        messages.info(request, 'Объявление удалено из избранного')
    else:
        messages.success(request, 'Объявление добавлено в избранное')
    return redirect('equipment:equipment_detail', equipment.pk)

@login_required
def add_to_comparison(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    comparison_list, created = ComparisonList.objects.get_or_create(user=request.user)
    ComparisonItem.objects.get_or_create(
        comparison_list=comparison_list,
        equipment=equipment
    )
    messages.success(request, f'{equipment.title} добавлен к сравнению')
    return redirect('equipment:equipment_list')

def comparison_view(request):
    try:
        comparison_list = ComparisonList.objects.get(user=request.user)
        items = ComparisonItem.objects.filter(comparison_list=comparison_list)
        equipments = [item.equipment for item in items]
    except ComparisonList.DoesNotExist:
        equipments = []
    return render(request, 'equipment/comparison.html', {'equipments': equipments})

@login_required
def chat_view(request, equipment_id=None, user_id=None):
    if equipment_id:
        equipment = get_object_or_404(Equipment, id=equipment_id)
        other_user = equipment.owner
    elif user_id:
        other_user = get_object_or_404(User, id=user_id)
        equipment = None
    else:
        messages.error(request, 'Не указан получатель или объявление')
        return redirect('equipment:equipment_list')

    messages_list = ChatMessage.objects.filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    unread_messages = messages_list.filter(sender=other_user, is_read=False)
    unread_messages.update(is_read=True)

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                equipment=equipment,
                message=message_text
            )
            if other_user != request.user:
                create_notification(
                    user=other_user,
                    message=f'Новое сообщение от {request.user.username}',
                    equipment=equipment
                )
            if equipment_id:
                return redirect('equipment:chat_for_equipment', equipment_id=equipment_id)
            else:
                return redirect('equipment:chat_general', user_id=user_id)
        messages.error(request, 'Сообщение не может быть пустым')
        return redirect(request.get_full_path())

    return render(request, 'equipment/chat.html', {
        'messages': messages_list,
        'other_user': other_user,
        'equipment': equipment
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('equipment:equipment_list')
    else:
        form = UserCreationForm()
    return render(request, 'equipment/register.html', {'form': form})

def equipment_list(request):
    view = EquipmentListView()
    view.setup(request)
    return view.dispatch(request)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required

@method_decorator(csrf_exempt, name='dispatch')
class SaveSearchView(View):
    @method_decorator(login_required)
    def post(self, request):
        import json
        data = json.loads(request.body)
        name = data.get('name')
        filters = data.get('filters', {})
        notify = data.get('notify', True)

        SavedSearch.objects.create(
            user=request.user,
            name=name,
            filters=filters,
            notify=notify
        )
        return JsonResponse({'status': 'saved'})

@method_decorator(csrf_exempt, name='dispatch')
class ToggleNotificationView(View):
    @method_decorator(login_required)
    def post(self, request, search_id):
        try:
            search = SavedSearch.objects.get(id=search_id, user=request.user)
            search.notify = not search.notify
            search.save()
            return JsonResponse({'status': 'updated', 'notify': search.notify})
        except SavedSearch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Поиск не найден'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteSearchView(View):
    @method_decorator(login_required)
    def delete(self, request, search_id):
        try:
            search = SavedSearch.objects.get(id=search_id, user=request.user)
            search.delete()
            return JsonResponse({'status': 'deleted'})
        except SavedSearch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Поиск не найден'}, status=404)

def export_comparison_to_pdf(request, comparison_id):
    comparison = get_object_or_404(ComparisonList, id=comparison_id)
    items = comparison.comparisonitem_set.select_related('equipment').all()
    equipments = [item.equipment for item in items]
    html_template = render_to_string(
        'equipment/comparison_pdf.html',
        {'comparison': comparison, 'equipments': equipments}
    )
    pdf_file = HTML(string=html_template).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comparison_{comparison_id}.pdf"'
    return response

@login_required
def user_profile(request):
    """
    Представление для отображения профиля пользователя.
    """
    user_equipment = Equipment.objects.filter(owner=request.user)

    favorites = Favorite.objects.filter(user=request.user).select_related('equipment')

    context = {
        'user': request.user,
        'user_equipment': user_equipment,
        'favorites': favorites,
        'equipment_count': user_equipment.count(),
        'favorite_count': favorites.count(),
    }

    return render(request, 'equipment/user_profile.html', context)
