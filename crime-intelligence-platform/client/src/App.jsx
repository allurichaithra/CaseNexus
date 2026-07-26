import { useEffect } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Search, Network, MapPin, TrendingUp, ShieldAlert, Users, FileText } from 'lucide-react';
import DashboardPage from './pages/DashboardPage';
import FirsPage from './pages/FirsPage';
import CaseDetailPage from './pages/CaseDetailPage';
import RelatedCasesPage from './pages/RelatedCasesPage';
import EntitiesPage from './pages/EntitiesPage';
import HotspotsPage from './pages/HotspotsPage';
import NetworkPage from './pages/NetworkPage';
import TrendsPage from './pages/TrendsPage';

const navItems = [
  { path: '/', label: 'Command Center', icon: LayoutDashboard },
  { path: '/firs', label: 'FIR Explorer', icon: FileText },
  { path: '/related', label: 'Case Intelligence', icon: ShieldAlert },
  { path: '/entities', label: 'Entity Matching', icon: Users },
  { path: '/hotspots', label: 'Hotspots', icon: MapPin },
  { path: '/network', label: 'Network View', icon: Network },
  { path: '/trends', label: 'Analytics', icon: TrendingUp },
];

const pageMeta = {
  '/': { eyebrow: 'Live intelligence workspace', title: 'Command Center' },
  '/firs': { eyebrow: 'First Information Reports', title: 'FIR Explorer' },
  '/related': { eyebrow: 'Cross-case analysis', title: 'Case Intelligence' },
  '/entities': { eyebrow: 'Person resolution', title: 'Entity Matching' },
  '/hotspots': { eyebrow: 'Geographic distribution', title: 'Crime Hotspots' },
  '/network': { eyebrow: 'Relationship mapping', title: 'Investigation Network' },
  '/trends': { eyebrow: 'Temporal patterns', title: 'Analytics' },
};

function App() {
  const location = useLocation();
  const meta = pageMeta[location.pathname] || pageMeta['/'];

  useEffect(() => {
    document.title = `${meta.title} — Crime Intelligence`;
  }, [meta.title]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-icon">🛡️</div>
          <div>
            <h1>CaseNexus</h1>
            <p>Connecting cases. Revealing patterns. Accelerating investigations.</p>
          </div>
        </div>

        <nav className="nav-links">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <NavLink key={path} to={path} className={`nav-link ${isActive ? 'active' : ''}`}>
                <Icon size={17} />
                <span>{label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="main-panel" key={location.pathname}>
        <header className="topbar">
          <div className="topbar-left">
            <div className="topbar-status" />
            <div>
              <p className="eyebrow">{meta.eyebrow}</p>
              <h2>{meta.title}</h2>
            </div>
          </div>
          <div className="topbar-badge">Backend live · :8001</div>
        </header>

        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/firs" element={<FirsPage />} />
          <Route path="/firs/:caseId" element={<CaseDetailPage />} />
          <Route path="/related" element={<RelatedCasesPage />} />
          <Route path="/entities" element={<EntitiesPage />} />
          <Route path="/hotspots" element={<HotspotsPage />} />
          <Route path="/network" element={<NetworkPage />} />
          <Route path="/trends" element={<TrendsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
