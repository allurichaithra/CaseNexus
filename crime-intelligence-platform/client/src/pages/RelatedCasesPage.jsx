import { useEffect, useMemo, useState } from 'react';
import { getFirs, getRelatedCases } from '../services/api';

function scoreLabel(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : 'N/A';
}

function scoreColor(value) {
  if (typeof value !== 'number') return 'var(--text-muted)';
  if (value >= 0.7) return '#22c55e';
  if (value >= 0.4) return '#f59e0b';
  return '#ef4444';
}

function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-line w-40" style={{ marginBottom: 16 }} />
      <div className="skeleton skeleton-line w-80" style={{ height: 40, borderRadius: 10 }} />
      <div className="skeleton" style={{ height: 80, borderRadius: 10, marginTop: 12 }} />
      <div className="score-grid" style={{ marginTop: 12 }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 40, borderRadius: 10 }} />
        ))}
      </div>
    </div>
  );
}

export default function RelatedCasesPage() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFirs(40)
      .then((data) => {
        const items = data?.items || [];
        setCases(items);
        if (items.length) {
          setSelectedCase(items[0].CaseMasterID);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCase) return;
    setRelated([]);
    getRelatedCases(selectedCase, 8).then((data) => setRelated(data?.items || []));
  }, [selectedCase]);

  const topMatch = related[0] || null;

  if (loading) {
    return (
      <div className="grid">
        <div className="skeleton-card">
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          <div className="skeleton skeleton-line w-100" style={{ height: 40, borderRadius: 10 }} />
        </div>
        <div className="grid grid-2">
          <SkeletonCard />
          <div className="skeleton-card">
            <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 80, borderRadius: 10, marginBottom: 8 }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row">
          <h3>Related Case Intelligence</h3>
          <span className="badge">Explainable matches</span>
        </div>
        <select
          className="select"
          value={selectedCase || ''}
          onChange={(event) => setSelectedCase(Number(event.target.value))}
        >
          {cases.map((item) => (
            <option key={item.CaseMasterID} value={item.CaseMasterID}>
              FIR {item.CaseMasterID}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-2">
        <div className="card hero-card">
          <div className="heading-row">
            <h3>Top Candidate Explanation</h3>
            <span className="badge">Best match</span>
          </div>
          {topMatch ? (
            <div className="list">
              <div className="list-item emphasis-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Overall match confidence</span>
                <strong style={{ fontSize: '1.4rem', color: scoreColor(topMatch.overall_score) }}>
                  {scoreLabel(topMatch.overall_score)}
                </strong>
              </div>
              <div className="list-item narrative-box">
                <p className="eyebrow" style={{ marginBottom: 6 }}>Evidence-based explanation</p>
                <p className="secondary-copy">{topMatch.explanation}</p>
              </div>
              <div className="score-grid">
                {[
                  ['Narrative', topMatch.narrative_score],
                  ['Crime pattern', topMatch.crime_pattern_score],
                  ['Legal section', topMatch.legal_section_score],
                  ['Geographic', topMatch.geographic_score],
                  ['Temporal', topMatch.temporal_score],
                  ['Entity', topMatch.entity_score],
                ].map(([label, value]) => (
                  <div key={label} className="score-pill">
                    <span>{label}</span>
                    <strong style={{ color: scoreColor(value) }}>{scoreLabel(value)}</strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <h4>No candidates found</h4>
              <p>No related cases were returned for this selection.</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="heading-row">
            <h3>Ranked Candidates</h3>
            <span className="badge">{related.length} matches</span>
          </div>
          <div className="list list-scroll">
            {related.map((item, index) => (
              <div key={`${item.related_case_id}-${item.overall_score}`} className="list-item">
                <div className="row">
                  <strong>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '0.8rem', marginRight: 6 }}>
                      #{index + 1}
                    </span>
                    FIR {item.related_case_id}
                  </strong>
                  <span className="badge" style={{ background: `rgba(${Math.round(scoreColor(item.overall_score) === '#22c55e' ? 34 : scoreColor(item.overall_score) === '#f59e0b' ? 245 : 239)}, ${Math.round(scoreColor(item.overall_score) === '#22c55e' ? 197 : scoreColor(item.overall_score) === '#f59e0b' ? 158 : 68)}, ${Math.round(scoreColor(item.overall_score) === '#22c55e' ? 94 : scoreColor(item.overall_score) === '#f59e0b' ? 11 : 68)}, 0.15)`, color: scoreColor(item.overall_score) }}>
                    {scoreLabel(item.overall_score)}
                  </span>
                </div>
                <div className="meta-column">
                  {[
                    ['Narrative', item.narrative_score],
                    ['Pattern', item.crime_pattern_score],
                    ['Legal', item.legal_section_score],
                    ['Geo', item.geographic_score],
                    ['Temporal', item.temporal_score],
                    ['Entity', item.entity_score],
                  ].filter(([, v]) => typeof v === 'number' && v > 0).map(([label, value]) => (
                    <span key={label}>{label} {scoreLabel(value)}</span>
                  ))}
                </div>
                <p className="muted secondary-copy">{item.explanation}</p>
              </div>
            ))}
            {related.length === 0 && (
              <div className="empty-state">
                <h4>No matches</h4>
                <p>Select a different case to find related investigations.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
