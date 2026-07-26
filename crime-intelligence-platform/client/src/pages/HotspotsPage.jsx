import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { getHotspots } from '../services/api';
import 'leaflet/dist/leaflet.css';

const PAGE_SIZE = 20;

function SkeletonMap() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 380, borderRadius: 14 }} />
    </div>
  );
}

function MapTracker({ onBoundsChange }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    const emit = () => {
      const b = map.getBounds();
      onBoundsChange({
        south: b.getSouth(),
        north: b.getNorth(),
        west: b.getWest(),
        east: b.getEast(),
        zoom: map.getZoom(),
      });
    };
    map.on('moveend', emit);
    map.on('zoomend', emit);
    emit();
    return () => { map.off('moveend', emit); map.off('zoomend', emit); };
  }, [map, onBoundsChange]);

  return null;
}

function MapFlyTo({ target }) {
  const map = useMap();
  useEffect(() => {
    if (target && map) map.setView(target, 14);
  }, [target, map]);
  return null;
}

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    const q = query.trim();
    if (!q) return;
    setSearching(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`,
        { headers: { 'Accept-Language': 'en' } }
      );
      const results = await res.json();
      if (results.length) {
        const { lat, lon } = results[0];
        onSearch([parseFloat(lat), parseFloat(lon)]);
      }
    } catch { /* ignore */ }
    setSearching(false);
  };

  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
      <input
        className="input"
        placeholder="Search area (e.g. Koramangala, Bangalore)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        style={{ flex: 1 }}
      />
      <button
        className="button"
        onClick={handleSearch}
        disabled={searching}
        style={{ whiteSpace: 'nowrap', minWidth: 90 }}
      >
        {searching ? '...' : 'Search'}
      </button>
    </div>
  );
}

export default function HotspotsPage() {
  const navigate = useNavigate();
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bounds, setBounds] = useState(null);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [flyTarget, setFlyTarget] = useState(null);
  const [listPage, setListPage] = useState(0);

  useEffect(() => {
    getHotspots(5000)
      .then((data) => setHotspots(data?.items || []))
      .catch(() => setHotspots([]))
      .finally(() => setLoading(false));
  }, []);

  const center = useMemo(() => {
    const coords = hotspots.filter((h) => Number.isFinite(h.latitude) && Number.isFinite(h.longitude));
    if (!coords.length) return [12.97, 77.59];
    const avgLat = coords.reduce((s, h) => s + h.latitude, 0) / coords.length;
    const avgLng = coords.reduce((s, h) => s + h.longitude, 0) / coords.length;
    return [avgLat, avgLng];
  }, [hotspots]);

  const inBounds = useMemo(() => {
    if (!bounds) return hotspots;
    return hotspots.filter(
      (h) => h.latitude >= bounds.south && h.latitude <= bounds.north &&
             h.longitude >= bounds.west && h.longitude <= bounds.east
    );
  }, [hotspots, bounds]);

  const visible = useMemo(() => {
    if (selectedCaseId != null) return inBounds.filter((h) => h.case_id === selectedCaseId);
    return inBounds;
  }, [inBounds, selectedCaseId]);

  const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const pageItems = visible.slice(listPage * PAGE_SIZE, (listPage + 1) * PAGE_SIZE);

  const handleBoundsChange = useCallback((b) => setBounds(b), []);

  const selectCase = useCallback((caseId, lat, lng) => {
    setSelectedCaseId(caseId);
    setFlyTarget([lat, lng]);
    setListPage(0);
  }, []);

  if (loading) {
    return (
      <div className="grid">
        <SkeletonMap />
        <div className="skeleton-card">
          <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 60, borderRadius: 10, marginBottom: 8 }} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row">
          <h3>Crime Hotspots</h3>
          <span className="badge">{inBounds.length} visible / {hotspots.length} total</span>
        </div>
        <SearchBar onSearch={setFlyTarget} />
        <div className="map-wrapper">
          <MapContainer center={center} zoom={11} scrollWheelZoom className="map-frame">
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; OpenStreetMap contributors &copy; CARTO'
            />
            <MapTracker onBoundsChange={handleBoundsChange} />
            <MapFlyTo target={flyTarget} />
            {inBounds.map((item) => (
              <Marker
                key={`${item.case_id}-${item.latitude}-${item.longitude}`}
                position={[item.latitude, item.longitude]}
                eventHandlers={{
                  click: () => selectCase(item.case_id, item.latitude, item.longitude),
                }}
              >
                <Popup>
                  <strong>FIR {item.case_id}</strong><br />
                  Crime type: {item.crime_major_head_id ?? 'N/A'}<br />
                  <span style={{ fontSize: 12, color: '#666' }}>
                    {item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}
                  </span>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>

      <div className="card">
        <div className="heading-row">
          <h3>Hotspot List</h3>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {selectedCaseId != null && (
              <button
                className="button"
                onClick={() => { setSelectedCaseId(null); setListPage(0); }}
                style={{ fontSize: '0.75rem', padding: '4px 12px', background: 'var(--surface-hover)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              >
                Clear
              </button>
            )}
            <span className="badge green">{visible.length} {selectedCaseId != null ? 'selected' : 'in view'}</span>
          </div>
        </div>
        <div className="list list-scroll">
          {pageItems.map((item, index) => (
            <div
              key={`${item.case_id}-${index}`}
              className={`list-item ${selectedCaseId === item.case_id ? 'selected' : ''}`}
              onClick={() => selectCase(item.case_id, item.latitude, item.longitude)}
              style={{ cursor: 'pointer' }}
            >
              <div className="row">
                <strong>FIR {item.case_id}</strong>
                <span className="badge">#{item.crime_major_head_id ?? 'N/A'}</span>
              </div>
              <p className="muted secondary-copy">
                {item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}
              </p>
              <button
                className="button"
                style={{ marginTop: 6, fontSize: '0.78rem', padding: '5px 12px', width: '100%' }}
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/firs/${item.case_id}`);
                }}
              >
                View Detail
              </button>
            </div>
          ))}
          {visible.length === 0 && (
            <div className="empty-state" style={{ padding: '24px 16px' }}>
              <h4>No cases in view</h4>
              <p>Zoom out or search a different area to see hotspots.</p>
            </div>
          )}
        </div>
        {totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, padding: '12px 0' }}>
            <button
              className="button"
              disabled={listPage === 0}
              onClick={() => setListPage((p) => p - 1)}
              style={{ fontSize: '0.78rem', padding: '5px 14px' }}
            >
              Prev
            </button>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {listPage + 1} / {totalPages}
            </span>
            <button
              className="button"
              disabled={listPage >= totalPages - 1}
              onClick={() => setListPage((p) => p + 1)}
              style={{ fontSize: '0.78rem', padding: '5px 14px' }}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
