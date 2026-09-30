import React, { useState, useEffect } from 'react';

interface Metric {
  id: string;
  label: string;
  value: string | number;
  status: 'healthy' | 'warning' | 'critical';
}

export const DashboardWidget: React.FC = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMetrics([
        { id: 'm1', label: 'API Latency', value: '42ms', status: 'healthy' },
        { id: 'm2', label: 'Memory Usage', value: '78%', status: 'warning' },
        { id: 'm3', label: 'Active Sessions', value: 1420, status: 'healthy' },
        { id: 'm4', label: 'Error Rate', value: '0.02%', status: 'healthy' },
      ]);
      setLoading(false);
    }, 600);

    return () => clearTimeout(timer);
  }, []);

  const getStatusColor = (status: Metric['status']) => {
    switch (status) {
      case 'healthy': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Loading Telemetry Dashboard...</div>;
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '20px auto',
      padding: '24px',
      borderRadius: '12px',
      backgroundColor: '#1E293B',
      color: '#F8FAFC',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h2 style={{ marginTop: 0, borderBottom: '1px solid #334155' }}>
        System Telemetry
      </h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '16px',
        marginTop: '16px'
      }}>
        {metrics.map((m) => (
          <div key={m.id} style={{
            backgroundColor: '#0F172A',
            padding: '16px',
            borderRadius: '8px',
            borderLeft: `4px solid ${getStatusColor(m.status)}`
          }}>
            <div style={{ fontSize: '12px', color: '#94A3B8' }}>{m.label}</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>{m.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DashboardWidget;
