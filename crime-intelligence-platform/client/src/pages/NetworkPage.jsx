import { useEffect, useMemo, useState } from 'react';
import { getNetwork } from '../services/api';

function SkeletonGraph() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-line w-40" style={{ marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 380, borderRadius: 14 }} />
    </div>
  );
}

const nodeColors = {
  case: { fill: '#2563eb', stroke: '#3b82f6' },
  related_case: { fill: '#7c3aed', stroke: '#a78bfa' },
};

export default function NetworkPage() {
  const [network, setNetwork] = useState({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNetwork()
      .then((data) => setNetwork(data))
      .finally(() => setLoading(false));
  }, []);

  const graphPositions = useMemo(() => {
    return network.nodes.map((node, index) => {
      const angle = (index / Math.max(network.nodes.length, 1)) * Math.PI * 2;
      const radius = 150;
      return {
        ...node,
        x: 250 + Math.cos(angle) * radius,
        y: 180 + Math.sin(angle) * radius,
      };
    });
  }, [network.nodes]);

  if (loading) return <SkeletonGraph />;

  return (
    <div className="grid">
      <div className="card">
        <div className="heading-row">
          <h3>Investigation Network</h3>
          <span className="badge">{network.nodes.length} nodes · {network.edges.length} edges</span>
        </div>
        <div className="network-stage">
          <svg viewBox="0 0 500 360" className="network-svg">
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {network.edges.map((edge, index) => {
              const source = graphPositions.find((node) => node.id === edge.source);
              const target = graphPositions.find((node) => node.id === edge.target);
              if (!source || !target) return null;
              const isHighlighted = selectedNode === edge.source || selectedNode === edge.target;
              return (
                <line
                  key={`${edge.source}-${edge.target}-${index}`}
                  x1={source.x} y1={source.y}
                  x2={target.x} y2={target.y}
                  stroke={isHighlighted ? '#2563eb' : 'rgba(37, 99, 236, 0.25)'}
                  strokeWidth={isHighlighted ? 2.5 : 1.5}
                  strokeDasharray={isHighlighted ? 'none' : '6 4'}
                />
              );
            })}
            {graphPositions.map((node) => {
              const colors = nodeColors[node.type] || nodeColors.case;
              const isSelected = selectedNode === node.id;
              return (
                <g
                  key={`${node.id}-${node.type}`}
                  onClick={() => setSelectedNode(isSelected ? null : node.id)}
                  style={{ cursor: 'pointer' }}
                  filter={isSelected ? 'url(#glow)' : undefined}
                >
                  <circle
                    cx={node.x} cy={node.y}
                    r={isSelected ? 26 : 22}
                    fill={colors.fill}
                    stroke={isSelected ? '#fff' : colors.stroke}
                    strokeWidth={isSelected ? 3 : 2}
                    style={{ transition: 'all 0.2s ease' }}
                  />
                  <text
                    x={node.x} y={node.y + 4}
                    textAnchor="middle"
                    fontSize="9"
                    fill="#f8fafc"
                    fontWeight="600"
                    style={{ pointerEvents: 'none' }}
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      <div className="card">
        <div className="heading-row">
          <h3>Network Entities</h3>
          <span className="badge">{network.nodes.length} nodes</span>
        </div>
        <div className="list list-scroll">
          {network.nodes.map((node, index) => (
            <div
              key={`${node.id}-${node.type}-${index}`}
              className={`list-item ${selectedNode === node.id ? 'selected' : ''}`}
              onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
            >
              <div className="row">
                <strong>{node.label}</strong>
                <span className="badge">{node.type === 'case' ? 'FIR' : 'Related'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
