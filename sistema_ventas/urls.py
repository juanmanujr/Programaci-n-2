# sistema_ventas/urls.py 

from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views # Se puede eliminar si no se usa nada de aquí

# Importamos las dos vistas de autenticación de tu aplicación 'gestion'
from gestion.views import LoginView, LogoutView 

urlpatterns = [
    # URLs de la administración de Django
    path('admin/', admin.site.urls),
    
    # =========================================================
    # AUTENTICACIÓN
    # =========================================================
    
    # Mapea la ruta '/login/' usando tu vista personalizada
    path('login/', LoginView.as_view(), name='login'),
    
    # Mapea la ruta '/logout/' usando tu vista personalizada de gestion
    # Se recomienda usar la versión de gestion.views por consistencia.
    path('logout/', LogoutView.as_view(), name='logout'), 
    
    # =========================================================
    # INCLUSIÓN DE LA APLICACIÓN
    # =========================================================
    # Incluye todas las URLs de tu aplicación 'gestion' bajo la raíz
    path('', include('gestion.urls')), 
]