from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    address = models.CharField(max_length=200)
    unit_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address} - Unit {self.unit_number}"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')]
    URGENCY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('emergency', 'Emergency')]
    CATEGORY_CHOICES = [('plumbing', 'Plumbing'), ('electrical', 'Electrical'), ('heating', 'Heating'),
                        ('other', 'Other')]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    description = models.TextField()
    photo = models.ImageField(upload_to='requests/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dark_mode = models.BooleanField(default=False)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

class TicketMessage(models.Model):
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} on request #{self.request.id}"

class Announcement(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RequestPhoto(models.Model):
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='requests/')

    def __str__(self):
        return f"Photo for request #{self.request.id}"
from django.db import models

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"








# Create your models here.
