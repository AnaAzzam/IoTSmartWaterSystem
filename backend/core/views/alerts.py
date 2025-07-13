from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models.base import WaterConsumptionThreshold, WaterConsumptionAlert
from core.serializers.user import WaterConsumptionThresholdSerializer, WaterConsumptionAlertSerializer

class ThresholdView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Only homeowners can set thresholds
        if request.user.role != 'homeowner':
            return Response({'error': 'Only homeowners can set thresholds'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = WaterConsumptionThresholdSerializer(data=request.data)
        if serializer.is_valid():
            # Check if threshold exists
            existing = WaterConsumptionThreshold.objects.filter(
                user=request.user,
                period=serializer.validated_data['period']
            ).first()
            if existing:
                return Response({'error': 'Threshold already exists for this period'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, period):
        # Only homeowners can update thresholds
        if request.user.role != 'homeowner':
            return Response({'error': 'Only homeowners can update thresholds'}, status=status.HTTP_403_FORBIDDEN)
        
        valid_periods = ['daily', 'weekly', 'monthly', 'minute']
        if period not in valid_periods:
            return Response({'error': 'Invalid period'}, status=status.HTTP_400_BAD_REQUEST)
        
        threshold = WaterConsumptionThreshold.objects.filter(user=request.user, period=period).first()
        if not threshold:
            return Response({'error': 'Threshold not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WaterConsumptionThresholdSerializer(threshold, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AlertListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role == 'admin':
            alerts = WaterConsumptionAlert.objects.all()
        else:
            alerts = WaterConsumptionAlert.objects.filter(user=request.user)
        serializer = WaterConsumptionAlertSerializer(alerts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AlertLatestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, period):
        valid_periods = ['daily', 'weekly', 'monthly', 'minute']
        if period not in valid_periods:
            return Response({'error': 'Invalid period'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role == 'admin':
            alert = WaterConsumptionAlert.objects.filter(period=period).order_by('-timestamp').first()
        else:
            alert = WaterConsumptionAlert.objects.filter(user=request.user, period=period).order_by('-timestamp').first()
        if alert:
            serializer = WaterConsumptionAlertSerializer(alert)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': f'No {period} alert found'}, status=status.HTTP_404_NOT_FOUND)