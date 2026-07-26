# CaseNexus — Explainable Crime Intelligence Platform

CaseNexus is a hackathon-ready crime intelligence prototype that connects FIR records, surfaces explainable related-case signals, and helps investigators explore entity matches, hotspots, network patterns, and trend analytics from a single workspace.

> Connecting cases. Revealing patterns. Accelerating investigations.

## Problem

Investigative teams often need to work across fragmented FIR data, multiple case records, and supporting entities without a clear, explainable way to identify likely relationships. This project addresses that gap by combining structured crime data with deterministic, explainable intelligence signals to support case triage and investigative analysis.

## Solution

CaseNexus builds a lightweight intelligence pipeline over a synthetic crime dataset and exposes it through a React-based dashboard plus a FastAPI backend. The system generates:

- case fingerprints for each FIR/case record
- explainable related-FIR candidates based on narrative, crime, legal, geographic, temporal, and entity evidence
- entity match candidates for accused-person resolution
- hotspot, network, and trend views for operational analysis

## What is implemented

### Core capabilities

- FIR browsing and detail inspection
- Explainable related-case intelligence with ranked scores and evidence-based explanations
- Entity intelligence for accused identity matching candidates
- Crime hotspot mapping using case coordinates
- Investigation network visualization for selected cases
- Analytics dashboards for daily and monthly trends
- Evaluation artifacts derived from the available ground-truth data

### Explainable related-FIR intelligence

The backend uses a deterministic scoring engine to rank likely related cases for a selected FIR. The scoring combines:

- narrative similarity from brief facts
- matching crime major head
- overlapping legal sections
- geographic proximity
- temporal proximity
- shared accused identity

Each candidate returns an explanation string describing the evidence that contributed to the score.

### Entity intelligence

The entity engine generates candidate accused-entity matches using a lightweight rule-based approach. It considers:

- normalized name token overlap
- compatible age window
- matching gender

Matches are returned with confidence and evidence lists.

### Hotspots, networks, and analytics

The frontend includes separate views for:

- crime hotspots on an interactive map
- an investigation network graph for case relationships
- trend analytics for daily and monthly activity

## Architecture

The project is organized into two main layers:

- Frontend: React + Vite + React Router + Recharts + Leaflet
- Backend: FastAPI service with pandas-based data loading and deterministic intelligence engines

### Backend modules

- [server/main.py](server/main.py): FastAPI application, endpoints, and startup logic
- [server/data_loader.py](server/data_loader.py): dataset discovery and CSV loading
- [server/intelligence/case_fingerprinting.py](server/intelligence/case_fingerprinting.py): case fingerprint generation
- [server/intelligence/related_fir_engine.py](server/intelligence/related_fir_engine.py): related-case scoring and explanation generation
- [server/intelligence/entity_resolution.py](server/intelligence/entity_resolution.py): accused entity match generation
- [server/generate_outputs.py](server/generate_outputs.py): produces processed CSV outputs and evaluation files

### Frontend modules

- [client/src/App.jsx](client/src/App.jsx): shell layout, navigation, and branding
- [client/src/pages](client/src/pages): dashboard, FIR explorer, related cases, entities, hotspots, network, and trends pages
- [client/src/services/api.js](client/src/services/api.js): frontend API client

## Tech stack

### Frontend

- React 18
- Vite
- React Router DOM
- Recharts
- Leaflet and react-leaflet
- Lucide icons

### Backend

- Python
- FastAPI
- Uvicorn
- pandas

## Dataset

The platform loads CSV files from the workspace dataset directory under the datathon generator output area. The backend expects tables such as:

- cases / CaseMaster
- accused
- victims
- act sections
- units
- districts
- crime heads and sub-heads
- ground-truth case links and entity matches

The current working dataset produced the following generated summary artifacts:

- 3003 case fingerprints
- 160 case-link rows
- 200 entity-match rows
- 16 ground-truth case-link rows
- 10 ground-truth entity-match rows

## APIs

The FastAPI backend exposes the following implemented endpoints:

- GET /health
- GET /api/dataset-info
- GET /api/dashboard
- GET /api/firs
- GET /api/firs/{case_id}
- GET /api/firs/{case_id}/related
- GET /api/entities
- GET /api/entities/{entity_id}
- GET /api/entities/{entity_id}/cases
- GET /api/hotspots
- GET /api/trends
- GET /api/network
- GET /api/evaluation

## Project structure

```text
crime-intelligence-platform/
  client/
    src/
      App.jsx
      pages/
      services/
  server/
    intelligence/
    tests/
    data_loader.py
    generate_outputs.py
    main.py
    requirements.txt
```

## Setup and run

### 1. Create and activate a Python environment

From the workspace root:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install backend dependencies

```bash
cd crime-intelligence-platform/server
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd ../client
npm install
```

### 4. Start the backend

```bash
cd ../server
python main.py
```

The API runs on http://127.0.0.1:8001.

### 5. Start the frontend

In a separate terminal:

```bash
cd ../client
npm run dev
```

The Vite app is served on http://localhost:5173 by default.

## Evaluation

The project includes evaluation support through generated outputs and summary JSON files in the server evaluation directory. The current implementation writes:

- case fingerprint CSV output
- case link result CSV output
- entity match result CSV output
- evaluation JSON files for case links and entity matches
- a summary JSON file describing counts

## Limitations

This implementation is intentionally lightweight and deterministic. Current limitations include:

- entity matching is rule-based rather than learned or probabilistic
- related-case scoring is heuristic and based on available structured fields
- hotspot and network views are derived from the available dataset and do not include advanced geospatial modeling
- the UI is a prototype designed for hackathon demonstration and exploration

## Future scope

Potential extensions include:

- integration with richer real-world crime data sources
- more advanced entity resolution and graph analytics
- temporal clustering and anomaly detection
- enhanced explainability and officer workflow tooling
- production-ready deployment, authentication, and audit trails

## Verification

The current implementation was verified against the repository contents and the frontend build configuration. The frontend branding was updated to CaseNexus and the tagline was added in the shell and document title without changing the app’s structure or behavior.
