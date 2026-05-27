# gestion/views_base.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin # <-- Importación de Seguridad

# -----------------------------------------------------------
# 1. BASE LIST VIEW
# -----------------------------------------------------------
# Ahora requiere que el usuario esté logueado
class BaseListView(LoginRequiredMixin, ListView): 
    """
    Clase base para listar modelos. Incluye paginación y título dinámico.
    """
    paginate_by = 15
    titulo_pagina = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = self.titulo_pagina
        return context

# -----------------------------------------------------------
# 2. BASE CREATE VIEW
# -----------------------------------------------------------
# Ahora requiere que el usuario esté logueado
class BaseCreateView(LoginRequiredMixin, CreateView): 
    """
    Clase base para crear un nuevo registro. Maneja mensajes de éxito y requiere login.
    """
    success_message = "Registro creado exitosamente."
    success_url_name = ''

    def get_success_url(self):
        # Asegura la redirección usando el nombre de la URL
        return reverse_lazy(self.success_url_name)

    def form_valid(self, form):
        # Añade un mensaje de éxito antes de redirigir
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

# -----------------------------------------------------------
# 3. BASE UPDATE VIEW
# -----------------------------------------------------------
# Ahora requiere que el usuario esté logueado
class BaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    Clase base para editar un registro existente. Maneja mensajes de éxito y requiere login.
    """
    success_message = "Registro actualizado exitosamente."
    success_url_name = ''

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

# -----------------------------------------------------------
# 4. BASE DELETE VIEW
# -----------------------------------------------------------
# Ahora requiere que el usuario esté logueado
class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    Clase base para eliminar un registro. Maneja mensajes de éxito y requiere login.
    """
    success_message = "Registro eliminado exitosamente."
    success_url_name = ''
    
    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def form_valid(self, form):
        # DeleteView no usa form.save(), por eso eliminamos el objeto directamente.
        self.object.delete()
        messages.warning(self.request, self.success_message) # Usa warning para la eliminación
        return HttpResponseRedirect(self.get_success_url())