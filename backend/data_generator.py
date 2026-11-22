"""
PowerPredict AI - Domain-Calibrated Stochastic Dataset Generator
Calibrated with Central Electricity Authority (CEA) & Ministry of Power Infrastructure Baselines.
Generates 6,000 stochastic project archetypes with realistic non-linear bottlenecks,
log-normal fat-tail schedule slippages, and empirical unobserved variance.
Supports all 36 Indian States/UTs and 19 Infrastructure Project Categories.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from backend.config import SAMPLE_DATA_DIR, INDIAN_POWER_STATES, PROJECT_TYPES

def generate_indian_power_dataset(num_samples: int = 6000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    
    states = list(INDIAN_POWER_STATES.keys())
    # State weights proportional to power activity in India
    weights = []
    for s in states:
        info = INDIAN_POWER_STATES[s]
        w = float(info.get("installed_cap_mw", info.get("solar_potential_gw", 15.0) * 800.0))
        weights.append(max(100.0, w))
    weights = np.array(weights)
    state_weights = weights / weights.sum()

    districts_by_state = {
        "Rajasthan": ["Jaisalmer", "Bikaner", "Jodhpur", "Barmer", "Nagaur"],
        "Gujarat": ["Kutch", "Banaskantha", "Patan", "Surendranagar", "Jamnagar"],
        "Uttar Pradesh": ["Mirzapur", "Jhansi", "Lalitpur", "Prayagraj", "Sonbhadra"],
        "Tamil Nadu": ["Tirunelveli", "Tuticorin", "Ramanathapuram", "Coimbatore", "Karur"],
        "Karnataka": ["Tumkur (Pavagada)", "Ballari", "Chitradurga", "Koppal", "Gadag"],
        "Madhya Pradesh": ["Rewa", "Neemuch", "Mandsaur", "Agar", "Shajapur"],
        "Maharashtra": ["Dhule", "Solapur", "Osmanabad", "Nagpur", "Beed"],
        "Andhra Pradesh": ["Kurnool", "Anantapur", "Kadapa", "Nellore"],
        "Odisha": ["Jharsuguda", "Sundargarh", "Angul", "Sambalpur"],
        "Bihar": ["Kahalgaon", "Barh", "Buxar", "Nabinagar"],
        "Assam": ["Dima Hasao", "Kamrup", "Cachar", "Dibrugarh"],
        "Uttarakhand": ["Chamoli", "Tehri Garhwal", "Pithoragarh", "Dehradun"],
        "Himachal Pradesh": ["Kinnaur", "Kullu", "Chamba", "Shimla"]
    }

    contractor_tiers = [
        "Tier-1 (L&T, Tata Power, BHEL, Sterling & Wilson)",
        "Tier-2 (Inox Wind, Vikram Solar, Megha Engineering)",
        "Tier-3 (Regional EPC Contractors & Civil Joint Ventures)"
    ]
    env_cats = [
        "Category-A (Central MoEFCC)",
        "Category-B1 (SEIAA State Oversight)",
        "Category-B2 (Exempt / Fast-track Procedures)"
    ]

    records = []
    for i in range(num_samples):
        proj_type = np.random.choice(PROJECT_TYPES)
        state = np.random.choice(states, p=state_weights)
        
        if state in districts_by_state:
            district = np.random.choice(districts_by_state[state])
        else:
            district = f"{state} Capital Industrial Hub"
            
        contractor = np.random.choice(contractor_tiers, p=[0.42, 0.40, 0.18])
        env_cat = np.random.choice(env_cats, p=[0.35, 0.45, 0.20])

        st_info = INDIAN_POWER_STATES[state]
        state_land_base = float(st_info.get("avg_land_delay_months", 12.0)) / 22.0
        forest_pct = float(st_info.get("forest_cover_pct", 15.0)) / 40.0

        # Sector-Specific Scale & Cost Dynamics (Calibrated with CEA Norms)
        if "Solar" in proj_type:
            capacity_mw = float(np.random.choice([50, 100, 200, 300, 500, 750, 1000, 1500]))
            land_acres = float(np.round(capacity_mw * np.random.uniform(3.5, 4.4), 0))
            cost_per_mw = np.random.uniform(3.7, 4.4) # Rs 3.7 - 4.4 Cr / MW
            est_cost_cr = round(capacity_mw * cost_per_mw, 1)
            est_timeline_months = int(np.round(12 + (capacity_mw / 250) * 2.2))
            sector_delay_factor = 0.95
        elif "Wind" in proj_type:
            capacity_mw = float(np.random.choice([50, 100, 150, 250, 300, 500]))
            land_acres = float(np.round(capacity_mw * np.random.uniform(1.4, 2.2), 0))
            cost_per_mw = np.random.uniform(5.5, 6.7)
            est_cost_cr = round(capacity_mw * cost_per_mw, 1)
            est_timeline_months = int(np.round(14 + (capacity_mw / 120) * 2.5))
            sector_delay_factor = 1.05
        elif "Thermal" in proj_type or "Coal" in proj_type:
            capacity_mw = float(np.random.choice([500, 660, 800, 1320, 1600, 2400]))
            land_acres = float(np.round(capacity_mw * np.random.uniform(0.8, 1.3), 0))
            cost_per_mw = np.random.uniform(7.5, 9.5)
            est_cost_cr = round(capacity_mw * cost_per_mw, 1)
            est_timeline_months = int(np.round(36 + (capacity_mw / 500) * 5.0))
            sector_delay_factor = 1.35
        elif "Hydro" in proj_type or "Pumped" in proj_type:
            capacity_mw = float(np.random.choice([100, 250, 500, 800, 1200]))
            land_acres = float(np.round(capacity_mw * np.random.uniform(3.5, 6.5), 0))
            cost_per_mw = np.random.uniform(8.5, 13.5)
            est_cost_cr = round(capacity_mw * cost_per_mw, 1)
            est_timeline_months = int(np.round(44 + (capacity_mw / 200) * 6.0))
            sector_delay_factor = 1.60
        elif "Transmission" in proj_type or "Substation" in proj_type:
            capacity_mw = float(np.random.choice([400, 765, 1200, 2500, 4000]))
            land_acres = float(np.round(np.random.uniform(60, 280), 0))
            est_cost_cr = round(float(np.random.uniform(180, 1100)), 1)
            est_timeline_months = int(np.round(np.random.uniform(16, 30)))
            sector_delay_factor = 1.15
        else: # Hybrid, Nuclear, BESS, Bioenergy
            capacity_mw = float(np.random.choice([100, 250, 500, 1000]))
            land_acres = float(np.round(capacity_mw * np.random.uniform(2.0, 4.0), 0))
            cost_per_mw = np.random.uniform(5.0, 7.5)
            est_cost_cr = round(capacity_mw * cost_per_mw, 1)
            est_timeline_months = int(np.round(20 + (capacity_mw / 200) * 3.0))
            sector_delay_factor = 1.20

        # Realistic 6 Ground Risk Factors with Heteroscedastic Noise
        land_scale = min(1.0, land_acres / 2200.0)
        land_risk = float(np.clip(0.40 * state_land_base + 0.35 * land_scale + np.random.normal(0.12, 0.12), 0.08, 0.96))

        env_weight = 0.85 if "Category-A" in env_cat else (0.55 if "Category-B1" in env_cat else 0.25)
        env_risk = float(np.clip(0.45 * env_weight + 0.35 * forest_pct + np.random.normal(0.08, 0.10), 0.08, 0.96))

        contractor_base = 0.25 if "Tier-1" in contractor else (0.55 if "Tier-2" in contractor else 0.80)
        contractor_risk = float(np.clip(contractor_base + np.random.normal(0.02, 0.11), 0.08, 0.96))

        weather_risk = float(np.clip(0.25 + (0.35 if ("Hydro" in proj_type or "Transmission" in proj_type) else 0.10) + np.random.normal(0.0, 0.10), 0.08, 0.96))
        supply_chain_risk = float(np.clip(0.35 + (0.15 if ("Solar" in proj_type or "Battery" in proj_type) else 0.05) + np.random.normal(0.0, 0.10), 0.08, 0.96))
        financing_risk = float(np.clip(0.30 + (0.12 if est_cost_cr > 1500 else 0.0) + np.random.normal(0.0, 0.10), 0.08, 0.96))

        # Multi-factor Threat Score D
        delay_risk_score = round(float(
            0.25 * land_risk +
            0.20 * env_risk +
            0.20 * contractor_risk +
            0.15 * weather_risk +
            0.10 * supply_chain_risk +
            0.10 * financing_risk
        ), 3)

        # Realistic Non-Linear Timeline Slippage Mechanics:
        # 1. Systemic schedule drag
        systemic_delay = est_timeline_months * (0.22 * delay_risk_score + 0.12 * (delay_risk_score**2)) * sector_delay_factor
        
        # 2. Critical path bottlenecks (non-linear powers)
        bottleneck_delay = (
            (land_risk**1.3) * 5.2 +
            (contractor_risk**1.2) * 4.5 +
            (env_risk**1.1) * 3.2 +
            weather_risk * 2.2 +
            supply_chain_risk * 1.8 +
            financing_risk * 1.6
        ) * sector_delay_factor
        
        # 3. Compounding synergy: high land risk + struggling contractor multiplies idle periods
        synergy_delay = 3.2 * (land_risk * contractor_risk) + 2.5 * (env_risk * weather_risk)
        
        # 4. Stochastic fat-tailed shock (representing legal injunctions, NGT stays, or NCLT contractor insolvency)
        shock_val = float(np.random.lognormal(mean=0.30 * delay_risk_score, sigma=0.45) - 1.0)
        shock_delay = max(0.0, shock_val * 4.0)
        
        # 5. Genuine unobserved real-world variance (sigma = 2.8 months)
        empirical_noise = float(np.random.normal(0.0, 2.8))

        timeline_delay_months = int(np.round(systemic_delay + bottleneck_delay + synergy_delay + shock_delay + empirical_noise))
        timeline_delay_months = max(1, timeline_delay_months)
        actual_timeline_months = est_timeline_months + timeline_delay_months

        # Realistic Capital Overrun Mechanics:
        # 1. Interest During Construction (IDC): 9.5% annual rate on 70% debt proportion
        idc_factor = 0.70 * (((1.0 + 0.095)**(timeline_delay_months / 12.0)) - 1.0)
        
        # 2. Contractor idle remobilization & price escalation
        contractor_remobilization = 0.06 * (contractor_risk**1.3)
        land_revision_cost = 0.05 * (land_risk**1.2)
        supply_cost = 0.04 * supply_chain_risk
        
        # 3. Real-world cost variance (sigma = 3.2%)
        cost_noise = float(np.random.normal(0.0, 0.032))

        cost_overrun_pct = round(float(idc_factor + contractor_remobilization + land_revision_cost + supply_cost + cost_noise), 4)
        cost_overrun_pct = max(0.03, min(0.85, cost_overrun_pct))
        actual_cost_cr = round(est_cost_cr * (1.0 + cost_overrun_pct), 1)

        records.append({
            "project_id": f"PP-HIST-{1000 + i}",
            "project_type": proj_type,
            "capacity_mw": capacity_mw,
            "state": state,
            "district": district,
            "contractor_tier": contractor,
            "environmental_category": env_cat,
            "land_area_acres": land_acres,
            "estimated_cost_cr": est_cost_cr,
            "estimated_timeline_months": est_timeline_months,
            "land_risk": round(land_risk, 3),
            "env_risk": round(env_risk, 3),
            "contractor_risk": round(contractor_risk, 3),
            "weather_risk": round(weather_risk, 3),
            "supply_chain_risk": round(supply_chain_risk, 3),
            "financing_risk": round(financing_risk, 3),
            "delay_risk_score": delay_risk_score,
            "timeline_delay_months": timeline_delay_months,
            "actual_timeline_months": actual_timeline_months,
            "cost_overrun_pct": cost_overrun_pct,
            "actual_cost_cr": actual_cost_cr
        })

    df = pd.DataFrame(records)
    csv_path = SAMPLE_DATA_DIR / "power_projects.csv"
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} stochastic power project archetypes to {csv_path}")
    return df

if __name__ == "__main__":
    generate_indian_power_dataset()
