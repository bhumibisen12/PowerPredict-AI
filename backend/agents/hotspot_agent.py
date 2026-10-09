"""
Agent 3: Delay Hotspot Agent (Multi-Factor Delay Threat Scoring)
Responsible for computing 6-factor weighted Delay Risk Score:
D = w1*L + w2*E + w3*C + w4*W + w5*S + w6*F
and classifying critical bottlenecks into Red, Yellow, and Green zones.
"""

from typing import Dict, Any
from backend.risk_engine import calculate_delay_risk_score

class DelayHotspotAgent:
    def __init__(self):
        self.name = "Delay Hotspot Agent"
        self.agent_id = "agent_03_hotspot"
        self.role = "Multi-Criteria Threat Scoring & Spatial Bottleneck Mapping"
        self.algorithm = "Weighted Multi-Attribute Utility Function (CEA Risk Standard)"

    def execute(self, project_data: Dict[str, Any], risk_factors: Dict[str, float]) -> Dict[str, Any]:
        logs = []
        logs.append(f"[{self.name}] Ingesting 6 ground vulnerability dimensions (L, E, C, W, S, F).")
        
        assessment = calculate_delay_risk_score(risk_factors)
        score = assessment["overall_score"]
        level = assessment["risk_level"]
        
        logs.append(f"[{self.name}] Computed Delay Risk Score: D = {score:.2f} ({level}).")
        logs.append(f"[{self.name}] Identified Critical Hotspots: {', '.join(assessment['hotspots']) if assessment['hotspots'] else 'None (nominal)'}.")
        logs.append(f"[{self.name}] Categorized Red Zones: {', '.join(assessment['zones']['red_zones'])}; Yellow Zones: {', '.join(assessment['zones']['yellow_zones'])}.")
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "COMPLETED",
            "logs": logs,
            "output": assessment
        }
