import React, { useState, useEffect } from 'react';
import { PlusCircle, Clock, AlertCircle, MapPin, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/StatusBadge';
import { SLAIndicator } from '../components/SLAIndicator';
import { CreateIncidentModal } from '../components/CreateIncidentModal';

export function StudentView() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.listIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err.message || 'Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const handleCreateSuccess = async (formData) => {
    await apiService.createIncident(formData);
    await fetchIncidents();
  };

  // Metrics calculation
  const total = incidents.length;
  const activeCount = incidents.filter((i) => i.status !== 'RESOLVED' && i.status !== 'CLOSED').length;
  const resolvedCount = incidents.filter((i) => i.status === 'RESOLVED').length;

  return (
    <div>
      {/* Top Banner & Quick Action */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>Student Maintenance Portal</h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Report classroom, lab, or hostel infrastructure problems and monitor resolution deadlines.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <PlusCircle size={18} /> Report Maintenance Issue
        </button>
      </div>

      {/* Metrics Row */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
            <Clock size={24} />
          </div>
          <div>
            <div className="stat-val">{activeCount}</div>
            <div className="stat-lbl">Active Tickets</div>
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

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#f1f5f9', color: '#475569' }}>
            <AlertCircle size={24} />
          </div>
          <div>
            <div className="stat-val">{total}</div>
            <div className="stat-lbl">Total Reported</div>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button className="btn btn-secondary btn-sm" onClick={fetchIncidents}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="state-center">
          <div className="spinner"></div>
          <p>Querying DynamoDB for your tickets...</p>
        </div>
      ) : incidents.length === 0 ? (
        <div className="state-center" style={{ background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <CheckCircle2 size={48} color="#22c55e" style={{ marginBottom: '1rem' }} />
          <h3>All clear! No active complaints.</h3>
          <p style={{ marginTop: '0.5rem', marginBottom: '1.5rem' }}>
            Notice any faulty equipment, flickering lights, or broken plumbing on campus?
          </p>
          <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
            <PlusCircle size={16} /> Submit Your First Incident
          </button>
        </div>
      ) : (
        <div className="incident-grid">
          {incidents.map((incident) => (
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
                    <span>{incident.location}</span>
                  </div>
                  <div className="meta-row">
                    <span style={{ fontWeight: 600 }}>Category:</span>
                    <span>{incident.category}</span>
                  </div>
                  {incident.assigned_to_name && (
                    <div className="meta-row">
                      <span style={{ fontWeight: 600 }}>Technician:</span>
                      <span>{incident.assigned_to_name}</span>
                    </div>
                  )}
                  {incident.resolution_notes && (
                    <div style={{ marginTop: '0.5rem', background: '#f0fdf4', padding: '0.5rem', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                      <strong style={{ color: '#166534', fontSize: '0.75rem' }}>Resolution Notes:</strong>
                      <p style={{ color: '#14532d', fontSize: '0.8rem', marginTop: '2px' }}>{incident.resolution_notes}</p>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <SLAIndicator
                    deadline={incident.sla_deadline}
                    status={incident.status}
                    slaStatus={incident.sla_status}
                  />
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    {new Date(incident.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <CreateIncidentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmitSuccess={handleCreateSuccess}
      />
    </div>
  );
}
