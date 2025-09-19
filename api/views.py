import json
import hashlib
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Device, Alert

# Helper function to generate a cryptographic Kindred ID



def generate_kindred_id(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Placeholder function for notifications
def send_notification(message):
    print(f"Notification: {message}")

@csrf_exempt
def analyze_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            kindred_id = data.get('kindredId', '')

            score = 0
            flagged_lines = []

            # Rule-based scoring logic
            keywords_high_risk = ['dont tell', 'meet me', 'come alone']
            keywords_medium_risk = ['send pic', 'how old are you', 'meet', 'alone', 'secret', 'nudes']

            for line in text.split('\n'):
                line_lower = line.lower()
                for keyword in keywords_high_risk:
                    if keyword in line_lower:
                        score += 5
                        flagged_lines.append(line)
                for keyword in keywords_medium_risk:
                    if keyword in line_lower:
                        score += 2
                        flagged_lines.append(line)
            
            device, created = Device.objects.get_or_create(kindred_id=kindred_id, defaults={'owner_parent_id': 'default_parent'})

            if score >= 7:
                Alert.objects.create(device=device, excerpt=text, score=score)
                send_notification(f"High-risk alert for device {kindred_id}: {text}")

            return JsonResponse({'score': score, 'flagged_lines': list(set(flagged_lines))})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def device_heartbeat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kindred_id = data.get('kindredId', '')
            
            try:
                device = Device.objects.get(kindred_id=kindred_id)
                device.last_heartbeat = timezone.now()
                device.save()
                return JsonResponse({'status': 'heartbeat updated'})
            except Device.DoesNotExist:
                return JsonResponse({'error': 'Device not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def reset_device(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kindred_id = data.get('kindredId', '')

            try:
                device = Device.objects.get(kindred_id=kindred_id)
                device.delete()
                return JsonResponse({'status': 'device deleted'})
            except Device.DoesNotExist:
                return JsonResponse({'error': 'Device not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def dashboard(request):
    risk_filter = request.GET.get('risk', 'all')
    alerts = Alert.objects.all().order_by('-timestamp')
    
    if risk_filter == 'high':
        alerts = alerts.filter(score__gte=7)
    elif risk_filter == 'medium':
        alerts = alerts.filter(score__gte=4, score__lt=7)
    elif risk_filter == 'low':
        alerts = alerts.filter(score__lt=4)
    
    paginator = Paginator(alerts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    critical_alerts = alerts.filter(score__gte=7)
    
    context = {
        'page_obj': page_obj,
        'critical_alerts': critical_alerts,
        'risk_filter': risk_filter
    }
    return render(request, 'dashboard.html', context)

def get_alerts(request):
    if request.method == 'GET':
        alerts = Alert.objects.all().order_by('-timestamp')
        alerts_data = [{
            'id': alert.id,
            'device_kindred_id': alert.device.kindred_id,
            'excerpt': alert.excerpt,
            'score': alert.score,
            'timestamp': alert.timestamp.isoformat()
        } for alert in alerts]
        return JsonResponse({'alerts': alerts_data})
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    

