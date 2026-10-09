"""
PowerPredict AI - FastAPI Application Server
Integrates Multi-Factor ML Models & Autonomous Agents with REST APIs and Web Hosting.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import BASE_DIR, INDIAN_POWER_STATES, PROJECT_TYPES, ALERT_LEVELS
from backend.agents.orchestrator import orchestrator
from backend.evidence_bundler import evidence_bundler
from backend.rag_engine import rag_engine
from backend.auth_service import auth_service

app = FastAPI(
    title="PowerPredict AI",
    description="National Enterprise Platform for Predicting Delays & Cost Overruns in Indian Power Sector Projects",
    version="2.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ProjectSubmission(BaseModel):
    project_id: Optional[str] = "PP-DL-2026-001"
    name: Optional[str] = "Utility Power Project"
    project_type: str = "Solar Photovoltaic (Ground-Mounted)"
    capacity_mw: float = 500.0
    state: str = "Rajasthan"
    district: Optional[str] = "Jaisalmer"
    land_area_acres: float = 500.0
    estimated_cost_cr: float = 500.0
    estimated_timeline_months: int = 18
    contractor_tier: Optional[str] = "Tier-2 (Sterling & Wilson, Vikram Solar)"
    environmental_category: Optional[str] = "Category-B1 (SEIAA)"
    
    # 6 Risk Factors
    land_acquisition_risk: float = Field(default=0.85, ge=0.0, le=1.0)
    environmental_clearance_risk: float = Field(default=0.65, ge=0.0, le=1.0)
    contractor_track_record_risk: float = Field(default=0.75, ge=0.0, le=1.0)
    weather_climate_risk: float = Field(default=0.30, ge=0.0, le=1.0)
    supply_chain_risk: float = Field(default=0.55, ge=0.0, le=1.0)
    financing_risk: float = Field(default=0.40, ge=0.0, le=1.0)

class WhatIfScenario(BaseModel):
    base_project: ProjectSubmission
    interventions: Dict[str, float]

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    organization: Optional[str] = "State Power Board"
    role: Optional[str] = "Project Director"
    site_url: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ResendVerificationRequest(BaseModel):
    email: str
    site_url: Optional[str] = None

evidence_store: Dict[str, Any] = {}

# ============================================================================
# ENTERPRISE AUTHENTICATION & EMAIL VERIFICATION APIS
# ============================================================================

@app.post("/api/auth/signup")
def auth_signup(payload: SignupRequest):
    site = payload.site_url or "http://localhost:8000"
    res = auth_service.register_user(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        organization=payload.organization or "State Power Board",
        role=payload.role or "Project Director",
        site_url=site
    )
    if not res.get("success"):
        return JSONResponse(status_code=400, content=res)
    return res

@app.post("/api/auth/login")
def auth_login(payload: LoginRequest):
    res = auth_service.login_user(payload.email, payload.password)
    if not res.get("success"):
        if res.get("code") == "EMAIL_NOT_VERIFIED":
            return JSONResponse(status_code=403, content=res)
        return JSONResponse(status_code=401, content=res)
    return res

@app.get("/api/auth/verify")
def auth_verify(token: str):
    res = auth_service.verify_email_token(token)
    if not res.get("success"):
        return JSONResponse(status_code=400, content=res)
    return res

@app.post("/api/auth/resend-verification")
def auth_resend(payload: ResendVerificationRequest):
    site = payload.site_url or "http://localhost:8000"
    res = auth_service.resend_verification_email(payload.email, site)
    if not res.get("success"):
        return JSONResponse(status_code=400, content=res)
    return res


@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "PowerPredict AI",
        "pillars_active": 4,
        "agents_ready": 5,
        "states_tracked": len(INDIAN_POWER_STATES),
        "version": "2.1.0"
    }

@app.get("/api/metadata")
def get_metadata():
    return {
        "project_types": PROJECT_TYPES,
        "states": list(INDIAN_POWER_STATES.keys()),
        "state_details": INDIAN_POWER_STATES,
        "alert_levels": ALERT_LEVELS
    }

@app.post("/api/predict")
def predict_project(submission: ProjectSubmission):
    try:
        project_dict = {
            "project_id": submission.project_id or "PP-DL-2026-001",
            "name": submission.name or "Utility Power Project",
            "project_type": submission.project_type,
            "capacity_mw": submission.capacity_mw,
            "state": submission.state,
            "district": submission.district or "District HQ",
            "land_area_acres": submission.land_area_acres,
            "estimated_cost_cr": submission.estimated_cost_cr,
            "estimated_timeline_months": submission.estimated_timeline_months,
            "contractor_tier": submission.contractor_tier,
            "environmental_category": submission.environmental_category
        }

        risk_factors = {
            "land_acquisition": submission.land_acquisition_risk,
            "environmental_clearance": submission.environmental_clearance_risk,
            "contractor_track_record": submission.contractor_track_record_risk,
            "weather_climate": submission.weather_climate_risk,
            "supply_chain": submission.supply_chain_risk,
            "financing": submission.financing_risk
        }

        # Run 5-agent orchestrator pipeline
        pipeline_output = orchestrator.run_pipeline(project_dict, risk_factors)

        # Generate standardized evidence bundle
        bundle = evidence_bundler.create_evidence_bundle(pipeline_output)
        evidence_store[submission.project_id] = bundle
        pipeline_output["evidence_bundle"] = bundle

        return pipeline_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/what-if")
def simulate_what_if(scenario: WhatIfScenario):
    """
    Simulates impact of preventive management interventions compared to original baseline.
    """
    try:
        base = scenario.base_project
        base_factors = {
            "land_acquisition": base.land_acquisition_risk,
            "environmental_clearance": base.environmental_clearance_risk,
            "contractor_track_record": base.contractor_track_record_risk,
            "weather_climate": base.weather_climate_risk,
            "supply_chain": base.supply_chain_risk,
            "financing": base.financing_risk
        }
        base_dict = {
            "project_id": base.project_id,
            "name": base.name,
            "project_type": base.project_type,
            "capacity_mw": base.capacity_mw,
            "state": base.state,
            "district": base.district,
            "land_area_acres": base.land_area_acres,
            "estimated_cost_cr": base.estimated_cost_cr,
            "estimated_timeline_months": base.estimated_timeline_months,
            "contractor_tier": base.contractor_tier,
            "environmental_category": base.environmental_category
        }
        base_res = orchestrator.run_pipeline(base_dict, base_factors)

        # Intervened run
        sim_factors = dict(base_factors)
        for k, delta in scenario.interventions.items():
            if k in sim_factors:
                sim_factors[k] = max(0.10, min(0.95, sim_factors[k] + delta))

        sim_res = orchestrator.run_pipeline(base_dict, sim_factors)

        timeline_delta = base_res["predictions"]["predicted_timeline"]["value_months"] - sim_res["predictions"]["predicted_timeline"]["value_months"]
        cost_delta = round(base_res["predictions"]["predicted_cost"]["value_cr"] - sim_res["predictions"]["predicted_cost"]["value_cr"], 1)

        return {
            "baseline": {
                "predicted_timeline_months": base_res["predictions"]["predicted_timeline"]["value_months"],
                "predicted_cost_cr": base_res["predictions"]["predicted_cost"]["value_cr"],
                "delay_risk_score": base_res["delay_risk_assessment"]["overall_score"]
            },
            "simulated": {
                "predicted_timeline_months": sim_res["predictions"]["predicted_timeline"]["value_months"],
                "predicted_cost_cr": sim_res["predictions"]["predicted_cost"]["value_cr"],
                "delay_risk_score": sim_res["delay_risk_assessment"]["overall_score"]
            },
            "savings": {
                "months_saved": max(0, timeline_delta),
                "cost_saved_cr": max(0.0, cost_delta),
                "risk_score_reduction": round(base_res["delay_risk_assessment"]["overall_score"] - sim_res["delay_risk_assessment"]["overall_score"], 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evidence-bundle/{project_id}")
def get_bundle(project_id: str):
    if project_id in evidence_store:
        return evidence_store[project_id]
    raise HTTPException(status_code=404, detail="Evidence bundle not found")

@app.get("/api/national-overview")
def get_national_overview():
    """Returns India all-states power capex & delay baseline analytics."""
    state_stats = []
    for state_name, info in INDIAN_POWER_STATES.items():
        ongoing_mw = round(info["solar_potential_gw"] * 110, 0)
        risk_index = round(0.35 + (info["avg_land_delay_months"] / 38.0), 2)
        state_stats.append({
            "state": state_name,
            "ongoing_capacity_mw": ongoing_mw,
            "solar_potential_gw": info["solar_potential_gw"],
            "avg_land_delay_months": info["avg_land_delay_months"],
            "avg_delay_risk_index": risk_index,
            "risk_band": "Critical" if risk_index >= 0.75 else ("High" if risk_index >= 0.65 else ("Medium" if risk_index >= 0.50 else "Low")),
            "zone": info.get("zone", "General"),
            "critical_hazard": "Land Title Disputes & Private Litigation" if info["avg_land_delay_months"] > 14 else ("Forest & Wildlife Clearances" if info["forest_cover_pct"] > 30 else "Transmission Grid Interconnection")
        })
    return {"states": state_stats, "total_states": len(state_stats)}

@app.get("/api/knowledge-base")
def get_kb(query: Optional[str] = None):
    if query:
        docs = rag_engine.retrieve(query, top_k=5)
    else:
        docs = rag_engine.documents
    return {"documents": docs, "total": len(docs)}

FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "PowerPredict AI Backend is running."}
