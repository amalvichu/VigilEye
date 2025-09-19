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
