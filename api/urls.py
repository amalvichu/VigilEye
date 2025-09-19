from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('heartbeat/', views.device_heartbeat, name='device_heartbeat'),
    path('device/reset/', views.reset_device, name='reset_device'),
    path('alerts/', views.get_alerts, name='get_alerts'),
]