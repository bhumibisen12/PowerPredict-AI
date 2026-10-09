"""
PowerPredict AI - Multi-Agent Orchestrator
Coordinates 5 autonomous specialized agents:
- Agent 1: Cost Prediction Agent (XGBoost Regressor)
- Agent 2: Timeline Prediction Agent (Time-Series & Temporal Model)
- Agent 3: Delay Hotspot Agent (Multi-Factor Delay Threat Scoring)
- Agent 4: RAG Recommendation Agent (NLP & Vector Knowledge Retrieval)
- Agent 5: Stakeholder Coordination Agent (Autonomous Multi-Channel Escalation)
"""

import time
from typing import Dict, Any, List
from backend.agents.cost_agent import CostPredictionAgent
from backend.agents.timeline_agent import TimelinePredictionAgent
from backend.agents.hotspot_agent import DelayHotspotAgent
from backend.agents.rag_agent import RAGRecommendationAgent
from backend.agents.coordination_agent import StakeholderCoordinationAgent

class PowerPredictOrchestrator:
    def __init__(self):
        self.cost_agent = CostPredictionAgent()
        self.timeline_agent = TimelinePredictionAgent()
        self.hotspot_agent = DelayHotspotAgent()
        self.rag_agent = RAGRecommendationAgent()
        self.coordination_agent = StakeholderCoordinationAgent()

    def run_pipeline(self, project_data: Dict[str, Any], risk_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Executes end-to-end multi-agent orchestration pipeline.
        Records step-by-step logs, inter-agent message passing, and outputs.
        """
        start_time = time.time()
        pipeline_logs = []
        agent_traces = []

        pipeline_logs.append("⚡ [Orchestrator] Multi-Agent Pipeline activated for PowerPredict AI.")
        pipeline_logs.append(f"⚡ [Orchestrator] Target Project: {project_data.get('name', 'Power Project')} ({project_data.get('capacity_mw')} MW {project_data.get('project_type')}) in {project_data.get('state', 'India')}.")

        # Step 1: Agent 3 Delay Hotspot Agent runs first to calculate threat score D
        t0 = time.time()
        hotspot_res = self.hotspot_agent.execute(project_data, risk_factors)
        hotspot_time = round((time.time() - t0) * 1000, 1)
        agent_traces.append({
            "agent_id": self.hotspot_agent.agent_id,
            "agent_name": self.hotspot_agent.name,
            "role": self.hotspot_agent.role,
            "latency_ms": hotspot_time,
            "logs": hotspot_res["logs"],
            "summary": f"Delay Risk Score: {hotspot_res['output']['overall_score']} ({hotspot_res['output']['risk_level']})"
        })

        # Step 2: Agent 1 Cost Prediction Agent
        t0 = time.time()
        cost_res = self.cost_agent.execute(project_data, risk_factors)
        cost_time = round((time.time() - t0) * 1000, 1)
        agent_traces.append({
            "agent_id": self.cost_agent.agent_id,
            "agent_name": self.cost_agent.name,
            "role": self.cost_agent.role,
            "latency_ms": cost_time,
            "logs": cost_res["logs"],
            "summary": f"Predicted Cost: {cost_res['output']['formatted']} ({cost_res['output']['overrun_formatted']})"
        })

        # Step 3: Agent 2 Timeline Prediction Agent
        t0 = time.time()
        timeline_res = self.timeline_agent.execute(project_data, risk_factors)
        timeline_time = round((time.time() - t0) * 1000, 1)
        agent_traces.append({
            "agent_id": self.timeline_agent.agent_id,
            "agent_name": self.timeline_agent.name,
            "role": self.timeline_agent.role,
            "latency_ms": timeline_time,
            "logs": timeline_res["logs"],
            "summary": f"Predicted Timeline: {timeline_res['output']['formatted']} ({timeline_res['output']['delay_formatted']})"
        })

        # Step 4: Agent 4 RAG Recommendation Agent
        predictions_combined = {
            "predicted_cost": cost_res["output"],
            "predicted_timeline": timeline_res["output"],
            "model_metadata": cost_res.get("model_metadata", {})
        }
        
        project_details_normalized = {
            "project_id": project_data.get("project_id", "PP-DL-2026-001"),
            "name": project_data.get("name", "Power Project"),
            "type": project_data.get("project_type", "Solar Photovoltaic (Ground-Mounted)"),
            "capacity": f"{project_data.get('capacity_mw', 500)} MW",
            "capacity_mw": project_data.get("capacity_mw", 500),
            "location": {
                "district": project_data.get("district", "Jaisalmer"),
                "state": project_data.get("state", "Rajasthan")
            },
            "estimated_cost": f"₹{project_data.get('estimated_cost_cr', 500)} crore",
            "estimated_cost_cr": project_data.get("estimated_cost_cr", 500),
            "estimated_timeline": f"{project_data.get('estimated_timeline_months', 18)} months",
            "estimated_timeline_months": project_data.get("estimated_timeline_months", 18),
            "land_area": f"{project_data.get('land_area_acres', 500)} acres",
            "land_area_acres": project_data.get("land_area_acres", 500),
            "contractor_tier": project_data.get("contractor_tier", "Tier-2 (Sterling & Wilson, Vikram Solar)"),
            "environmental_category": project_data.get("environmental_category", "Category-B1 (SEIAA)")
        }

        t0 = time.time()
        rag_res = self.rag_agent.execute(project_details_normalized, predictions_combined, hotspot_res["output"])
        rag_time = round((time.time() - t0) * 1000, 1)
        agent_traces.append({
            "agent_id": self.rag_agent.agent_id,
            "agent_name": self.rag_agent.name,
            "role": self.rag_agent.role,
            "latency_ms": rag_time,
            "logs": rag_res["logs"],
            "summary": f"Saved {rag_res['output']['total_timeline_reduction']} & {rag_res['output']['total_cost_saving']}"
        })

        # Step 5: Agent 5 Stakeholder Coordination Agent
        t0 = time.time()
        coord_res = self.coordination_agent.execute(project_details_normalized, hotspot_res["output"], rag_res["output"])
        coord_time = round((time.time() - t0) * 1000, 1)
        agent_traces.append({
            "agent_id": self.coordination_agent.agent_id,
            "agent_name": self.coordination_agent.name,
            "role": self.coordination_agent.role,
            "latency_ms": coord_time,
            "logs": coord_res["logs"],
            "summary": f"{coord_res['total_dispatched']} Communications Dispatched ({coord_res['stakeholders_notified_count']} Stakeholders)"
        })

        total_elapsed_ms = round((time.time() - start_time) * 1000, 1)
        pipeline_logs.append(f"⚡ [Orchestrator] Multi-Agent Pipeline completed successfully in {total_elapsed_ms} ms.")

        return {
            "status": "SUCCESS",
            "execution_duration_ms": total_elapsed_ms,
            "project_details": project_details_normalized,
            "predictions": predictions_combined,
            "delay_risk_assessment": hotspot_res["output"],
            "recommendations": rag_res["output"],
            "coordination": coord_res,
            "alerts_sent": coord_res["alerts_sent"],
            "milestones": timeline_res["milestones"],
            "explainable_ai": timeline_res["explainable_ai"],
            "agent_traces": agent_traces,
            "pipeline_logs": pipeline_logs
        }

orchestrator = PowerPredictOrchestrator()
