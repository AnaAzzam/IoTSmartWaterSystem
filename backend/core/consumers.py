import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.models.base import WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert
from core.serializers.user import WaterConsumptionSerializer, TankFlowMetricSerializer, LeakageDetectionSerializer, WaterConsumptionAlertSerializer

class WaterDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'water_data_{self.user_id}'
        
        # Authenticate
        user = await self.get_user()
        if user is None or str(user.id) != self.user_id:
            await self.close()
            return
        
        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Handle client messages (optional)
        pass

    # Receive message from group
    async def water_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_user(self):
        from django.contrib.auth import get_user_model
        try:
            return get_user_model().objects.get(id=self.user_id)
        except:
            return None