import React, { useState } from 'react';
import { X, Send, AlertCircle, Clock } from 'lucide-react';

const CATEGORIES = [
  { value: 'ELECTRICAL', label: 'Electrical (Wiring, Lights, Switches)' },
  { value: 'PLUMBING', label: 'Plumbing (Taps, Pipes, Drains, Washrooms)' },
  { value: 'WIFI_NETWORK', label: 'Wi-Fi & Network (Router, Lab Internet)' },
  { value: 'LAB_EQUIPMENT', label: 'Lab Equipment (PC, Projector, Oscilloscope)' },
  { value: 'CLASSROOM_INFRA', label: 'Classroom Infra (Desks, Benches, AC, Fans)' },
  { value: 'OTHER', label: 'Other Campus Facilities' }
];

const PRIORITIES = [
  { value: 'CRITICAL', label: 'Critical (Safety hazard / Campus outage)', hours: '1 hour SLA' },
  { value: 'HIGH', label: 'High (Disrupts classes or lab work)', hours: '4 hours SLA' },
  { value: 'MEDIUM', label: 'Medium (Standard maintenance issue)', hours: '12 hours SLA' },
  { value: 'LOW', label: 'Low (Cosmetic / Minor fix)', hours: '24 hours SLA' }
];

export function CreateIncidentModal({ isOpen, onClose, onSubmitSuccess }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('ELECTRICAL');
  const [priority, setPriority] = useState('HIGH');
  const [location, setLocation] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (title.trim().length < 3) {
      setError('Title must be at least 3 characters long.');
      return;
    }
    if (description.trim().length < 5) {
      setError('Description must be at least 5 characters long.');
      return;
    }
    if (location.trim().length < 2) {
      setError('Location is required (e.g. Lab 204, Block B).');
      return;
    }

    try {
      setSubmitting(true);
      await onSubmitSuccess({
        title,
        description,
        category,
        priority,
        location
      });
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit incident');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Report Campus Maintenance Issue</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="error-banner" style={{ fontSize: '0.85rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={16} /> {error}
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Incident Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Broken overhead projector in Seminar Hall"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Location *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Academic Block B, Room 302"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select
                className="form-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Priority Level</label>
              <select
                className="form-select"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.value} ({p.hours})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Description of Issue *</label>
            <textarea
              className="form-textarea"
              placeholder="Describe symptoms, equipment details, or safety risks..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Submitting to AWS...' : (
                <>
                  <Send size={16} /> Submit Incident
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
