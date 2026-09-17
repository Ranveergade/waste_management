from .models import AuditLog

def log_audit(action, entity, entity_id, user=None, metadata=None):
    """
    Helper function to record an event in the AuditLog timeline.
    """
    if metadata is None:
        metadata = {}
    return AuditLog.objects.create(
        user=user,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        metadata=metadata
    )
