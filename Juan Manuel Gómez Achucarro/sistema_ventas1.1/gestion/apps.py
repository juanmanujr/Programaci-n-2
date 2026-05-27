from django.apps import AppConfig


class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'
    # Esta línea agrega el nombre con acento (tilde)
    verbose_name = 'Gestión'
    
    def ready(self):
        import gestion.signals