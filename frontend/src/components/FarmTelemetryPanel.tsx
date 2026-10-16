import React, { useEffect, useState } from 'react';
import { AlertTriangle, Flame, Droplets, Camera, Video, Sparkles, Building2, Eye } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

export const FarmTelemetryPanel: React.FC = () => {
  const { farmOverview, setFarmOverview, currentUser } = useRagulStore();
  const [recentActivities, setRecentActivities] = useState<any[]>([]);

  useEffect(() => {
    const fetchFarmOverview = async () => {
      try {
        const farmParam = currentUser?.farm_id ? `?farm_id=${currentUser.farm_id}` : '';
        const res = await fetch(`/api/farm/overview${farmParam}`);
        if (res.ok) {
          const data = await res.json();
          setFarmOverview(data);
        }

        const actRes = await fetch(`/api/farm/activities${farmParam ? `${farmParam}&limit=6` : '?limit=6'}`);
        if (actRes.ok) {
          const actData = await actRes.json();
          setRecentActivities(actData);
        }
      } catch (e) {
        console.error('Failed to fetch farm overview:', e);
      }
    };

    fetchFarmOverview();
    const interval = setInterval(fetchFarmOverview, 8000);
    return () => clearInterval(interval);
  }, [currentUser?.farm_id, setFarmOverview]);

  return (
    <aside className="sidebar-panel">
      {/* Farm Identity Header */}
      <div className="glass-card farm-identity-card">
        <div className="farm-id-row">
          <div className="farm-icon-box">
            <Building2 size={20} className="text-cyan-400" />
          </div>
          <div>
            <div className="farm-card-name">{farmOverview?.farm_name || currentUser?.farm_name || 'PashuX Dairy Farm'}</div>
            <div className="farm-card-code">
              Code: <strong>{farmOverview?.farm_code || currentUser?.farm_code || 'FARM_B01F3C'}</strong>
              {currentUser?.owner_name && ` • Owner: ${currentUser.owner_name}`}
            </div>
          </div>
          <span className="live-status-pill">LIVE AI</span>
        </div>
      </div>

      {/* Overview Stat Card */}
      <div className="glass-card">
        <div className="card-title">
          <span>Vision Telemetry</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 500 }}>
            {farmOverview?.cameras_connected ? `${farmOverview.cameras_connected} Cam Connected` : 'CAM01 Vision Stream'}
          </span>
        </div>
        <div className="stat-grid">
          <div className="stat-box">
            <div className="stat-label">Monitored Cattle</div>
            <div className="stat-value cyan">{farmOverview?.monitored_cattle_count || 3}</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">AI Detections</div>
            <div className="stat-value success">{farmOverview?.total_activities_detected || 11}</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Estrus (Heat)</div>
            <div className="stat-value warning">{farmOverview?.active_estrus_count || 5} Events</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Feeding Logs</div>
            <div className="stat-value purple">{farmOverview?.feeding_activity_count || 1} Manger</div>
          </div>
        </div>
      </div>

      {/* Estrus & Heat Alerts Card */}
      <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Flame size={16} color="var(--accent-amber)" /> Live Estrus (Heat) Alerts
          </span>
          <span className="badge-heat-live">Active</span>
        </div>

        {farmOverview?.active_estrus_alerts && farmOverview.active_estrus_alerts.length > 0 ? (
          <div className="estrus-alerts-scroll">
            {farmOverview.active_estrus_alerts.slice(0, 3).map((alert, idx) => (
              <div key={idx} className="cow-alert-card estrus-card">
                <div className="cow-alert-header">
                  <span className="cow-id-tag">🐮 {alert.cattle_id}</span>
                  <span className="badge-confidence">{alert.confidence} AI Match</span>
                </div>
                <div className="cow-alert-desc">
                  {alert.description}
                </div>
                <div className="alert-meta-footer">
                  <span>📹 {alert.camera}</span>
                  <span>⏰ {alert.time}</span>
                  <span className="breeding-tag">AI Window Active</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-alert-box">
            No active heat mounting signs detected right now. Herd behavior is calm.
          </div>
        )}

        {/* Live Camera Activity Feed */}
        <div style={{ marginTop: '16px' }}>
          <div className="card-title" style={{ marginBottom: '8px', fontSize: '0.82rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Camera size={14} /> CAM01 Camera Vision Feed
            </span>
          </div>
          <div className="activity-feed-mini">
            {recentActivities.map((act) => (
              <div key={act.activity_id} className="activity-item-card">
                <div className="activity-item-top">
                  <span className="act-type-tag">
                    {act.activity_type === 'estrus_detected' ? '🔥 Estrus' : '🌾 Feeding'}
                  </span>
                  <span className="act-cow">{act.cattle_id || 'Herd'}</span>
                  <span className="act-conf">{Math.round((act.confidence_score || 0.8) * 100)}%</span>
                </div>
                <div className="act-desc">{act.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
};
