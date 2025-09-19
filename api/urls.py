from django.urls import path
from . import views

urlpatterns = [

    path('heartbeat/', views.device_heartbeat, name='device_heartbeat'),
    path('device/reset/', views.reset_device, name='reset_device'),
    path('alerts/', views.get_alerts, name='get_alerts'),
]