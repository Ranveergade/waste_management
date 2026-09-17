from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from containers.models import Container
from sensors.models import SensorReading
from vision.models import VisionEvent
from risk.models import RiskPrediction
from risk.services import calculate_container_risk
from actions.models import Action, ActionPriority, ActionStatus
from alerts.models import Alert, AlertSeverity, AlertType, AlertStatus
from audit_logs.services import log_audit

class DeviceTelemetryView(APIView):
    """
    Endpoint for IoT ESP32 / Telemetry hardware ingestion:
    POST /api/devices/sensor-data/
    """
    permission_classes = [permissions.AllowAny]  # Device telemetry may use API token or open ingestion in demo

    def post(self, request):
        data = request.data
        container_id = data.get('container_id')
        if not container_id:
            return Response({'error': 'Missing container_id in payload'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch or initialize container
        container, created = Container.objects.get_or_create(
            container_id=container_id,
            defaults={
                'name': f'Waste Unit {container_id}',
                'location': data.get('location', 'General Ward Corridor'),
                'ward': data.get('ward', 'Emergency Ward'),
                'capacity_liters': 60.0
            }
        )

        device_status = data.get('device_status', 'ONLINE')
        container.device_status = device_status
        container.save()

        # 2. Store raw SensorReading
        weight = float(data.get('weight', 0.0))
        fill_level = float(data.get('fill_level', 0.0))
        temperature = float(data.get('temperature', 24.0))
        humidity = float(data.get('humidity', 50.0))
        gas_indicator = float(data.get('gas_indicator', 120.0))
        moisture = float(data.get('moisture', 20.0))

        reading = SensorReading.objects.create(
            container=container,
            weight=weight,
            fill_level=fill_level,
            temperature=temperature,
            humidity=humidity,
            gas_indicator=gas_indicator,
            moisture=moisture,
            device_status=device_status
        )

        # 3. Retrieve latest vision event if available
        vision_event = container.vision_events.first()

        # 4. Calculate Risk
        risk_result = calculate_container_risk(container, reading, vision_event)

        risk_pred = RiskPrediction.objects.create(
            container=container,
            risk_score=risk_result['risk_score'],
            risk_level=risk_result['risk_level'],
            recommended_action=risk_result['recommended_action'],
            reason=risk_result['reason']
        )

        # 5. Generate / Update Action
        priority = ActionPriority.LOW
        if risk_result['risk_level'] == 'CRITICAL':
            priority = ActionPriority.CRITICAL
        elif risk_result['risk_level'] == 'HIGH':
            priority = ActionPriority.HIGH
        elif risk_result['risk_level'] == 'MEDIUM':
            priority = ActionPriority.MEDIUM

        action_item = None
        if risk_result['recommended_action'] not in ['NO ACTION']:
            action_item = Action.objects.create(
                container=container,
                action_type=risk_result['recommended_action'],
                priority=priority,
                reason=risk_result['reason'],
                status=ActionStatus.PENDING
            )

        # 6. Generate Alert if high risk or abnormal gas/temp
        created_alert = None
        if risk_result['risk_level'] in ['HIGH', 'CRITICAL'] or gas_indicator >= 350:
            severity = AlertSeverity.CRITICAL if risk_result['risk_level'] == 'CRITICAL' else AlertSeverity.HIGH
            alert_type = AlertType.GAS_ANOMALY if gas_indicator >= 350 else AlertType.HIGH_RISK
            created_alert = Alert.objects.create(
                container=container,
                severity=severity,
                alert_type=alert_type,
                message=f"Telemetry Alert: {risk_result['reason']}",
                recommended_action=risk_result['recommended_action'],
                status=AlertStatus.NEW
            )

        # 7. Audit Log Entry
        log_audit(
            action="TELEMETRY_RECEIVED",
            entity="Container",
            entity_id=container_id,
            metadata={
                'fill_level': fill_level,
                'weight': weight,
                'gas_indicator': gas_indicator,
                'risk_score': risk_result['risk_score'],
                'risk_level': risk_result['risk_level'],
                'recommended_action': risk_result['recommended_action']
            }
        )

        return Response({
            'status': 'success',
            'container_id': container_id,
            'timestamp': reading.timestamp,
            'risk_assessment': {
                'score': risk_result['risk_score'],
                'level': risk_result['risk_level'],
                'action': risk_result['recommended_action'],
                'reason': risk_result['reason']
            },
            'action_generated': action_item.id if action_item else None,
            'alert_generated': created_alert.id if created_alert else None
        }, status=status.HTTP_201_CREATED)
