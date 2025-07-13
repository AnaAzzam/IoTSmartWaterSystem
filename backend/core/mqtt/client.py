import paho.mqtt.client as mqtt
import json
import logging
import os
from django.conf import settings
from core.models.base import WaterConsumption, TankFlowMetric, LeakageDetection, CustomUser, WaterConsumptionAlert
from threading import Thread
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.serializers.user import WaterConsumptionSerializer, TankFlowMetricSerializer, LeakageDetectionSerializer, WaterConsumptionAlertSerializer

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(log_dir, 'mqtt.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        # Configure broker (localhost for now, update for cloud)
        #self.broker = 'localhost'  # Replace with your broker address
        self.broker =  'mqtt'
        self.port = 1883
        self.client.connect(self.broker, self.port, 60)
        self.subscribed_topics = [
            'home/tankRoom/tankLevel',
            'home/tankRoom/mainFlowrate',
            'home/tankRoom/secondFlowrate',
            'home/waterConsumption/+',
            'home/leakageRoom/firstPIRSensor',
            'home/leakageRoom/secondPIRSensor',
            'home/leakageRoom/leakAlarm',
            'home/waterConsumption/alert/+',
        ]
        # Assume one user per home for now; configurable later
        self.default_user = None
        self.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            for topic in self.subscribed_topics:
                client.subscribe(topic)
                logging.info(f"Subscribed to {topic}")
        else:
            logging.error(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logging.warning(f"Disconnected from MQTT broker with code {rc}")
        self.client.reconnect()

    async def broadcast_update(self, data_type, instance):
        channel_layer = get_channel_layer()
        serializer_map = {
            'consumption': WaterConsumptionSerializer,
            'tank_flow': TankFlowMetricSerializer,
            'leakage': LeakageDetectionSerializer,
            'alert': WaterConsumptionAlertSerializer,
        }
        serializer = serializer_map[data_type](instance)
        await channel_layer.group_send(
            f'water_data_{self.default_user.id}',
            {
                'type': 'water.update',
                'data': {'type': data_type, 'data': serializer.data}
            }
        )

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logging.info(f"Received message on {topic}: {payload}")
            
            # Get default user (first homeowner for simplicity)
            if not self.default_user:
                self.default_user = CustomUser.objects.filter(role='homeowner').first()
                if not self.default_user:
                    logging.error("No homeowner found")
                    return
            
            # Process tank and flow metrics
            if topic == 'home/tankRoom/tankLevel':
                instance = TankFlowMetric.objects.create(
                    user=self.default_user,
                    value=float(payload),
                    metric_type='tank_level',
                    sensor_id='tank_level_sensor'
                )
                async_to_sync(self.broadcast_update)('tank_flow', instance)
            elif topic == 'home/tankRoom/mainFlowrate':
                instance = TankFlowMetric.objects.create(
                    user=self.default_user,
                    value=float(payload),
                    metric_type='main_flow_rate',
                    sensor_id='main_flow_sensor'
                )
                async_to_sync(self.broadcast_update)('tank_flow', instance)
            elif topic == 'home/tankRoom/secondFlowrate':
                instance = TankFlowMetric.objects.create(
                    user=self.default_user,
                    value=float(payload),
                    metric_type='secondary_flow_rate',
                    sensor_id='secondary_flow_sensor'
                )
                async_to_sync(self.broadcast_update)('tank_flow', instance)
            # Process water consumption
            elif topic.startswith('home/waterConsumption/') and not topic.startswith('home/waterConsumption/alert/'):
                period = topic.split('/')[-1]
                if period in ['total', 'daily', 'weekly', 'monthly', 'minute']:
                    instance = WaterConsumption.objects.create(
                        user=self.default_user,
                        consumption=float(payload),
                        period=period,
                        sensor_id='main_flow_sensor'
                    )
                    async_to_sync(self.broadcast_update)('consumption', instance)
                else:
                    logging.warning(f"Invalid consumption period: {period}")
            # Process consumption alerts
            elif topic.startswith('home/waterConsumption/alert/'):
                period = topic.split('/')[-1]
                if period in ['daily', 'weekly', 'monthly', 'minute']:
                    is_active = payload.lower() == 'true'
                    instance = WaterConsumptionAlert.objects.create(
                        user=self.default_user,
                        is_active=is_active,
                        period=period
                    )
                    async_to_sync(self.broadcast_update)('alert', instance)
                else:
                    logging.warning(f"Invalid alert period: {period}")
            # Process leakage detection
            elif topic.startswith('home/leakageRoom/'):
                detection_map = {
                    'firstPIRSensor': ('first_pir', 'first_pir_sensor'),
                    'secondPIRSensor': ('second_pir', 'second_pir_sensor'),
                    'leakAlarm': ('leak_alarm', 'leak_alarm_sensor')
                }
                for key, (detection_type, sensor_id) in detection_map.items():
                    if topic.endswith(key):
                        is_active = payload.lower() == 'true'
                        instance = LeakageDetection.objects.create(
                            user=self.default_user,
                            is_active=is_active,
                            detection_type=detection_type,
                            sensor_id=sensor_id
                        )
                        async_to_sync(self.broadcast_update)('leakage', instance)
                        break
                            
        except ValueError as e:
            logging.error(f"Invalid payload format on {topic}: {payload} - {e}")
        except Exception as e:
            logging.error(f"Error processing message on {topic}: {e}")

    def publish(self, topic, payload):
        try:
            result = self.client.publish(topic, str(payload))
            if result.rc == mqtt.MQTT_OK:
                logging.info(f"Published to {topic}: {payload}")
            else:
                logging.error(f"Failed to publish to {topic}: {result.rc}")
        except Exception as e:
            logging.error(f"Error publishing to {topic}: {e}")

    def start(self):
        # Start MQTT loop in a separate thread
        Thread(target=self.client.loop_forever, daemon=True).start()

# Singleton instance
mqtt_client = MQTTClient()