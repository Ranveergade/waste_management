from .models import RiskPrediction, RiskLevel
from vision.models import VisionClass

def calculate_container_risk(container, sensor_reading=None, vision_event=None):
    """
    Modular Risk Engine service.
    Evaluates:
    - Sensor readings (fill, weight, temp, humidity, gas_indicator, moisture)
    - AI vision results (classification, confidence, unknown_prob)
    - Device health
    Returns a dict with risk_score, risk_level, recommended_action, reason.
    """
    reasons = []
    score = 0

    # 1. Device Health Check
    is_offline = False
    if sensor_reading and sensor_reading.device_status == 'OFFLINE':
        is_offline = True
    elif container.device_status == 'OFFLINE':
        is_offline = True

    if is_offline:
        return {
            'risk_score': 50,
            'risk_level': RiskLevel.MEDIUM,
            'recommended_action': 'CLEAN / MAINTENANCE',
            'reason': 'Telemetry connection offline. Physical sensor inspection required.'
        }

    # 2. Gas / VOC Sensor Check
    gas_val = sensor_reading.gas_indicator if sensor_reading else 0.0
    if gas_val >= 400:
        score += 35
        reasons.append("Abnormal elevated VOC/gas indicator (>400 ppm)")
    elif gas_val >= 250:
        score += 20
        reasons.append("Elevated VOC gas readings")

    # 3. Temperature Check
    temp_val = sensor_reading.temperature if sensor_reading else 25.0
    if temp_val >= 38.0:
        score += 25
        reasons.append(f"Abnormal container temperature ({temp_val:.1f}°C)")
    elif temp_val >= 32.0:
        score += 15
        reasons.append(f"Elevated temperature ({temp_val:.1f}°C)")

    # 4. Moisture Check
    moist_val = sensor_reading.moisture if sensor_reading else 0.0
    if moist_val >= 75.0:
        score += 25
        reasons.append(f"High moisture / liquid hazard detected ({moist_val:.0f}%)")
    elif moist_val >= 55.0:
        score += 10
        reasons.append("Moderate moisture level detected")

    # 5. Fill Level Check
    fill_val = sensor_reading.fill_level if sensor_reading else 0.0
    weight_val = sensor_reading.weight if sensor_reading else 0.0
    if fill_val >= 90.0:
        score += 20
        reasons.append(f"Overfilled status ({fill_val:.0f}%, {weight_val:.1f} kg)")
    elif fill_val >= 80.0:
        score += 10
        reasons.append(f"High fill level ({fill_val:.0f}%)")

    # 6. AI Vision Classification Check
    v_class = vision_event.predicted_class if vision_event else VisionClass.NORMAL
    v_conf = vision_event.confidence if vision_event else 90.0
    v_unk = vision_event.unknown_probability if vision_event else 0.0

    if v_class in [VisionClass.HAZARD, VisionClass.BIOHAZARD]:
        if v_conf >= 80.0:
            score += 30
            reasons.append(f"AI Vision classified hazardous biomedical waste ({v_class}, {v_conf:.0f}% confidence)")
        else:
            score += 20
            reasons.append(f"Possible hazardous contents ({v_class})")
    elif v_class == VisionClass.SHARPS:
        score += 15
        reasons.append("Sharps biohazard classification detected")
    elif v_class == VisionClass.UNKNOWN or v_conf < 65.0 or v_unk > 20.0:
        score += 15
        reasons.append(f"AI Vision uncertainty ({v_conf:.0f}% confidence, {v_unk:.0f}% unknown probability)")

    # Normalize score 0 - 100
    risk_score = min(100, score)

    # Risk Level assignment
    if risk_score >= 80:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 60:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 35:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    # Recommended Action Engine logic
    if risk_level == RiskLevel.CRITICAL or (v_class == VisionClass.HAZARD and gas_val >= 350):
        recommended_action = 'ISOLATE'
    elif v_class == VisionClass.BIOHAZARD and risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        recommended_action = 'SPECIALIST REQUIRED'
    elif v_class == VisionClass.SHARPS and risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        recommended_action = 'MECHANICALLY TRANSFER'
    elif v_class == VisionClass.UNKNOWN or v_conf < 65.0 or v_unk > 20.0:
        recommended_action = 'INSPECT'
    elif fill_val >= 80.0:
        recommended_action = 'HANDLE NOW'
    elif risk_level == RiskLevel.MEDIUM:
        recommended_action = 'INSPECT'
    else:
        recommended_action = 'HANDLE LATER' if fill_val >= 50.0 else 'NO ACTION'

    if not reasons:
        reason_text = "All sensor telemetry and AI vision metrics within normal baseline operational limits."
    else:
        reason_text = " + ".join(reasons)

    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'recommended_action': recommended_action,
        'reason': reason_text
    }
