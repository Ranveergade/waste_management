from rest_framework import viewsets, permissions
from .models import RiskPrediction
from .serializers import RiskPredictionSerializer

class RiskPredictionViewSet(viewsets.ModelViewSet):
    queryset = RiskPrediction.objects.all()
    serializer_class = RiskPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        container_id = self.request.query_params.get('container_id')
        if container_id:
            qs = qs.filter(container__container_id=container_id)
        return qs
