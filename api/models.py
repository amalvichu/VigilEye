from django.contrib.auth.models import AbstractUser
from django.db import models


class Device(models.Model):
    kindred_id = models.CharField(max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    owner_parent_id = models.CharField(max_length=255)
    location_tracking_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.kindred_id

class Alert(models.Model):
    RISK_LEVELS = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    excerpt = models.TextField()
    score = models.IntegerField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='safe')
    acknowledged = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def get_risk_level(self):
        """Determine risk level based on score"""
        if self.score >= 7:
            return 'high'
        elif self.score >= 4:
            return 'medium'
        elif self.score >= 1:
            return 'low'
        else:
            return 'safe'
    
    def save(self, *args, **kwargs):
        # Auto-set risk level based on score
        self.risk_level = self.get_risk_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Alert for {self.device.kindred_id} ({self.risk_level.title()} Risk - Score: {self.score})"

class Message(models.Model):
    """Model to store individual messages from children"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    message_text = models.TextField()
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=10, choices=Alert.RISK_LEVELS, default='safe')
    flagged_keywords = models.JSONField(default=list, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def get_risk_level(self):
        """Determine risk level based on score"""
        if self.risk_score >= 7:
            return 'high'
        elif self.risk_score >= 4:
            return 'medium'
        elif self.risk_score >= 1:
            return 'low'
        else:
            return 'safe'
    
    def save(self, *args, **kwargs):
        # Auto-set risk level based on score
        self.risk_level = self.get_risk_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.device.kindred_id}: {self.message_text[:50]}..."

class Location(models.Model):
    """Model to store location data for devices"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField(null=True, blank=True)  # GPS accuracy in meters
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def get_google_maps_url(self):
        """Generate Google Maps URL for this location"""
        return f"https://maps.google.com/?q={self.latitude},{self.longitude}"
    
    def get_google_maps_embed_url(self):
        """Generate Google Maps embed URL"""
        return f"https://www.google.com/maps/embed/v1/view?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dO5Z5K5K5K5K5K&center={self.latitude},{self.longitude}&zoom=15"
    
    def __str__(self):
        return f"Location for {self.device.kindred_id} at {self.latitude}, {self.longitude}"


class Vigileye_user(AbstractUser):
    Fname = models.CharField(max_length=200, blank=True)
    Phone_no = models.CharField(max_length=20, unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='vigileye_users',  # Corrected related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='vigileye_users_permissions',  # Corrected related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    def __str__(self):
        return self.username

from django.db import models
from django.contrib.auth.models import AbstractUser

class ParentUser(AbstractUser):
    """
    A custom user model to handle parent registration.
    We will use the default 'username' field for the email address.
    """
    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True) # Added Date of Birth field

    # It's good practice to set the email field as the username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number', 'full_name']

    # Add related_name to avoid clashes with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='parent_users',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='parent_users_permissions',
        blank=True,
    )

    def __str__(self):
        return self.email