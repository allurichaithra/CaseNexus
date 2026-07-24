import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Search, Network, MapPin, TrendingUp, ShieldAlert, Users, FileText } from 'lucide-react';
import DashboardPage from './pages/DashboardPage';
import FirsPage from './pages/FirsPage';
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

function App() {
  const location = useLocation();

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
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">CaseNexus • Live intelligence workspace</p>
            <h2>Investigative decision support</h2>
          </div>
          <div className="topbar-badge">Backend • http://127.0.0.1:8001</div>
        </header>

        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/firs" element={<FirsPage />} />
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
