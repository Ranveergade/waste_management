import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import UserProfile, Role
from containers.models import Container, ContainerStatus, DeviceStatus, WasteCategory
from sensors.models import SensorReading
from vision.models import VisionEvent, VisionClass
from risk.models import RiskPrediction, RiskLevel
from risk.services import calculate_container_risk
from actions.models import Action, ActionPriority, ActionStatus
from alerts.models import Alert, AlertSeverity, AlertType, AlertStatus
from collection.models import CollectionRecord, CollectionStatus
from audit_logs.models import AuditLog

class Command(BaseCommand):
    help = 'Seeds realistic hospital waste management demo data for SIH 2026 WasteGuard prototype'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting WasteGuard Demo Data Seeding...'))

        # 1. Create Role Accounts
        users_def = [
            {'username': 'admin', 'email': 'admin@hospital.org', 'role': Role.ADMIN, 'emp_id': 'EMP-001', 'name': 'Dr. Alok Verma', 'ward': 'Administration'},
            {'username': 'supervisor', 'email': 'supervisor@hospital.org', 'role': Role.SUPERVISOR, 'emp_id': 'EMP-002', 'name': 'Sunita Rao', 'ward': 'Biomedical Waste Department'},
            {'username': 'raj_sharma', 'email': 'raj.sharma@hospital.org', 'role': Role.OPERATOR, 'emp_id': 'EMP-003', 'name': 'Raj Sharma', 'ward': 'Emergency & ICU Wards'},
            {'username': 'safety_officer', 'email': 'safety@hospital.org', 'role': Role.SAFETY_OFFICER, 'emp_id': 'EMP-004', 'name': 'Priya Mehta', 'ward': 'Hospital Safety Division'},
        ]

        user_objects = {}
        for u in users_def:
            user_obj, created = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'first_name': u['name'].split()[0], 'last_name': ' '.join(u['name'].split()[1:])}
            )
            user_obj.set_password('password123')
            user_obj.save()
            user_objects[u['username']] = user_obj

            UserProfile.objects.update_or_create(
                user=user_obj,
                defaults={
                    'role': u['role'],
                    'employee_id': u['emp_id'],
                    'ward_assigned': u['ward'],
                    'phone_number': '+91-9876543210'
                }
            )
            self.stdout.write(self.style.SUCCESS(f"User ready: {u['username']} (Role: {u['role']}, EmpID: {u['emp_id']})"))

        # 2. Containers Setup (24 Realistic Hospital Bins)
        containers_def = [
            {'id': 'H-014', 'name': 'Emergency Red Bin 2', 'ward': 'Emergency Ward', 'loc': 'Triage Bay 3', 'cat': WasteCategory.HAZARDOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-002', 'name': 'ICU Biohazard Container A', 'ward': 'ICU', 'loc': 'Isolation Room 102', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-008', 'name': 'Surgery Sharps Collector 1', 'ward': 'Surgery Wing', 'loc': 'Operating Theater 4', 'cat': WasteCategory.SHARPS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-019', 'name': 'Oncology Cytotoxic Station', 'ward': 'Oncology Unit', 'loc': 'Chemo Preparation Room', 'cat': WasteCategory.CYTOTOXIC, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-021', 'name': 'Ward 3 General Point B', 'ward': 'Ward 3', 'loc': 'General Corridor West', 'cat': WasteCategory.GENERAL, 'status': ContainerStatus.MAINTENANCE, 'dev': DeviceStatus.OFFLINE},
            {'id': 'H-001', 'name': 'ICU Waste Point 1', 'ward': 'ICU', 'loc': 'Bedside Station 01', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-003', 'name': 'Ward 3 Infectious Bin', 'ward': 'Ward 3', 'loc': 'Nursing Station 3', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-004', 'name': 'Emergency Yellow Bin 1', 'ward': 'Emergency Ward', 'loc': 'Trauma Care Bay 1', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-005', 'name': 'Surgery Waste Bin OT-1', 'ward': 'Surgery Wing', 'loc': 'Operating Theater 1', 'cat': WasteCategory.ANATOMICAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-006', 'name': 'Surgery Waste Bin OT-2', 'ward': 'Surgery Wing', 'loc': 'Operating Theater 2', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-007', 'name': 'ICU Bedside Bin 04', 'ward': 'ICU', 'loc': 'Ventilator Unit 4', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-009', 'name': 'Oncology Waste Bin 2', 'ward': 'Oncology Unit', 'loc': 'Infusion Bay 2', 'cat': WasteCategory.CYTOTOXIC, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-010', 'name': 'Pediatric Ward Waste', 'ward': 'Pediatric Ward', 'loc': 'Play Area Station', 'cat': WasteCategory.GENERAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-011', 'name': 'Radiology Waste Station', 'ward': 'Radiology Dept', 'loc': 'CT Control Room', 'cat': WasteCategory.GENERAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-012', 'name': 'Pathology Lab Bin A', 'ward': 'Pathology Laboratory', 'loc': 'Blood Specimen Lab', 'cat': WasteCategory.HAZARDOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-013', 'name': 'Pathology Lab Bin B', 'ward': 'Pathology Laboratory', 'loc': 'Tissue Processing Lab', 'cat': WasteCategory.ANATOMICAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-015', 'name': 'Dialysis Unit Bin 1', 'ward': 'Dialysis Unit', 'loc': 'Hemodialysis Room', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-016', 'name': 'Dialysis Unit Bin 2', 'ward': 'Dialysis Unit', 'loc': 'Dialysis Station 4', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-017', 'name': 'Isolation Ward Bin 101', 'ward': 'Isolation Unit', 'loc': 'Negative Pressure Room 1', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-018', 'name': 'Isolation Ward Bin 102', 'ward': 'Isolation Unit', 'loc': 'Negative Pressure Room 2', 'cat': WasteCategory.INFECTIOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-020', 'name': 'Maternity Ward Bin', 'ward': 'Maternity Ward', 'loc': 'Delivery Room 1', 'cat': WasteCategory.ANATOMICAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-022', 'name': 'OPD Complex Bin 1', 'ward': 'Outpatient Dept', 'loc': 'Main Waiting Hall', 'cat': WasteCategory.GENERAL, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-023', 'name': 'OPD Complex Bin 2', 'ward': 'Outpatient Dept', 'loc': 'Injection Room', 'cat': WasteCategory.SHARPS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
            {'id': 'H-024', 'name': 'Central Waste Holding A', 'ward': 'Central Biohazard Storage', 'loc': 'Basement Dock 2', 'cat': WasteCategory.HAZARDOUS, 'status': ContainerStatus.ACTIVE, 'dev': DeviceStatus.ONLINE},
        ]

        now = timezone.now()

        for cdata in containers_def:
            container, _ = Container.objects.get_or_create(
                container_id=cdata['id'],
                defaults={
                    'name': cdata['name'],
                    'ward': cdata['ward'],
                    'location': cdata['loc'],
                    'waste_category': cdata['cat'],
                    'status': cdata['status'],
                    'device_status': cdata['dev'],
                    'capacity_liters': 60.0
                }
            )

            # Assign telemetry profile based on container ID
            if cdata['id'] == 'H-014':
                # Critical/High Risk Bin: Gas anomaly + Moisture + Hazardous vision
                fill = 87.0
                weight = 24.2
                temp = 31.2
                humidity = 68.0
                gas = 420.0
                moisture = 72.0
                v_class = VisionClass.HAZARD
                v_conf = 94.0
                v_contam = 85.0
                v_unk = 3.0
                v_exc = "Abnormal gas VOC spike with chemical odor indicator"
            elif cdata['id'] == 'H-002':
                # High Risk Biohazard Bin
                fill = 91.0
                weight = 26.5
                temp = 33.5
                humidity = 62.0
                gas = 280.0
                moisture = 58.0
                v_class = VisionClass.BIOHAZARD
                v_conf = 91.0
                v_contam = 60.0
                v_unk = 4.0
                v_exc = "High-concentration infectious fluid detected"
            elif cdata['id'] == 'H-008':
                # Sharps transfer bin
                fill = 84.0
                weight = 19.8
                temp = 26.0
                humidity = 50.0
                gas = 90.0
                moisture = 20.0
                v_class = VisionClass.SHARPS
                v_conf = 88.0
                v_contam = 25.0
                v_unk = 2.0
                v_exc = "Uncapped surgical needles visual detection"
            elif cdata['id'] == 'H-019':
                # AI uncertainty bin
                fill = 45.0
                weight = 8.5
                temp = 25.0
                humidity = 48.0
                gas = 110.0
                moisture = 15.0
                v_class = VisionClass.UNKNOWN
                v_conf = 52.0
                v_contam = 40.0
                v_unk = 24.0
                v_exc = "Obscured vision sensor lens / unclassified packaging"
            elif cdata['id'] == 'H-021':
                # Offline bin
                fill = 60.0
                weight = 12.0
                temp = 24.0
                humidity = 50.0
                gas = 80.0
                moisture = 10.0
                v_class = VisionClass.NORMAL
                v_conf = 90.0
                v_contam = 0.0
                v_unk = 1.0
                v_exc = "Sensor telemetry timeout > 2 hours"
            else:
                # Normal baseline bins
                fill = random.uniform(25.0, 82.0)
                weight = round(fill * 0.25, 1)
                temp = random.uniform(23.0, 27.5)
                humidity = random.uniform(45.0, 55.0)
                gas = random.uniform(40.0, 140.0)
                moisture = random.uniform(10.0, 35.0)
                v_class = VisionClass.NORMAL
                v_conf = random.uniform(88.0, 98.0)
                v_contam = random.uniform(0.0, 10.0)
                v_unk = random.uniform(1.0, 5.0)
                v_exc = None

            # Create Sensor Reading
            reading = SensorReading.objects.create(
                container=container,
                timestamp=now,
                weight=weight,
                fill_level=fill,
                temperature=temp,
                humidity=humidity,
                gas_indicator=gas,
                moisture=moisture,
                device_status=cdata['dev']
            )

            # Create Vision Event
            vision_event = VisionEvent.objects.create(
                container=container,
                timestamp=now,
                predicted_class=v_class,
                confidence=v_conf,
                contamination_score=v_contam,
                unknown_probability=v_unk,
                exception_reason=v_exc
            )

            # Calculate Risk
            risk_dict = calculate_container_risk(container, reading, vision_event)
            risk_pred = RiskPrediction.objects.create(
                container=container,
                timestamp=now,
                risk_score=risk_dict['risk_score'],
                risk_level=risk_dict['risk_level'],
                recommended_action=risk_dict['recommended_action'],
                reason=risk_dict['reason']
            )

            # Create Action Queue Item if recommended
            if risk_dict['recommended_action'] not in ['NO ACTION']:
                prio = ActionPriority.LOW
                if risk_dict['risk_level'] == RiskLevel.CRITICAL:
                    prio = ActionPriority.CRITICAL
                elif risk_dict['risk_level'] == RiskLevel.HIGH:
                    prio = ActionPriority.HIGH
                elif risk_dict['risk_level'] == RiskLevel.MEDIUM:
                    prio = ActionPriority.MEDIUM

                Action.objects.create(
                    container=container,
                    action_type=risk_dict['recommended_action'],
                    priority=prio,
                    reason=risk_dict['reason'],
                    assigned_to=user_objects['raj_sharma'] if prio in [ActionPriority.HIGH, ActionPriority.CRITICAL] else None,
                    status=ActionStatus.PENDING
                )

            # Create Alert if High/Critical risk or gas anomaly
            if risk_dict['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL] or gas >= 350:
                sev = AlertSeverity.CRITICAL if risk_dict['risk_level'] == RiskLevel.CRITICAL else AlertSeverity.HIGH
                atype = AlertType.GAS_ANOMALY if gas >= 350 else AlertType.HIGH_RISK
                Alert.objects.create(
                    container=container,
                    severity=sev,
                    alert_type=atype,
                    message=f"Risk Alert for {container.container_id} ({container.ward}): {risk_dict['reason']}",
                    recommended_action=risk_dict['recommended_action'],
                    status=AlertStatus.NEW
                )

            # Generate historical collection records for analytics
            if random.choice([True, False]):
                CollectionRecord.objects.create(
                    container=container,
                    worker=user_objects['raj_sharma'],
                    started_at=now - timedelta(hours=random.randint(4, 48)),
                    completed_at=now - timedelta(hours=random.randint(2, 46)),
                    weight_collected=round(random.uniform(12.0, 28.0), 1),
                    fill_at_collection=round(random.uniform(80.0, 95.0), 1),
                    status=CollectionStatus.COMPLETED,
                    notes="Standard biomedical collection completed safely."
                )

        # 3. Create Key Audit Log Entries
        AuditLog.objects.create(
            user=user_objects['admin'],
            action="SYSTEM_INITIALIZED",
            entity="System",
            entity_id="GLOBAL",
            metadata={'message': 'WasteGuard Hospital System initialized successfully with demo thresholds.'}
        )
        AuditLog.objects.create(
            user=user_objects['safety_officer'],
            action="RISK_LEVEL_CHANGED",
            entity="Container",
            entity_id="H-014",
            metadata={'previous_risk': 'MEDIUM', 'new_risk': 'HIGH', 'reason': 'Abnormal gas VOC + high moisture + hazardous vision class'}
        )
        AuditLog.objects.create(
            user=user_objects['supervisor'],
            action="ACTION_RECOMMENDED",
            entity="Action",
            entity_id="ISOLATE_H014",
            metadata={'container_id': 'H-014', 'recommendation': 'ISOLATE', 'priority': 'HIGH'}
        )
        AuditLog.objects.create(
            user=user_objects['raj_sharma'],
            action="ISOLATION_CONFIRMED",
            entity="Container",
            entity_id="H-014",
            metadata={'operator': 'Raj Sharma', 'status': 'IN_PROGRESS', 'location': 'Emergency Ward Triage Bay 3'}
        )

        self.stdout.write(self.style.SUCCESS('\n======================================================='))
        self.stdout.write(self.style.SUCCESS('WasteGuard Demo Data Successfully Seeded!'))
        self.stdout.write(self.style.SUCCESS('Demo Accounts Available:'))
        self.stdout.write(self.style.SUCCESS('  1. ADMIN:          username="admin"          password="password123"'))
        self.stdout.write(self.style.SUCCESS('  2. SUPERVISOR:     username="supervisor"     password="password123"'))
        self.stdout.write(self.style.SUCCESS('  3. OPERATOR:       username="raj_sharma"     password="password123"'))
        self.stdout.write(self.style.SUCCESS('  4. SAFETY OFFICER: username="safety_officer" password="password123"'))
        self.stdout.write(self.style.SUCCESS('=======================================================\n'))
