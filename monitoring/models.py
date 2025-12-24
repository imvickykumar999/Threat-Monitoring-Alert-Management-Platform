from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='analyst',
        help_text="User role for access control"
    )

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
        ]

    def is_admin(self):
        return self.role == 'admin'

    def is_analyst(self):
        return self.role == 'analyst'


class Event(models.Model):
    """Security event model for threat monitoring"""
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    source_name = models.CharField(
        max_length=255,
        help_text="Source system name"
    )
    event_type = models.CharField(
        max_length=100,
        help_text="Type of security event (e.g., intrusion, malware, anomaly)"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        help_text="Severity level of the event"
    )
    description = models.TextField(
        help_text="Detailed description of the security event"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the event was recorded"
    )

    class Meta:
        db_table = 'events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source_name']),
        ]

    def __str__(self):
        return f"{self.source_name} - {self.event_type} ({self.severity})"

    def should_create_alert(self):
        """Check if this event should trigger an alert"""
        return self.severity in ['High', 'Critical']


class Alert(models.Model):
    """Alert model for tracking security alerts"""
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Acknowledged', 'Acknowledged'),
        ('Resolved', 'Resolved'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text="The event that triggered this alert"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='Open',
        help_text="Current status of the alert"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the alert was created"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the alert was resolved"
    )

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['event']),
        ]

    def __str__(self):
        return f"Alert for {self.event} - {self.status}"

    def save(self, *args, **kwargs):
        """Override save to set resolved_at timestamp"""
        if self.status == 'Resolved' and not self.resolved_at:
            # Set time when resolving
            from django.utils import timezone
            self.resolved_at = timezone.now()
        elif self.status != 'Resolved':
            # CLEAR time if re-opening or acknowledging
            self.resolved_at = None
        super().save(*args, **kwargs)


@receiver(post_save, sender=Event)
def create_alert_for_high_severity_event(sender, instance, created, **kwargs):
    """Signal handler to automatically create alerts for high/critical severity events"""
    if created and instance.should_create_alert():
        Alert.objects.create(event=instance)
