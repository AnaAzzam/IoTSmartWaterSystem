
from django.urls import path
from .views import auth, water_consumption, tank_flow, mqtt, alerts

urlpatterns = [
    # Authentication
    path('register/', auth.RegisterView.as_view(), name='register'),
    path('login/', auth.LoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('profile/', auth.UserProfileView.as_view(), name='user_profile'),

    # Water Consumption
    path('water-consumption/', water_consumption.WaterConsumptionListView.as_view(), name='water_consumption_list'),
    path('water-consumption/latest/<str:period>/', water_consumption.WaterConsumptionLatestView.as_view(), name='water_consumption_latest'),
    path('water-consumption/history/', mqtt.HistoricalConsumptionView.as_view(), name='water_consumption_history'),

    # Tank Flow
    path('tank-flow/', tank_flow.TankFlowMetricListView.as_view(), name='tank_flow_list'),
    path('tank-flow/latest/<str:metric_type>/', tank_flow.TankFlowMetricLatestView.as_view(), name='tank_flow_latest'),
    path('tank-flow/history/', mqtt.HistoricalTankFlowView.as_view(), name='tank_flow_history'),

    # Device Control
    path('control-device/', mqtt.ControlDeviceView.as_view(), name='control_device'),
    path('bulk-control/', mqtt.BulkControlView.as_view(), name='bulk_control'),

    # Leakage Detection
    path('leakage-detection/', mqtt.LeakageDetectionListView.as_view(), name='leakage_detection_list'),
    path('leakage-detection/latest/<str:detection_type>/', mqtt.LeakageDetectionLatestView.as_view(), name='leakage_detection_latest'),

    # Alerts & Thresholds
    path('threshold/', alerts.ThresholdView.as_view(), name='threshold'),
    path('threshold/<str:period>/', alerts.ThresholdView.as_view(), name='threshold_update'),
    path('alerts/', alerts.AlertListView.as_view(), name='alert_list'),
    path('alerts/latest/<str:period>/', alerts.AlertLatestView.as_view(), name='alert_latest'),
]
