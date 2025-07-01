from django.urls import path
from accounts.views_api import RegisterAPI, LoginAPI
from .views import SignupView, LoginView, ProfileView, YandexCallbackView, LoginErrorView, LogoutView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('yandex/callback/', YandexCallbackView.as_view(), name='yandex_callback'),
    path('login-error/', LoginErrorView.as_view(), name='login_error'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/register/', RegisterAPI.as_view(), name='api-register'),
    path('api/login/', LoginAPI.as_view(), name='api-login')
]
