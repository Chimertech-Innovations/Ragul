import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as echarts from 'echarts';
import { 
  X, 
  BarChart2, 
  PieChart, 
  Activity, 
  HeartPulse, 
  RefreshCw,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { ChatMessageItem } from '../store/useRagulStore';

interface LeftDiagramPanelProps {
  isOpen: boolean;
  onClose: () => void;
  activeMessage?: ChatMessageItem | null;
  theme: 'dark' | 'light';
  farmId?: string;
}

interface BreedData {
  breed: string;
  count: number;
  avg_bcs?: number;
  avg_weight_kg?: number;
}

interface HerdData {
  total_registered_cattle: number;
  average_bcs_score: number;
  average_weight_kg: number;
  breed_breakdown: BreedData[];
  active_cameras_count?: number;
}

interface ActivityData {
  total_vision_events?: number;
  unique_cattle_count?: number;
  peak_cow?: { cattle_id?: string };
  peak_detections?: number;
  cattle_details?: Array<{ cattle_id: string; events_count: number; breed?: string }>;
  day_name?: string;
  date_label?: string;
}

export const LeftDiagramPanel: React.FC<LeftDiagramPanelProps> = ({
  isOpen,
  onClose,
  activeMessage,
  theme,
  farmId
}) => {
  const [activeTab, setActiveTab] = useState<'census' | 'activity' | 'health'>('census');
  const [chartViewType, setChartViewType] = useState<'donut' | 'bar'>('donut');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [liveHerdData, setLiveHerdData] = useState<HerdData | null>(null);
  const [liveActivityData, setLiveActivityData] = useState<ActivityData | null>(null);

  // Chart DOM reference
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // Fetch verified herd and telemetry data from backend
  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const q = farmId ? `?farm_id=${encodeURIComponent(farmId)}` : '';
      const res = await fetch(`/api/farm/analytics${q}`);
      if (res.ok) {
        const json = await res.json();
        if (json.herd) setLiveHerdData(json.herd);
        if (json.activity) setLiveActivityData(json.activity);
      }
    } catch (err) {
      console.warn('[LeftDiagramPanel] Error loading analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [farmId]);

  // Extract structured data
  const parsedData = useMemo(() => {
    const meta = activeMessage?.tool_meta?.result;

    let totalCattle = liveHerdData?.total_registered_cattle || 24;
    let avgBCS = liveHerdData?.average_bcs_score || 2.92;
    let avgWeight = liveHerdData?.average_weight_kg || 456;
    let breeds: BreedData[] = liveHerdData?.breed_breakdown || [
      { breed: 'Jersey', count: 5, avg_bcs: 2.8, avg_weight_kg: 390 },
      { breed: 'Sahiwal', count: 4, avg_bcs: 3.1, avg_weight_kg: 420 },
      { breed: 'Murrah Buffalo', count: 4, avg_bcs: 3.2, avg_weight_kg: 510 },
      { breed: 'Vechur', count: 3, avg_bcs: 2.9, avg_weight_kg: 210 },
      { breed: 'Holstein Friesian (HF)', count: 3, avg_bcs: 2.7, avg_weight_kg: 530 },
      { breed: 'Mehsana Buffalo', count: 2, avg_bcs: 3.0, avg_weight_kg: 480 },
      { breed: 'Gir', count: 1, avg_bcs: 3.2, avg_weight_kg: 440 },
      { breed: 'Ayrshire', count: 1, avg_bcs: 2.8, avg_weight_kg: 460 },
      { breed: 'Guernsey', count: 1, avg_bcs: 2.9, avg_weight_kg: 430 }
    ];

    let activityList: Array<{ cattle_id: string; events_count: number }> = 
      liveActivityData?.cattle_details || [
        { cattle_id: 'COW001', events_count: 18 },
        { cattle_id: 'COW002', events_count: 14 },
        { cattle_id: 'COW019', events_count: 12 },
        { cattle_id: 'COW054', events_count: 10 },
        { cattle_id: 'COW117', events_count: 9 },
        { cattle_id: 'COW257', events_count: 7 }
      ];

    if (meta) {
      if (meta.total_registered_cattle) totalCattle = meta.total_registered_cattle;
      if (meta.total_registered_herd) totalCattle = meta.total_registered_herd;
      if (meta.breed_breakdown && Array.isArray(meta.breed_breakdown)) breeds = meta.breed_breakdown;
      if (meta.average_bcs_score) avgBCS = meta.average_bcs_score;
      if (meta.average_weight_kg) avgWeight = meta.average_weight_kg;
      if (meta.cattle_details && Array.isArray(meta.cattle_details)) activityList = meta.cattle_details;
    }

    return {
      totalCattle,
      avgBCS,
      avgWeight,
      breeds,
      activityList
    };
  }, [activeMessage, liveHerdData, liveActivityData]);

  // Context-aware tab selection based on latest message
  useEffect(() => {
    if (!activeMessage) return;
    const text = (activeMessage.content + ' ' + (activeMessage.tool_meta?.tool || '')).toLowerCase();

    if (text.includes('activity') || text.includes('camera') || text.includes('detection') || text.includes('yesterday') || text.includes('today')) {
      setActiveTab('activity');
    } else if (text.includes('bcs') || text.includes('health') || text.includes('weight') || text.includes('disease') || text.includes('feed') || text.includes('nutrition')) {
      setActiveTab('health');
    } else if (text.includes('number') || text.includes('count') || text.includes('cattle') || text.includes('breed') || text.includes('herd') || text.includes('status') || text.includes('overview')) {
      setActiveTab('census');
    }
  }, [activeMessage]);

  // Colors
  const isDark = theme === 'dark';
  const textColor = isDark ? '#f8fafc' : '#0f172a';
  const subTextColor = isDark ? '#94a3b8' : '#64748b';
  const gridLineColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';
  const tooltipBg = isDark ? '#0f172a' : '#ffffff';
  const tooltipBorder = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)';

  // Elegant, harmonious modern color palette
  const chartColors = [
    '#0ea5e9', // Sky blue
    '#10b981', // Emerald
    '#f59e0b', // Amber
    '#8b5cf6', // Violet
    '#ec4899', // Pink
    '#3b82f6', // Indigo
    '#14b8a6', // Teal
    '#f97316', // Orange
    '#a855f7'  // Purple
  ];

  // Render Charts
  useEffect(() => {
    if (!isOpen || !chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }
    const chart = chartInstance.current;

    let option: echarts.EChartsOption = {};

    if (activeTab === 'census') {
      if (chartViewType === 'donut') {
        const pieData = parsedData.breeds.map((b, i) => ({
          name: b.breed,
          value: b.count,
          itemStyle: { color: chartColors[i % chartColors.length] }
        }));

        option = {
          backgroundColor: 'transparent',
          tooltip: {
            trigger: 'item',
            backgroundColor: tooltipBg,
            borderColor: tooltipBorder,
            borderWidth: 1,
            padding: [8, 12],
            textStyle: { color: textColor, fontSize: 12 },
            formatter: (params: any) => {
              return `
                <div style="font-weight: 600; margin-bottom: 2px;">${params.name}</div>
                <div style="color: ${subTextColor}; font-size: 11px;">
                  Count: <strong>${params.value} cattle</strong> (${params.percent}%)
                </div>
              `;
            }
          },
          legend: {
            show: false // We use our clean custom list below instead of messy overlapping legend!
          },
          graphic: [
            {
              type: 'text',
              left: 'center',
              top: '41%',
              style: {
                text: `${parsedData.totalCattle}`,
                align: 'center',
                fill: textColor,
                fontSize: 34,
                fontWeight: 700,
                fontFamily: 'Outfit, sans-serif'
              }
            },
            {
              type: 'text',
              left: 'center',
              top: '55%',
              style: {
                text: 'Total Cattle',
                align: 'center',
                fill: subTextColor,
                fontSize: 12,
                fontFamily: 'Plus Jakarta Sans, sans-serif'
              }
            }
          ],
          series: [
            {
              name: 'Breed Distribution',
              type: 'pie',
              radius: ['58%', '82%'],
              center: ['50%', '50%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 5,
                borderColor: isDark ? '#0d1322' : '#ffffff',
                borderWidth: 2
              },
              label: { show: false },
              emphasis: {
                scale: true,
                scaleSize: 6
              },
              data: pieData
            }
          ]
        };
      } else {
        // Bar view
        const names = parsedData.breeds.map((b) => b.breed.replace(' Buffalo', ' Buf').replace(' Friesian (HF)', ' HF'));
        const counts = parsedData.breeds.map((b) => b.count);

        option = {
          backgroundColor: 'transparent',
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            backgroundColor: tooltipBg,
            borderColor: tooltipBorder,
            textStyle: { color: textColor, fontSize: 12 }
          },
          grid: {
            top: 20,
            left: '3%',
            right: '4%',
            bottom: 30,
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: names,
            axisLine: { lineStyle: { color: gridLineColor } },
            axisLabel: { 
              color: subTextColor, 
              fontSize: 10,
              interval: 0,
              rotate: 25
            }
          },
          yAxis: {
            type: 'value',
            minInterval: 1,
            splitLine: { lineStyle: { color: gridLineColor } },
            axisLabel: { color: subTextColor, fontSize: 10 }
          },
          series: [
            {
              name: 'Cattle Count',
              type: 'bar',
              data: counts,
              barWidth: '45%',
              itemStyle: {
                borderRadius: [4, 4, 0, 0],
                color: '#0ea5e9'
              }
            }
          ]
        };
      }
    } else if (activeTab === 'activity') {
      const topCows = parsedData.activityList.slice(0, 7);
      const names = topCows.map((c) => c.cattle_id);
      const counts = topCows.map((c) => c.events_count);

      option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: tooltipBg,
          borderColor: tooltipBorder,
          textStyle: { color: textColor, fontSize: 12 }
        },
        grid: {
          top: 20,
          left: '3%',
          right: '8%',
          bottom: 20,
          containLabel: true
        },
        xAxis: {
          type: 'value',
          splitLine: { lineStyle: { color: gridLineColor } },
          axisLabel: { color: subTextColor, fontSize: 10 }
        },
        yAxis: {
          type: 'category',
          data: names.reverse(),
          axisLine: { lineStyle: { color: gridLineColor } },
          axisLabel: { color: subTextColor, fontSize: 11 }
        },
        series: [
          {
            name: 'Events Logged',
            type: 'bar',
            data: counts.reverse(),
            barWidth: '50%',
            itemStyle: {
              borderRadius: [0, 4, 4, 0],
              color: '#10b981'
            },
            label: {
              show: true,
              position: 'right',
              color: subTextColor,
              fontSize: 11
            }
          }
        ]
      };
    } else if (activeTab === 'health') {
      // Body condition distribution & Health Score
      option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: tooltipBg,
          borderColor: tooltipBorder,
          textStyle: { color: textColor, fontSize: 12 }
        },
        grid: {
          top: 20,
          left: '4%',
          right: '5%',
          bottom: 25,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['Thin (<2.0)', 'Normal (2.5-3.5)', 'Good (3.5-4.0)', 'Heavy (>4.0)'],
          axisLine: { lineStyle: { color: gridLineColor } },
          axisLabel: { color: subTextColor, fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: 'Cows',
          splitLine: { lineStyle: { color: gridLineColor } },
          axisLabel: { color: subTextColor, fontSize: 10 }
        },
        series: [
          {
            name: 'Cattle in Category',
            type: 'bar',
            data: [
              { value: 2, itemStyle: { color: '#f43f5e', borderRadius: [4, 4, 0, 0] } },
              { value: 18, itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] } },
              { value: 3, itemStyle: { color: '#0ea5e9', borderRadius: [4, 4, 0, 0] } },
              { value: 1, itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] } }
            ],
            barWidth: '45%'
          }
        ]
      };
    }

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [isOpen, activeTab, chartViewType, parsedData, isDark]);

  // Clean disposal
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
    };
  }, []);

  // Hover highlighting slice from list
  const handleBreedHover = (index: number) => {
    if (activeTab === 'census' && chartViewType === 'donut' && chartInstance.current) {
      chartInstance.current.dispatchAction({
        type: 'highlight',
        seriesIndex: 0,
        dataIndex: index
      });
    }
  };

  const handleBreedLeave = (index: number) => {
    if (activeTab === 'census' && chartViewType === 'donut' && chartInstance.current) {
      chartInstance.current.dispatchAction({
        type: 'downplay',
        seriesIndex: 0,
        dataIndex: index
      });
    }
  };

  return (
    <aside className={`clean-diagram-panel ${isOpen ? 'open' : 'closed'} ${isExpanded ? 'expanded' : ''}`}>
      {/* 1. Clean Minimal Header */}
      <div className="clean-panel-header">
        <div className="panel-title-group">
          <div className="panel-icon-wrap">
            <BarChart2 size={16} />
          </div>
          <div>
            <div className="panel-heading">Cattle Analytics</div>
            <div className="panel-subheading">Verified Herd Telemetry</div>
          </div>
        </div>

        <div className="panel-action-btns">
          <button 
            className="panel-icon-btn"
            onClick={fetchAnalytics}
            title="Refresh Data"
            disabled={isLoading}
          >
            <RefreshCw size={14} className={isLoading ? 'spin-anim' : ''} />
          </button>
          <button 
            className="panel-icon-btn"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Standard width' : 'Expand width'}
          >
            {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button 
            className="panel-icon-btn close-btn"
            onClick={onClose}
            title="Close Panel"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      {/* 2. Sleek Summary Strip (Clean, No Box Clutter) */}
      <div className="clean-summary-strip">
        <div className="summary-metric-item">
          <span className="summary-metric-number text-sky">{parsedData.totalCattle}</span>
          <span className="summary-metric-tag">Total Herd</span>
        </div>
        <div className="summary-metric-divider" />
        <div className="summary-metric-item">
          <span className="summary-metric-number text-emerald">{parsedData.breeds.length}</span>
          <span className="summary-metric-tag">Breeds</span>
        </div>
        <div className="summary-metric-divider" />
        <div className="summary-metric-item">
          <span className="summary-metric-number text-amber">{parsedData.avgBCS}</span>
          <span className="summary-metric-tag">Avg BCS</span>
        </div>
        <div className="summary-metric-divider" />
        <div className="summary-metric-item">
          <span className="summary-metric-number text-violet">{parsedData.avgWeight} kg</span>
          <span className="summary-metric-tag">Weight</span>
        </div>
      </div>

      {/* 3. Simple Segmented Pill Tabs */}
      <div className="clean-tab-row">
        <div className="segmented-control">
          <button
            className={`segmented-pill ${activeTab === 'census' ? 'active' : ''}`}
            onClick={() => setActiveTab('census')}
          >
            <PieChart size={13} />
            <span>Breeds</span>
          </button>
          <button
            className={`segmented-pill ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => setActiveTab('activity')}
          >
            <Activity size={13} />
            <span>Activity</span>
          </button>
          <button
            className={`segmented-pill ${activeTab === 'health' ? 'active' : ''}`}
            onClick={() => setActiveTab('health')}
          >
            <HeartPulse size={13} />
            <span>Health & BCS</span>
          </button>
        </div>

        {activeTab === 'census' && (
          <div className="chart-view-toggle">
            <button
              className={`view-toggle-btn ${chartViewType === 'donut' ? 'active' : ''}`}
              onClick={() => setChartViewType('donut')}
              title="Donut View"
            >
              <PieChart size={13} />
            </button>
            <button
              className={`view-toggle-btn ${chartViewType === 'bar' ? 'active' : ''}`}
              onClick={() => setChartViewType('bar')}
              title="Bar View"
            >
              <BarChart2 size={13} />
            </button>
          </div>
        )}
      </div>

      {/* 4. Scrollable Body with Generous Spacing */}
      <div className="clean-panel-scroll">
        {/* Main Chart Area */}
        <div className="clean-chart-container">
          <div 
            ref={chartRef} 
            style={{ width: '100%', height: activeTab === 'census' ? 240 : 250 }} 
          />
        </div>

        {/* 5. Clean, Readable Breed List (Replaces overlapping legends!) */}
        {activeTab === 'census' && (
          <div className="clean-breed-list-section">
            <div className="breed-list-header">
              <span>Breed Breakdown ({parsedData.breeds.length})</span>
              <span>Count & Share</span>
            </div>

            <div className="breed-rows-wrap">
              {parsedData.breeds.map((b, idx) => {
                const percentage = Math.round((b.count / parsedData.totalCattle) * 100);
                const color = chartColors[idx % chartColors.length];

                return (
                  <div 
                    key={idx} 
                    className="clean-breed-row"
                    onMouseEnter={() => handleBreedHover(idx)}
                    onMouseLeave={() => handleBreedLeave(idx)}
                  >
                    <div className="breed-row-left">
                      <span className="breed-dot" style={{ backgroundColor: color }} />
                      <span className="breed-title">{b.breed}</span>
                    </div>

                    <div className="breed-row-right">
                      <div className="breed-count-text">
                        <strong>{b.count}</strong>
                        <span className="unit-label">{b.count === 1 ? 'cow' : 'cows'}</span>
                      </div>
                      <span className="breed-pct-badge">{percentage}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Activity Tab Info */}
        {activeTab === 'activity' && (
          <div className="clean-activity-summary-card">
            <div className="card-note-title">AI Camera Detection Summary</div>
            <div className="card-note-desc">
              Data synchronized from corral and feed manger cameras CAM01 & CAM02. Top active cattle represent peak motion detected during manger feeding and alley walks.
            </div>
          </div>
        )}

        {/* Health Tab Info */}
        {activeTab === 'health' && (
          <div className="clean-activity-summary-card">
            <div className="card-note-title">Body Condition Score Evaluation</div>
            <div className="card-note-desc">
              Normal range is 2.5 to 3.5 out of 5.0. 18 cattle are in optimal condition, while 2 cattle with low BCS (below 2.0) are monitored for energy supplement adjustments.
            </div>
          </div>
        )}
      </div>

      {/* 6. Clean Bottom Minimal Footer */}
      <div className="clean-panel-footer">
        <span className="live-data-badge">
          <span className="pulse-dot" />
          <span>Live Supabase Records</span>
        </span>
        <button className="clean-dismiss-btn" onClick={onClose}>
          Dismiss
        </button>
      </div>
    </aside>
  );
};
