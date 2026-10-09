"""
PowerPredict AI - Configuration & Constants
National Power Sector Standards, Multi-Factor Threat Weights, and State Baselines
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
MODELS_DIR = BASE_DIR / "backend" / "models_saved"

os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Load .env file if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception as e:
        print(f"[CONFIG] Warning loading .env: {e}")


# Multi-Factor Delay Risk Weights:
# D = w1*L + w2*E + w3*C + w4*W + w5*S + w6*F
RISK_WEIGHTS = {
    "land_acquisition": 0.25,        # w1
    "environmental_clearance": 0.20, # w2
    "contractor_track_record": 0.20, # w3
    "weather_climate": 0.15,         # w4
    "supply_chain": 0.10,            # w5
    "financing": 0.10                # w6
}

# Hierarchical Alert Thresholds & Escalation Matrix
ALERT_LEVELS = {
    "LEVEL_1": {
        "name": "Medium Risk",
        "name_hi": "मध्यम जोखिम",
        "min_score": 0.40,
        "max_score": 0.60,
        "badge": "warning",
        "escalation_target": "Project Manager",
        "escalation_target_hi": "परियोजना प्रबंधक",
        "action_required": "Weekly progress review meetings, land demarcation inspection.",
        "action_required_hi": "साप्ताहिक प्रगति समीक्षा बैठक, भूमि सीमांकन निरीक्षण।",
        "description": "Medium delay risk detected. Review land acquisition progress and long-lead material procurement lead times.",
        "description_hi": "मध्यम विलंब जोखिम पाया गया। भूमि अधिग्रहण प्रगति और सामग्री आपूर्ति चक्र की समीक्षा करें।"
    },
    "LEVEL_2": {
        "name": "High Risk",
        "name_hi": "उच्च जोखिम",
        "min_score": 0.60,
        "max_score": 0.80,
        "badge": "high",
        "escalation_target": "Project Manager + EPC Contractor",
        "escalation_target_hi": "परियोजना प्रबंधक + EPC ठेकेदार",
        "action_required": "Bi-weekly review meetings scheduled, District Collector fast-track coordination, liquidated damages caution.",
        "action_required_hi": "पाक्षिक समीक्षा बैठकें, जिला कलेक्टर समन्वय और लिक्विडेटेड डैमेजेस नोटिस।",
        "description": "High delay risk. Land acquisition or contractor progress lagging behind baseline schedule.",
        "description_hi": "उच्च विलंब जोखिम। भूमि अधिग्रहण या ठेकेदार कार्य प्रगति निर्धारित समयसीमा से पीछे है।"
    },
    "LEVEL_3": {
        "name": "Critical Risk",
        "name_hi": "गंभीर जोखिम",
        "min_score": 0.80,
        "max_score": 0.95,
        "badge": "critical",
        "escalation_target": "Project Manager + Contractor + State Electricity Board (DISCOM/TRANSCO)",
        "escalation_target_hi": "परियोजना प्रबंधक + ठेकेदार + राज्य विद्युत बोर्ड (DISCOM/TRANSCO)",
        "action_required": "Emergency review meeting with Secretary (Power), liquidated damages enforcement warning, cabinet fast-track intervention.",
        "action_required_hi": "सचिव (ऊर्जा) के साथ आपातकालीन समीक्षा बैठक, बैंक गारंटी जब्ती चेतावनी, कैबिनेट फास्ट-ट्रैक हस्तक्षेप।",
        "description": "Critical delay risk. 10+ months delay predicted. Immediate multi-stakeholder statutory intervention needed.",
        "description_hi": "गंभीर विलंब जोखिम। 10+ महीने के विलंब की संभावना। तत्काल वैधानिक हस्तक्षेप आवश्यक।"
    },
    "LEVEL_4": {
        "name": "Project Failure Risk",
        "name_hi": "परियोजना विफलता जोखिम",
        "min_score": 0.95,
        "max_score": 1.00,
        "badge": "emergency",
        "escalation_target": "Ministry of Power + National Empowered Infrastructure Committee",
        "escalation_target_hi": "विद्युत मंत्रालय + राष्ट्रीय अवसंरचना समिति",
        "action_required": "National emergency taskforce formed, contractor substitution, PPA restructuring, statutory emergency land takeover.",
        "action_required_hi": "राष्ट्रीय आपातकालीन टास्कफोर्स का गठन, ठेकेदार प्रतिस्थापन, PPA पुनर्गठन, वैधानिक भूमि अधिग्रहण।",
        "description": "Severe project failure risk. 18+ months delay and >40% cost overrun predicted. Urgent policy intervention.",
        "description_hi": "अत्यंत गंभीर विफलता जोखिम। 18+ माह का विलंब और 40% से अधिक लागत वृद्धि संभावित।"
    }
}

# Complete List of Indian States and Union Territories with Baseline Metrics
INDIAN_POWER_STATES = {
    # 28 States
    "Andhra Pradesh": {"solar_potential_gw": 38.4, "avg_land_delay_months": 9.2, "forest_cover_pct": 17.86, "zone": "South"},
    "Arunachal Pradesh": {"solar_potential_gw": 8.6, "avg_land_delay_months": 19.5, "forest_cover_pct": 79.63, "zone": "North-East"},
    "Assam": {"solar_potential_gw": 13.7, "avg_land_delay_months": 15.2, "forest_cover_pct": 36.11, "zone": "North-East"},
    "Bihar": {"solar_potential_gw": 11.2, "avg_land_delay_months": 18.2, "forest_cover_pct": 7.84, "zone": "East"},
    "Chhattisgarh": {"solar_potential_gw": 18.2, "avg_land_delay_months": 13.8, "forest_cover_pct": 41.13, "zone": "Central"},
    "Goa": {"solar_potential_gw": 0.8, "avg_land_delay_months": 8.1, "forest_cover_pct": 60.44, "zone": "West"},
    "Gujarat": {"solar_potential_gw": 35.7, "avg_land_delay_months": 7.2, "forest_cover_pct": 7.57, "zone": "West"},
    "Haryana": {"solar_potential_gw": 4.5, "avg_land_delay_months": 10.4, "forest_cover_pct": 3.63, "zone": "North"},
    "Himachal Pradesh": {"solar_potential_gw": 33.8, "avg_land_delay_months": 16.9, "forest_cover_pct": 27.72, "zone": "North"},
    "Jharkhand": {"solar_potential_gw": 18.1, "avg_land_delay_months": 17.4, "forest_cover_pct": 29.76, "zone": "East"},
    "Karnataka": {"solar_potential_gw": 24.7, "avg_land_delay_months": 8.5, "forest_cover_pct": 20.11, "zone": "South"},
    "Kerala": {"solar_potential_gw": 6.1, "avg_land_delay_months": 14.8, "forest_cover_pct": 54.70, "zone": "South"},
    "Madhya Pradesh": {"solar_potential_gw": 61.6, "avg_land_delay_months": 12.1, "forest_cover_pct": 25.14, "zone": "Central"},
    "Maharashtra": {"solar_potential_gw": 64.3, "avg_land_delay_months": 13.0, "forest_cover_pct": 16.50, "zone": "West"},
    "Manipur": {"solar_potential_gw": 10.5, "avg_land_delay_months": 18.6, "forest_cover_pct": 75.46, "zone": "North-East"},
    "Meghalaya": {"solar_potential_gw": 5.8, "avg_land_delay_months": 17.1, "forest_cover_pct": 76.00, "zone": "North-East"},
    "Mizoram": {"solar_potential_gw": 9.1, "avg_land_delay_months": 19.0, "forest_cover_pct": 84.53, "zone": "North-East"},
    "Nagaland": {"solar_potential_gw": 7.3, "avg_land_delay_months": 18.4, "forest_cover_pct": 73.90, "zone": "North-East"},
    "Odisha": {"solar_potential_gw": 25.7, "avg_land_delay_months": 16.4, "forest_cover_pct": 33.50, "zone": "East"},
    "Punjab": {"solar_potential_gw": 2.8, "avg_land_delay_months": 9.5, "forest_cover_pct": 3.67, "zone": "North"},
    "Rajasthan": {"solar_potential_gw": 142.3, "avg_land_delay_months": 11.4, "forest_cover_pct": 4.87, "zone": "North"},
    "Sikkim": {"solar_potential_gw": 4.9, "avg_land_delay_months": 17.8, "forest_cover_pct": 47.11, "zone": "North-East"},
    "Tamil Nadu": {"solar_potential_gw": 17.6, "avg_land_delay_months": 9.8, "forest_cover_pct": 20.31, "zone": "South"},
    "Telangana": {"solar_potential_gw": 20.4, "avg_land_delay_months": 9.1, "forest_cover_pct": 18.36, "zone": "South"},
    "Tripura": {"solar_potential_gw": 2.1, "avg_land_delay_months": 16.0, "forest_cover_pct": 77.26, "zone": "North-East"},
    "Uttar Pradesh": {"solar_potential_gw": 22.8, "avg_land_delay_months": 15.6, "forest_cover_pct": 6.15, "zone": "North"},
    "Uttarakhand": {"solar_potential_gw": 16.8, "avg_land_delay_months": 15.3, "forest_cover_pct": 45.44, "zone": "North"},
    "West Bengal": {"solar_potential_gw": 6.2, "avg_land_delay_months": 17.5, "forest_cover_pct": 19.04, "zone": "East"},
    
    # 8 Union Territories
    "Andaman and Nicobar Islands": {"solar_potential_gw": 1.2, "avg_land_delay_months": 14.0, "forest_cover_pct": 81.74, "zone": "UT"},
    "Chandigarh": {"solar_potential_gw": 0.1, "avg_land_delay_months": 5.2, "forest_cover_pct": 21.05, "zone": "UT"},
    "Dadra and Nagar Haveli and Daman and Diu": {"solar_potential_gw": 0.4, "avg_land_delay_months": 6.5, "forest_cover_pct": 37.60, "zone": "UT"},
    "Delhi (NCT)": {"solar_potential_gw": 2.0, "avg_land_delay_months": 7.0, "forest_cover_pct": 13.15, "zone": "UT"},
    "Jammu and Kashmir": {"solar_potential_gw": 111.0, "avg_land_delay_months": 15.0, "forest_cover_pct": 21.35, "zone": "UT"},
    "Ladakh": {"solar_potential_gw": 131.0, "avg_land_delay_months": 13.5, "forest_cover_pct": 1.48, "zone": "UT"},
    "Lakshadweep": {"solar_potential_gw": 0.1, "avg_land_delay_months": 6.0, "forest_cover_pct": 90.33, "zone": "UT"},
    "Puducherry": {"solar_potential_gw": 0.6, "avg_land_delay_months": 6.8, "forest_cover_pct": 10.60, "zone": "UT"}
}

# Exhaustive Power Project Types across Indian Energy Infrastructure
PROJECT_TYPES = [
    "Solar Photovoltaic (Ground-Mounted)",
    "Floating Solar PV",
    "Rooftop Solar (Commercial / Industrial)",
    "Onshore Wind Energy",
    "Offshore Wind Energy",
    "Supercritical Thermal Power (Coal)",
    "Ultra Supercritical Thermal Power",
    "Gas-Based Combined Cycle (CCPP)",
    "Large Hydroelectric (>25 MW)",
    "Small Hydroelectric (SHP ≤25 MW)",
    "Pumped Storage Hydro (PSP)",
    "Interstate Transmission System (ISTS 765kV/400kV)",
    "High Voltage Direct Current (HVDC)",
    "Battery Energy Storage System (BESS)",
    "Wind-Solar Hybrid (with BESS)",
    "Green Hydrogen & Green Ammonia Plant",
    "Nuclear Power Project (NPCIL)",
    "Biomass & Waste-to-Energy (WtE)",
    "Sub-station & Grid Interconnection Package"
]
