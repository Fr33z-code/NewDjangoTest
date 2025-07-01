from core.BaseService import BaseService
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from django.contrib.auth import authenticate
from django.contrib.auth import login

User = get_user_model()


class AccountService(BaseService):
    @staticmethod
    def register_user(request, form):
        user = form.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return user

    @staticmethod
    def authenticate_and_login(request, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return user
        return None

    @staticmethod
    def get_display_username(user):
        username = user.username
        if user.password == '':
            username = username.split('_')[0]
        return username


class YandexAuthService(BaseService):
    @staticmethod
    def get_access_token(code):
        token_url = 'https://oauth.yandex.ru/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.YANDEX_CLIENT_ID,
            'client_secret': settings.YANDEX_CLIENT_SECRET,
            'redirect_uri': settings.YANDEX_REDIRECT_URI
        }
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            raise Exception('Failed to get access token')
        return response.json().get('access_token')

    @staticmethod
    def get_user_info(access_token):
        user_info_url = 'https://login.yandex.ru/info'
        headers = {'Authorization': f'OAuth {access_token}'}
        response = requests.get(user_info_url, headers=headers)
        if response.status_code != 200:
            raise Exception('Failed to fetch user info')
        return response.json()

    @staticmethod
    def get_or_create_user(user_data):
        yandex_id = user_data.get('id')
        email = user_data.get('default_email') or f'{yandex_id}@yandex.fake'
        username = f"{user_data.get('login')}_{yandex_id}"
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        return user
