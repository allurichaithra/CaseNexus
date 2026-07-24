import { useEffect, useMemo, useState } from 'react';
import { getFirs, getRelatedCases } from '../services/api';

function scoreLabel(value) {
  return typeof value === 'number' ? `${Math.round(value * 100)}%` : 'N/A';
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
    getRelatedCases(selectedCase, 8).then((data) => setRelated(data?.items || []));
  }, [selectedCase]);

  const topMatch = related[0] || null;
  const scoreGrid = useMemo(
    () => [
      ['Narrative score', topMatch?.narrative_score],
      ['Crime pattern score', topMatch?.crime_pattern_score],
      ['Legal section score', topMatch?.legal_section_score],
      ['Geographic score', topMatch?.geographic_score],
      ['Temporal score', topMatch?.temporal_score],
      ['Entity score', topMatch?.entity_score],
    ],
    [topMatch],
  );

  if (loading) return <div className="card">Loading related-case intelligence…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>Related case intelligence</h3>
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
          <div className="row heading-row">
            <h3>Top candidate explanation</h3>
            <span className="badge">Hero card</span>
          </div>
          {topMatch ? (
            <div className="list">
              <div className="list-item row emphasis-row">
                <span>Overall match percentage</span>
                <strong>{scoreLabel(topMatch.overall_score)}</strong>
              </div>
              <div className="list-item narrative-box">
                <div className="row">
                  <span>Evidence-based explanation</span>
                </div>
                <p className="muted secondary-copy">{topMatch.explanation}</p>
              </div>
              <div className="score-grid">
                {scoreGrid.map(([label, value]) => (
                  <div key={label} className="score-pill">
                    <span>{label}</span>
                    <strong>{scoreLabel(value)}</strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="muted">No related candidates were returned for this case.</p>
          )}
        </div>

        <div className="card">
          <div className="row heading-row">
            <h3>Ranked candidates</h3>
            <span className="badge">{related.length} matches</span>
          </div>
          <div className="list list-scroll">
            {related.map((item) => (
              <div key={`${item.related_case_id}-${item.overall_score}`} className="list-item">
                <div className="row">
                  <strong>FIR {item.related_case_id}</strong>
                  <span className="badge">{scoreLabel(item.overall_score)}</span>
                </div>
                <div className="meta-column">
                  <span>Narrative {scoreLabel(item.narrative_score)}</span>
                  <span>Pattern {scoreLabel(item.crime_pattern_score)}</span>
                  <span>Legal {scoreLabel(item.legal_section_score)}</span>
                  <span>Geo {scoreLabel(item.geographic_score)}</span>
                  <span>Temporal {scoreLabel(item.temporal_score)}</span>
                  <span>Entity {scoreLabel(item.entity_score)}</span>
                </div>
                <p className="muted secondary-copy">{item.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
