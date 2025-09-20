from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('text-input/', views.text_input_view, name='text_input'),
    path('api/analyze/', views.analyze_chat, name='analyze_chat'),
    path('api/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('api/location/update/', views.update_location, name='update_location'),
    path('api/location/status/', views.get_location_tracking_status, name='get_location_tracking_status'),
    path('api/location/status', views.get_location_tracking_status, name='get_location_tracking_status_no_slash'),
    path('api/location/toggle/', views.toggle_location_tracking, name='toggle_location_tracking'),
    path('api/locations/', views.get_locations, name='get_locations'),
    path('heartbeat/', views.device_heartbeat, name='device_heartbeat'),
    path('device/reset/', views.reset_device, name='reset_device'),
    path('alerts/', views.get_alerts, name='get_alerts'),
]