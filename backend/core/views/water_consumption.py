from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models.base import WaterConsumption
from core.serializers.user import WaterConsumptionSerializer
from rest_framework.permissions import IsAuthenticated

class WaterConsumptionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # For homeowners, show only their data; for admins, show all
        if request.user.role == 'admin':
            records = WaterConsumption.objects.all()
        else:
            records = WaterConsumption.objects.filter(user=request.user)
        serializer = WaterConsumptionSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WaterConsumptionLatestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, period):
        # Validate period
        valid_periods = ['total', 'daily', 'weekly', 'monthly', 'minute']
        if period not in valid_periods:
            return Response({'error': 'Invalid period'}, status=status.HTTP_400_BAD_REQUEST)
        # Get latest record for the specified period
        if request.user.role == 'admin':
            record = WaterConsumption.objects.filter(period=period).order_by('-timestamp').first()
        else:
            record = WaterConsumption.objects.filter(user=request.user, period=period).order_by('-timestamp').first()
        if record:
            serializer = WaterConsumptionSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': f'No {period} consumption data found'}, status=status.HTTP_404_NOT_FOUND)