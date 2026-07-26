const configuredBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const API_BASE = configuredBase
  ? configuredBase.endsWith('/api')
    ? configuredBase
    : `${configuredBase}/api`
  : '/api';

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json();
}

async function requestPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed with ${response.status}`);
  }
  return response.json();
}

export async function getDashboard() {
  return request('/dashboard');
}

export async function getFirs(limit = 50) {
  return request(`/firs?limit=${limit}`);
}

export async function getFir(caseId) {
  return request(`/firs/${caseId}`);
}

export async function getRelatedCases(caseId, limit = 10) {
  return request(`/firs/${caseId}/related?limit=${limit}`);
}

export async function getEntities(limit = 20) {
  return request(`/entities?limit=${limit}`);
}

export async function getEntityCases(entityId) {
  return request(`/entities/${entityId}/cases`);
}

export async function getHotspots(limit = 50) {
  const safeLimit = Math.max(1, Math.min(50, Number(limit) || 50));
  return request(`/hotspots?limit=${safeLimit}`);
}

export async function getTrends() {
  return request('/trends');
}

export async function getNetwork(caseId) {
  return caseId ? request(`/network?case_id=${caseId}`) : request('/network');
}

export async function getEvaluation() {
  return request('/evaluation');
}

export async function decideCaseLink(caseId, payload) {
  return requestPost(`/firs/${caseId}/related/action`, payload);
}

export async function getCaseLinkDecisions(caseId) {
  return request(`/firs/${caseId}/related/decisions`);
}

export async function decideEntityMatch(payload) {
  return requestPost('/entities/action', payload);
}

export async function getEntityDecisions() {
  return request('/entities/decisions');
}
