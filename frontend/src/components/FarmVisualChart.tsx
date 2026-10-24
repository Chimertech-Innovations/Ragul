import React, { useState } from 'react';
import { BarChart3, TrendingUp, PieChart, Info } from 'lucide-react';

export interface ChartDataPayload {
  type: 'bar' | 'line' | 'donut' | 'pie';
  title: string;
  labels: string[];
  values: number[];
  unit?: string;
  colors?: string[];
  subtitle?: string;
}

interface FarmVisualChartProps {
  data: ChartDataPayload;
}

const DEFAULT_PALETTE = [
  '#06b6d4', // Cyan
  '#10b981', // Emerald
  '#3b82f6', // Blue
  '#8b5cf6', // Violet
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#14b8a6', // Teal
  '#6366f1', // Indigo
];

export const FarmVisualChart: React.FC<FarmVisualChartProps> = ({ data }) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const { type = 'bar', title, labels = [], values = [], unit = 'Cattle', subtitle } = data;
  if (!labels.length || !values.length) return null;

  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values);
  const totalVal = values.reduce((acc, v) => acc + v, 0);
  const avgVal = (totalVal / values.length).toFixed(1);

  // 1. BAR CHART RENDERER
  if (type === 'bar') {
    return (
      <div className="farm-visual-chart-box">
        <div className="chart-header">
          <div className="chart-title-group">
            <div className="chart-icon-badge">
              <BarChart3 size={16} className="text-cyan-400" />
            </div>
            <div>
              <h4 className="chart-title">{title}</h4>
              <p className="chart-subtitle">{subtitle || `Tracking ${labels.length} Days • Peak: ${maxVal} ${unit}`}</p>
            </div>
          </div>
          <div className="chart-stat-chips">
            <span className="stat-chip">Avg: <strong>{avgVal}</strong></span>
            <span className="stat-chip peak">Peak: <strong>{maxVal}</strong></span>
          </div>
        </div>

        <div className="chart-bar-canvas">
          <div className="bars-container">
            {values.map((val, idx) => {
              const heightPct = Math.round((val / maxVal) * 100);
              const isHovered = hoveredIdx === idx;
              const isPeak = val === maxVal;
              const barColor = (data.colors && data.colors[idx]) || (isPeak ? '#10b981' : '#06b6d4');

              return (
                <div
                  key={idx}
                  className={`bar-column ${isHovered ? 'hovered' : ''}`}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                >
                  <div className="bar-tooltip-wrapper">
                    {isHovered && (
                      <div className="bar-tooltip">
                        <span className="tooltip-label">{labels[idx]}</span>
                        <span className="tooltip-val">{val} {unit}</span>
                      </div>
                    )}
                  </div>
                  <div className="bar-track">
                    <div
                      className={`bar-fill ${isPeak ? 'peak-fill' : ''}`}
                      style={{
                        height: `${Math.max(heightPct, 12)}%`,
                        background: isPeak
                          ? 'linear-gradient(180deg, #34d399 0%, #059669 100%)'
                          : 'linear-gradient(180deg, #38bdf8 0%, #0284c7 100%)',
                        boxShadow: isHovered
                          ? '0 0 16px rgba(56, 189, 248, 0.6)'
                          : '0 0 8px rgba(6, 182, 212, 0.25)',
                      }}
                    >
                      <span className="bar-val-badge">{val}</span>
                    </div>
                  </div>
                  <div className="bar-x-label" title={labels[idx]}>
                    {labels[idx]}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="chart-footer">
          <div className="chart-legend-item">
            <span className="legend-indicator" style={{ backgroundColor: '#06b6d4' }} />
            <span>Daily Count ({unit})</span>
          </div>
          <div className="chart-legend-item">
            <span className="legend-indicator" style={{ backgroundColor: '#10b981' }} />
            <span>Peak Detection</span>
          </div>
        </div>
      </div>
    );
  }

  // 2. DONUT / PIE CHART RENDERER (Breed / Health Breakdown)
  if (type === 'donut' || type === 'pie') {
    const size = 180;
    const strokeWidth = 28;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    let accumulatedOffset = 0;

    return (
      <div className="farm-visual-chart-box">
        <div className="chart-header">
          <div className="chart-title-group">
            <div className="chart-icon-badge">
              <PieChart size={16} className="text-emerald-400" />
            </div>
            <div>
              <h4 className="chart-title">{title}</h4>
              <p className="chart-subtitle">{subtitle || `Total Herd: ${totalVal} ${unit}`}</p>
            </div>
          </div>
          <span className="stat-chip"><strong>{labels.length} Breeds</strong></span>
        </div>

        <div className="donut-chart-layout">
          <div className="donut-svg-wrapper">
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="donut-svg">
              <circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                className="donut-bg-ring"
                strokeWidth={strokeWidth}
              />
              {values.map((val, idx) => {
                const fraction = val / totalVal;
                const strokeDasharray = `${fraction * circumference} ${circumference}`;
                const strokeDashoffset = -accumulatedOffset;
                accumulatedOffset += fraction * circumference;
                const color = DEFAULT_PALETTE[idx % DEFAULT_PALETTE.length];
                const isHovered = hoveredIdx === idx;

                return (
                  <circle
                    key={idx}
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={isHovered ? strokeWidth + 4 : strokeWidth}
                    strokeDasharray={strokeDasharray}
                    strokeDashoffset={strokeDashoffset}
                    className="donut-segment"
                    onMouseEnter={() => setHoveredIdx(idx)}
                    onMouseLeave={() => setHoveredIdx(null)}
                    style={{
                      transformOrigin: '50% 50%',
                      transform: 'rotate(-90deg)',
                      transition: 'all 0.25s ease',
                      filter: isHovered ? `drop-shadow(0 0 8px ${color})` : 'none',
                    }}
                  />
                );
              })}
            </svg>
            <div className="donut-center-label">
              <span className="donut-center-val">{hoveredIdx !== null ? values[hoveredIdx] : totalVal}</span>
              <span className="donut-center-unit">{hoveredIdx !== null ? labels[hoveredIdx] : unit}</span>
            </div>
          </div>

          <div className="donut-legend-grid">
            {labels.map((lbl, idx) => {
              const val = values[idx];
              const pct = Math.round((val / totalVal) * 100);
              const color = DEFAULT_PALETTE[idx % DEFAULT_PALETTE.length];
              const isHovered = hoveredIdx === idx;

              return (
                <div
                  key={idx}
                  className={`donut-legend-row ${isHovered ? 'active' : ''}`}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                >
                  <span className="donut-legend-dot" style={{ backgroundColor: color }} />
                  <span className="donut-legend-name">{lbl}</span>
                  <span className="donut-legend-count"><strong>{val}</strong> ({pct}%)</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // 3. LINE / TREND CHART RENDERER
  const width = 360;
  const height = 140;
  const padding = 25;
  const plotW = width - padding * 2;
  const plotH = height - padding * 2;

  const points = values.map((val, idx) => {
    const x = padding + (idx / (values.length - 1 || 1)) * plotW;
    const y = height - padding - ((val - Math.min(minVal * 0.9, 0)) / (maxVal * 1.1 - Math.min(minVal * 0.9, 0) || 1)) * plotH;
    return { x, y, val, label: labels[idx] };
  });

  const pathD = points.reduce((acc, p, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`, '');
  const areaD = `${pathD} L ${points[points.length - 1].x.toFixed(1)} ${height - padding} L ${points[0].x.toFixed(1)} ${height - padding} Z`;

  return (
    <div className="farm-visual-chart-box">
      <div className="chart-header">
        <div className="chart-title-group">
          <div className="chart-icon-badge">
            <TrendingUp size={16} className="text-cyan-400" />
          </div>
          <div>
            <h4 className="chart-title">{title}</h4>
            <p className="chart-subtitle">{subtitle || `Multi-day Trend Analysis`}</p>
          </div>
        </div>
        <div className="chart-stat-chips">
          <span className="stat-chip">Avg: <strong>{avgVal}</strong></span>
          <span className="stat-chip peak">Peak: <strong>{maxVal}</strong></span>
        </div>
      </div>

      <div className="line-chart-svg-wrap">
        <svg viewBox={`0 0 ${width} ${height}`} className="line-chart-svg">
          <defs>
            <linearGradient id="lineAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Area fill */}
          <path d={areaD} fill="url(#lineAreaGrad)" />

          {/* Line stroke */}
          <path d={pathD} fill="none" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />

          {/* Data points */}
          {points.map((p, idx) => {
            const isHovered = hoveredIdx === idx;
            return (
              <g key={idx}>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={isHovered ? 6 : 4}
                  fill={isHovered ? '#34d399' : '#06b6d4'}
                  stroke="#0f172a"
                  strokeWidth="2"
                  style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                />
                <text
                  x={p.x}
                  y={height - 8}
                  textAnchor="middle"
                  className="line-x-text"
                >
                  {p.label}
                </text>
              </g>
            );
          })}
        </svg>

        {hoveredIdx !== null && (
          <div className="line-active-tooltip">
            <strong>{labels[hoveredIdx]}</strong>: {values[hoveredIdx]} {unit}
          </div>
        )}
      </div>
    </div>
  );
};
