import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Users,
  AlertTriangle,
  Clock,
  CheckCircle2,
  UserPlus,
  X,
  Filter,
  Check
} from 'lucide-react';
import { apiService } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/StatusBadge';
import { SLAIndicator } from '../components/SLAIndicator';

const TECHNICIANS = [
  { id: 'usr-staff-002', name: 'Ramesh Kumar', trade: 'Senior Electrician' },
  { id: 'usr-staff-003', name: 'Suresh Patel', trade: 'Master Plumber' },
  { id: 'usr-staff-004', name: 'Priya Sharma', trade: 'IT & Network Engineer' },
  { id: 'usr-staff-005', name: 'Abdul Khan', trade: 'HVAC & AC Technician' },
  { id: 'usr-staff-006', name: 'Vikram Singh', trade: 'Classroom Infrastructure Carpenter' }
];

export function AdminView() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Assignment Modal
  const [assigningIncident, setAssigningIncident] = useState(null);
  const [selectedTech, setSelectedTech] = useState(TECHNICIANS[0].id);
  const [submitting, setSubmitting] = useState(false);

  const fetchAll = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.listIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err.message || 'Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    const tech = TECHNICIANS.find((t) => t.id === selectedTech);
    if (!tech || !assigningIncident) return;

    try {
      setSubmitting(true);
      await apiService.assignStaff(
        assigningIncident.incident_id,
        tech.id,
        `${tech.name} (${tech.trade})`
      );
      setAssigningIncident(null);
      await fetchAll();
    } catch (err) {
      alert(err.message || 'Failed to assign technician');
    } finally {
      setSubmitting(false);
    }
  };

  // KPI Metrics
  const total = incidents.length;
  const openCount = incidents.filter((i) => i.status === 'OPEN').length;
  const inProgressCount = incidents.filter((i) => i.status === 'IN_PROGRESS' || i.status === 'ASSIGNED').length;
  const resolvedCount = incidents.filter((i) => i.status === 'RESOLVED').length;
  
  // Breached count: unresolved tickets past deadline
  const overdueCount = incidents.filter((i) => {
    if (i.status === 'RESOLVED' || i.status === 'CLOSED') return false;
    return new Date(i.sla_deadline).getTime() < Date.now() || i.sla_status === 'BREACHED';
  }).length;

  const filteredList = incidents.filter((item) => {
    if (statusFilter === 'ALL') return true;
    if (statusFilter === 'BREACHED') {
      return (
        item.status !== 'RESOLVED' &&
        item.status !== 'CLOSED' &&
        new Date(item.sla_deadline).getTime() < Date.now()
      );
    }
    return item.status === statusFilter;
  });

  return (
    <div>
      {/* Title */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>Campus Operations Control Room</h1>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
          Centralized administrative oversight across all campus departments, staff allocations, and automated SLA compliance.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#f1f5f9', color: '#0f172a' }}>
            <Users size={24} />
          </div>
          <div>
            <div className="stat-val">{total}</div>
            <div className="stat-lbl">Total Incidents</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
            <Clock size={24} />
          </div>
          <div>
            <div className="stat-val">{openCount}</div>
            <div className="stat-lbl">Unassigned / Open</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7', color: '#b45309' }}>
            <Clock size={24} />
          </div>
          <div>
            <div className="stat-val">{inProgressCount}</div>
            <div className="stat-lbl">Active In Progress</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dcfce7', color: '#15803d' }}>
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div className="stat-val">{resolvedCount}</div>
            <div className="stat-lbl">Resolved Issues</div>
          </div>
        </div>

        <div className="stat-card" style={{ borderColor: overdueCount > 0 ? '#fca5a5' : '#e2e8f0', background: overdueCount > 0 ? '#fff5f5' : 'white' }}>
          <div className="stat-icon" style={{ background: '#fee2e2', color: '#dc2626' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div className="stat-val" style={{ color: overdueCount > 0 ? '#dc2626' : 'inherit' }}>
              {overdueCount}
            </div>
            <div className="stat-lbl" style={{ color: overdueCount > 0 ? '#dc2626' : 'inherit' }}>
              SLA Breaches
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} color="#64748b" />
          <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>View:</span>
          {['ALL', 'OPEN', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'BREACHED'].map((st) => (
            <button
              key={st}
              className={`btn btn-sm ${statusFilter === st ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter(st)}
            >
              {st === 'BREACHED' ? '⚠️ Overdue' : st.replace('_', ' ')}
            </button>
          ))}
        </div>
        <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
          Showing {filteredList.length} tickets
        </span>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button className="btn btn-secondary btn-sm" onClick={fetchAll}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="state-center">
          <div className="spinner"></div>
          <p>Querying API Gateway for campus maintenance records...</p>
        </div>
      ) : filteredList.length === 0 ? (
        <div className="state-center" style={{ background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <CheckCircle2 size={48} color="#22c55e" style={{ marginBottom: '1rem' }} />
          <h3>No incidents found for this filter.</h3>
        </div>
      ) : (
        <div className="incident-grid">
          {filteredList.map((incident) => (
            <div key={incident.incident_id} className="incident-card">
              <div>
                <div className="incident-header">
                  <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#64748b' }}>
                    {incident.incident_id}
                  </span>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <PriorityBadge priority={incident.priority} />
                    <StatusBadge status={incident.status} />
                  </div>
                </div>

                <h3 className="incident-title">{incident.title}</h3>
                <p className="incident-desc">{incident.description}</p>
              </div>

              <div>
                <div className="incident-meta">
                  <div className="meta-row">
                    <strong>Location:</strong>
                    <span>{incident.location}</span>
                  </div>
                  <div className="meta-row">
                    <strong>Category:</strong>
                    <span>{incident.category}</span>
                  </div>
                  <div className="meta-row">
                    <strong>Reported by:</strong>
                    <span>{incident.created_by_name}</span>
                  </div>
                  <div className="meta-row">
                    <strong>Assigned to:</strong>
                    <span>{incident.assigned_to_name || 'Unassigned'}</span>
                  </div>
                  {incident.resolution_notes && (
                    <div style={{ marginTop: '0.5rem', background: '#f0fdf4', padding: '0.5rem', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                      <strong style={{ color: '#166534', fontSize: '0.75rem' }}>Resolution:</strong>
                      <p style={{ color: '#14532d', fontSize: '0.8rem', marginTop: '2px' }}>{incident.resolution_notes}</p>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <SLAIndicator
                    deadline={incident.sla_deadline}
                    status={incident.status}
                    slaStatus={incident.sla_status}
                  />
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    SLA: {incident.sla_hours}h
                  </span>
                </div>

                {/* Admin Actions */}
                <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '0.75rem' }}>
                  {incident.status === 'OPEN' ? (
                    <button
                      className="btn btn-primary btn-sm"
                      style={{ width: '100%' }}
                      onClick={() => {
                        setAssigningIncident(incident);
                        setSelectedTech(TECHNICIANS[0].id);
                      }}
                    >
                      <UserPlus size={15} /> Assign Maintenance Staff
                    </button>
                  ) : (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                      <span style={{ color: '#64748b' }}>Assigned: {incident.assigned_to_name}</span>
                      {incident.status !== 'RESOLVED' && (
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                          onClick={() => {
                            setAssigningIncident(incident);
                            setSelectedTech(TECHNICIANS[0].id);
                          }}
                        >
                          Reassign
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Staff Assignment Modal */}
      {assigningIncident && (
        <div className="modal-overlay" onClick={() => setAssigningIncident(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Assign Maintenance Technician</h2>
              <button className="close-btn" onClick={() => setAssigningIncident(null)}>
                <X size={20} />
              </button>
            </div>

            <div style={{ marginBottom: '1.25rem', background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Incident:</div>
              <div style={{ fontWeight: 600, color: '#0f172a' }}>{assigningIncident.title}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>
                📍 {assigningIncident.location} | Category: {assigningIncident.category}
              </div>
            </div>

            <form onSubmit={handleAssignSubmit}>
              <div className="form-group">
                <label className="form-label">Select Campus Technician *</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {TECHNICIANS.map((tech) => (
                    <label
                      key={tech.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '0.65rem 0.85rem',
                        border: selectedTech === tech.id ? '2px solid #2563eb' : '1px solid #cbd5e1',
                        background: selectedTech === tech.id ? '#eff6ff' : 'white',
                        borderRadius: '8px',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <input
                          type="radio"
                          name="technician"
                          value={tech.id}
                          checked={selectedTech === tech.id}
                          onChange={() => setSelectedTech(tech.id)}
                        />
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{tech.name}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{tech.trade}</div>
                        </div>
                      </div>
                      {selectedTech === tech.id && <Check size={18} color="#2563eb" />}
                    </label>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setAssigningIncident(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? 'Assigning...' : (
                    <>
                      <UserPlus size={16} /> Confirm Assignment
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
