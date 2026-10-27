from django.shortcuts import render

def index(request):
    return render(request, 'reportes/index.html', {'titulo': 'Reportes'})
