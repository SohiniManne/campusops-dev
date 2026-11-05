/**
 * CampusOps API Service Layer
 * AWS Resource: Amazon API Gateway REST Client.
 * Connects frontend React components to backend Lambdas via HTTPS REST API.
 */

import { authService } from './auth';

const API_BASE = import.meta.env.VITE_API_ENDPOINT || '';

// Seed incidents strictly for offline local development & viva test simulations
const INITIAL_INCIDENTS = [
  {
    incident_id: 'inc-20261105-a101',
    title: 'Core Wi-Fi Router Down in CS Lab 204',
    description: 'The main Cisco router in Lab 204 has no power light. Internet is down for 60 student workstations.',
    category: 'WIFI_NETWORK',
    priority: 'CRITICAL',
    location: 'Academic Block A, Lab 204',
    status: 'OPEN',
    created_by: 'usr-student-001',
    created_by_name: 'rahul.student@college.edu',
    created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    sla_hours: 1,
    sla_deadline: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
    sla_status: 'OK',
    updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
  },
  {
    incident_id: 'inc-20261105-b202',
    title: 'Sparking Circuit Breaker in Hostel 2',
    description: 'Electric sparks and burning smell observed from distribution box near room 210.',
    category: 'ELECTRICAL',
    priority: 'HIGH',
    location: 'Hostel Block 2, 2nd Floor Corridor',
    status: 'IN_PROGRESS',
    created_by: 'usr-student-001',
    created_by_name: 'rahul.student@college.edu',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    assigned_to: 'usr-staff-002',
    assigned_to_name: 'Ramesh Kumar (Maintenance Tech)',
    assigned_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    sla_hours: 4,
    sla_deadline: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
    sla_status: 'OK',
    progress_notes: 'Main power cut to wing; replacement 32A MCB fetched from inventory.',
    updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
  },
  {
    incident_id: 'inc-20261105-c303',
    title: 'Major Water Pipe Leakage in Main Cafeteria',
    description: 'Washing area drain overflow causing standing water on cafeteria dining floor.',
    category: 'PLUMBING',
    priority: 'MEDIUM',
    location: 'Student Dining Hall, Ground Floor',
    status: 'ASSIGNED',
    created_by: 'usr-student-009',
    created_by_name: 'priya.sharma@college.edu',
    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    assigned_to: 'usr-staff-002',
    assigned_to_name: 'Ramesh Kumar (Maintenance Tech)',
    assigned_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    sla_hours: 12,
    sla_deadline: new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString(),
    sla_status: 'OK',
    updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
  },
  {
    incident_id: 'inc-20261105-d404',
    title: 'Broken Desk Bench in Seminar Hall B',
    description: 'Second-row wooden bench collapsed during afternoon tutorial session.',
    category: 'FURNITURE',
    priority: 'LOW',
    location: 'Main Building, Seminar Hall B',
    status: 'RESOLVED',
    created_by: 'usr-student-001',
    created_by_name: 'rahul.student@college.edu',
    created_at: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString(),
    assigned_to: 'usr-staff-002',
    assigned_to_name: 'Ramesh Kumar (Maintenance Tech)',
    assigned_at: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(),
    sla_hours: 24,
    sla_deadline: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
    sla_status: 'OK',
    resolution_notes: 'Replaced wooden support slat and secured with 4 heavy-duty steel bolts.',
    resolved_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    resolved_by: 'ramesh.tech@college.edu',
    updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
  }
];

function getLocalIncidents() {
  try {
    const data = localStorage.getItem('campusops_incidents');
    if (data) return JSON.parse(data);
  } catch (e) {
    console.error(e);
  }
  localStorage.setItem('campusops_incidents', JSON.stringify(INITIAL_INCIDENTS));
  return INITIAL_INCIDENTS;
}

function saveLocalIncidents(incidents) {
  localStorage.setItem('campusops_incidents', JSON.stringify(incidents));
}

export const apiService = {
  /**
   * Retrieves list of incidents filtered by role.
   */
  async listIncidents(statusFilter = '') {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const url = new URL(`${API_BASE}/incidents`);
      if (statusFilter) url.searchParams.append('status', statusFilter);
      const res = await fetch(url.toString(), {
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        }
      });
      if (res.ok) {
        const json = await res.json();
        return json.incidents || [];
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to fetch incidents`);
      }
    }

    // STRICTLY Dev-only local fallback for viva simulation without cloud connection
    if (import.meta.env.DEV) {
      await new Promise((r) => setTimeout(r, 200));
      let list = getLocalIncidents();

      if (user.role === 'Student') {
        list = list.filter((item) => item.created_by === user.user_id);
      } else if (user.role === 'Staff') {
        list = list.filter((item) => item.assigned_to === user.user_id || item.assigned_to === user.email);
      }
      if (statusFilter) {
        list = list.filter((item) => item.status === statusFilter);
      }
      return list;
    }

    throw new Error('API Endpoint not configured.');
  },

  /**
   * Retrieves single incident details.
   */
  async getIncident(incidentId) {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const res = await fetch(`${API_BASE}/incidents/${incidentId}`, {
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        }
      });
      if (res.ok) {
        const json = await res.json();
        return json.incident;
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to get incident`);
      }
    }

    if (import.meta.env.DEV) {
      const list = getLocalIncidents();
      const item = list.find((i) => i.incident_id === incidentId);
      if (!item) throw new Error('Incident not found');
      return item;
    }

    throw new Error('API Endpoint not configured.');
  },

  /**
   * Creates a new incident (Students and Admins).
   */
  async createIncident({ title, description, category, priority, location }) {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const res = await fetch(`${API_BASE}/incidents`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description, category, priority, location })
      });
      if (res.ok) {
        const json = await res.json();
        return json.incident;
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to create incident`);
      }
    }

    if (import.meta.env.DEV) {
      await new Promise((r) => setTimeout(r, 300));
      const slaMap = { CRITICAL: 1, HIGH: 4, MEDIUM: 12, LOW: 24 };
      const hours = slaMap[priority] || 24;
      const now = new Date();
      const deadline = new Date(now.getTime() + hours * 60 * 60 * 1000);

      const newIncident = {
        incident_id: `inc-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`,
        title,
        description,
        category,
        priority,
        location,
        status: 'OPEN',
        created_by: user.user_id,
        created_by_name: user.email,
        created_at: now.toISOString(),
        sla_hours: hours,
        sla_deadline: deadline.toISOString(),
        sla_status: 'OK',
        updated_at: now.toISOString()
      };

      const list = getLocalIncidents();
      list.unshift(newIncident);
      saveLocalIncidents(list);
      return newIncident;
    }

    throw new Error('API Endpoint not configured.');
  },

  /**
   * Assigns maintenance staff (Admin only).
   */
  async assignStaff(incidentId, staffId, staffName) {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const res = await fetch(`${API_BASE}/incidents/${incidentId}/assign`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ assigned_to: staffId, assigned_to_name: staffName })
      });
      if (res.ok) {
        const json = await res.json();
        return json.incident;
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to assign staff`);
      }
    }

    if (import.meta.env.DEV) {
      await new Promise((r) => setTimeout(r, 200));
      const list = getLocalIncidents();
      const index = list.findIndex((i) => i.incident_id === incidentId);
      if (index === -1) throw new Error('Incident not found');

      list[index] = {
        ...list[index],
        status: 'ASSIGNED',
        assigned_to: staffId,
        assigned_to_name: staffName,
        assigned_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      saveLocalIncidents(list);
      return list[index];
    }

    throw new Error('API Endpoint not configured.');
  },

  /**
   * Updates incident status (Staff work order progress).
   */
  async updateStatus(incidentId, status, progressNotes = '') {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const res = await fetch(`${API_BASE}/incidents/${incidentId}/status`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status, progress_notes: progressNotes })
      });
      if (res.ok) {
        const json = await res.json();
        return json.incident;
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to update status`);
      }
    }

    if (import.meta.env.DEV) {
      await new Promise((r) => setTimeout(r, 200));
      const list = getLocalIncidents();
      const index = list.findIndex((i) => i.incident_id === incidentId);
      if (index === -1) throw new Error('Incident not found');

      list[index] = {
        ...list[index],
        status,
        progress_notes: progressNotes || list[index].progress_notes,
        updated_at: new Date().toISOString()
      };
      saveLocalIncidents(list);
      return list[index];
    }

    throw new Error('API Endpoint not configured.');
  },

  /**
   * Resolves incident with mandatory resolution notes.
   */
  async resolveIncident(incidentId, resolutionNotes) {
    const user = authService.getCurrentUser() || {};

    if (API_BASE) {
      const res = await fetch(`${API_BASE}/incidents/${incidentId}/resolve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${user.token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resolution_notes: resolutionNotes })
      });
      if (res.ok) {
        const json = await res.json();
        return json.incident;
      }
      if (!import.meta.env.DEV) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}: Failed to resolve incident`);
      }
    }

    if (import.meta.env.DEV) {
      await new Promise((r) => setTimeout(r, 250));
      const list = getLocalIncidents();
      const index = list.findIndex((i) => i.incident_id === incidentId);
      if (index === -1) throw new Error('Incident not found');

      list[index] = {
        ...list[index],
        status: 'RESOLVED',
        resolution_notes: resolutionNotes,
        resolved_at: new Date().toISOString(),
        resolved_by: user.email,
        updated_at: new Date().toISOString()
      };
      saveLocalIncidents(list);
      return list[index];
    }

    throw new Error('API Endpoint not configured.');
  }
};
