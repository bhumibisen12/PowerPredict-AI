"""
Agent 1: Cost Prediction Agent (ML / XGBoost)
Responsible for computing projected project cost, cost overrun %, confidence bounds,
and isolating monetary financial exposure across work packages.
"""

from typing import Dict, Any
from backend.ml_engine import ml_engine

class CostPredictionAgent:
    def __init__(self):
        self.name = "Cost Prediction Agent"
        self.agent_id = "agent_01_cost"
        self.role = "Supervised Machine Learning & Financial Risk Attribution"
        self.model_framework = "Tuned XGBoost Regressor (Trained on 6,000+ Verified Power Projects across 36 States/UTs)"

    def execute(self, project_data: Dict[str, Any], risk_factors: Dict[str, float]) -> Dict[str, Any]:
        logs = []
        logs.append(f"[{self.name}] Initializing feature vector for {project_data.get('capacity_mw')} MW {project_data.get('project_type')} project.")
        logs.append(f"[{self.name}] Reading base estimated cost: ₹{project_data.get('estimated_cost_cr')} Cr.")
        
        # Execute ML model
        preds = ml_engine.predict(project_data, risk_factors)
        cost_info = preds["predicted_cost"]
        
        logs.append(f"[{self.name}] XGBoost Regressor computed predicted cost: {cost_info['formatted']} (Overrun: {cost_info['overrun_formatted']}, +₹{cost_info['overrun_cr']} Cr).")
        logs.append(f"[{self.name}] Statistical confidence level: {int(cost_info['confidence']*100)}% (R² = {preds['model_metadata']['cost_r2_score']}).")
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "COMPLETED",
            "logs": logs,
            "output": cost_info,
            "model_metadata": preds["model_metadata"]
        }
