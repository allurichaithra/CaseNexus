# CaseNexus — Explainable Crime Intelligence Platform

A human-in-the-loop crime intelligence platform that links related FIRs and detects repeat accused across jurisdictions using explainable multi-signal scoring. AI proposes, officers decide — never auto-merging.

## Architecture

```
client/                 React 18 + Vite
  src/
    pages/              FIR Explorer, Hotspots, Entities, Case Detail
    services/api.js     HTTP client for all backend endpoints
    demo-config.js      Golden demo case IDs for pitch

server/                 FastAPI + Python 3.13
  main.py               API endpoints, global engine singletons
  intelligence/
    case_fingerprinting.py   Generates per-case feature vectors
    related_fir_engine.py    Multi-signal case linking with inverted index
    entity_resolution.py     Cross-case accused matching
  data/processed/
    CaseLinkResult.csv       Persisted case link decisions
    EntityMatchResult.csv    Persisted entity match decisions
```

## Quick Start

```bash
# Backend
cd server
pip install -r requirements.txt
python main.py              # Starts on http://localhost:8001

# Frontend (separate terminal)
cd client
npm install
npm run dev                 # Starts on http://localhost:5173
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard` | Aggregate stats |
| GET | `/api/firs?limit=&offset=` | Paginated FIR list |
| GET | `/api/firs/{id}` | FIR detail + accused + victims + act sections |
| GET | `/api/firs/{id}/related?limit=` | Related case recommendations |
| POST | `/api/firs/{id}/related/action` | Record officer CONFIRMED/REJECTED decision |
| GET | `/api/firs/{id}/related/decisions` | Retrieve decisions for a case |
| GET | `/api/entities?limit=` | Entity resolution candidates |
| POST | `/api/entities/action` | Record entity match decision |
| GET | `/api/entities/decisions` | Retrieve all entity decisions |
| GET | `/api/hotspots?limit=` | Geospatial crime coordinates |
| GET | `/api/trends` | Daily/monthly crime trends |
| GET | `/api/network?case_id=` | Case relationship graph |
| GET | `/api/evaluation` | Ground truth data info |

## How Case Linking Works

Each candidate pair is scored on four independent signals:

| Signal | Weight | What It Measures |
|--------|--------|------------------|
| Narrative | 25% | Token-level Brief Facts similarity via inverted index |
| Geographic | 30% | Distance between police stations (km buckets) |
| Crime Head | 15% | CrimeMajorHeadID / CrimeMinorHeadID match |
| Legal Sections | 10% | Shared IPC/BNS act-section pairs |
| Temporal | 10% | Days between crime registration dates |
| Entity | 10% | Shared accused names across cases |

Overall confidence = weighted sum. No black-box metrics — every number maps to an investigative signal.

## How Entity Resolution Works

Matches accused persons across FIRs using:

- **Full name match** (0.65 base score)
- **Surname-only match** (0.45 base score)
- **Age tolerance** within ±10 years
- **Shared case context** boost

Threshold: 0.40 minimum confidence.

## Human-in-the-Loop

1. Engine proposes related cases / entity matches with confidence scores
2. Officer reviews the evidence panel (narrative, geography, sections, temporal)
3. Officer clicks **CONFIRM** or **REJECT**
4. Decision persists to `CaseLinkResult.csv` / `EntityMatchResult.csv` with timestamp and officer ID
5. Cases are **never** auto-merged — every link requires human sign-off

## Performance

- Global engine singletons — no per-request instantiation
- Inverted index for O(token) narrative lookup instead of O(n) full scan
- Precomputed accused names and act sections for O(1) scoring
- Lazy related-cases cache — first request computes, subsequent requests return instantly
- Cached `/api/firs/{id}/related`: ~8ms response time

## Golden Demo Cases

| Demo | IDs | Confidence | Why It Works |
|------|-----|------------|--------------|
| Case Link | FIR 1792 → FIR 2823 | 80% | Identical chain-snatching narrative, same district |
| Cross-Jurisdiction | FIR 803 → FIR 2917 | 90% | Same modus operandi across different districts |
| Entity Resolution | "Sunita Kulkarni" | — | Appears across 56 FIRs |

See `DEMO_SCRIPT.md` for the full 3-minute pitch sequence.

## Tech Stack

- **Frontend:** React 18, React Router, React-Leaflet, Recharts, Vite
- **Backend:** FastAPI, Pandas, Python 3.13
- **Data:** CSV-based persistence (3,003 cases, 5,317 accused records)
- **Maps:** CARTO light basemap via OpenStreetMap tiles

## Dataset

Synthetic crime dataset generated for the Datathon 2026 challenge. Contains:

- `CaseMaster.csv` — 3,003 FIR records with coordinates, crime heads, narratives
- `Accused.csv` — 5,317 accused persons linked to cases
- `Victims.csv` — Victim records
- `ActSection.csv` — IPC/BNS sections per case
- `GroundTruthCaseLink.csv` — 16 verified case link pairs
- `GroundTruthEntityMatch.csv` — 10 verified entity match pairs

## Evaluation

Run the evaluation pipeline:

```bash
cd server
python generate_outputs.py
```

Results saved to `server/evaluation/`:
- `case_link_evaluation.json` — 4/16 ground truth recall
- `entity_match_evaluation.json` — 10/10 ground truth recall

## Project Structure

```
crime-intelligence-platform/
├── client/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── FirsPage.jsx          FIR Explorer with pagination
│   │   │   ├── CaseDetailPage.jsx    Full FIR record + related cases
│   │   │   ├── HotspotsPage.jsx      Map + search + viewport filtering
│   │   │   ├── EntitiesPage.jsx      Repeat accused queue
│   │   │   └── DashboardPage.jsx     Overview stats
│   │   ├── services/api.js           All API calls
│   │   ├── demo-config.js            Demo case IDs
│   │   └── App.jsx                   Router
│   └── package.json
├── server/
│   ├── main.py                       FastAPI app + endpoints
│   ├── data_loader.py                CSV ingestion
│   ├── intelligence/
│   │   ├── case_fingerprinting.py    Feature vector generation
│   │   ├── related_fir_engine.py     Case linking engine
│   │   └── entity_resolution.py      Entity matching engine
│   ├── generate_outputs.py           Evaluation pipeline
│   ├── data/
│   │   └── processed/                Decision CSVs
│   └── evaluation/                   Accuracy reports
├── DEMO_SCRIPT.md                    3-minute pitch script
└── README.md
```
