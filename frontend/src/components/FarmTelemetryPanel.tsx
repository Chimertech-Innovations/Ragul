import React, { useEffect } from 'react';
import { AlertTriangle, Flame, Droplets, CheckSquare, Sparkles } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

export const FarmTelemetryPanel: React.FC = () => {
  const { farmOverview, setFarmOverview } = useRagulStore();

  useEffect(() => {
    const fetchFarmOverview = async () => {
      try {
        const res = await fetch('/api/farm/overview');
        if (res.ok) {
          const data = await res.json();
          setFarmOverview(data);
        }
      } catch (e) {
        console.error('Failed to fetch farm overview:', e);
      }
    };
    fetchFarmOverview();
    const interval = setInterval(fetchFarmOverview, 10000);
    return () => clearInterval(interval);
  }, [setFarmOverview]);

  return (
    <aside className="sidebar-panel">
      {/* Overview Stat Card */}
      <div className="glass-card">
        <div className="card-title">
          <span>Herd Telemetry</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 500 }}>Live Feed</span>
        </div>
        <div className="stat-grid">
          <div className="stat-box">
            <div className="stat-label">Total Cattle</div>
            <div className="stat-value cyan">{farmOverview?.total_cows || 50}</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Daily Yield</div>
            <div className="stat-value success">{farmOverview?.total_daily_yield_litres || 720.5}L</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Mastitis Risk</div>
            <div className="stat-value danger">{farmOverview?.high_risk_mastitis || 1} Cow</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">In Estrus / Heat</div>
            <div className="stat-value warning">{farmOverview?.in_estrus_cows || 1} Cow</div>
          </div>
        </div>
      </div>

      {/* Health Alerts Card */}
      <div className="glass-card" style={{ flex: 1 }}>
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={16} color="var(--accent-rose)" /> Priority Health Alerts
          </span>
        </div>

        {/* Cow 37 Mastitis Highlight */}
        <div className="cow-alert-card">
          <div className="cow-alert-header">
            <span>Cow #37 (Kamadhenu)</span>
            <span className="badge-risk">Mastitis High Risk</span>
          </div>
          <div className="cow-alert-desc">
            Milk yield down <strong>16%</strong> (13.2L vs 15.8L). Somatic cells elevated in <strong>Left Rear Quarter</strong>. Feed deficit: 2.6kg.
          </div>
        </div>

        {/* Cow 14 Estrus Highlight */}
        <div className="cow-alert-card" style={{ background: 'rgba(245, 158, 11, 0.08)', borderColor: 'rgba(245, 158, 11, 0.25)' }}>
          <div className="cow-alert-header">
            <span>Cow #14 (Lakshmi)</span>
            <span className="badge-estrus">Active Heat (AI Window)</span>
          </div>
          <div className="cow-alert-desc">
            Pedometer activity at 320%. Optimal AI breeding window is between <strong>4:00 PM - 7:00 PM today</strong>.
          </div>
        </div>

        {/* Farm Tasks */}
        <div style={{ marginTop: '16px' }}>
          <div className="stat-label" style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckSquare size={13} /> Active Clinical Tasks
          </div>
          {farmOverview?.urgent_tasks?.map((task) => (
            <div key={task.id} style={{ fontSize: '0.78rem', padding: '6px 10px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px', marginBottom: '6px', borderLeft: '3px solid var(--accent-cyan)' }}>
              {task.title}
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
