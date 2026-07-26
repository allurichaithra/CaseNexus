from contextlib import asynccontextmanager
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

import pandas as pd
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_loader import (
    load_dataset,
    dataframe_summary,
    DATASET_DIR,
)
from intelligence.case_fingerprinting import CaseFingerprintingEngine
from intelligence.related_fir_engine import RelatedFIREngine
from intelligence.entity_resolution import EntityResolutionEngine


# ---------------------------------------------------------
# GLOBAL DATA
# ---------------------------------------------------------

DATA = {}
INTELLIGENCE = {}

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
CASE_LINK_CSV = os.path.join(PROCESSED_DIR, "CaseLinkResult.csv")
ENTITY_MATCH_CSV = os.path.join(PROCESSED_DIR, "EntityMatchResult.csv")


# ---------------------------------------------------------
# PYDANTIC MODELS
# ---------------------------------------------------------

class CaseLinkAction(BaseModel):
    target_case_id: int
    status: str = Field(..., pattern=r"^(CONFIRMED|REJECTED)$")
    officer_kgid: str = "IO_DEMO_01"
    notes: str | None = None


class EntityMatchAction(BaseModel):
    entity_a_id: int
    entity_b_id: int
    status: str = Field(..., pattern=r"^(CONFIRMED|REJECTED)$")
    officer_kgid: str = "IO_DEMO_01"
    notes: str | None = None


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def clean_value(value):
    """
    Convert pandas/numpy values into JSON-safe Python values.
    """

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def deep_clean(value):
    """
    Recursively clean a value, dict, or list of numpy/pandas types.
    """
    if isinstance(value, dict):
        return {k: deep_clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [deep_clean(v) for v in value]
    return clean_value(value)


def row_to_dict(row):

    return {
        column: clean_value(value)
        for column, value in row.to_dict().items()
    }


def find_column(df, possible_names):
    """
    Find a column without depending on exact capitalization.
    """

    lookup = {
        str(column).lower(): column
        for column in df.columns
    }

    for name in possible_names:

        if name.lower() in lookup:
            return lookup[name.lower()]

    return None


# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    global DATA, INTELLIGENCE

    try:

        DATA = load_dataset()

        # Build engines once
        fingerprint_engine = CaseFingerprintingEngine(DATA)
        entity_engine = EntityResolutionEngine(DATA)

        # Precompute fingerprints as dict by case_id for O(1) lookup
        fingerprints_list = fingerprint_engine.build_fingerprints()
        fingerprint_cache = {
            fp['case_master_id']: fp
            for fp in fingerprints_list
            if fp.get('case_master_id') is not None
        }

        # Build inverted index: token → set of case_ids
        # Eliminates O(n²) full-table scan during narrative matching
        inverted_index = defaultdict(set)
        cases = DATA.get('cases', pd.DataFrame())
        case_id_col = find_column(cases, ['CaseMasterID', 'case_master_id'])
        if case_id_col:
            for _, row in cases.iterrows():
                cid = int(row[case_id_col])
                text = str(row.get('BriefFacts') or '').lower()
                text = re.sub(r'[^a-z0-9\s]', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                for token in text.split():
                    if len(token) >= 3:
                        inverted_index[token].add(cid)

        # Precompute accused names per case for O(1) entity scoring
        case_accused_names = defaultdict(set)
        accused = DATA.get('accused', pd.DataFrame())
        accused_case_col = find_column(accused, ['CaseMasterID', 'case_master_id'])
        if accused_case_col:
            for _, row in accused.iterrows():
                name = str(row.get('AccusedName') or '').strip().lower()
                if name:
                    case_accused_names[int(row[accused_case_col])].add(name)

        # Precompute act sections per case for O(1) legal scoring
        case_act_sections = defaultdict(list)
        act_sections_df = DATA.get('act_sections', pd.DataFrame())
        act_case_col = find_column(act_sections_df, ['CaseMasterID', 'case_master_id'])
        if act_case_col:
            for _, row in act_sections_df.iterrows():
                if pd.notna(row.get('ActID')) and pd.notna(row.get('SectionID')):
                    case_act_sections[int(row[act_case_col])].append(
                        f"{row.get('ActID')}:{row.get('SectionID')}"
                    )

        # Build related engine with precomputed indexes (no per-request rebuilds)
        related_engine = RelatedFIREngine(
            DATA,
            inverted_index=inverted_index,
            case_accused_names=case_accused_names,
            case_act_sections=case_act_sections,
        )

        INTELLIGENCE = {
            'fingerprints': fingerprint_cache,
            'related_engine': related_engine,
            'entity_engine': entity_engine,
            'related_cases': {},
        }

        print("\nDataset loaded successfully.")

        for table, info in dataframe_summary(DATA).items():

            print(
                f"{table}: "
                f"{info['rows']} rows"
            )

    except Exception as error:

        print("\nDATASET LOADING ERROR")
        print(error)

        raise error

    yield

    DATA.clear()
    INTELLIGENCE.clear()


# ---------------------------------------------------------
# APP
# ---------------------------------------------------------

app = FastAPI(
    title="Explainable Crime Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)


# React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "message": "Crime Intelligence API is running",
        "dataset_path": str(DATASET_DIR),
        "cases_loaded": len(
            DATA.get(
                "cases",
                pd.DataFrame()
            )
        ),
    }


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------

@app.get("/api/dataset-info")
def dataset_info():

    return dataframe_summary(DATA)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.get("/api/dashboard")
def dashboard():

    cases = DATA.get("cases", pd.DataFrame())
    accused = DATA.get("accused", pd.DataFrame())
    victims = DATA.get("victims", pd.DataFrame())
    gt_links = DATA.get("ground_truth_case_links", pd.DataFrame())

    district_column = find_column(
        cases,
        [
            "DistrictID",
            "district_id",
        ],
    )

    unit_column = find_column(
        cases,
        [
            "UnitID",
            "unit_id",
        ],
    )

    major_head_column = find_column(
        cases,
        [
            "CrimeMajorHeadID",
            "crime_major_head_id",
        ],
    )

    result = {
        "total_cases": len(cases),
        "total_accused_records": len(accused),
        "total_victim_records": len(victims),
        "total_districts": (
            int(cases[district_column].nunique())
            if district_column and not cases.empty
            else 0
        ),
        "total_units": (
            int(cases[unit_column].nunique())
            if unit_column and not cases.empty
            else 0
        ),
        "crime_categories": (
            int(cases[major_head_column].nunique())
            if major_head_column and not cases.empty
            else 0
        ),
        "ground_truth_case_links": len(gt_links),
        "fingerprints_generated": len(INTELLIGENCE.get("fingerprints", {})),
    }

    return result


# ---------------------------------------------------------
# FIR LIST
# ---------------------------------------------------------

@app.get("/api/firs")
def get_firs(
    limit: int | None = Query(
        default=50,
        ge=1,
        le=5000,
    ),
    offset: int | None = Query(
        default=0,
        ge=0,
    ),
):

    def coerce_value(value, default):
        if value is None:
            return default
        if hasattr(value, 'default') and getattr(value, 'default', None) is not None:
            return int(value.default)
        if hasattr(value, 'value'):
            return int(value.value)
        return int(value)

    resolved_limit = coerce_value(limit, 50)
    resolved_offset = coerce_value(offset, 0)

    cases = DATA.get("cases", pd.DataFrame())
    if cases.empty:
        return {
            "total": 0,
            "limit": resolved_limit,
            "offset": resolved_offset,
            "items": [],
        }

    page = cases.iloc[
        resolved_offset : resolved_offset + resolved_limit
    ]

    return {
        "total": len(cases),
        "limit": resolved_limit,
        "offset": resolved_offset,
        "items": [
            row_to_dict(row)
            for _, row in page.iterrows()
        ],
    }


# ---------------------------------------------------------
# FIR DETAIL
# ---------------------------------------------------------

@app.get("/api/firs/{case_id}")
def get_fir(case_id: int):

    cases = DATA.get("cases", pd.DataFrame())

    case_id_column = find_column(
        cases,
        [
            "CaseMasterID",
            "case_master_id",
        ],
    )

    if cases.empty or case_id_column is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "CaseMasterID column could not "
                "be identified."
            ),
        )

    matching_cases = cases[
        cases[case_id_column] == case_id
    ]

    if matching_cases.empty:

        raise HTTPException(
            status_code=404,
            detail="FIR not found",
        )

    case = row_to_dict(
        matching_cases.iloc[0]
    )

    # ---------------------------------------------
    # RELATED ACCUSED
    # ---------------------------------------------

    accused_records = []

    accused = DATA["accused"]

    accused_case_column = find_column(
        accused,
        [
            "CaseMasterID",
            "case_master_id",
        ],
    )

    if (
        not accused.empty
        and accused_case_column
    ):

        rows = accused[
            accused[accused_case_column]
            == case_id
        ]

        accused_records = [
            row_to_dict(row)
            for _, row in rows.iterrows()
        ]

    # ---------------------------------------------
    # RELATED VICTIMS
    # ---------------------------------------------

    victim_records = []

    victims = DATA["victims"]

    victim_case_column = find_column(
        victims,
        [
            "CaseMasterID",
            "case_master_id",
        ],
    )

    if (
        not victims.empty
        and victim_case_column
    ):

        rows = victims[
            victims[victim_case_column]
            == case_id
        ]

        victim_records = [
            row_to_dict(row)
            for _, row in rows.iterrows()
        ]

    # ---------------------------------------------
    # ACT / SECTION RECORDS
    # ---------------------------------------------

    section_records = []

    sections = DATA.get("act_sections", pd.DataFrame())

    section_case_column = find_column(
        sections,
        [
            "CaseMasterID",
            "case_master_id",
        ],
    )

    if (
        not sections.empty
        and section_case_column
    ):

        rows = sections[
            sections[section_case_column]
            == case_id
        ]

        section_records = [
            row_to_dict(row)
            for _, row in rows.iterrows()
        ]

    fingerprint = deep_clean(INTELLIGENCE['fingerprints'].get(case_id, {}))

    return {
        "case": case,
        "accused": accused_records,
        "victims": victim_records,
        "act_sections": section_records,
        "fingerprint": fingerprint,
    }


@app.get("/api/firs/{case_id}/related")
def get_related_firs(case_id: int, limit: int = Query(default=10, ge=1, le=25)):
    if case_id not in INTELLIGENCE['related_cases']:
        INTELLIGENCE['related_cases'][case_id] = INTELLIGENCE['related_engine'].find_related_cases(case_id, limit=25)
    cached = INTELLIGENCE['related_cases'][case_id]
    return {
        'case_id': case_id,
        'count': min(limit, len(cached)),
        'items': cached[:limit],
    }


@app.get("/api/entities")
def get_entities(limit: int = Query(default=20, ge=1, le=100)):
    matches = INTELLIGENCE['entity_engine'].find_candidate_matches(limit=limit)
    return {
        "count": len(matches),
        "items": matches,
    }


@app.get("/api/entities/decisions")
def get_entity_decisions():
    df = _read_csv_safe(ENTITY_MATCH_CSV)
    if df.empty:
        return {"count": 0, "decisions": []}

    decisions = []
    for _, row in df.iterrows():
        decisions.append(deep_clean({
            "entity_a_id": row.get("AccusedMasterID_A"),
            "entity_b_id": row.get("AccusedMasterID_B"),
            "confidence": row.get("MatchConfidence"),
            "status": row.get("OfficerDecision"),
            "officer_id": row.get("ReviewedByOfficerID"),
            "timestamp": row.get("Timestamp"),
        }))

    return {"count": len(decisions), "decisions": decisions}


@app.get("/api/entities/{entity_id}")
def get_entity(entity_id: int):
    accused = DATA.get("accused", pd.DataFrame())
    accused_id_col = find_column(accused, ['AccusedMasterID', 'accused_master_id'])
    if accused.empty or accused_id_col is None:
        raise HTTPException(status_code=404, detail='Entity not found')
    row = accused[accused[accused_id_col] == entity_id]
    if row.empty:
        raise HTTPException(status_code=404, detail='Entity not found')
    return {
        'entity': row_to_dict(row.iloc[0]),
    }


@app.get("/api/entities/{entity_id}/cases")
def get_entity_cases(entity_id: int):
    accused = DATA.get("accused", pd.DataFrame())
    case_col = find_column(accused, ['CaseMasterID', 'case_master_id'])
    accused_id_col = find_column(accused, ['AccusedMasterID', 'accused_master_id'])
    if accused.empty or case_col is None or accused_id_col is None:
        return {'entity_id': entity_id, 'cases': []}
    rows = accused[accused[accused_id_col] == entity_id]
    if rows.empty:
        return {'entity_id': entity_id, 'cases': []}
    return {
        'entity_id': entity_id,
        'cases': [int(value) for value in rows[case_col].dropna().astype(int).tolist()],
    }


@app.get("/api/hotspots")
def get_hotspots(limit: int = Query(default=10, ge=1, le=5000)):
    cases = DATA.get('cases', pd.DataFrame())
    if cases.empty:
        return {'items': []}
    lat_col = find_column(cases, ['latitude'])
    lon_col = find_column(cases, ['longitude'])
    major_col = find_column(cases, ['CrimeMajorHeadID', 'crime_major_head_id'])
    items = []
    for _, row in cases.iterrows():
        if lat_col and lon_col and not pd.isna(row.get(lat_col)) and not pd.isna(row.get(lon_col)):
            items.append({
                'case_id': int(row.get('CaseMasterID')) if not pd.isna(row.get('CaseMasterID')) else None,
                'latitude': float(row.get(lat_col)),
                'longitude': float(row.get(lon_col)),
                'crime_major_head_id': row.get(major_col) if major_col else None,
            })
    return {'count': len(items), 'items': items[:limit]}


@app.get("/api/trends")
def get_trends():
    cases = DATA.get('cases', pd.DataFrame())
    if cases.empty:
        return {'daily': {}, 'monthly': {}}

    date_col = find_column(cases, ['CrimeRegisteredDate', 'crime_registered_date'])
    if not date_col:
        return {'daily': {}, 'monthly': {}}

    parsed_dates = pd.to_datetime(cases[date_col], errors='coerce').dropna()
    daily = {
        str(value): int(count)
        for value, count in parsed_dates.dt.strftime('%Y-%m-%d').value_counts().sort_index().items()
    }
    monthly = {
        str(period): int(count)
        for period, count in parsed_dates.dt.to_period('M').value_counts().sort_index().items()
    }

    return {
        'daily': daily,
        'monthly': monthly,
    }


@app.get("/api/network")
def get_network(case_id: int | None = None):
    cases = DATA.get('cases', pd.DataFrame())
    if cases.empty:
        return {'nodes': [], 'edges': []}
    nodes = []
    edges = []
    case_id_col = find_column(cases, ['CaseMasterID', 'case_master_id'])
    if case_id_col is None:
        return {'nodes': [], 'edges': []}
    target_cases = cases if case_id is None else cases[cases[case_id_col] == case_id]
    for _, row in target_cases.iterrows():
        nodes.append({'id': int(row.get(case_id_col)), 'type': 'case', 'label': f"FIR {row.get(case_id_col)}"})
    if case_id is not None and not target_cases.empty:
        related = INTELLIGENCE['related_engine'].find_related_cases(case_id, limit=5)
        for item in related:
            nodes.append({'id': item['related_case_id'], 'type': 'related_case', 'label': f"FIR {item['related_case_id']}"})
            edges.append({'source': case_id, 'target': item['related_case_id'], 'label': 'related'})
    return {'nodes': nodes, 'edges': edges}


@app.get("/api/evaluation")
def get_evaluation():
    gt_case_links = DATA.get('ground_truth_case_links', pd.DataFrame())
    gt_entities = DATA.get('ground_truth_entity_matches', pd.DataFrame())
    return {
        'case_link_ground_truth': {
            'rows': len(gt_case_links),
            'columns': list(gt_case_links.columns),
        },
        'entity_match_ground_truth': {
            'rows': len(gt_entities),
            'columns': list(gt_entities.columns),
        },
    }


# ---------------------------------------------------------
# CSV PERSISTENCE HELPERS
# ---------------------------------------------------------

def _read_csv_safe(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df.where(pd.notna(df), None)
        return df
    return pd.DataFrame()


def _write_csv_safe(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# ---------------------------------------------------------
# CASE LINK DECISIONS
# ---------------------------------------------------------

@app.post("/api/firs/{case_id}/related/action")
def decide_case_link(case_id: int, action: CaseLinkAction):
    df = _read_csv_safe(CASE_LINK_CSV)
    if df.empty:
        raise HTTPException(status_code=500, detail="CaseLinkResult.csv not found")

    query_col = "QueryCaseMasterID"
    candidate_col = "CandidateCaseMasterID"

    mask = (df[query_col] == case_id) & (df[candidate_col] == action.target_case_id)
    if not mask.any():
        mask = (df[query_col] == action.target_case_id) & (df[candidate_col] == case_id)

    if not mask.any():
        raise HTTPException(status_code=404, detail="No proposed link found for this pair")

    now = datetime.now(timezone.utc).isoformat()

    for col in ["OfficerDecision", "ReviewedByOfficerID", "Timestamp"]:
        if col in df.columns and df[col].dtype != object:
            df[col] = df[col].astype(object)

    df.loc[mask, "OfficerDecision"] = action.status
    df.loc[mask, "ReviewedByOfficerID"] = action.officer_kgid
    df.loc[mask, "Timestamp"] = now

    _write_csv_safe(df, CASE_LINK_CSV)

    return {
        "ok": True,
        "case_id": case_id,
        "target_case_id": action.target_case_id,
        "status": action.status,
        "officer_kgid": action.officer_kgid,
        "timestamp": now,
    }


@app.get("/api/firs/{case_id}/related/decisions")
def get_case_link_decisions(case_id: int):
    df = _read_csv_safe(CASE_LINK_CSV)
    if df.empty:
        return {"case_id": case_id, "decisions": []}

    query_col = "QueryCaseMasterID"
    candidate_col = "CandidateCaseMasterID"

    mask = (df[query_col] == case_id) | (df[candidate_col] == case_id)
    subset = df[mask]

    decisions = []
    for _, row in subset.iterrows():
        decisions.append(deep_clean({
            "query_case_id": row.get("QueryCaseMasterID"),
            "candidate_case_id": row.get("CandidateCaseMasterID"),
            "confidence": row.get("OverallConfidence"),
            "status": row.get("OfficerDecision"),
            "officer_id": row.get("ReviewedByOfficerID"),
            "timestamp": row.get("Timestamp"),
        }))

    return {"case_id": case_id, "count": len(decisions), "decisions": decisions}


# ---------------------------------------------------------
# ENTITY MATCH DECISIONS
# ---------------------------------------------------------

@app.post("/api/entities/action")
def decide_entity_match(action: EntityMatchAction):
    df = _read_csv_safe(ENTITY_MATCH_CSV)
    if df.empty:
        raise HTTPException(status_code=500, detail="EntityMatchResult.csv not found")

    col_a = "AccusedMasterID_A"
    col_b = "AccusedMasterID_B"

    mask = (df[col_a] == action.entity_a_id) & (df[col_b] == action.entity_b_id)
    if not mask.any():
        mask = (df[col_a] == action.entity_b_id) & (df[col_b] == action.entity_a_id)

    if not mask.any():
        raise HTTPException(status_code=404, detail="No proposed entity match found for this pair")

    now = datetime.now(timezone.utc).isoformat()

    for col in ["OfficerDecision", "ReviewedByOfficerID", "Timestamp"]:
        if col in df.columns and df[col].dtype != object:
            df[col] = df[col].astype(object)

    df.loc[mask, "OfficerDecision"] = action.status
    df.loc[mask, "ReviewedByOfficerID"] = action.officer_kgid
    df.loc[mask, "Timestamp"] = now

    _write_csv_safe(df, ENTITY_MATCH_CSV)

    return {
        "ok": True,
        "entity_a_id": action.entity_a_id,
        "entity_b_id": action.entity_b_id,
        "status": action.status,
        "officer_kgid": action.officer_kgid,
        "timestamp": now,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)