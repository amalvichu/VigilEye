import json
import hashlib
import re
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Device, Alert, Message, Location

# Helper function to generate a cryptographic Kindred ID
def generate_kindred_id(data):
    return hashlib.sha256(data.encode()).hexdigest()

def detect_risk(message):
    """
    Enhanced risk detection function
    Returns: (risk_score, flagged_keywords, risk_level)
    """
    if not message or not message.strip():
        return 0, [], 'safe'
    
    message_lower = message.lower()
    flagged_keywords = []
    risk_score = 0
    
    # High-risk keywords (score: 5 points each)
    high_risk_keywords = [
        'dont tell', 'meet me', 'come alone', 'keep secret', 'dont tell anyone',
        'meet up', 'come over', 'send pic', 'send photo', 'send picture',
        'nude', 'naked', 'sexy', 'hot body', 'send nudes', 'private chat',
        'my place', 'your place', 'alone together', 'no parents', 'dont tell mom',
        'dont tell dad', 'meet secretly', 'hidden', 'secret meeting'
    ]
    
    # Profanity and inappropriate language (score: 4 points each)
    profanity_keywords = [
        'fuck', 'shit', 'damn', 'hell', 'bitch', 'ass', 'asshole', 'bastard',
        'piss', 'crap', 'bullshit', 'fucking', 'fucked', 'shitty', 'damned',
        'bloody', 'freaking', 'screw', 'screwed', 'dammit', 'crap', 'wtf',
        'omfg', 'stfu', 'goddamn', 'motherfucker', 'son of a bitch'
    ]
    
    # Medium-risk keywords (score: 3 points each)
    medium_risk_keywords = [
        'how old are you', 'what grade', 'where do you live', 'what school',
        'meet', 'alone', 'secret', 'private', 'personal info', 'address',
        'phone number', 'social media', 'snapchat', 'instagram', 'tiktok',
        'follow me', 'add me', 'friend request', 'dm me', 'message me'
    ]
    
    # Low-risk keywords (score: 1 point each)
    low_risk_keywords = [
        'cute', 'beautiful', 'handsome', 'cool', 'awesome', 'amazing',
        'love you', 'like you', 'friend', 'buddy', 'pal', 'sweet',
        'darling', 'honey', 'babe', 'baby', 'cutie'
    ]
    
    # Check for high-risk keywords
    for keyword in high_risk_keywords:
        if keyword in message_lower:
            risk_score += 5
            flagged_keywords.append(keyword)
    
    # Check for profanity
    for keyword in profanity_keywords:
        if keyword in message_lower:
            risk_score += 4
            flagged_keywords.append('profanity')
    
    # Check for medium-risk keywords
    for keyword in medium_risk_keywords:
        if keyword in message_lower:
            risk_score += 3
            flagged_keywords.append(keyword)
    
    # Check for low-risk keywords
    for keyword in low_risk_keywords:
        if keyword in message_lower:
            risk_score += 1
            flagged_keywords.append(keyword)
    
    # Pattern-based detection
    patterns = [
        (r'\b\d{2,3}\b', 2, 'age_request'),  # Age requests
        (r'\b\d{3}-\d{3}-\d{4}\b', 3, 'phone_request'),  # Phone numbers
        (r'@\w+', 2, 'social_media'),  # Social media handles
        (r'http[s]?://\S+', 4, 'url_share'),  # URLs
        (r'f+u+c+k+', 4, 'profanity'),  # Variations of fuck
        (r's+h+i+t+', 4, 'profanity'),  # Variations of shit
        (r'd+a+m+n+', 4, 'profanity'),  # Variations of damn
    ]
    
    for pattern, score, category in patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            risk_score += score
            flagged_keywords.append(category)
    
    # Determine risk level
    if risk_score >= 7:
        risk_level = 'high'
    elif risk_score >= 4:
        risk_level = 'medium'
    elif risk_score >= 1:
        risk_level = 'low'
    else:
        risk_level = 'safe'
    
    return risk_score, list(set(flagged_keywords)), risk_level

# Enhanced notification function
def send_notification(message, risk_level='medium'):
    """Send notification for risky messages"""
    notification_msg = f"[{risk_level.upper()} RISK] {message}"
    print(f"Notification: {notification_msg}")
    # In a real app, this would send to parents via email/SMS/push notification

@csrf_exempt
def analyze_chat(request):
    """Analyze chat messages for risk and store them"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            kindred_id = data.get('kindredId', '')

            if not text or not kindred_id:
                return JsonResponse({'error': 'Text and kindredId are required'}, status=400)

            # Use enhanced risk detection
            risk_score, flagged_keywords, risk_level = detect_risk(text)
            
            # Get or create device
            device, created = Device.objects.get_or_create(
                kindred_id=kindred_id, 
                defaults={'owner_parent_id': 'default_parent'}
            )

            # Store the message
            message = Message.objects.create(
                device=device,
                message_text=text,
                risk_score=risk_score,
                flagged_keywords=flagged_keywords
            )

            # Create alert if risky
            alert = None
            if risk_score > 0:
                alert = Alert.objects.create(
                    device=device,
                    excerpt=text,
                    score=risk_score
                )
                
                # Send notification for high-risk messages
                if risk_level == 'high':
                    send_notification(f"High-risk alert for device {kindred_id}: {text}", risk_level)

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'alert_id': alert.id if alert else None,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'flagged_keywords': flagged_keywords,
                'message': 'Message analyzed successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
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
    
    # Filter alerts by risk level
    if risk_filter == 'high':
        alerts = alerts.filter(score__gte=7)
    elif risk_filter == 'medium':
        alerts = alerts.filter(score__gte=4, score__lt=7)
    elif risk_filter == 'low':
        alerts = alerts.filter(score__gte=1, score__lt=4)
    
    paginator = Paginator(alerts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get critical alerts (high risk)
    critical_alerts = Alert.objects.filter(score__gte=7).order_by('-timestamp')
    
    # Get statistics
    total_alerts = Alert.objects.count()
    high_risk_count = Alert.objects.filter(score__gte=7).count()
    medium_risk_count = Alert.objects.filter(score__gte=4, score__lt=7).count()
    low_risk_count = Alert.objects.filter(score__gte=1, score__lt=4).count()
    
    # Get recent locations
    recent_locations = Location.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'page_obj': page_obj,
        'critical_alerts': critical_alerts,
        'risk_filter': risk_filter,
        'total_alerts': total_alerts,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'recent_locations': recent_locations,
    }
    return render(request, 'dashboard.html', context)

def text_input_view(request):
    """View for children to input text messages"""
    if request.method == 'POST':
        kindred_id = request.POST.get('kindred_id', 'CHILD-001')
        message_text = request.POST.get('message_text', '')
        
        if message_text:
            # Analyze the message
            risk_score, flagged_keywords, risk_level = detect_risk(message_text)
            
            # Get or create device
            device, created = Device.objects.get_or_create(
                kindred_id=kindred_id,
                defaults={'owner_parent_id': 'default_parent'}
            )
            
            # Store message
            message = Message.objects.create(
                device=device,
                message_text=message_text,
                risk_score=risk_score,
                flagged_keywords=flagged_keywords
            )
            
            # Create alert if risky
            if risk_score > 0:
                Alert.objects.create(
                    device=device,
                    excerpt=message_text,
                    score=risk_score
                )
                
                if risk_level == 'high':
                    send_notification(f"High-risk message detected: {message_text}", risk_level)
            
            # Add message to Django messages
            if risk_score > 0:
                messages.warning(request, f"Message flagged as {risk_level} risk (Score: {risk_score}) - Flagged keywords: {', '.join(flagged_keywords)}")
            else:
                messages.success(request, "Message is safe!")
            
            return redirect('text_input')
    
    return render(request, 'text_input.html')

@csrf_exempt
def acknowledge_alert(request):
    """Acknowledge an alert"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            alert_id = data.get('alert_id')
            
            if alert_id:
                alert = Alert.objects.get(id=alert_id)
                alert.acknowledged = True
                alert.save()
                return JsonResponse({'success': True, 'message': 'Alert acknowledged'})
            else:
                return JsonResponse({'error': 'Alert ID required'}, status=400)
        except Alert.DoesNotExist:
            return JsonResponse({'error': 'Alert not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def update_location(request):
    """Update device location"""
    print(f"Location update request: {request.method} {request.path}")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kindred_id = data.get('kindredId', '')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            accuracy = data.get('accuracy')
            
            print(f"Location data: {data}")
            
            if not kindred_id or latitude is None or longitude is None:
                return JsonResponse({'error': 'kindredId, latitude, and longitude are required'}, status=400)
            
            # Get or create device
            device, created = Device.objects.get_or_create(
                kindred_id=kindred_id,
                defaults={'owner_parent_id': 'default_parent', 'location_tracking_enabled': True}
            )
            
            print(f"Device: {device}, Created: {created}")
            
            # Store location
            location = Location.objects.create(
                device=device,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy
            )
            
            print(f"Location created: {location}")
            
            return JsonResponse({
                'success': True,
                'location_id': location.id,
                'message': 'Location updated successfully',
                'google_maps_url': location.get_google_maps_url()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Location update error: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def get_location_tracking_status(request):
    """Get location tracking status for a device"""
    print(f"Location status request: {request.method} {request.path}")
    print(f"Query params: {request.GET}")
    
    if request.method == 'GET':
        kindred_id = request.GET.get('kindredId', '')
        
        if not kindred_id:
            return JsonResponse({'error': 'kindredId is required'}, status=400)
        
        try:
            device = Device.objects.get(kindred_id=kindred_id)
            print(f"Device found: {device.kindred_id}, tracking: {device.location_tracking_enabled}")
            return JsonResponse({
                'kindred_id': kindred_id,
                'tracking_enabled': device.location_tracking_enabled
            })
        except Device.DoesNotExist:
            print(f"Device not found: {kindred_id}")
            return JsonResponse({'error': 'Device not found'}, status=404)
    
    return JsonResponse({'error': 'Only GET requests allowed'}, status=405)

@csrf_exempt
def toggle_location_tracking(request):
    """Toggle location tracking for a device"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kindred_id = data.get('kindredId', '')
            enabled = data.get('enabled', False)
            
            if not kindred_id:
                return JsonResponse({'error': 'kindredId is required'}, status=400)
            
            # Get or create device
            device, created = Device.objects.get_or_create(
                kindred_id=kindred_id,
                defaults={'owner_parent_id': 'default_parent'}
            )
            
            # Update tracking status
            device.location_tracking_enabled = enabled
            device.save()
            
            return JsonResponse({
                'success': True,
                'kindred_id': kindred_id,
                'tracking_enabled': device.location_tracking_enabled,
                'message': f'Location tracking {"enabled" if enabled else "disabled"}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

def get_locations(request):
    """Get all locations for dashboard display"""
    if request.method == 'GET':
        kindred_id = request.GET.get('kindredId', '')
        
        if kindred_id:
            # Get locations for specific device
            try:
                device = Device.objects.get(kindred_id=kindred_id)
                locations = Location.objects.filter(device=device).order_by('-timestamp')
            except Device.DoesNotExist:
                return JsonResponse({'error': 'Device not found'}, status=404)
        else:
            # Get all recent locations
            locations = Location.objects.all().order_by('-timestamp')
        
        locations_data = []
        for location in locations[:50]:  # Limit to 50 most recent
            locations_data.append({
                'id': location.id,
                'kindred_id': location.device.kindred_id,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'accuracy': location.accuracy,
                'timestamp': location.timestamp.isoformat(),
                'google_maps_url': location.get_google_maps_url()
            })
        
        return JsonResponse({'locations': locations_data})
    
    return JsonResponse({'error': 'Only GET requests allowed'}, status=405)

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
    
