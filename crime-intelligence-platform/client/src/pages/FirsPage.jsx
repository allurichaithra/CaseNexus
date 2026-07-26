import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFirs } from '../services/api';

const PAGE_SIZE = 20;

function SkeletonList({ count = 5 }) {
  return (
    <div className="list">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-row">
          <div className="skeleton skeleton-line w-40" />
          <div className="skeleton skeleton-badge" />
        </div>
      ))}
    </div>
  );
}

export default function FirsPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getFirs(5000)
      .then((data) => {
        const caseItems = Array.isArray(data?.items) ? data.items : [];
        const normalized = caseItems.map((item) => ({
          ...item,
          CaseMasterID: item?.CaseMasterID ?? item?.case_id ?? item?.id,
          BriefFacts: item?.BriefFacts ?? item?.brief_facts ?? item?.narrative ?? 'No narrative available for this FIR.',
          CaseNo: item?.CaseNo ?? item?.case_no ?? 'Unknown',
          CrimeNo: item?.CrimeNo ?? item?.crime_no ?? 'Unknown',
          CrimeRegisteredDate: item?.CrimeRegisteredDate ?? item?.crime_registered_date ?? 'Unknown',
          DistrictID: item?.DistrictID ?? item?.district_id ?? 'Unknown',
          CrimeMajorHeadID: item?.CrimeMajorHeadID ?? item?.crime_major_head_id ?? 'Unknown',
        }));
        setItems(normalized);
        setTotalCount(data?.total || normalized.length);
        if (normalized.length && selectedCaseId == null) {
          setSelectedCaseId(normalized[0].CaseMasterID);
        }
      })
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return items;
    return items.filter((item) => {
      const haystack = [
        item?.CaseMasterID,
        item?.CaseNo,
        item?.CrimeNo,
        item?.BriefFacts,
        item?.CrimeMajorHeadID,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(term);
    });
  }, [items, search]);

  const totalPages = Math.max(1, Math.ceil(filteredItems.length / PAGE_SIZE));
  const pageItems = filteredItems.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const selectedItem = filteredItems.find((item) => item.CaseMasterID === selectedCaseId) || filteredItems[0] || null;

  const handleSearchChange = (val) => {
    setSearch(val);
    setPage(0);
  };

  if (loading) {
    return (
      <div className="grid">
        <div className="skeleton-card">
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          <div className="skeleton skeleton-line w-100" style={{ height: 40, borderRadius: 10 }} />
          <div className="skeleton skeleton-line w-100" style={{ height: 40, borderRadius: 10, marginTop: 10 }} />
        </div>
        <div className="grid grid-2">
          <div className="skeleton-card">
            <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
            <SkeletonList count={8} />
          </div>
          <div className="skeleton-card">
            <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
            <SkeletonList count={6} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row">
          <h3>FIR Explorer</h3>
          <span className="badge">{filteredItems.length} of {totalCount} records</span>
        </div>
        <div className="field-stack">
          <input
            className="input"
            placeholder="Search by case ID, crime number, or narrative..."
            value={search}
            onChange={(event) => handleSearchChange(event.target.value)}
          />
          <select
            className="select"
            value={selectedCaseId || ''}
            onChange={(event) => setSelectedCaseId(Number(event.target.value))}
          >
            {filteredItems.slice(0, 200).map((item) => (
              <option key={item.CaseMasterID} value={item.CaseMasterID}>
                FIR {item.CaseMasterID} — {item.CaseNo}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="heading-row">
            <h3>Case List</h3>
            <span className="badge green">Page {page + 1}/{totalPages}</span>
          </div>
          <div className="list list-scroll">
            {pageItems.map((item) => (
              <div
                key={item.CaseMasterID}
                className={`list-item ${selectedCaseId === item.CaseMasterID ? 'selected' : ''}`}
                onClick={() => setSelectedCaseId(item.CaseMasterID)}
              >
                <div className="row">
                  <strong>FIR {item.CaseMasterID}</strong>
                  <span className="badge">#{item.CaseNo}</span>
                </div>
                <p className="muted secondary-copy" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {item.BriefFacts || 'No narrative available.'}
                </p>
                <button
                  className="button"
                  style={{ marginTop: 8, fontSize: '0.78rem', padding: '6px 14px', width: '100%' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/firs/${item.CaseMasterID}`);
                  }}
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, padding: '12px 0' }}>
              <button
                className="button"
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
                style={{ fontSize: '0.78rem', padding: '5px 14px' }}
              >
                Prev
              </button>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                {page + 1} / {totalPages}
              </span>
              <button
                className="button"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
                style={{ fontSize: '0.78rem', padding: '5px 14px' }}
              >
                Next
              </button>
            </div>
          )}
        </div>

        <div className="card">
          <div className="heading-row">
            <h3>Case Detail</h3>
            <span className="badge purple">Record</span>
          </div>

          {selectedItem ? (
            <div className="list">
              {[
                ['Case ID', selectedItem.CaseMasterID],
                ['Crime number', selectedItem.CrimeNo],
                ['Registered date', selectedItem.CrimeRegisteredDate],
                ['District', selectedItem.DistrictID],
                ['Major head', selectedItem.CrimeMajorHeadID],
                ['Location', selectedItem.latitude && selectedItem.longitude ? `${selectedItem.latitude}, ${selectedItem.longitude}` : 'N/A'],
              ].map(([label, value]) => (
                <div key={label} className="list-item row">
                  <span>{label}</span>
                  <strong>{value ?? 'Unknown'}</strong>
                </div>
              ))}
              <div className="list-item narrative-box">
                <p className="eyebrow" style={{ marginBottom: 6 }}>Brief Facts</p>
                <p className="secondary-copy">{selectedItem.BriefFacts || 'No narrative available.'}</p>
              </div>
              <button
                className="button"
                style={{ width: '100%', marginTop: 8 }}
                onClick={() => navigate(`/firs/${selectedItem.CaseMasterID}`)}
              >
                View Details
              </button>
            </div>
          ) : (
            <div className="empty-state">
              <h4>No case selected</h4>
              <p>Pick a case from the list to view its investigative record.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
