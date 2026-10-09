"""
PowerPredict AI - Pillar 2: Delay Hotspot & Threat Scoring Engine
Implements Multi-Factor Delay Risk Scoring Formula:
D = w1*L + w2*E + w3*C + w4*W + w5*S + w6*F
"""

from typing import Dict, Any, List
from backend.config import RISK_WEIGHTS, ALERT_LEVELS

def calculate_delay_risk_score(factors: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes overall Delay Risk Score D and classifies hotspot severity.
    factors dict keys:
      - land_acquisition: float (0.0 to 1.0)
      - environmental_clearance: float (0.0 to 1.0)
      - contractor_track_record: float (0.0 to 1.0)
      - weather_climate: float (0.0 to 1.0)
      - supply_chain: float (0.0 to 1.0)
      - financing: float (0.0 to 1.0)
    """
    weighted_sum = 0.0
    factor_details = {}
    
    # Thresholds for qualitative levels
    def get_level(score: float) -> str:
        if score >= 0.80:
            return "Critical"
        elif score >= 0.60:
            return "High"
        elif score >= 0.40:
            return "Medium"
        else:
            return "Low"

    # Human-readable labels (English & Hindi)
    display_names = {
        "land_acquisition": {"en": "Land Acquisition", "hi": "भूमि अधिग्रहण"},
        "environmental_clearance": {"en": "Environmental Clearance", "hi": "पर्यावरणीय मंजूरी"},
        "contractor_track_record": {"en": "Contractor Track Record", "hi": "ठेकेदार कार्य इतिहास"},
        "weather_climate": {"en": "Weather & Climate", "hi": "मौसम एवं जलवायु"},
        "supply_chain": {"en": "Supply Chain", "hi": "आपूर्ति श्रृंखला"},
        "financing": {"en": "Financing & PPAs", "hi": "वित्तीय पोषण एवं PPA"}
    }
    
    # Probability and delay duration mapping based on factor scores
    delay_prob_map = {
        "land_acquisition": lambda s: (
            int(min(96, round(s * 100))), 
            "12-18 months delay probability" if s > 0.6 else "6-9 months delay probability",
            "12-18 महीने विलंब की संभावना" if s > 0.6 else "6-9 महीने विलंब की संभावना"
        ),
        "environmental_clearance": lambda s: (
            int(min(94, round(s * 100))), 
            "8-12 months clearance lag" if s > 0.6 else "3-6 months review",
            "8-12 महीने मंजूरी अंतराल" if s > 0.6 else "3-6 महीने समीक्षा"
        ),
        "contractor_track_record": lambda s: (
            int(min(95, round(s * 100))), 
            "6-9 months slippage risk" if s > 0.6 else "2-4 months minor variance",
            "6-9 महीने कार्य पिछड़ने का जोखिम" if s > 0.6 else "2-4 महीने सामान्य विचलन"
        ),
        "weather_climate": lambda s: (
            int(min(90, round(s * 100))), 
            "2-4 months seasonal disruption" if s > 0.5 else "minimal seasonal impact",
            "2-4 महीने मौसमी रुकावट" if s > 0.5 else "न्यूनतम मौसमी प्रभाव"
        ),
        "supply_chain": lambda s: (
            int(min(92, round(s * 100))), 
            "3-6 months equipment logistics lag" if s > 0.5 else "standard domestic lead time",
            "3-6 महीने उपकरण लॉजिस्टिक्स अंतराल" if s > 0.5 else "सामान्य आपूर्ति समय"
        ),
        "financing": lambda s: (
            int(min(90, round(s * 100))), 
            "3-5 months tariff adoption / LC lag" if s > 0.5 else "adequate financial closure liquidity",
            "3-5 महीने टैरिफ स्वीकृति / LC विलंब" if s > 0.5 else "पर्याप्त वित्तीय तरलता"
        )
    }

    hotspots = []
    hotspots_hi = []
    red_zones = []
    yellow_zones = []
    green_zones = []

    for key, weight in RISK_WEIGHTS.items():
        score = float(factors.get(key, 0.50))
        score = max(0.0, min(1.0, score))
        contribution = score * weight
        weighted_sum += contribution
        level = get_level(score)
        prob, impact_desc_en, impact_desc_hi = delay_prob_map[key](score)
        
        detail = {
            "name": display_names[key]["en"],
            "name_hi": display_names[key]["hi"],
            "score": round(score, 2),
            "weight": weight,
            "weighted_impact": round(contribution, 3),
            "level": level,
            "delay_probability_pct": prob,
            "impact_description": impact_desc_en,
            "impact_description_hi": impact_desc_hi
        }
        factor_details[key] = detail
        
        if level in ["Critical", "High"]:
            hotspots.append(display_names[key]["en"])
            hotspots_hi.append(display_names[key]["hi"])
            red_zones.append(display_names[key]["en"])
        elif level == "Medium":
            yellow_zones.append(display_names[key]["en"])
        else:
            green_zones.append(display_names[key]["en"])

    overall_score = round(weighted_sum, 2)
    
    # Overall risk level determination
    if overall_score >= 0.95:
        risk_level = "Project Failure Risk"
        risk_level_hi = "परियोजना विफलता जोखिम"
        alert_info = ALERT_LEVELS["LEVEL_4"]
        level_code = "LEVEL_4"
    elif overall_score >= 0.80:
        risk_level = "Critical"
        risk_level_hi = "गंभीर जोखिम"
        alert_info = ALERT_LEVELS["LEVEL_3"]
        level_code = "LEVEL_3"
    elif overall_score >= 0.60:
        risk_level = "Medium-High"
        risk_level_hi = "मध्यम-उच्च जोखिम"
        alert_info = ALERT_LEVELS["LEVEL_2"]
        level_code = "LEVEL_2"
    elif overall_score >= 0.40:
        risk_level = "Medium"
        risk_level_hi = "मध्यम जोखिम"
        alert_info = ALERT_LEVELS["LEVEL_1"]
        level_code = "LEVEL_1"
    else:
        risk_level = "Low"
        risk_level_hi = "सामान्य / कम जोखिम"
        alert_info = {
            "name": "Low Risk",
            "name_hi": "कम जोखिम",
            "min_score": 0.0,
            "max_score": 0.40,
            "badge": "normal",
            "escalation_target": "Standard Site Supervisor",
            "escalation_target_hi": "कार्यस्थल पर्यवेक्षक",
            "action_required": "Routine monthly progress review.",
            "action_required_hi": "नियमित मासिक प्रगति समीक्षा।",
            "description": "Project operating within acceptable variance parameters.",
            "description_hi": "परियोजना सामान्य स्वीकार्य मानकों के भीतर प्रगति पर है।"
        }
        level_code = "LEVEL_0"

    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "risk_level_hi": risk_level_hi,
        "alert_level_code": level_code,
        "alert_info": alert_info,
        "risk_factors": factor_details,
        "hotspots": hotspots,
        "hotspots_hi": hotspots_hi,
        "zones": {
            "red_zones": red_zones,
            "yellow_zones": yellow_zones,
            "green_zones": green_zones
        },
        "formula_breakdown": {
            "formula": "D = 0.25*L + 0.20*E + 0.20*C + 0.15*W + 0.10*S + 0.10*F",
            "calculation_steps": [
                f"L: 0.25 * {factors.get('land_acquisition', 0.5):.2f} = {0.25 * factors.get('land_acquisition', 0.5):.3f}",
                f"E: 0.20 * {factors.get('environmental_clearance', 0.5):.2f} = {0.20 * factors.get('environmental_clearance', 0.5):.3f}",
                f"C: 0.20 * {factors.get('contractor_track_record', 0.5):.2f} = {0.20 * factors.get('contractor_track_record', 0.5):.3f}",
                f"W: 0.15 * {factors.get('weather_climate', 0.5):.2f} = {0.15 * factors.get('weather_climate', 0.5):.3f}",
                f"S: 0.10 * {factors.get('supply_chain', 0.5):.2f} = {0.10 * factors.get('supply_chain', 0.5):.3f}",
                f"F: 0.10 * {factors.get('financing', 0.5):.2f} = {0.10 * factors.get('financing', 0.5):.3f}",
            ],
            "total": overall_score
        }
    }
