from cloudinary.provisioning import account_config
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView, RedirectView, View
from django.shortcuts import redirect, render
from django.http import JsonResponse
import requests
from rest_framework.permissions import IsAuthenticated

from accounts.service import YandexAuthService, AccountService


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    success_url = '/catalog'

    def form_valid(self, form):
        account_service = AccountService()
        account_service.register_user(self.request, form)
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['yandex_client_id'] = settings.YANDEX_CLIENT_ID
        context['redirect_uri'] = settings.YANDEX_REDIRECT_URI
        return context

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        account_service = AccountService()
        user = account_service.authenticate_and_login(self.request, username, password)
        if user:
            return redirect('catalog')
        return self.form_invalid(form)


class ProfileView(TemplateView):
    permission_classes = [IsAuthenticated]
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        account_service = AccountService()
        context['username'] = account_service.get_display_username(user)
        return context


class YandexCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return redirect('login')

        service = YandexAuthService()
        try:
            access_token = service.get_access_token(code)
            user_data = service.get_user_info(access_token)
            user = service.get_or_create_user(user_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('catalog')


class LoginErrorView(TemplateView):
    template_name = 'users/login_error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_msg'] = self.request.GET.get('message', 'Ошибка при входе. Попробуйте снова.')
        return context


class LogoutView(RedirectView):
    pattern_name = 'login'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
