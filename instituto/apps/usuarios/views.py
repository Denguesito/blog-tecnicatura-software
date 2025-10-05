from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import Usuario

# Registro
class RegistroUsuarioView(View):
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/registro.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"Bienvenido {usuario.username}, tu cuenta fue creada correctamente.")
            return redirect('index')
        return render(request, self.template_name, {'form': form})

# Login
class LoginUsuarioView(View):
    template_name = 'usuarios/login.html'

    def personalizar_formulario(self, form):
        form.fields['username'].label = 'Usuario'
        form.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario'
        })
        form.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })

    def get(self, request):
        form = AuthenticationForm()
        self.personalizar_formulario(form)
        next_url = request.GET.get('next', '')  #  por defecto string vacío
        return render(request, self.template_name, {'form': form, 'next': next_url})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        self.personalizar_formulario(form)

        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f"Bienvenido {usuario.username}")

            #  obtenemos next del POST o GET
            next_url = request.POST.get('next') or request.GET.get('next')

            #  validamos que next_url exista y sea una ruta
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            #  fallback: si no hay next_url, vamos al index
            return redirect('index')

        messages.error(request, "Usuario o contraseña incorrectos")
        return render(request, self.template_name, {'form': form})

# Perfil detalle
class PerfilDetalleView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context

# Perfil editar
class PerfilUsuarioView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/editar_perfil.html'
    success_url = reverse_lazy('usuarios:perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente")
        return super().form_valid(form)
    

class EliminarUsuarioView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/eliminar_perfil.html')

    def post(self, request):
        usuario = request.user
        logout(request)
        usuario.delete()
        messages.success(request, "Tu cuenta fue eliminada correctamente.")
        return redirect('index')


# Logout con confirmación
class LogoutUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/logout.html'

    def post(self, request):
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente")
        return redirect('index')
