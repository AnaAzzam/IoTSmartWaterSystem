from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
import re
from django.core.exceptions import ValidationError




# Custom validation for Egyptian phone numbers
def validate_egyptian_phone_number(value):
    if not re.match(r'^\+20[0-1]\d{10}$', value):
        raise ValidationError('Phone number must be in the format +20XXXXXXXXXX (e.g., +201234567890)')

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('homeowner', 'Homeowner'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='homeowner')
    full_name = models.CharField(max_length=255, blank=True)
    home_address = models.TextField(blank=True, null=True)  # Optional
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[validate_egyptian_phone_number],
        blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



class WaterConsumption(models.Model):
    # Choices for consumption period
    PERIOD_CHOICES = (
        ('total', 'Total'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('minute', 'Minute'),
    )
    
    # Link to homeowner
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='water_consumption_records'
    )
    # Consumption data
    consumption = models.FloatField(
        help_text="Water consumption in liters"
    )
    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        help_text="Time period of consumption (total, daily, weekly, monthly, minute)"
    )
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the reading was recorded"
    )
    sensor_id = models.CharField(
        max_length=50,
        help_text="Unique identifier for the sensor (e.g., 'main_flow_sensor')"
    )
    
    def clean(self):
        # Validate consumption (non-negative)
        if self.consumption < 0:
            raise ValidationError("Water consumption cannot be negative")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'period', 'timestamp']),
            models.Index(fields=['sensor_id']),
        ]
    
    def __str__(self):
        return f"{self.period.title()} Water Consumption for {self.user.username} at {self.timestamp}: {self.consumption}L"
    





class TankFlowMetric(models.Model):
    # Choices for metric type
    METRIC_CHOICES = (
        ('tank_level', 'Tank Level'),
        ('main_flow_rate', 'Main Flow Rate'),
        ('secondary_flow_rate', 'Secondary Flow Rate'),
    )
    
    # Link to homeowner
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='tank_flow_metrics'
    )
    # Metric data
    value = models.FloatField(
        help_text="Value of the metric (liters for tank level, liters/min for flow rates)"
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_CHOICES,
        help_text="Type of metric (tank_level, main_flow_rate, secondary_flow_rate)"
    )
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the reading was recorded"
    )
    sensor_id = models.CharField(
        max_length=50,
        help_text="Unique identifier for the sensor (e.g., 'tank_level_sensor')"
    )
    
    def clean(self):
        # Validate value (non-negative)
        if self.value < 0:
            raise ValidationError("Metric value cannot be negative")
        # Optional: Reasonable upper limits
        if self.metric_type == 'tank_level' and self.value > 10000:
            raise ValidationError("Tank level cannot exceed 10,000 liters")
        if self.metric_type in ['main_flow_rate', 'secondary_flow_rate'] and self.value > 100:
            raise ValidationError("Flow rate cannot exceed 100 liters/min")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'metric_type', 'timestamp']),
            models.Index(fields=['sensor_id']),
        ]
    
    def __str__(self):
        unit = 'L' if self.metric_type == 'tank_level' else 'L/min'
        return f"{self.metric_type.replace('_', ' ').title()} for {self.user.username} at {self.timestamp}: {self.value}{unit}"
    








# Model for detecting water leakage using PIR sensors and leak alarms
class LeakageDetection(models.Model):
    # Choices for detection type
    DETECTION_CHOICES = (
        ('first_pir', 'First PIR Sensor'),
        ('second_pir', 'Second PIR Sensor'),
        ('leak_alarm', 'Leak Alarm'),
    )
    
    # Link to homeowner
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='leakage_detections'
    )
    # Detection data
    is_active = models.BooleanField(
        help_text="True if sensor detects motion (PIR) or leakage (alarm)"
    )
    detection_type = models.CharField(
        max_length=20,
        choices=DETECTION_CHOICES,
        help_text="Type of detection (first_pir, second_pir, leak_alarm)"
    )
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the reading was recorded"
    )
    sensor_id = models.CharField(
        max_length=50,
        help_text="Unique identifier for the sensor (e.g., 'first_pir_sensor')"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'detection_type', 'timestamp']),
            models.Index(fields=['sensor_id']),
        ]
    
    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.detection_type.replace('_', ' ').title()} for {self.user.username} at {self.timestamp}: {status}"
    








## Model for setting water consumption thresholds and alerts
class WaterConsumptionThreshold(models.Model):
    # Choices for period
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('minute', 'Minute'),
    )
    
    # Link to homeowner
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='consumption_thresholds'
    )
    # Threshold data
    threshold = models.FloatField(
        help_text="Threshold value in liters"
    )
    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        help_text="Time period for threshold (daily, weekly, monthly, minute)"
    )
    
    def clean(self):
        if self.threshold <= 0:
            raise ValidationError("Threshold must be positive")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['user', 'period']
        indexes = [
            models.Index(fields=['user', 'period']),
        ]
    
    def __str__(self):
        return f"{self.period.title()} Threshold for {self.user.username}: {self.threshold}L"

class WaterConsumptionAlert(models.Model):
    # Choices for period
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('minute', 'Minute'),
    )
    
    # Link to homeowner
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='consumption_alerts'
    )
    # Alert data
    is_active = models.BooleanField(
        help_text="True if alert is triggered"
    )
    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        help_text="Time period for alert (daily, weekly, monthly, minute)"
    )
    # Metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the alert was recorded"
    )
    



    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'period', 'timestamp']),
        ]
    
    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.period.title()} Alert for {self.user.username} at {self.timestamp}: {status}"
    









