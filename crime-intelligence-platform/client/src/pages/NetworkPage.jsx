import { useEffect, useMemo, useState } from 'react';
import { getNetwork } from '../services/api';

export default function NetworkPage() {
  const [network, setNetwork] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNetwork()
      .then((data) => setNetwork(data))
      .finally(() => setLoading(false));
  }, []);

  const graphPositions = useMemo(() => {
    return network.nodes.map((node, index) => {
      const angle = (index / Math.max(network.nodes.length, 1)) * Math.PI * 2;
      const radius = 160;
      return {
        ...node,
        x: 250 + Math.cos(angle) * radius,
        y: 180 + Math.sin(angle) * radius,
      };
    });
  }, [network.nodes]);

  if (loading) return <div className="card">Loading investigation network…</div>;

  return (
    <div className="grid">
      <div className="card">
        <div className="row heading-row">
          <h3>Investigation network</h3>
          <span className="badge">Interactive graph</span>
        </div>
        <div className="network-stage">
          <svg viewBox="0 0 500 360" className="network-svg">
            {network.edges.map((edge, index) => {
              const source = graphPositions.find((node) => node.id === edge.source);
              const target = graphPositions.find((node) => node.id === edge.target);
              if (!source || !target) return null;
              return (
                <g key={`${edge.source}-${edge.target}-${index}`}>
                  <line x1={source.x} y1={source.y} x2={target.x} y2={target.y} stroke="#60a5fa" strokeWidth="2" strokeDasharray="6 4" />
                </g>
              );
            })}
            {graphPositions.map((node) => (
              <g key={`${node.id}-${node.type}`}>
                <circle cx={node.x} cy={node.y} r="22" fill="#1d4ed8" stroke="#bfdbfe" strokeWidth="2" />
                <text x={node.x} y={node.y + 4} textAnchor="middle" fontSize="10" fill="#f8fafc">
                  {node.label}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </div>

      <div className="card">
        <div className="row heading-row">
          <h3>Network entities</h3>
          <span className="badge">{network.nodes.length} nodes</span>
        </div>
        <div className="list list-scroll">
          {network.nodes.map((node, index) => (
            <div key={`${node.id}-${node.type}-${index}`} className="list-item">
              <div className="row">
                <strong>{node.label}</strong>
                <span className="badge">{node.type}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
