import { useEffect, useMemo, useState } from 'react';
import { getFirs } from '../services/api';

export default function FirsPage() {
  const [items, setItems] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFirs(40)
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
        if (normalized.length) {
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

  const selectedItem = filteredItems.find((item) => item.CaseMasterID === selectedCaseId) || filteredItems[0] || null;

  if (loading) return <div className="card">Loading FIR records…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>FIR Explorer</h3>
          <span className="badge">{filteredItems.length} visible</span>
        </div>
        <div className="field-stack">
          <input
            className="input"
            placeholder="Search by case ID, crime number, or narrative"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select
            className="select"
            value={selectedCaseId || ''}
            onChange={(event) => setSelectedCaseId(Number(event.target.value))}
          >
            {filteredItems.map((item) => (
              <option key={item.CaseMasterID} value={item.CaseMasterID}>
                FIR {item.CaseMasterID} • {item.CaseNo}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="row heading-row">
            <h3>Case list</h3>
            <span className="badge">Live snapshot</span>
          </div>
          <div className="list list-scroll">
            {filteredItems.map((item) => (
              <div
                key={item.CaseMasterID}
                className={`list-item ${selectedCaseId === item.CaseMasterID ? 'selected' : ''}`}
                onClick={() => setSelectedCaseId(item.CaseMasterID)}
              >
                <div className="row">
                  <strong>FIR {item.CaseMasterID}</strong>
                  <span className="badge">#{item.CaseNo}</span>
                </div>
                <p className="muted secondary-copy">{item.BriefFacts || 'No narrative available for this FIR.'}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="row heading-row">
            <h3>Case detail</h3>
            <span className="badge">Investigative record</span>
          </div>

          {selectedItem ? (
            <div className="list">
              <div className="list-item">
                <div className="row">
                  <span>Case ID</span>
                  <strong>{selectedItem.CaseMasterID}</strong>
                </div>
              </div>
              <div className="list-item">
                <div className="row">
                  <span>Crime number</span>
                  <strong>{selectedItem.CrimeNo}</strong>
                </div>
              </div>
              <div className="list-item">
                <div className="row">
                  <span>Registered date</span>
                  <strong>{selectedItem.CrimeRegisteredDate}</strong>
                </div>
              </div>
              <div className="list-item">
                <div className="row">
                  <span>District</span>
                  <strong>{selectedItem.DistrictID ?? 'Unknown'}</strong>
                </div>
              </div>
              <div className="list-item">
                <div className="row">
                  <span>Major head</span>
                  <strong>{selectedItem.CrimeMajorHeadID ?? 'Unknown'}</strong>
                </div>
              </div>
              <div className="list-item">
                <div className="row">
                  <span>Location</span>
                  <strong>{selectedItem.latitude}, {selectedItem.longitude}</strong>
                </div>
              </div>
              <div className="list-item narrative-box">
                <div className="row">
                  <span>Brief facts</span>
                </div>
                <p className="muted secondary-copy">{selectedItem.BriefFacts || 'No narrative available.'}</p>
              </div>
            </div>
          ) : (
            <p className="muted">Select a case to inspect the detail view.</p>
          )}
        </div>
      </div>
    </div>
  );
}
