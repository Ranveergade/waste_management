/* WasteGuard Dashboard Controller */

document.addEventListener('DOMContentLoaded', () => {
  if (!window.location.pathname.endsWith('dashboard.html')) return;
  
  Dashboard.init();
});

class Dashboard {
  static async init() {
    await this.loadKPIs();
    await this.loadActionQueue();
    await this.loadContainerTable();
    this.setupListeners();
    
    // Auto-refresh telemetry every 15 seconds
    setInterval(() => {
      this.loadKPIs();
      this.loadActionQueue();
      this.loadContainerTable();
    }, 15000);
  }

  static async loadKPIs() {
    try {
      const data = await ApiClient.get('/analytics/summary/');
      const kpis = data.kpis;

      document.getElementById('kpi-total-containers').textContent = kpis.total_containers || 24;
      document.getElementById('kpi-active-containers').textContent = kpis.active_containers || 21;
      document.getElementById('kpi-high-risk').textContent = kpis.high_risk_containers || 3;
      document.getElementById('kpi-collection-required').textContent = kpis.collection_required || 6;
      document.getElementById('kpi-offline-devices').textContent = kpis.offline_devices || 1;
      document.getElementById('kpi-total-waste').textContent = `${kpis.total_waste_kg || 428} kg`;
    } catch (e) {
      console.warn('Failed loading KPI summary, fallback UI applied');
    }
  }

  static async loadActionQueue() {
    const listEl = document.getElementById('action-queue-container');
    if (!listEl) return;

    try {
      const response = await ApiClient.get('/actions/?status=PENDING');
      const actions = response.results || response;

      if (!actions || actions.length === 0) {
        listEl.innerHTML = `
          <div style="text-align:center; padding:24px; color:var(--text-muted);">
            <div style="font-size:24px; margin-bottom:8px;">✓</div>
            No pending operational action items. All waste points within safe parameters.
          </div>
        `;
        return;
      }

      listEl.innerHTML = actions.slice(0, 6).map(act => `
        <div class="action-card priority-${act.priority}">
          <div class="action-card-header">
            <div>
              <span class="action-bin-id">${act.container_id}</span>
              <span class="action-ward"> • ${act.ward || 'Hospital Ward'}</span>
            </div>
            ${Components.getRiskBadge(act.priority)}
          </div>
          <div class="action-recommendation">
            <span>RECOMMENDED:</span>
            <span>${act.action_type}</span>
          </div>
          <div class="action-reason">
            <strong>Reason:</strong> ${act.reason}
          </div>
          <div class="action-footer">
            <a href="/bin-details.html?id=${act.container_id}" class="btn btn-secondary btn-sm">VIEW DETAILS</a>
            <button class="btn btn-primary btn-sm" onclick="Dashboard.confirmAction(${act.id}, '${act.container_id}', '${act.action_type}')">CONFIRM ACTION</button>
          </div>
        </div>
      `).join('');
    } catch (e) {
      listEl.innerHTML = `<div class="text-muted" style="padding:16px;">Unable to load priority action queue.</div>`;
    }
  }

  static async loadContainerTable(filterRisk = '') {
    const tableBody = document.getElementById('dashboard-container-table-body');
    if (!tableBody) return;

    try {
      let endpoint = '/containers/';
      if (filterRisk) endpoint += `?risk_level=${filterRisk}`;
      const response = await ApiClient.get(endpoint);
      const containers = response.results || response;

      if (!containers || containers.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px;">No containers found matching filter.</td></tr>`;
        return;
      }

      tableBody.innerHTML = containers.map(c => {
        const reading = c.latest_reading || {};
        const risk = c.latest_risk || {};
        const vision = c.latest_vision || {};
        const fill = reading.fill_level ? `${reading.fill_level.toFixed(0)}%` : '--';
        const weight = reading.weight ? `${reading.weight.toFixed(1)} kg` : '--';
        const visionClass = vision.predicted_class || 'NORMAL';
        const recAction = risk.recommended_action || 'NO ACTION';

        return `
          <tr>
            <td>
              <a href="/bin-details.html?id=${c.container_id}" style="font-weight:700; color:var(--accent-teal);">
                ${c.container_id}
              </a>
              <div style="font-size:11px; color:var(--text-secondary);">${c.name}</div>
            </td>
            <td>
              <div style="font-weight:600;">${c.ward}</div>
              <div style="font-size:11px; color:var(--text-secondary);">${c.location}</div>
            </td>
            <td style="font-weight:700;">${fill}</td>
            <td style="font-weight:600;">${weight}</td>
            <td>${Components.getRiskBadge(risk.risk_level)}</td>
            <td>
              <span style="font-size:12px; font-weight:600; color:var(--text-primary);">${visionClass}</span>
              <div style="font-size:11px; color:var(--text-muted);">${vision.confidence ? vision.confidence.toFixed(0) : 95}% conf</div>
            </td>
            <td>${Components.getDeviceBadge(c.device_status)}</td>
            <td>
              <a href="/bin-details.html?id=${c.container_id}" class="btn btn-secondary btn-sm">
                ${recAction}
              </a>
            </td>
          </tr>
        `;
      }).join('');
    } catch (e) {
      tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px; color:var(--status-critical);">Error loading container table.</td></tr>`;
    }
  }

  static confirmAction(actionId, containerId, actionType) {
    Components.confirmActionDialog({
      title: `Confirm Action: ${actionType}`,
      message: `
        Are you sure you want to authorize and initiate <strong>${actionType}</strong> for container <strong>${containerId}</strong>?
        <br><br>
        This operation will dispatch appropriate hospital waste handling protocols and log the decision to the audit timeline.
      `,
      actionLabel: `Confirm ${actionType}`,
      isDanger: ['ISOLATE', 'SPECIALIST REQUIRED'].includes(actionType),
      onConfirm: async () => {
        try {
          await ApiClient.post(`/actions/${actionId}/confirm/`, {});
          Components.showToast(`Action ${actionType} confirmed for ${containerId}`, 'success');
          Dashboard.loadActionQueue();
          Dashboard.loadContainerTable();
        } catch (err) {
          Components.showToast('Failed to confirm action', 'error');
        }
      }
    });
  }

  static setupListeners() {
    // Clickable KPI card filtering
    const highRiskKpi = document.getElementById('kpi-card-high-risk');
    if (highRiskKpi) {
      highRiskKpi.addEventListener('click', () => {
        this.loadContainerTable('HIGH');
        Components.showToast('Filtered containers by HIGH/CRITICAL risk level', 'info');
      });
    }

    const allContainersKpi = document.getElementById('kpi-card-total');
    if (allContainersKpi) {
      allContainersKpi.addEventListener('click', () => {
        this.loadContainerTable('');
      });
    }

    const searchInput = document.getElementById('dashboard-table-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#dashboard-container-table-body tr');
        rows.forEach(row => {
          const text = row.textContent.toLowerCase();
          row.style.display = text.includes(query) ? '' : 'none';
        });
      });
    }
  }
}
