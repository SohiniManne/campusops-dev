import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';

export function SLAIndicator({ deadline, status, slaStatus }) {
  const [timeLeft, setTimeLeft] = useState('');
  const [isOverdue, setIsOverdue] = useState(false);
  const [isNearWarning, setIsNearWarning] = useState(false);

  useEffect(() => {
    if (status === 'RESOLVED' || status === 'CLOSED') {
      return;
    }

    function calculateTime() {
      if (!deadline) {
        setTimeLeft('No SLA');
        return;
      }

      const diff = new Date(deadline).getTime() - Date.now();
      if (diff <= 0 || slaStatus === 'BREACHED') {
        setIsOverdue(true);
        const overdueMins = Math.abs(Math.floor(diff / (1000 * 60)));
        const hours = Math.floor(overdueMins / 60);
        const mins = overdueMins % 60;
        setTimeLeft(`Overdue by ${hours > 0 ? `${hours}h ` : ''}${mins}m`);
        return;
      }

      setIsOverdue(false);
      const totalMins = Math.floor(diff / (1000 * 60));
      const hours = Math.floor(totalMins / 60);
      const mins = totalMins % 60;

      if (totalMins < 60) {
        setIsNearWarning(true);
      } else {
        setIsNearWarning(false);
      }

      setTimeLeft(`${hours > 0 ? `${hours}h ` : ''}${mins}m left`);
    }

    calculateTime();
    const interval = setInterval(calculateTime, 30000);
    return () => clearInterval(interval);
  }, [deadline, status, slaStatus]);

  if (status === 'RESOLVED' || status === 'CLOSED') {
    return (
      <span className="sla-pill sla-ok">
        <CheckCircle size={14} /> Resolved
      </span>
    );
  }

  if (isOverdue) {
    return (
      <span className="sla-pill sla-breached">
        <AlertTriangle size={14} /> {timeLeft}
      </span>
    );
  }

  if (isNearWarning) {
    return (
      <span className="sla-pill sla-warning">
        <Clock size={14} /> {timeLeft}
      </span>
    );
  }

  return (
    <span className="sla-pill sla-ok">
      <Clock size={14} /> {timeLeft}
    </span>
  );
}
