from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models.base import TankFlowMetric
from core.serializers.user import TankFlowMetricSerializer
from rest_framework.permissions import IsAuthenticated

class TankFlowMetricListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # For homeowners, show only their data; for admins, show all
        if request.user.role == 'admin':
            metrics = TankFlowMetric.objects.all()
        else:
            metrics = TankFlowMetric.objects.filter(user=request.user)
        serializer = TankFlowMetricSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TankFlowMetricLatestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, metric_type):
        # Validate metric_type
        valid_metrics = ['tank_level', 'main_flow_rate', 'secondary_flow_rate']
        if metric_type not in valid_metrics:
            return Response({'error': 'Invalid metric type'}, status=status.HTTP_400_BAD_REQUEST)
        # Get latest record for the specified metric
        if request.user.role == 'admin':
            metric = TankFlowMetric.objects.filter(metric_type=metric_type).order_by('-timestamp').first()
        else:
            metric = TankFlowMetric.objects.filter(user=request.user, metric_type=metric_type).order_by('-timestamp').first()
        if metric:
            serializer = TankFlowMetricSerializer(metric)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': f'No {metric_type} data found'}, status=status.HTTP_404_NOT_FOUND)