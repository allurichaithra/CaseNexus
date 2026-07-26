import { useEffect, useState } from 'react';
import { getEntities } from '../services/api';

function scoreLabel(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : 'N/A';
}

function confidenceColor(value) {
  if (typeof value !== 'number') return 'var(--blue)';
  if (value >= 0.8) return '#22c55e';
  if (value >= 0.6) return '#f59e0b';
  return 'var(--blue)';
}

function SkeletonEntityList() {
  return (
    <div className="list">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 90, borderRadius: 10, marginBottom: 8 }} />
      ))}
    </div>
  );
}

export default function EntitiesPage() {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEntities(20)
      .then((data) => setEntities(data?.items || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid">
        <div className="skeleton-card">
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          <SkeletonEntityList />
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row">
          <h3>Entity Intelligence</h3>
          <span className="badge">{entities.length} candidates</span>
        </div>
        <div className="list list-scroll">
          {entities.map((item, index) => (
            <div key={`${item.accused_a_id}-${item.accused_b_id}-${index}`} className="list-item">
              <div className="row">
                <strong>
                  Entity pair {item.accused_a_id}
                  <span style={{ margin: '0 6px', color: 'var(--text-muted)' }}>↔</span>
                  {item.accused_b_id}
                </strong>
                <span className="badge" style={{ background: `rgba(${confidenceColor(item.confidence) === '#22c55e' ? '34,197,94' : confidenceColor(item.confidence) === '#f59e0b' ? '245,158,11' : '59,130,246'}, 0.15)`, color: confidenceColor(item.confidence) }}>
                  {scoreLabel(item.confidence)}
                </span>
              </div>
              {item.evidence?.length > 0 && (
                <div className="meta-column">
                  {item.evidence.map((proof) => (
                    <span key={proof}>{proof}</span>
                  ))}
                </div>
              )}
              <p className="muted secondary-copy">{item.explanation}</p>
            </div>
          ))}
          {entities.length === 0 && (
            <div className="empty-state">
              <h4>No entity matches</h4>
              <p>No cross-case entity matches were found in the current dataset.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
