import React from 'react';
import { ShieldCheck, UserCheck, LogOut, Wrench, GraduationCap, LayoutDashboard } from 'lucide-react';
import { authService } from '../services/auth';

export function Navbar({ currentUser, onUserChange, onLogout }) {
  const handleRoleSwitch = (newRole) => {
    const updatedUser = authService.switchRole(newRole);
    onUserChange(updatedUser);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <a href="#" className="brand">
          <ShieldCheck size={28} color="#2563eb" />
          <span>CampusOps</span>
          <span className="brand-badge">AWS Cloud-Native</span>
        </a>

        <div className="nav-controls">
          {/* Viva Role Switcher: STRICTLY visible only in local development / testing, never in production */}
          {import.meta.env.DEV && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#f1f5f9', padding: '3px', borderRadius: '8px' }}>
              <button
                className={`btn btn-sm ${currentUser.role === 'Student' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ border: 'none', padding: '4px 10px' }}
                onClick={() => handleRoleSwitch('Student')}
              >
                <GraduationCap size={15} /> Student
              </button>
              <button
                className={`btn btn-sm ${currentUser.role === 'Staff' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ border: 'none', padding: '4px 10px' }}
                onClick={() => handleRoleSwitch('Staff')}
              >
                <Wrench size={15} /> Staff
              </button>
              <button
                className={`btn btn-sm ${currentUser.role === 'Admin' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ border: 'none', padding: '4px 10px' }}
                onClick={() => handleRoleSwitch('Admin')}
              >
                <LayoutDashboard size={15} /> Admin
              </button>
            </div>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <span style={{ color: '#64748b' }}>Signed in as:</span>
            <strong style={{ color: '#0f172a' }}>{currentUser.name}</strong>
          </div>

          <button className="btn btn-secondary btn-sm" onClick={onLogout} title="Log out">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </nav>
  );
}
