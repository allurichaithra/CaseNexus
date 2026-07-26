import { useEffect, useMemo, useRef, useState } from 'react';
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts';
import { getDashboard, getEvaluation, getTrends } from '../services/api';

const metricCards = [
  { key: 'total_cases', label: 'Total Cases', accent: 'blue', badge: 'Live' },
  { key: 'total_accused_records', label: 'Accused Records', accent: 'purple', badge: 'Linked' },
  { key: 'total_victim_records', label: 'Victim Records', accent: 'green', badge: 'Tracked' },
];

function useCountUp(target, duration = 800) {
  const [value, setValue] = useState(0);
  const raf = useRef(null);
  useEffect(() => {
    if (target == null) return;
    const start = performance.now();
    const from = 0;
    const to = Number(target) || 0;
    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(from + (to - from) * eased));
      if (progress < 1) raf.current = requestAnimationFrame(tick);
    }
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration]);
  return value;
}

function StatCard({ item, dashboard }) {
  const displayValue = useCountUp(dashboard?.[item.key], 900);
  return (
    <div className="card stat">
      <div style={{ display: 'flex', gap: '12px', alignItems: 'stretch' }}>
        <div className={`stat-accent ${item.accent}`} />
        <div>
          <p className="eyebrow">{item.label}</p>
          <h3>{Number.isFinite(displayValue) ? displayValue.toLocaleString() : '—'}</h3>
          <p>Snapshot from live backend</p>
        </div>
      </div>
      <span className="badge live">{item.badge}</span>
    </div>
  );
}

function SkeletonDashboard() {
  return (
    <div className="grid">
      <section className="grid grid-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton skeleton-line w-40" />
            <div className="skeleton skeleton-stat" />
            <div className="skeleton skeleton-line w-60" />
          </div>
        ))}
      </section>
      <section className="grid grid-2">
        {[0, 1].map((i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton skeleton-line w-40" style={{ marginBottom: 16 }} />
            {[0, 1, 2, 3].map((j) => (
              <div key={j} className="skeleton-row" style={{ marginBottom: 6 }}>
                <div className="skeleton skeleton-line w-60" />
                <div className="skeleton skeleton-badge" />
              </div>
            ))}
          </div>
        ))}
      </section>
      <section className="grid grid-2">
        {[0, 1].map((i) => (
          <div key={i} className="skeleton-card" style={{ minHeight: 300 }}>
            <div className="skeleton skeleton-line w-40" style={{ marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 220, borderRadius: 8 }} />
          </div>
        ))}
      </section>
    </div>
  );
}

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
      <div style={{ color: '#0f172a', fontWeight: 700 }}>{payload[0].value.toLocaleString()} cases</div>
    </div>
  );
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [trends, setTrends] = useState({ daily: {}, monthly: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getDashboard(), getEvaluation(), getTrends()])
      .then((results) => {
        const dashboardData = results[0].status === 'fulfilled' ? results[0].value : null;
        const evaluationData = results[1].status === 'fulfilled' ? results[1].value : null;
        const trendData = results[2].status === 'fulfilled' ? results[2].value : { daily: {}, monthly: {} };
        setDashboard(dashboardData);
        setEvaluation(evaluationData);
        setTrends(trendData);
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

  if (loading) return <SkeletonDashboard />;

  return (
    <div className="grid">
      <section className="grid grid-3">
        {metricCards.map((item) => (
          <StatCard key={item.key} item={item} dashboard={dashboard} />
        ))}
      </section>

      <section className="grid grid-2">
        <div className="card">
          <div className="heading-row">
            <h3>Operational Overview</h3>
            <span className="badge">Dataset</span>
          </div>
          <div className="list">
            {[
              ['District coverage', dashboard?.total_districts],
              ['Crime categories', dashboard?.crime_categories],
              ['Ground-truth links', dashboard?.ground_truth_case_links],
              ['Fingerprints generated', dashboard?.fingerprints_generated],
            ].map(([label, value]) => (
              <div key={label} className="list-item row">
                <span>{label}</span>
                <strong>{Number.isFinite(value) ? value.toLocaleString() : 0}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="heading-row">
            <h3>Evaluation Coverage</h3>
            <span className="badge purple">Ground Truth</span>
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
      </section>

      <section className="grid grid-2">
        <div className="card chart-card">
          <div className="heading-row">
            <h3>Monthly Case Volume</h3>
            <span className="badge">Temporal trend</span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={monthlySeries}>
                <defs>
                  <linearGradient id="volumeGrad" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.1)" strokeDasharray="3 3" />
                <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} fill="url(#volumeGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card chart-card">
          <div className="heading-row">
            <h3>Recent Daily Activity</h3>
            <span className="badge green">Live signal</span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={dailySeries}>
                <defs>
                  <linearGradient id="dailyGrad" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.1)" strokeDasharray="3 3" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} fill="url(#dailyGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}
