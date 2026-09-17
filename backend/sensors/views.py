from rest_framework import viewsets, permissions
from .models import SensorReading
from .serializers import SensorReadingSerializer

class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        container_id = self.request.query_params.get('container_id')
        if container_id:
            qs = qs.filter(container__container_id=container_id)
        return qs
