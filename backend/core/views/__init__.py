from .auth import LoginView, UserProfileView, RegisterView
from .water_consumption import WaterConsumptionListView, WaterConsumptionLatestView
from .tank_flow import TankFlowMetricListView, TankFlowMetricLatestView
from .mqtt import ControlDeviceView, LeakageDetectionListView, LeakageDetectionLatestView
from .alerts import ThresholdView, AlertListView, AlertLatestView