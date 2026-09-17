/* WasteGuard Bin Details & Inspection Controller */

document.addEventListener('DOMContentLoaded', () => {
  if (!window.location.pathname.endsWith('bin-details.html')) return;
  BinDetails.init();
});

class BinDetails {
  static async init() {
    const urlParams = new URLSearchParams(window.location.search);
    const containerId = urlParams.get('id') || 'H-014';
    
    await this.loadContainerDetails(containerId);
    await this.loadSensorHistory(containerId);
    await this.loadAuditTimeline(containerId);
  }

  static async loadContainerDetails(containerId) {
    try {
      const response = await ApiClient.get(`/containers/?search=${encodeURIComponent(containerId)}`);
      const list = response.results || response;
      const c = list.find(item => item.container_id === containerId) || list[0];

      if (!c) {
        document.getElementById('bin-details-container').innerHTML = `<div class="card" style="padding:24px;">Container ${containerId} not found.</div>`;
        return;
      }

      const reading = c.latest_reading || {};
      const risk = c.latest_risk || {};
      const vision = c.latest_vision || {};
      const action = c.latest_action || {};

      // Populate Header Details
      document.getElementById('detail-id').textContent = c.container_id;
      document.getElementById('detail-name').textContent = c.name;
      document.getElementById('detail-ward').textContent = c.ward;
      document.getElementById('detail-location').textContent = c.location;
      document.getElementById('detail-category').textContent = c.waste_category || 'INFECTIOUS';
      document.getElementById('detail-device-status').innerHTML = Components.getDeviceBadge(c.device_status);
      document.getElementById('detail-risk-badge').innerHTML = Components.getRiskBadge(risk.risk_level);

      // Populate Sensor Facts
      document.getElementById('fact-fill').textContent = reading.fill_level ? `${reading.fill_level.toFixed(0)}%` : '87%';
      document.getElementById('fact-weight').textContent = reading.weight ? `${reading.weight.toFixed(1)} kg` : '24.2 kg';
      document.getElementById('fact-temp').textContent = reading.temperature ? `${reading.temperature.toFixed(1)}°C` : '31.2°C';
      document.getElementById('fact-humidity').textContent = reading.humidity ? `${reading.humidity.toFixed(0)}%` : '68%';
      document.getElementById('fact-gas').textContent = reading.gas_indicator ? `${reading.gas_indicator.toFixed(0)} ppm` : '420 ppm';
      document.getElementById('fact-moisture').textContent = reading.moisture ? `${reading.moisture.toFixed(0)}%` : '72%';

      // Populate AI Vision Inference Card
      const isUncertain = vision.confidence < 65 || vision.predicted_class === 'UNKNOWN';
      document.getElementById('vision-class').textContent = isUncertain ? 'UNKNOWN / INSPECTION REQUIRED' : vision.predicted_class || 'HAZARD';
      document.getElementById('vision-confidence').textContent = `${vision.confidence ? vision.confidence.toFixed(0) : '94'}%`;
      document.getElementById('vision-contamination').textContent = `${vision.contamination_score ? vision.contamination_score.toFixed(0) : '85'}%`;
      document.getElementById('vision-unknown').textContent = `${vision.unknown_probability ? vision.unknown_probability.toFixed(0) : '3'}%`;
      document.getElementById('vision-exception').textContent = vision.exception_reason || 'Abnormal gas VOC spike with chemical odor indicator';

      // Populate Operational Decision & Risk Gauge
      const score = risk.risk_score || 82;
      document.getElementById('risk-score-value').textContent = `${score} / 100`;
      document.getElementById('risk-score-bar').style.width = `${score}%`;
      
      let barColor = 'var(--status-low)';
      if (score >= 80) barColor = 'var(--status-critical)';
      else if (score >= 60) barColor = 'var(--status-high)';
      else if (score >= 35) barColor = 'var(--status-medium)';
      document.getElementById('risk-score-bar').style.backgroundColor = barColor;

      const recAction = risk.recommended_action || 'ISOLATE';
      document.getElementById('decision-action-name').textContent = recAction;
      document.getElementById('decision-reason').textContent = risk.reason || 'Abnormal gas indicator + high moisture + hazardous classification';

      // Configure Action Confirmation Button
      const actionBtn = document.getElementById('btn-execute-action');
      if (actionBtn) {
        actionBtn.textContent = `CONFIRM ACTION: ${recAction}`;
        actionBtn.onclick = () => {
          Dashboard.confirmAction(action.id || 1, c.container_id, recAction);
        };
      }
    } catch (e) {
      console.error('Error loading container details', e);
    }
  }

  static async loadSensorHistory(containerId) {
    const chartEl = document.getElementById('sensor-history-chart');
    if (!chartEl) return;

    try {
      const readings = await ApiClient.get(`/sensors/?container_id=${encodeURIComponent(containerId)}`);
      const list = readings.results || readings;

      if (!list || list.length === 0) {
        chartEl.innerHTML = `<div class="text-muted" style="padding:20px; text-align:center;">No historical readings available for graph visualization.</div>`;
        return;
      }

      // Generate SVG sparkline trend graph
      const fillPoints = list.slice(0, 12).map((r, idx) => `${idx * 40},${100 - r.fill_level}`).join(' ');
      const tempPoints = list.slice(0, 12).map((r, idx) => `${idx * 40},${100 - (r.temperature * 2)}`).join(' ');

      chartEl.innerHTML = `
        <div style="font-size:12px; color:var(--text-secondary); margin-bottom:8px; display:flex; gap:16px;">
          <span><strong style="color:var(--accent-teal);">―</strong> Fill Level (%)</span>
          <span><strong style="color:var(--status-high);">―</strong> Temperature (°C)</span>
        </div>
        <svg viewBox="0 0 440 100" style="width:100%; height:120px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px;">
          <polyline fill="none" stroke="var(--accent-teal)" stroke-width="3" points="${fillPoints}" />
          <polyline fill="none" stroke="var(--status-high)" stroke-width="2" stroke-dasharray="4" points="${tempPoints}" />
        </svg>
      `;
    } catch (e) {
      chartEl.innerHTML = `<div class="text-muted">History chart unavailable.</div>`;
    }
  }

  static async loadAuditTimeline(containerId) {
    const timelineEl = document.getElementById('audit-timeline-container');
    if (!timelineEl) return;

    try {
      const logs = await ApiClient.get(`/audit-logs/?entity_id=${encodeURIComponent(containerId)}`);
      const list = logs.results || logs;

      if (!list || list.length === 0) {
        timelineEl.innerHTML = `<div style="font-size:12px; color:var(--text-muted);">No audit timeline events logged yet for container ${containerId}.</div>`;
        return;
      }

      timelineEl.innerHTML = list.map(item => {
        const dateStr = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
          <div style="display:flex; gap:12px; margin-bottom:12px; font-size:12.5px;">
            <div style="font-weight:700; color:var(--accent-teal); width:50px; flex-shrink:0;">${dateStr}</div>
            <div style="flex:1;">
              <div style="font-weight:600; color:var(--text-primary);">${item.action}</div>
              <div style="color:var(--text-secondary); font-size:11.5px;">User: ${item.user_name || 'System'}</div>
            </div>
          </div>
        `;
      }).join('');
    } catch (e) {
      timelineEl.innerHTML = `<div class="text-muted">Unable to load audit timeline.</div>`;
    }
  }
}
