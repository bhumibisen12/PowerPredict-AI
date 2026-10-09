"""
Agent 2: Timeline Prediction Agent (Time-Series & Temporal ML)
Responsible for projecting expected project completion milestones, delay months,
temporal slippage probability, and critical path bottleneck analysis.
"""

from typing import Dict, Any
from backend.ml_engine import ml_engine

class TimelinePredictionAgent:
    def __init__(self):
        self.name = "Timeline Prediction Agent"
        self.agent_id = "agent_02_timeline"
        self.role = "Temporal Milestone Forecasting & Schedule Risk Analytics"
        self.model_framework = "Multi-Factor Temporal Projection (Calibrated with CEA Historical Baselines)"

    def execute(self, project_data: Dict[str, Any], risk_factors: Dict[str, float]) -> Dict[str, Any]:
        logs = []
        logs.append(f"[{self.name}] Ingesting baseline schedule: {project_data.get('estimated_timeline_months')} months.")
        logs.append(f"[{self.name}] Evaluating temporal dependencies across civil, grid-evacuation, and licensing stages.")
        
        preds = ml_engine.predict(project_data, risk_factors)
        timeline_info = preds["predicted_timeline"]
        xai = preds["explainable_ai"]
        
        logs.append(f"[{self.name}] Projected actual timeline: {timeline_info['formatted']} (Delay: {timeline_info['delay_formatted']}).")
        logs.append(f"[{self.name}] Temporal Model Accuracy: R² = {preds['model_metadata']['timeline_r2_score']} (MAE: {preds['model_metadata']['timeline_mae_months']} mo).")
        logs.append(f"[{self.name}] Top critical path driver: {xai['feature_importance'][0]['factor']} (+{xai['feature_importance'][0]['delay_months_impact']} months).")
        
        # Build milestones schedule
        est_t = timeline_info["estimated_timeline_months"]
        pred_t = timeline_info["value_months"]
        
        milestones = [
            {"milestone": "Site Acquisition & Cadastral Demarcation", "baseline_month": round(est_t * 0.25, 1), "predicted_month": round(pred_t * 0.38, 1), "status": "At High Risk"},
            {"milestone": "Statutory Clearances (MoEFCC/SEIAA & PPA)", "baseline_month": round(est_t * 0.40, 1), "predicted_month": round(pred_t * 0.55, 1), "status": "Delayed"},
            {"milestone": "Civil Foundations & Sub-station Erection", "baseline_month": round(est_t * 0.70, 1), "predicted_month": round(pred_t * 0.80, 1), "status": "Pending"},
            {"milestone": "Transmission Interconnection & COD (Commercial Operation)", "baseline_month": est_t, "predicted_month": pred_t, "status": "Severe Slippage"}
        ]
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "COMPLETED",
            "logs": logs,
            "output": timeline_info,
            "milestones": milestones,
            "explainable_ai": xai
        }
