import React, { useState, useEffect } from 'react';
import { Wrench, CheckCircle, PlayCircle, MapPin, AlertCircle, FileText, X } from 'lucide-react';
import { apiService } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/StatusBadge';
import { SLAIndicator } from '../components/SLAIndicator';

export function StaffView() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('ALL');

  // Resolution modal state
  const [resolvingId, setResolvingId] = useState(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchAssigned = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.listIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch assigned incidents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssigned();
  }, []);

  const handleStartWork = async (id) => {
    try {
      await apiService.updateStatus(id, 'IN_PROGRESS', 'Technician started physical inspection.');
      await fetchAssigned();
    } catch (err) {
      alert(err.message || 'Failed to update status');
    }
  };

  const handleResolveSubmit = async (e) => {
    e.preventDefault();
    if (resolutionNotes.trim().length < 5) {
      alert('Please enter at least 5 characters detailing the repair done.');
      return;
    }
    try {
      setSubmitting(true);
      await apiService.resolveIncident(resolvingId, resolutionNotes.trim());
      setResolvingId(null);
      setResolutionNotes('');
      await fetchAssigned();
    } catch (err) {
      alert(err.message || 'Failed to resolve incident');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredIncidents = incidents.filter((item) => {
    if (filter === 'ALL') return true;
    return item.status === filter;
  });

  const assignedCount = incidents.filter((i) => i.status === 'ASSIGNED').length;
  const inProgressCount = incidents.filter((i) => i.status === 'IN_PROGRESS').length;
  const resolvedCount = incidents.filter((i) => i.status === 'RESOLVED').length;

  return (
    <div>
      {/* Title */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>Maintenance Staff Workbench</h1>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
          Inspect campus maintenance tasks assigned to your technician profile, update repair progress, and log resolutions.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e0e7ff', color: '#4338ca' }}>
            <Wrench size={24} />
          </div>
          <div>
            <div className="stat-val">{assignedCount}</div>
            <div className="stat-lbl">New Assignments</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7', color: '#b45309' }}>
            <PlayCircle size={24} />
          </div>
          <div>
            <div className="stat-val">{inProgressCount}</div>
            <div className="stat-lbl">Work In Progress</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dcfce7', color: '#15803d' }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <div className="stat-val">{resolvedCount}</div>
            <div className="stat-lbl">Completed Fixes</div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#334155' }}>
          Filter Work Orders:
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['ALL', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'].map((f) => (
            <button
              key={f}
              className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilter(f)}
            >
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button className="btn btn-secondary btn-sm" onClick={fetchAssigned}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="state-center">
          <div className="spinner"></div>
          <p>Loading assigned tasks from DynamoDB...</p>
        </div>
      ) : filteredIncidents.length === 0 ? (
        <div className="state-center" style={{ background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <CheckCircle size={48} color="#22c55e" style={{ marginBottom: '1rem' }} />
          <h3>No tasks in this category.</h3>
          <p style={{ marginTop: '0.5rem', color: '#64748b' }}>
            Great job! No pending repairs matching the selected filter.
          </p>
        </div>
      ) : (
        <div className="incident-grid">
          {filteredIncidents.map((incident) => (
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
                    <MapPin size={14} color="#64748b" />
                    <strong>Location:</strong>
                    <span>{incident.location}</span>
                  </div>
                  <div className="meta-row">
                    <strong>Reported by:</strong>
                    <span>{incident.created_by_name}</span>
                  </div>
                  {incident.progress_notes && (
                    <div className="meta-row" style={{ color: '#b45309' }}>
                      <strong>Latest Note:</strong>
                      <span>{incident.progress_notes}</span>
                    </div>
                  )}
                  {incident.resolution_notes && (
                    <div style={{ marginTop: '0.5rem', background: '#f0fdf4', padding: '0.5rem', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                      <strong style={{ color: '#166534', fontSize: '0.75rem' }}>Resolution:</strong>
                      <p style={{ color: '#14532d', fontSize: '0.8rem' }}>{incident.resolution_notes}</p>
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
                    Target: {incident.sla_hours}h
                  </span>
                </div>

                {/* Staff Actions */}
                <div style={{ display: 'flex', gap: '0.5rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.75rem' }}>
                  {incident.status === 'ASSIGNED' && (
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ flex: 1 }}
                      onClick={() => handleStartWork(incident.incident_id)}
                    >
                      <PlayCircle size={15} /> Start Work
                    </button>
                  )}
                  {incident.status === 'IN_PROGRESS' && (
                    <button
                      className="btn btn-success btn-sm"
                      style={{ flex: 1 }}
                      onClick={() => {
                        setResolvingId(incident.incident_id);
                        setResolutionNotes('');
                      }}
                    >
                      <CheckCircle size={15} /> Resolve Issue
                    </button>
                  )}
                  {incident.status === 'RESOLVED' && (
                    <span style={{ fontSize: '0.8rem', color: '#16a34a', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle size={14} /> Closed by {incident.resolved_by || 'Staff'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Resolution Notes Modal */}
      {resolvingId && (
        <div className="modal-overlay" onClick={() => setResolvingId(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Complete & Resolve Incident</h2>
              <button className="close-btn" onClick={() => setResolvingId(null)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleResolveSubmit}>
              <div className="form-group">
                <label className="form-label">Resolution Details *</label>
                <textarea
                  className="form-textarea"
                  placeholder="Explain exactly what maintenance or replacement was performed (e.g. Replaced capacitor, rewired socket, verified ground voltage)..."
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  required
                />
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Minimum 5 characters required for college viva audit trail.
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setResolvingId(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-success" disabled={submitting}>
                  {submitting ? 'Updating...' : (
                    <>
                      <CheckCircle size={16} /> Mark as Resolved
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
