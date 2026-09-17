from rest_framework import viewsets, permissions
from .models import VisionEvent
from .serializers import VisionEventSerializer

class VisionEventViewSet(viewsets.ModelViewSet):
    queryset = VisionEvent.objects.all()
    serializer_class = VisionEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        container_id = self.request.query_params.get('container_id')
        if container_id:
            qs = qs.filter(container__container_id=container_id)
        return qs
