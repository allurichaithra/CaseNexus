import { useEffect, useMemo, useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts';
import { getEvaluation, getTrends } from '../services/api';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid rgba(0,0,0,0.1)',
      borderRadius: 10,
      padding: '10px 14px',
      fontSize: '0.82rem',
      boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
    }}>
      <div style={{ color: '#64748b', marginBottom: 4 }}>{label}</div>
      <div style={{ color: '#0f172a', fontWeight: 700 }}>{payload[0].value.toLocaleString()}</div>
    </div>
  );
}

function SkeletonTrends() {
  return (
    <div className="grid">
      {[0, 1].map((i) => (
        <div key={i} className="skeleton-card" style={{ minHeight: 320 }}>
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          <div className="skeleton" style={{ height: 250, borderRadius: 8 }} />
        </div>
      ))}
      <div className="skeleton-card">
        <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 44, borderRadius: 10, marginBottom: 8 }} />
        ))}
      </div>
    </div>
  );
}

export default function TrendsPage() {
  const [trends, setTrends] = useState({ daily: {}, monthly: {} });
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getTrends(), getEvaluation()])
      .then((results) => {
        const trendData = results[0].status === 'fulfilled' ? results[0].value : { daily: {}, monthly: {} };
        const evaluationData = results[1].status === 'fulfilled' ? results[1].value : null;
        setTrends(trendData);
        setEvaluation(evaluationData);
      })
      .finally(() => setLoading(false));
  }, []);

  const monthlySeries = useMemo(() => {
    const source = trends?.monthly && typeof trends.monthly === 'object' ? trends.monthly : {};
    return Object.entries(source)
      .map(([month, value]) => ({ month, value: Number(value) || 0 }))
      .slice(-12);
  }, [trends.monthly]);

  const dailySeries = useMemo(() => {
    const source = trends?.daily && typeof trends.daily === 'object' ? trends.daily : {};
    return Object.entries(source)
      .slice(-14)
      .map(([day, value]) => ({ day, value: Number(value) || 0 }));
  }, [trends.daily]);

  if (loading) return <SkeletonTrends />;

  return (
    <div className="grid">
      <div className="card chart-card">
        <div className="heading-row">
          <h3>Monthly Trend</h3>
          <span className="badge">12-month view</span>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthlySeries}>
              <defs>
                <linearGradient id="barGrad" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.5} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(148, 163, 184, 0.1)" strokeDasharray="3 3" />
              <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="url(#barGrad)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card chart-card">
        <div className="heading-row">
          <h3>Daily Signal</h3>
          <span className="badge green">Recent 14 days</span>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={dailySeries}>
              <defs>
                <linearGradient id="barGradGreen" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0.5} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(148, 163, 184, 0.1)" strokeDasharray="3 3" />
              <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="url(#barGradGreen)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="heading-row">
          <h3>Evaluation Dataset</h3>
          <span className="badge purple">Ground truth</span>
        </div>
        <div className="list">
          {[
            ['Case-link rows', evaluation?.case_link_ground_truth?.rows],
            ['Entity-match rows', evaluation?.entity_match_ground_truth?.rows],
            ['Case-link columns', (evaluation?.case_link_ground_truth?.columns || []).length],
            ['Entity-match columns', (evaluation?.entity_match_ground_truth?.columns || []).length],
          ].map(([label, value]) => (
            <div key={label} className="list-item row">
              <span>{label}</span>
              <strong>{value ?? 0}</strong>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
