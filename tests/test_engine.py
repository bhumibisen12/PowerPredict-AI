"""
PowerPredict AI - Comprehensive Test Suite
Validates all 4 Pillars, 5 Autonomous Agents, Threat Scoring Formula, RAG, and Evidence Bundling.
"""

import pytest
from backend.risk_engine import calculate_delay_risk_score
from backend.ml_engine import ml_engine
from backend.rag_engine import rag_engine
from backend.agents.orchestrator import orchestrator
from backend.evidence_bundler import evidence_bundler

def test_multi_factor_delay_risk_formula():
    """Validates the exact 6-factor mathematical threat scoring formula."""
    factors = {
        "land_acquisition": 0.85,
        "environmental_clearance": 0.65,
        "contractor_track_record": 0.75,
        "weather_climate": 0.30,
        "supply_chain": 0.55,
        "financing": 0.40
    }
    
    result = calculate_delay_risk_score(factors)
    # 0.25*0.85 + 0.20*0.65 + 0.20*0.75 + 0.15*0.30 + 0.10*0.55 + 0.10*0.40 = 0.6325 -> 0.63
    assert result["overall_score"] == 0.63
    assert result["risk_level"] == "Medium-High"
    assert "Land Acquisition" in result["hotspots"]
    assert "Contractor Track Record" in result["hotspots"]
    assert result["alert_level_code"] == "LEVEL_2"

def test_ml_prediction_engine():
    """Validates Pillar 1 ML engine for cost & timeline prediction and XAI feature attributions."""
    project_data = {
        "project_type": "Solar Photovoltaic (Ground-Mounted)",
        "state": "Rajasthan",
        "capacity_mw": 500,
        "land_area_acres": 500,
        "estimated_cost_cr": 500,
        "estimated_timeline_months": 18,
        "contractor_tier": "Tier-2 (Sterling & Wilson, Vikram Solar)",
        "environmental_category": "Category-B1 (SEIAA)"
    }
    risk_factors = {
        "land_acquisition": 0.85,
        "environmental_clearance": 0.65,
        "contractor_track_record": 0.75,
        "weather_climate": 0.30,
        "supply_chain": 0.55,
        "financing": 0.40
    }
    
    preds = ml_engine.predict(project_data, risk_factors)
    assert "predicted_cost" in preds
    assert "predicted_timeline" in preds
    assert preds["predicted_cost"]["value_cr"] > 500
    assert preds["predicted_timeline"]["value_months"] > 18
    assert preds["predicted_cost"]["confidence"] >= 0.75
    assert len(preds["explainable_ai"]["feature_importance"]) == 6

def test_rag_recommendations_engine():
    """Validates Pillar 3 RAG retrieval and quantified savings synthesis."""
    project_details = {
        "type": "Solar Photovoltaic (Ground-Mounted)",
        "location": {"state": "Rajasthan", "district": "Jaisalmer"}
    }
    predictions = {
        "predicted_cost": {"value_cr": 680.0, "estimated_cost_cr": 500.0},
        "predicted_timeline": {"value_months": 28, "estimated_timeline_months": 18}
    }
    risk_assessment = {
        "hotspots": ["Land acquisition", "Environmental clearance", "Contractor performance"],
        "risk_factors": {
            "land_acquisition": {"score": 0.85},
            "environmental_clearance": {"score": 0.65},
            "contractor_track_record": {"score": 0.75},
            "supply_chain": {"score": 0.55}
        }
    }
    
    recs = rag_engine.generate_recommendations(project_details, predictions, risk_assessment)
    assert recs["total_months_saved"] >= 6
    assert recs["total_cost_saving_cr"] >= 40.0
    assert len(recs["actions"]) >= 3

def test_multi_agent_pipeline_and_evidence_bundle():
    """Validates complete 5-agent orchestration and cryptographic evidence bundle."""
    project_dict = {
        "project_id": "PP-DL-2026-001",
        "name": "Utility Power Project",
        "project_type": "Solar Photovoltaic (Ground-Mounted)",
        "capacity_mw": 500,
        "state": "Rajasthan",
        "district": "Jaisalmer",
        "land_area_acres": 500,
        "estimated_cost_cr": 500,
        "estimated_timeline_months": 18,
        "contractor_tier": "Tier-2 (Sterling & Wilson, Vikram Solar)",
        "environmental_category": "Category-B1 (SEIAA)"
    }
    risk_factors = {
        "land_acquisition": 0.85,
        "environmental_clearance": 0.65,
        "contractor_track_record": 0.75,
        "weather_climate": 0.30,
        "supply_chain": 0.55,
        "financing": 0.40
    }
    
    pipeline_res = orchestrator.run_pipeline(project_dict, risk_factors)
    assert pipeline_res["status"] == "SUCCESS"
    assert len(pipeline_res["agent_traces"]) == 5
    
    # Test Evidence Bundle
    bundle = evidence_bundler.create_evidence_bundle(pipeline_res)
    assert bundle["project_id"] == "PP-DL-2026-001"
    assert "audit_verification" in bundle
    assert len(bundle["audit_verification"]["sha256_hash"]) == 64
    assert bundle["alerts_sent"]["project_manager"] is True
    assert bundle["alerts_sent"]["contractor"] is True

if __name__ == "__main__":
    pytest.main(["-v", __file__])
