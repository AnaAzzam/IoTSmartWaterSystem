from django.contrib import admin
from .models.base import CustomUser, WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionThreshold, WaterConsumptionAlert

@admin.register(WaterConsumption)
class WaterConsumptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'consumption', 'timestamp', 'sensor_id')
    list_filter = ('user', 'period', 'timestamp')
    search_fields = ('user__username', 'sensor_id', 'period')
    ordering = ('-timestamp',)

@admin.register(TankFlowMetric)
class TankFlowMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'metric_type', 'value', 'timestamp', 'sensor_id')
    list_filter = ('user', 'metric_type', 'timestamp')
    search_fields = ('user__username', 'sensor_id', 'metric_type')
    ordering = ('-timestamp',)

@admin.register(LeakageDetection)
class LeakageDetectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'detection_type', 'is_active', 'timestamp', 'sensor_id')
    list_filter = ('user', 'detection_type', 'is_active', 'timestamp')
    search_fields = ('user__username', 'sensor_id', 'detection_type')
    ordering = ('-timestamp',)

@admin.register(WaterConsumptionThreshold)
class WaterConsumptionThresholdAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'threshold')
    list_filter = ('user', 'period')
    search_fields = ('user__username', 'period')

@admin.register(WaterConsumptionAlert)
class WaterConsumptionAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'is_active', 'timestamp')
    list_filter = ('user', 'period', 'is_active', 'timestamp')
    search_fields = ('user__username', 'period')
    ordering = ('-timestamp',)

admin.site.register(CustomUser)