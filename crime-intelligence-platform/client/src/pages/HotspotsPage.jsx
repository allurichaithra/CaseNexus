import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { getHotspots } from '../services/api';
import 'leaflet/dist/leaflet.css';

export default function HotspotsPage() {
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHotspots(50)
      .then((data) => setHotspots(data?.items || []))
      .catch(() => setHotspots([]))
      .finally(() => setLoading(false));
  }, []);

  const center = useMemo(() => {
    const coords = hotspots.filter((item) => Number.isFinite(item.latitude) && Number.isFinite(item.longitude));
    if (!coords.length) return [12.97, 77.59];
    const avgLat = coords.reduce((sum, item) => sum + item.latitude, 0) / coords.length;
    const avgLng = coords.reduce((sum, item) => sum + item.longitude, 0) / coords.length;
    return [avgLat, avgLng];
  }, [hotspots]);

  if (loading) return <div className="card">Loading hotspot intelligence…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>Crime hotspots</h3>
          <span className="badge">Interactive map</span>
        </div>
        <div className="map-wrapper">
          <MapContainer center={center} zoom={11} scrollWheelZoom className="map-frame">
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
            {hotspots.map((item) => (
              <Marker key={`${item.case_id}-${item.latitude}-${item.longitude}`} position={[item.latitude, item.longitude]}>
                <Popup>
                  <strong>FIR {item.case_id}</strong><br />
                  Crime major head: {item.crime_major_head_id}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>

      <div className="card">
        <div className="row heading-row">
          <h3>Hotspot list</h3>
          <span className="badge">{hotspots.length} points</span>
        </div>
        <div className="list list-scroll">
          {hotspots.map((item, index) => (
            <div key={`${item.case_id}-${index}`} className="list-item">
              <div className="row">
                <strong>FIR {item.case_id}</strong>
                <span className="badge">#{item.crime_major_head_id ?? 'N/A'}</span>
              </div>
              <p className="muted secondary-copy">Latitude {item.latitude} • Longitude {item.longitude}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
