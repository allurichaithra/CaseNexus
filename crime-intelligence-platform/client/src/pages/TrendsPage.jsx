import { useEffect, useMemo, useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts';
import { getEvaluation, getTrends } from '../services/api';

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

  if (loading) return <div className="card">Loading analytics…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>Trend analytics</h3>
          <span className="badge">Operational insight</span>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={monthlySeries}>
              <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" />
              <XAxis dataKey="month" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#60a5fa" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="row heading-row">
          <h3>Daily signal</h3>
          <span className="badge">Recent activity</span>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={dailySeries}>
              <CartesianGrid stroke="rgba(148, 163, 184, 0.18)" />
              <XAxis dataKey="day" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#22c55e" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="row heading-row">
          <h3>Evaluation dataset</h3>
          <span className="badge">Ground truth reference</span>
        </div>
        <div className="list">
          <div className="list-item row">
            <span>Case-link rows</span>
            <strong>{evaluation?.case_link_ground_truth?.rows ?? 0}</strong>
          </div>
          <div className="list-item row">
            <span>Entity-match rows</span>
            <strong>{evaluation?.entity_match_ground_truth?.rows ?? 0}</strong>
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
    </div>
  );
}
