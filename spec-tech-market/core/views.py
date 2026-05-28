from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.http import HttpResponse
from django.urls import get_resolver

def home(request):
    return render(request, 'core/home.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Ваше сообщение успешно отправлено!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

def list_all_urls(request):
    resolver = get_resolver()
    url_list = []


    def traverse_patterns(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                new_prefix = prefix + str(pattern.pattern)
                traverse_patterns(pattern.url_patterns, new_prefix)
            elif hasattr(pattern, 'callback'):
                url_name = pattern.name or 'No name'
                full_pattern = prefix + str(pattern.pattern)
                url_list.append(f"{full_pattern} -> {url_name}")

    traverse_patterns(resolver.url_patterns)

    content = '<br>'.join(url_list)
    return HttpResponse(content, content_type='text/html')

def add_to_comparison(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    comparison_list, created = ComparisonList.objects.get_or_create(user=request.user)
    ComparisonItem.objects.get_or_create(
        comparison_list=comparison_list,
        equipment=equipment
    )
    return JsonResponse({'status': 'added', 'count': comparison_list.items.count()})

def comparison_view(request):
    try:
        comparison_list = ComparisonList.objects.get(user=request.user)
        items = ComparisonItem.objects.filter(comparison_list=comparison_list)
        equipments = [item.equipment for item in items]
    except ComparisonList.DoesNotExist:
        equipments = []
    return render(request, 'equipment/comparison.html', {'equipments': equipments})