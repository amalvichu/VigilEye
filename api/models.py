from django.contrib.auth.models import AbstractUser
from django.db import models

class Device(models.Model):
    kindred_id = models.CharField(max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    owner_parent_id = models.CharField(max_length=255)

    def __str__(self):
        return self.kindred_id

class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    excerpt = models.TextField()
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.device.kindred_id} (Score: {self.score})"


class Vigileye_user(AbstractUser):
    Name = models.CharField(max_length=200, blank=True)
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
