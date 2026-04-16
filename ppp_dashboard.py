import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Apex PPP Master Summary", layout="wide")

st.markdown("""
    <style>
        /* Target stApp for full background coverage */
        .stApp { background-color: #0f172a; color: #f8fafc; }
        .stSelectbox label { color: #94a3b8 !important; font-weight: 600; }
        .metric-card {
            background-color: #1e293b;
            padding: 25px;
            border-radius: 15px;
            border-top: 4px solid #e63946;
            margin-bottom: 20px;
        }
        .metric-value { font-size: 32px; font-weight: 800; color: #e63946; margin: 10px 0; }
        .metric-label { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; }
        .insight-box { 
            margin-top: 15px; font-size: 14px; color: #cbd5e1; 
            background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; 
        }
        h1 { border-left: 5px solid #e63946; padding-left: 20px; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

def calculate_rap(fresh_ftp, total_kj, tier_key):
    """Resilience-Adjusted Power (RAP) Engine"""
    if tier_key == 'pogi': 
        return fresh_ftp
        
    decay_coeffs = {
        'feather': 0.05,
        'female': 0.12,
        'young': 0.18,
        'warrior': 0.28,
        'abandon': 0.45
    }
    coeff = decay_coeffs.get(tier_key, 0.28)
    # Power-law decay based on kJ expenditure vs 5000kJ threshold
    degraded_ftp = fresh_ftp * (1 - (total_kj / 5000)**(1/coeff))
    return max(round(degraded_ftp), 0)

TIERS = {
    "S-Tier (Elite Performance)": {
        "key": "pogi", "vam": "1,845 m/h", "vamD": "Elite Pro ceiling. Record-shattering Monument pace.",
        "decay": "Dynamic Reset", "decayD": "Mechanical resilience. Surges >1,000W maintained.",
        "fuel": "120-140 g/hr", "fuelD": "Max metabolic uptake. 1:0.8 carb ratio.",
        "risk": "Immune", "riskD": "CNS stability maintained despite 'Spaghetti Legs' threshold."
    },
    "Specialist (Climbing)": {
        "key": "feather", "vam": "1,610 m/h", "vamD": "Specialist Peak. High W/kg anchor.",
        "decay": "-2.5%", "decayD": "Zero decay for anaerobic capacity < 60 mins.",
        "fuel": "45 g/hr", "fuelD": "Intense load focus. Pre-loading essential.",
        "risk": "Niche", "riskD": "Limited to specific power windows."
    },
    "Warrior (Endurance)": {
        "key": "warrior", "vam": "740 m/h", "vamD": "Endurance anchor. Long-duration resilience.",
        "decay": "-14.8%", "decayD": "Standard drift post-200km expenditure.",
        "fuel": "75 g/hr", "fuelD": "Balanced intake for extreme survival events.",
        "risk": "Safe", "riskD": "Paced for consistent durability."
    },
    "Masters (Safety Limit)": {
        "key": "abandon", "vam": "610 m/h", "vamD": "Masters Limit. 188km / 5,000 kJ cliff.",
        "decay": "CRITICAL", "decayD": "Metabolic cliff triggers 'Monument Hangover'.",
        "fuel": "95 g/hr", "fuelD": "Over-fuel early to buffer CNS fatigue.",
        "risk": "DNF ALERT", "riskD": "High risk of metabolic exhaustion."
    }
}

st.title("Apex Performance Master Summary")
st.caption("Universal PPP Engine • 360° Human Resilience Map")

selected_tier_name = st.selectbox("Select Athlete Profile", list(TIERS.keys()))
tier_data = TIERS[selected_tier_name]

st.sidebar.header("Real-Time RAP Engine")
fresh_ftp = st.sidebar.number_input("Fresh FTP (W)", value=300 if tier_data['key'] != 'pogi' else 415)
current_kj = st.sidebar.slider("Accumulated Work (kJ)", 0, 6000, 2500)

rap_value = calculate_rap(fresh_ftp, current_kj, tier_data['key'])

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown(f'<div class="metric-card"><span class="metric-label">VAM Anchor</span><div class="metric-value">{tier_data["vam"]}</div><div class="insight-box">{tier_data["vamD"]}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><span class="metric-label">Metabolic Decay</span><div class="metric-value">{tier_data["decay"]}</div><div class="insight-box">{tier_data["decayD"]}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><span class="metric-label">Fuelling Target</span><div class="metric-value">{tier_data["fuel"]}</div><div class="insight-box">{tier_data["fuelD"]}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><span class="metric-label">Pacing Risk Profile</span><div class="metric-value">{tier_data["risk"]}</div><div class="insight-box">{tier_data["riskD"]}</div></div>', unsafe_allow_html=True)

st.divider()
st.subheader(f"Current Resilience-Adjusted Power (RAP): {rap_value}W")
st.progress(min(max(rap_value / fresh_ftp, 0.0), 1.0))
