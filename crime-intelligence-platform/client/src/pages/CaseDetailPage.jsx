import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, FileText, Users, Shield, Scale, Fingerprint } from 'lucide-react';
import { getFir } from '../services/api';

function FieldGrid({ data }) {
  const entries = Object.entries(data || {}).filter(
    ([, v]) => v !== null && v !== undefined && v !== ''
  );
  if (!entries.length) {
    return <p className="muted secondary-copy">No data available.</p>;
  }
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 10 }}>
      {entries.map(([key, value]) => (
        <div key={key} className="score-pill" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
          <span className="muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            {key}
          </span>
          <strong style={{ color: 'var(--text-primary)', fontSize: '0.88rem', fontWeight: 500, wordBreak: 'break-word' }}>
            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
          </strong>
        </div>
      ))}
    </div>
  );
}

function SectionCard({ icon: Icon, title, badge, badgeColor, children }) {
  return (
    <div className="card">
      <div className="heading-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Icon size={17} style={{ color: 'var(--blue)' }} />
          <h3>{title}</h3>
        </div>
        {badge && <span className={`badge ${badgeColor || ''}`}>{badge}</span>}
      </div>
      {children}
    </div>
  );
}

function TableSection({ title, icon, items, emptyMsg }) {
  if (!items || !items.length) {
    return (
      <SectionCard icon={icon} title={title} badge="0">
        <p className="muted secondary-copy">{emptyMsg}</p>
      </SectionCard>
    );
  }
  const headers = Object.keys(items[0]);
  return (
    <SectionCard icon={icon} title={title} badge={`${items.length} records`}>
      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              {headers.map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((row, idx) => (
              <tr key={idx}>
                {headers.map((h) => (
                  <td key={h} style={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {row[h] !== null && row[h] !== undefined ? String(row[h]) : '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    getFir(caseId)
      .then(setData)
      .catch(() => setError('Failed to load case details.'))
      .finally(() => setLoading(false));
  }, [caseId]);

  if (loading) {
    return (
      <div className="grid">
        <div className="skeleton-card">
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          <div className="skeleton skeleton-line w-100" style={{ height: 60, borderRadius: 10 }} />
        </div>
        <div className="grid grid-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-card">
              <div className="skeleton skeleton-line w-40" style={{ marginBottom: 10 }} />
              <div className="skeleton skeleton-line w-100" style={{ height: 80, borderRadius: 10 }} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="grid">
        <div className="card">
          <div className="empty-state">
            <h4>{error}</h4>
            <button className="button" onClick={() => navigate('/firs')} style={{ marginTop: 12 }}>
              Back to FIR Explorer
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { case: caseData, accused, victims, act_sections, fingerprint } = data || {};

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button
              onClick={() => navigate('/firs')}
              style={{
                display: 'grid', placeItems: 'center', width: 36, height: 36,
                borderRadius: 10, border: '1px solid var(--border)', background: 'var(--surface)',
                cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0,
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--blue)'; e.currentTarget.style.background = 'var(--blue-dim)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--surface)'; }}
              aria-label="Back to FIR Explorer"
            >
              <ArrowLeft size={16} />
            </button>
            <div>
              <p className="eyebrow">Case Record</p>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em', margin: 0 }}>
                FIR {caseData?.CaseMasterID ?? caseId} — {caseData?.CaseNo || 'Unknown'}
              </h2>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            <Link to={`/firs`} className="badge purple" style={{ textDecoration: 'none', cursor: 'pointer' }}>
              All Cases
            </Link>
          </div>
        </div>
      </div>

      {/* Case Core Info */}
      <SectionCard icon={FileText} title="Case Information" badge="Core Record" badgeColor="blue">
        <FieldGrid data={caseData} />
      </SectionCard>

      {/* Fingerprint */}
      {fingerprint && (
        <SectionCard icon={Fingerprint} title="Case Fingerprint" badge="Intelligence" badgeColor="purple">
          <div className="score-grid">
            {Object.entries(fingerprint).filter(([, v]) => v !== null && v !== undefined && v !== '' && !(Array.isArray(v) && !v.length)).map(([key, value]) => (
              <div key={key} className="score-pill">
                <span>{key}</span>
                <strong>{Array.isArray(value) ? value.join(', ') : String(value)}</strong>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Act / Section Records */}
      <TableSection
        title="Act & Section Records"
        icon={Scale}
        items={act_sections}
        emptyMsg="No act or section records linked to this case."
      />

      {/* Accused */}
      <TableSection
        title="Accused Persons"
        icon={Users}
        items={accused}
        emptyMsg="No accused records linked to this case."
      />

      {/* Victims */}
      <TableSection
        title="Victim Records"
        icon={Shield}
        items={victims}
        emptyMsg="No victim records linked to this case."
      />
    </div>
  );
}
