from django.shortcuts import render
from .models import Project

def project_list(request):
    projects = Project.objects.filter(status='completed').select_related()
    return render(request, 'portfolio/project_list.html', {'projects': projects})
