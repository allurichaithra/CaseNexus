import { useEffect, useMemo, useState } from 'react';
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts';
import { getDashboard, getEvaluation, getTrends } from '../services/api';

const metricCards = [
  { key: 'total_cases', label: 'Total cases', accent: 'Live' },
  { key: 'total_accused_records', label: 'Accused records', accent: 'Linked' },
  { key: 'total_victim_records', label: 'Victim records', accent: 'Tracked' },
];

function numberLabel(value) {
  return Number.isFinite(value) ? value.toLocaleString() : 0;
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

  if (loading) return <div className="card">Loading intelligence dashboard…</div>;

  return (
    <div className="grid">
      <section className="grid grid-3">
        {metricCards.map((item) => (
          <div key={item.key} className="card stat">
            <div>
              <p className="eyebrow">{item.label}</p>
              <h3>{numberLabel(dashboard?.[item.key])}</h3>
              <p>Current intelligence snapshot from the live backend</p>
            </div>
            <span className="badge">{item.accent}</span>
          </div>
        ))}
      </section>

      <section className="grid grid-2">
        <div className="card">
          <div className="row heading-row">
            <h3>Operational overview</h3>
            <span className="badge">Dataset</span>
          </div>
          <div className="list">
            <div className="list-item row">
              <span>District coverage</span>
              <strong>{numberLabel(dashboard?.total_districts)}</strong>
            </div>
            <div className="list-item row">
              <span>Crime categories</span>
              <strong>{numberLabel(dashboard?.crime_categories)}</strong>
            </div>
            <div className="list-item row">
              <span>Ground-truth links</span>
              <strong>{numberLabel(dashboard?.ground_truth_case_links)}</strong>
            </div>
            <div className="list-item row">
              <span>Fingerprints generated</span>
              <strong>{numberLabel(dashboard?.fingerprints_generated)}</strong>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="row heading-row">
            <h3>Evaluation coverage</h3>
            <span className="badge">Ground truth</span>
          </div>
          <div className="list">
            <div className="list-item row">
              <span>Case-link rows</span>
              <strong>{numberLabel(evaluation?.case_link_ground_truth?.rows)}</strong>
            </div>
            <div className="list-item row">
              <span>Entity-match rows</span>
              <strong>{numberLabel(evaluation?.entity_match_ground_truth?.rows)}</strong>
            </div>
            <div className="list-item row">
              <span>Case-link columns</span>
              <strong>{(evaluation?.case_link_ground_truth?.columns || []).length}</strong>
            </div>
            <div className="list-item row">
              <span>Entity-match columns</span>
              <strong>{(evaluation?.entity_match_ground_truth?.columns || []).length}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-2">
        <div className="card chart-card">
          <div className="row heading-row">
            <h3>Monthly case volume</h3>
            <span className="badge">Temporal trend</span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={monthlySeries}>
                <defs>
                  <linearGradient id="volumeGradient" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" />
                <XAxis dataKey="month" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" allowDecimals={false} />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#60a5fa" fill="url(#volumeGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card chart-card">
          <div className="row heading-row">
            <h3>Recent daily activity</h3>
            <span className="badge">Live signal</span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={dailySeries}>
                <defs>
                  <linearGradient id="dailyGradient" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" />
                <XAxis dataKey="day" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" allowDecimals={false} />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#22c55e" fill="url(#dailyGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}
