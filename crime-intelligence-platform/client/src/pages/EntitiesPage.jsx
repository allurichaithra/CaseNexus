import { useEffect, useState } from 'react';
import { getEntities } from '../services/api';

function scoreLabel(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : 'N/A';
}

export default function EntitiesPage() {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEntities(20)
      .then((data) => setEntities(data?.items || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="card">Loading entity intelligence…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>Entity intelligence</h3>
          <span className="badge">{entities.length} candidates</span>
        </div>
        <div className="list list-scroll">
          {entities.map((item, index) => (
            <div key={`${item.accused_a_id}-${item.accused_b_id}-${index}`} className="list-item">
              <div className="row">
                <strong>Entity pair {item.accused_a_id} ↔ {item.accused_b_id}</strong>
                <span className="badge">Confidence {scoreLabel(item.confidence)}</span>
              </div>
              <div className="meta-column">
                {item.evidence?.map((proof) => (
                  <span key={proof}>{proof}</span>
                ))}
              </div>
              <p className="muted secondary-copy">{item.explanation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
