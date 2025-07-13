
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.mqtt import mqtt_client
from core.models.base import WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert
from core.serializers.user import (
    WaterConsumptionSerializer, TankFlowMetricSerializer,
    LeakageDetectionSerializer, WaterConsumptionAlertSerializer,
    HistoricalDataFilterSerializer, BulkControlSerializer
)
from django.utils import timezone
from datetime import timedelta
import paho.mqtt.publish as publish

class ControlDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'homeowner':
            return Response({'error': 'Only homeowners can send commands'}, status=status.HTTP_403_FORBIDDEN)
        
        topic = request.data.get('topic')
        payload = request.data.get('payload')
        
        valid_topics = [
            'home/tankRoom/motor',
            'home/tankRoom/tankValve',
            'home/tankRoom/mainValve',
            'home/tankRoom/cadoValve',
            'home/tankRoom/automode'
        ]
        
        if not topic or not payload:
            return Response({'error': 'Topic and payload are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if topic not in valid_topics:
            return Response({'error': 'Invalid topic'}, status=status.HTTP_400_BAD_REQUEST)
        
        if payload not in ['true', 'false']:
            return Response({'error': 'Payload must be "true" or "false"'}, status=status.HTTP_400_BAD_REQUEST)
        
        mqtt_client.publish(topic, payload)
        return Response({'status': 'Command sent', 'topic': topic, 'payload': payload}, status=status.HTTP_200_OK)

class LeakageDetectionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role == 'admin':
            leakage_records = LeakageDetection.objects.all()
        else:
            leakage_records = LeakageDetection.objects.filter(user=request.user)
        serializer = LeakageDetectionSerializer(leakage_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LeakageDetectionLatestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, detection_type):
        valid_types = ['first_pir', 'second_pir', 'leak_alarm']
        if detection_type not in valid_types:
            return Response({'error': 'Invalid detection type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.role == 'admin':
            leakage = LeakageDetection.objects.filter(detection_type=detection_type).order_by('-timestamp').first()
        else:
            leakage = LeakageDetection.objects.filter(
                user=request.user, detection_type=detection_type
            ).order_by('-timestamp').first()
        
        if leakage:
            serializer = LeakageDetectionSerializer(leakage)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': f'No {detection_type} detection found'}, status=status.HTTP_404_NOT_FOUND)

class HistoricalConsumptionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = HistoricalDataFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        filters = {}
        if request.user.role != 'admin':
            filters['user'] = request.user
        if serializer.validated_data.get('period'):
            filters['period'] = serializer.validated_data['period']
        if serializer.validated_data.get('start_date'):
            filters['timestamp__gte'] = serializer.validated_data['start_date']
        if serializer.validated_data.get('end_date'):
            filters['timestamp__lte'] = serializer.validated_data['end_date']
        
        records = WaterConsumption.objects.filter(**filters).order_by('-timestamp')
        serializer = WaterConsumptionSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HistoricalTankFlowView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = HistoricalDataFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        filters = {}
        if request.user.role != 'admin':
            filters['user'] = request.user
        if serializer.validated_data.get('metric_type'):
            filters['metric_type'] = serializer.validated_data['metric_type']
        if serializer.validated_data.get('start_date'):
            filters['timestamp__gte'] = serializer.validated_data['start_date']
        if serializer.validated_data.get('end_date'):
            filters['timestamp__lte'] = serializer.validated_data['end_date']
        
        records = TankFlowMetric.objects.filter(**filters).order_by('-timestamp')
        serializer = TankFlowMetricSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BulkControlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'homeowner':
            return Response({'error': 'Only homeowners can send commands'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BulkControlSerializer(data=request.data)
        if serializer.is_valid():
            results = []
            for command in serializer.validated_data['commands']:
                topic = command['topic']
                value = '1' if command['value'] else '0'
                try:
                    publish.single(
                        topic=topic,
                        payload=value,
                        hostname='mqtt',
                        port=1883,
                    )
                    results.append({'topic': topic, 'status': 'sent', 'payload': value})
                except Exception as e:
                    results.append({'topic': topic, 'status': 'error', 'message': f'Failed to publish: {str(e)}'})
            return Response({'message': 'Commands processed', 'results': results}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
















# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from core.mqtt import mqtt_client
# from core.models.base import WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert
# from core.serializers.user import (
#     WaterConsumptionSerializer, TankFlowMetricSerializer,
#     LeakageDetectionSerializer, WaterConsumptionAlertSerializer,
#     HistoricalDataFilterSerializer, BulkControlSerializer
# )
# from django.utils import timezone
# from datetime import timedelta
# import paho.mqtt.publish as publish

# class ControlDeviceView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         if request.user.role != 'homeowner':
#             return Response({'error': 'Only homeowners can send commands'}, status=status.HTTP_403_FORBIDDEN)
        
#         topic = request.data.get('topic')
#         payload = request.data.get('payload')
        
#         valid_topics = [
#             'home/tankRoom/motor',
#             'home/tankRoom/tankValve',
#             'home/tankRoom/mainValve',
#             'home/tankRoom/cadoValve',
#             'home/tankRoom/automode'
#         ]
        
#         if not topic or not payload:
#             return Response({'error': 'Topic and payload are required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         if topic not in valid_topics:
#             return Response({'error': 'Invalid topic'}, status=status.HTTP_400_BAD_REQUEST)
        
#         if payload not in ['true', 'false']:
#             return Response({'error': 'Payload must be "true" or "false"'}, status=status.HTTP_400_BAD_REQUEST)
        
#         mqtt_client.publish(topic, payload)
#         return Response({'status': 'Command sent', 'topic': topic, 'payload': payload}, status=status.HTTP_200_OK)

# class LeakageDetectionListView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         if request.user.role == 'admin':
#             leakage_records = LeakageDetection.objects.all()
#         else:
#             leakage_records = LeakageDetection.objects.filter(user=request.user)
#         serializer = LeakageDetectionSerializer(leakage_records, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class LeakageDetectionLatestView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, detection_type):
#         valid_types = ['first_pir', 'second_pir', 'leak_alarm']
#         if detection_type not in valid_types:
#             return Response({'error': 'Invalid detection type'}, status=status.HTTP_400_BAD_REQUEST)
        
#         if request.user.role == 'admin':
#             leakage = LeakageDetection.objects.filter(detection_type=detection_type).order_by('-timestamp').first()
#         else:
#             leakage = LeakageDetection.objects.filter(
#                 user=request.user, detection_type=detection_type
#             ).order_by('-timestamp').first()
        
#         if leakage:
#             serializer = LeakageDetectionSerializer(leakage)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response({'error': f'No {detection_type} detection found'}, status=status.HTTP_404_NOT_FOUND)

# class HistoricalConsumptionView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         serializer = HistoricalDataFilterSerializer(data=request.query_params)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         filters = {}
#         if request.user.role != 'admin':
#             filters['user'] = request.user
#         if serializer.validated_data.get('period'):
#             filters['period'] = serializer.validated_data['period']
#         if serializer.validated_data.get('start_date'):
#             filters['timestamp__gte'] = serializer.validated_data['start_date']
#         if serializer.validated_data.get('end_date'):
#             filters['timestamp__lte'] = serializer.validated_data['end_date']
        
#         records = WaterConsumption.objects.filter(**filters).order_by('-timestamp')
#         serializer = WaterConsumptionSerializer(records, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class HistoricalTankFlowView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         serializer = HistoricalDataFilterSerializer(data=request.query_params)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         filters = {}
#         if request.user.role != 'admin':
#             filters['user'] = request.user
#         if serializer.validated_data.get('metric_type'):
#             filters['metric_type'] = serializer.validated_data['metric_type']
#         if serializer.validated_data.get('start_date'):
#             filters['timestamp__gte'] = serializer.validated_data['start_date']
#         if serializer.validated_data.get('end_date'):
#             filters['timestamp__lte'] = serializer.validated_data['end_date']
        
#         records = TankFlowMetric.objects.filter(**filters).order_by('-timestamp')
#         serializer = TankFlowMetricSerializer(records, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class BulkControlView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = BulkControlSerializer(data=request.data)
#         if serializer.is_valid():
#             for command in serializer.validated_data['commands']:
#                 topic = command['topic']
#                 value = '1' if command['value'] else '0'
#                 try:
#                     publish.single(
#                         topic=topic,
#                         payload=value,
#                         hostname='mqtt',
#                         port=1883,
#                     )
#                 except Exception as e:
#                     return Response({"error": f"Failed to publish to {topic}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             return Response({"message": "Commands published successfully"}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

















# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.permissions import IsAuthenticated
# # from core.mqtt import mqtt_client
# # from core.models.base import WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert
# # from core.serializers.user import (
# #     WaterConsumptionSerializer, TankFlowMetricSerializer,
# #     LeakageDetectionSerializer, WaterConsumptionAlertSerializer,
# #     HistoricalDataFilterSerializer, BulkControlSerializer
# # )
# # from django.utils import timezone
# # from datetime import timedelta

# # class ControlDeviceView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         # Only homeowners can send control commands
# #         if request.user.role != 'homeowner':
# #             return Response({'error': 'Only homeowners can send commands'}, status=status.HTTP_403_FORBIDDEN)
        
# #         topic = request.data.get('topic')
# #         payload = request.data.get('payload')
        
# #         valid_topics = [
# #             'home/tankRoom/motor',
# #             'home/tankRoom/tankValve',
# #             'home/tankRoom/mainValve',
# #             'home/tankRoom/cadoValve',
# #             'home/tankRoom/automode'
# #         ]
        
# #         if not topic or not payload:
# #             return Response({'error': 'Topic and payload are required'}, status=status.HTTP_400_BAD_REQUEST)
        
# #         if topic not in valid_topics:
# #             return Response({'error': 'Invalid topic'}, status=status.HTTP_400_BAD_REQUEST)
        
# #         if payload not in ['true', 'false']:
# #             return Response({'error': 'Payload must be "true" or "false"'}, status=status.HTTP_400_BAD_REQUEST)
        
# #         mqtt_client.publish(topic, payload)
# #         return Response({'status': 'Command sent', 'topic': topic, 'payload': payload}, status=status.HTTP_200_OK)

# # class LeakageDetectionListView(APIView):
# #     permission_classes = [IsAuthenticated]
    
# #     def get(self, request):
# #         if request.user.role == 'admin':
# #             leakage_records = LeakageDetection.objects.all()
# #         else:
# #             leakage_records = LeakageDetection.objects.filter(user=request.user)
# #         serializer = LeakageDetectionSerializer(leakage_records, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)

# # class LeakageDetectionLatestView(APIView):
# #     permission_classes = [IsAuthenticated]
    
# #     def get(self, request, detection_type):
# #         valid_types = ['first_pir', 'second_pir', 'leak_alarm']
# #         if detection_type not in valid_types:
# #             return Response({'error': 'Invalid detection type'}, status=status.HTTP_400_BAD_REQUEST)
        
# #         if request.user.role == 'admin':
# #             leakage = LeakageDetection.objects.filter(detection_type=detection_type).order_by('-timestamp').first()
# #         else:
# #             leakage = LeakageDetection.objects.filter(
# #                 user=request.user, detection_type=detection_type
# #             ).order_by('-timestamp').first()
        
# #         if leakage:
# #             serializer = LeakageDetectionSerializer(leakage)
# #             return Response(serializer.data, status=status.HTTP_200_OK)
# #         return Response({'error': f'No {detection_type} detection found'}, status=status.HTTP_404_NOT_FOUND)

# # class HistoricalConsumptionView(APIView):
# #     permission_classes = [IsAuthenticated]
    
# #     def get(self, request):
# #         serializer = HistoricalDataFilterSerializer(data=request.query_params)
# #         if not serializer.is_valid():
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# #         filters = {}
# #         if request.user.role != 'admin':
# #             filters['user'] = request.user
# #         if serializer.validated_data.get('period'):
# #             filters['period'] = serializer.validated_data['period']
# #         if serializer.validated_data.get('start_date'):
# #             filters['timestamp__gte'] = serializer.validated_data['start_date']
# #         if serializer.validated_data.get('end_date'):
# #             filters['timestamp__lte'] = serializer.validated_data['end_date']
        
# #         records = WaterConsumption.objects.filter(**filters).order_by('-timestamp')
# #         serializer = WaterConsumptionSerializer(records, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)

# # class HistoricalTankFlowView(APIView):
# #     permission_classes = [IsAuthenticated]
    
# #     def get(self, request):
# #         serializer = HistoricalDataFilterSerializer(data=request.query_params)
# #         if not serializer.is_valid():
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# #         filters = {}
# #         if request.user.role != 'admin':
# #             filters['user'] = request.user
# #         if serializer.validated_data.get('metric_type'):
# #             filters['metric_type'] = serializer.validated_data['metric_type']
# #         if serializer.validated_data.get('start_date'):
# #             filters['timestamp__gte'] = serializer.validated_data['start_date']
# #         if serializer.validated_data.get('end_date'):
# #             filters['timestamp__lte'] = serializer.validated_data['end_date']
        
# #         records = TankFlowMetric.objects.filter(**filters).order_by('-timestamp')
# #         serializer = TankFlowMetricSerializer(records, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)

# # # class BulkControlView(APIView):
# # #     permission_classes = [IsAuthenticated]
    
# # #     def post(self, request):
# # #         if request.user.role != 'homeowner':
# # #             return Response({'error': 'Only homeowners can send commands'}, status=status.HTTP_403_FORBIDDEN)
        
# # #         serializer = BulkControlSerializer(data=request.data)
# # #         if not serializer.is_valid():
# # #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# # #         valid_topics = [
# # #             'home/tankRoom/motor', 'home/tankRoom/tankValve',
# # #             'home/tankRoom/mainValve', 'home/tankRoom/cadoValve',
# # #             'home/tankRoom/automode'
# # #         ]
# # #         results = []
# # #         for command in serializer.validated_data['commands']:
# # #             topic = command['topic']
# # #             value = command['value']
# # #             if topic not in valid_topics:
# # #                 results.append({'topic': topic, 'status': 'error', 'message': 'Invalid topic'})
# # #                 continue
# # #             if not isinstance(value, bool):
# # #                 results.append({'topic': topic, 'status': 'error', 'message': 'Value must be boolean'})
# # #                 continue
# # #             mqtt_client.publish(topic, str(value).lower())
# # #             results.append({'topic': topic, 'status': 'sent', 'payload': value})
        
# # #         return Response({'results': results}, status=status.HTTP_200_OK)



# # class BulkControlView(APIView):
# #    permission_classes = [IsAuthenticated]
 
# #     def post(self, request):
# #          serializer = BulkControlSerializer(data=request.data)
# #          if serializer.is_valid():
# #              for command in serializer.validated_data['commands']:
# #                  topic = command['topic']
# #                  value = '1' if command['value'] else '0'
# #                  try:
# #                      publish.single(
# #                          topic=topic,
# #                          payload=value,
# #                          hostname='mqtt',  # Mosquitto service name in Docker
# #                          port=1883,
# #                      )
# #                  except Exception as e:
# #                      return Response({"error": f"Failed to publish to {topic}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #              return Response({"message": "Commands published successfully"}, status=status.HTTP_200_OK)
# #          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
