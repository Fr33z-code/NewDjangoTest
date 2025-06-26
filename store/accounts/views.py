from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@csrf_exempt
def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('catalog')
    return render(request, 'login.html', {
        'form': form,
        'yandex_client_id': settings.YANDEX_CLIENT_ID,
        'redirect_uri': settings.YANDEX_REDIRECT_URI,
    })


@login_required
def profile_view(request):
    user = request.user
    username = user.username
    if user.password == '':
        username = username.split('_')[0]
    return render(request, 'profile.html', {'username': username})


def yandex_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('login')
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
        return JsonResponse({'error': 'Failed to get access token'}, status=400)

    token_data = response.json()
    access_token = token_data.get('access_token')

    user_info_url = 'https://login.yandex.ru/info'
    headers = {'Authorization': f'OAuth {access_token}'}
    user_response = requests.get(user_info_url, headers=headers)

    if user_response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch user info'}, status=400)

    user_data = user_response.json()
    yandex_id = user_data.get('id')
    email = user_data.get('default_email') or f'{yandex_id}@yandex.fake'
    username = f"{user_data.get('login')}_{yandex_id}"
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return redirect('catalog')


def login_error(request):
    error_msg = request.GET.get('message', 'Ошибка при входе. Попробуйте снова.')
    return render(request, 'users/login_error.html', {'error_msg': error_msg})
