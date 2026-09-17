from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import CollectionRecord, CollectionStatus
from .serializers import CollectionRecordSerializer
from audit_logs.services import log_audit

class CollectionRecordViewSet(viewsets.ModelViewSet):
    queryset = CollectionRecord.objects.all().select_related('container', 'worker')
    serializer_class = CollectionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        worker_id = self.request.query_params.get('worker_id')

        if status_param:
            qs = qs.filter(status__iexact=status_param)
        if worker_id:
            qs = qs.filter(worker_id=worker_id)

        return qs

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_collection(self, request, pk=None):
        record = self.get_object()
        record.status = CollectionStatus.COMPLETED
        record.completed_at = timezone.now()
        
        weight = request.data.get('weight_collected')
        if weight:
            record.weight_collected = float(weight)
        record.save()

        log_audit(
            action="COLLECTION_COMPLETED",
            entity="CollectionRecord",
            entity_id=record.id,
            user=request.user,
            metadata={'container_id': record.container.container_id, 'weight_kg': record.weight_collected}
        )

        return Response({
            'message': 'Collection marked COMPLETED.',
            'record': CollectionRecordSerializer(record).data
        })
