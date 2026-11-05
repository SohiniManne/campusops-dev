import React from 'react';

export function StatusBadge({ status }) {
  const normalized = (status || 'OPEN').toUpperCase();
  const classMap = {
    OPEN: 'badge badge-open',
    ASSIGNED: 'badge badge-assigned',
    IN_PROGRESS: 'badge badge-in_progress',
    RESOLVED: 'badge badge-resolved',
    CLOSED: 'badge badge-closed'
  };

  const labelMap = {
    OPEN: 'Open',
    ASSIGNED: 'Assigned',
    IN_PROGRESS: 'In Progress',
    RESOLVED: 'Resolved',
    CLOSED: 'Closed'
  };

  return (
    <span className={classMap[normalized] || 'badge badge-open'}>
      {labelMap[normalized] || normalized}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const normalized = (priority || 'LOW').toUpperCase();
  const classMap = {
    CRITICAL: 'badge priority-critical',
    HIGH: 'badge priority-high',
    MEDIUM: 'badge priority-medium',
    LOW: 'badge priority-low'
  };

  return (
    <span className={classMap[normalized] || 'badge priority-low'}>
      {normalized}
    </span>
  );
}
