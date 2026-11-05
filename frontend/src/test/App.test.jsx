import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { App } from '../App';
import { StatusBadge, PriorityBadge } from '../components/StatusBadge';
import { SLAIndicator } from '../components/SLAIndicator';
import { authService, DEMO_USERS } from '../services/auth';

describe('CampusOps Frontend Component Suite', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders application header and branding', () => {
    render(<App />);
    const brandElements = screen.getAllByText('CampusOps');
    expect(brandElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('AWS Cloud-Native')).toBeInTheDocument();
  });

  it('renders student dashboard with maintenance options by default', () => {
    authService.switchRole('Student');
    render(<App />);
    expect(screen.getByText('Student Maintenance Portal')).toBeInTheDocument();
    expect(screen.getByText('Report Maintenance Issue')).toBeInTheDocument();
  });

  it('renders status badges with appropriate classes', () => {
    const { container: openBadge } = render(<StatusBadge status="OPEN" />);
    expect(openBadge.textContent).toContain('Open');

    const { container: inProgressBadge } = render(<StatusBadge status="IN_PROGRESS" />);
    expect(inProgressBadge.textContent).toContain('In Progress');

    const { container: resolvedBadge } = render(<StatusBadge status="RESOLVED" />);
    expect(resolvedBadge.textContent).toContain('Resolved');
  });

  it('renders priority badges with appropriate text', () => {
    render(<PriorityBadge priority="CRITICAL" />);
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();

    render(<PriorityBadge priority="HIGH" />);
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('displays resolved state in SLAIndicator for completed issues', () => {
    render(
      <SLAIndicator
        deadline={new Date(Date.now() - 3600000).toISOString()}
        status="RESOLVED"
        slaStatus="OK"
      />
    );
    expect(screen.getByText('Resolved')).toBeInTheDocument();
  });

  it('renders staff workbench when role is switched to Staff', () => {
    authService.switchRole('Staff');
    render(<App />);
    expect(screen.getByText('Maintenance Staff Workbench')).toBeInTheDocument();
    expect(screen.getByText('Filter Work Orders:')).toBeInTheDocument();
  });

  it('renders admin control room when role is switched to Admin', () => {
    authService.switchRole('Admin');
    render(<App />);
    expect(screen.getByText('Campus Operations Control Room')).toBeInTheDocument();
    expect(screen.getByText('Total Incidents')).toBeInTheDocument();
    expect(screen.getByText('SLA Breaches')).toBeInTheDocument();
  });
});
