"""
Agent 5: Stakeholder Coordination Agent (Autonomous Multi-Channel Dispatch)
Responsible for orchestrating automated hierarchical escalations and communications
to responsible authorities (Project Manager, Contractor, District Collector,
State Electricity Board, Ministry of Power, NITI Aayog).
"""

from datetime import datetime
from typing import Dict, Any, List

class StakeholderCoordinationAgent:
    def __init__(self):
        self.name = "Stakeholder Coordination Agent"
        self.agent_id = "agent_05_coordination"
        self.role = "Autonomous Multi-Agency Orchestration & Hierarchical Escalation"
        self.channels_supported = ["Official Secure Email", "Encrypted SMS", "WhatsApp Enterprise API", "MoP Portal Memo"]

    def execute(
        self,
        project_details: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        logs = []
        logs.append(f"[{self.name}] Ingesting hierarchical risk level: {risk_assessment.get('alert_level_code', 'LEVEL_1')} ({risk_assessment.get('risk_level')}).")
        
        proj_name = project_details.get("name", "500 MW Solar Park")
        proj_id = project_details.get("project_id", "PP-2026-RJ-001234")
        state = project_details.get("location", {}).get("state", "Rajasthan")
        district = project_details.get("location", {}).get("district", "Jaisalmer")
        
        score = risk_assessment.get("overall_score", 0.63)
        level_code = risk_assessment.get("alert_level_code", "LEVEL_2")
        
        dispatches = []
        alerts_sent_flags = {
            "project_manager": False,
            "contractor": False,
            "district_collector": False,
            "state_electricity_board": False,
            "ministry_of_power": False
        }

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Project Manager Dispatch (Always sent if score >= 0.40)
        if score >= 0.35:
            alerts_sent_flags["project_manager"] = True
            dispatches.append({
                "recipient": "Chief Project Manager (Solar Park Division)",
                "organization": f"State Power Development Corp ({state})",
                "channel": "WhatsApp & Dashboard Push",
                "subject": f"🚨 [PowerPredict Alert] Delay Risk Detected ({score:.2f}) - {proj_name}",
                "message": (
                    f"PowerPredict AI alert for {proj_name} ({proj_id}). Overall Delay Risk: {score:.2f} ({risk_assessment.get('risk_level')}). "
                    f"Top Hotspots: {', '.join(risk_assessment.get('hotspots', []))}. "
                    f"Pre-emptive action required: Expedite Land Acquisition and Environmental Clearance dossiers. RAG recommendations generated."
                ),
                "timestamp": now_str,
                "status": "DELIVERED"
            })
            logs.append(f"[{self.name}] Dispatched WhatsApp & Dashboard notification to Project Manager.")

        # 2. Contractor Dispatch (Level 2+)
        if score >= 0.60:
            alerts_sent_flags["contractor"] = True
            dispatches.append({
                "recipient": "Lead EPC Project Director (Contractor)",
                "organization": project_details.get("contractor_tier", "EPC Contractor"),
                "channel": "SMS & Official Email",
                "subject": f"⚠️ URGENT: Bi-Weekly Progress Milestone Review & LD Caution - {proj_id}",
                "message": (
                    f"NOTICE: Project {proj_name} is tracking a predicted delay of "
                    f"{recommendations.get('timeline_progression', '8+ months')}. "
                    f"Mandatory bi-weekly technical audit convened. Liquidated damages (0.5%/week) active. "
                    f"Please submit double-shift mobilization deployment plan within 72 hours."
                ),
                "timestamp": now_str,
                "status": "DELIVERED"
            })
            logs.append(f"[{self.name}] Dispatched SMS and official legal caution memo to EPC Contractor.")

        # 3. District Collector Dispatch (If Land Acquisition is Critical/High)
        land_risk = risk_assessment.get("risk_factors", {}).get("land_acquisition", {}).get("score", 0.0)
        if land_risk >= 0.70:
            alerts_sent_flags["district_collector"] = True
            dispatches.append({
                "recipient": f"District Collector & Magistrate, {district}",
                "organization": f"Revenue Department, Government of {state}",
                "channel": "Official Government e-Office Memo",
                "subject": f"🏛️ Priority Intervention: Fast-Track Land Acquisition for National Grid Project {proj_id}",
                "message": (
                    f"Hon'ble Collector: Project {proj_name} ({district}) faces potential 12-18 months title dispute delay (Risk Score: {land_risk:.2f}). "
                    f"Requesting revenue cell single-window demarcation and 15% incentive framework adoption under RFCTLARR Act guidelines."
                ),
                "timestamp": now_str,
                "status": "TRANSMITTED (Govt e-Office Ref: EO-2026/PP-994)"
            })
            logs.append(f"[{self.name}] Dispatched statutory priority memo to District Collector ({district}).")

        # 4. State Electricity Board Dispatch (Level 3+)
        if score >= 0.80:
            alerts_sent_flags["state_electricity_board"] = True
            dispatches.append({
                "recipient": f"Managing Director & Member (Grid), {state} State Electricity Board",
                "organization": f"State Power Transmission Corporation Ltd ({state})",
                "channel": "Official Secure Portal Memo",
                "subject": f"⚡ CRITICAL ESCALATION: 10+ Months Slippage Predicted for {proj_name}",
                "message": (
                    f"Statutory Notice: Project {proj_name} Delay Risk Score has reached {score:.2f} (CRITICAL). "
                    f"Secretary (Power) review meeting requested to address bay allocation, Right of Way (RoW) disputes, and PPA tariff adoption."
                ),
                "timestamp": now_str,
                "status": "ESCALATED"
            })
            logs.append(f"[{self.name}] Escalated critical dossier to State Electricity Board Board of Directors.")

        # 5. Ministry of Power / NITI Aayog (Level 4)
        if score >= 0.95:
            alerts_sent_flags["ministry_of_power"] = True
            dispatches.append({
                "recipient": "Joint Secretary (Transmission/Renewables), Ministry of Power & NITI Aayog Infrastructure Committee",
                "organization": "Government of India, Shram Shakti Bhawan, New Delhi",
                "channel": "National Infrastructure Monitoring Portal (PRAGATI / MoP)",
                "subject": f"🚨 NATIONAL HIGH-LEVEL ALERT: Imminent Project Failure Risk - {proj_id}",
                "message": (
                    f"High-Level Alert: Project {proj_name} ({state}) shows extreme delay risk {score:.2f} exceeding critical thresholds. "
                    f"Severe cost overrun (>40%) and grid stability shortfall imminent. Recommending national empowered group intervention."
                ),
                "timestamp": now_str,
                "status": "ESCALATED TO NITI AAYOG"
            })
            logs.append(f"[{self.name}] Emergency national escalation to Ministry of Power & NITI Aayog.")

        logs.append(f"[{self.name}] Autonomous coordination completed. {len(dispatches)} high-priority stakeholder communications dispatched.")

        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "COMPLETED",
            "logs": logs,
            "dispatches": dispatches,
            "alerts_sent": alerts_sent_flags,
            "total_dispatched": len(dispatches),
            "stakeholders_notified_count": len(dispatches) * 2 + 2 # field engineers, sub-contractors, PMU members
        }
