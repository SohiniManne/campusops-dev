import React, { useState } from 'react';
import { ShieldCheck, LogIn, GraduationCap, Wrench, LayoutDashboard, AlertCircle } from 'lucide-react';
import { authService, DEMO_USERS } from '../services/auth';

export function LoginView({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Student');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFormLogin = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password) return;
    setLoading(true);
    setErrorMsg('');
    try {
      // In production, user cannot self-assign Staff or Admin: role defaults to Student
      const effectiveRole = import.meta.env.DEV ? role : 'Student';
      const user = await authService.login(email, password, effectiveRole);
      onLoginSuccess(user);
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (roleName) => {
    if (!import.meta.env.DEV) return;
    const user = authService.switchRole(roleName);
    onLoginSuccess(user);
  };

  return (
    <div style={{ minHeight: '85vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
      <div style={{ maxWidth: '440px', width: '100%', background: 'white', borderRadius: '16px', border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-flex', padding: '12px', background: '#eff6ff', borderRadius: '12px', color: '#2563eb', marginBottom: '0.75rem' }}>
            <ShieldCheck size={36} />
          </div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a' }}>CampusOps Portal</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
            Cloud-Native University Incident Management Platform
          </p>
        </div>

        {errorMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Quick Demo One-Click Access (STRICTLY visible only in local development / testing) */}
        {import.meta.env.DEV && (
          <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '10px', border: '1px solid #e2e8f0', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
              ⚡ Quick Viva Demo Access (Dev Only)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', background: 'white' }}
                onClick={() => handleQuickDemo('Student')}
              >
                <GraduationCap size={16} color="#2563eb" /> Sign in as <strong>Student</strong> (Rahul Sharma)
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', background: 'white' }}
                onClick={() => handleQuickDemo('Staff')}
              >
                <Wrench size={16} color="#d97706" /> Sign in as <strong>Staff</strong> (Ramesh Kumar)
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', background: 'white' }}
                onClick={() => handleQuickDemo('Admin')}
              >
                <LayoutDashboard size={16} color="#16a34a" /> Sign in as <strong>Admin</strong> (Dean / Ops)
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleFormLogin}>
          {import.meta.env.DEV ? (
            <div className="form-group">
              <label className="form-label">Role (Dev Simulation)</label>
              <select className="form-select" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="Student">Student</option>
                <option value="Staff">Maintenance Staff</option>
                <option value="Admin">Campus Administrator</option>
              </select>
            </div>
          ) : (
            <div className="form-group">
              <label className="form-label">Account Role</label>
              <input
                type="text"
                className="form-input"
                value="Student Account"
                disabled
                style={{ background: '#f8fafc', color: '#64748b' }}
              />
              <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                Note: Maintenance Staff and Administrator privileges are provisioned solely by college IT ops.
              </span>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">College Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="e.g. rahul@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.75rem' }}
            disabled={loading}
          >
            <LogIn size={18} /> {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
