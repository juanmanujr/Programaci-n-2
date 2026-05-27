# gestion/middleware.py

import threading

# Objeto local al hilo donde se almacenará el usuario
_thread_locals = threading.local()

def get_current_user():
    """
    Función de utilidad para obtener el usuario almacenado
    en el hilo actual (usado por signals y otros módulos).
    """
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware:
    """
    Middleware que captura el usuario actual (request.user) y lo
    almacena en el objeto threading.local() para acceso global.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        # Almacenar el usuario antes de procesar la solicitud
        _thread_locals.user = getattr(request, 'user', None)
        
        try:
            # Procesar la solicitud normalmente
            response = self.get_response(request)
        finally:
            # 🚨 LIMPIEZA GARANTIZADA: Desasignar el usuario
            # Esto previene que el contexto del usuario se filtre a otro request
            # si el hilo es reutilizado (ej. por Gunicorn).
            if hasattr(_thread_locals, 'user'):
                del _thread_locals.user
            
        return response