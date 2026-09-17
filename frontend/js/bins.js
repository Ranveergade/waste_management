/* WasteGuard Bins List Controller */

document.addEventListener('DOMContentLoaded', () => {
  if (!window.location.pathname.endsWith('bins.html')) return;
  BinsManager.init();
});

class BinsManager {
  static async init() {
    await this.loadContainers();
    this.setupFilters();
  }

  static async loadContainers() {
    const tableBody = document.getElementById('bins-table-body');
    if (!tableBody) return;

    try {
      const ward = document.getElementById('filter-ward')?.value || '';
      const status = document.getElementById('filter-status')?.value || '';
      const risk = document.getElementById('filter-risk')?.value || '';
      const search = document.getElementById('filter-search')?.value || '';

      let url = '/containers/?';
      if (ward) url += `ward=${encodeURIComponent(ward)}&`;
      if (status) url += `status=${encodeURIComponent(status)}&`;
      if (risk) url += `risk_level=${encodeURIComponent(risk)}&`;
      if (search) url += `search=${encodeURIComponent(search)}&`;

      const response = await ApiClient.get(url);
      const containers = response.results || response;

      if (!containers || containers.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:24px;">No hospital waste containers found matching search criteria.</td></tr>`;
        return;
      }

      tableBody.innerHTML = containers.map(c => {
        const reading = c.latest_reading || {};
        const risk = c.latest_risk || {};
        const vision = c.latest_vision || {};

        return `
          <tr>
            <td>
              <a href="/bin-details.html?id=${c.container_id}" style="font-weight:700; color:var(--accent-teal);">
                ${c.container_id}
              </a>
            </td>
            <td>
              <div style="font-weight:600;">${c.name}</div>
              <div style="font-size:11px; color:var(--text-secondary);">${c.hospital}</div>
            </td>
            <td>${c.ward}</td>
            <td>${c.location}</td>
            <td style="font-weight:700;">${reading.fill_level ? reading.fill_level.toFixed(0) + '%' : '--'}</td>
            <td style="font-weight:600;">${reading.weight ? reading.weight.toFixed(1) + ' kg' : '--'}</td>
            <td>${Components.getRiskBadge(risk.risk_level)}</td>
            <td>${Components.getDeviceBadge(c.device_status)}</td>
            <td>
              <a href="/bin-details.html?id=${c.container_id}" class="btn btn-secondary btn-sm">Inspect</a>
            </td>
          </tr>
        `;
      }).join('');
    } catch (e) {
      tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:20px; color:var(--status-critical);">Error loading container registry.</td></tr>`;
    }
  }

  static setupFilters() {
    ['filter-ward', 'filter-status', 'filter-risk'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', () => this.loadContainers());
    });

    const searchInput = document.getElementById('filter-search');
    if (searchInput) {
      searchInput.addEventListener('input', () => this.loadContainers());
    }
  }
}
