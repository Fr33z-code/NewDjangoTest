from django.urls import path
from . import views
from accounts.views_api import RegisterAPI, LoginAPI

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('yandex/callback/', views.yandex_callback, name='yandex_callback'),
    path('api/register/', RegisterAPI.as_view(), name='api-register'),
    path('api/login/', LoginAPI.as_view(), name='api-login'),
    path('login-error/', views.login_error, name='login_error'),
    path('logout/', views.logout_view, name='logout'),

]