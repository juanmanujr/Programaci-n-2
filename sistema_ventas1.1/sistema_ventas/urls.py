# Contenido ÚNICO de sistema_ventas/urls.py

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea usa 'include' para enlazar al archivo 'gestion.urls'
    path('', include('gestion.urls')), 
]