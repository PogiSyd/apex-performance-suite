import streamlit as st
import pandas as pd

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Apex PPP Master Summary", layout="wide")

# Custom CSS to match your high-end "Aero-Dark" aesthetic
st.markdown("""
    <style>
        .main { background-color: #0f172a; color: #f8fafc; }
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
        h1 { border-left: 5px solid #e63946; padding-left: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- CORE PPP RAP LOGIC (The Engine) ---
def calculate_rap(fresh_ftp, total_kj, tier_key):
    """Resilience-Adjusted Power (RAP) Engine"""
    decay_coeffs = {
        'pogi': 0.00,      # Resilience Reset
        'feather': 0.05,   # Specialist
        'female': 0.12,    # Durability anchor
        'young': 0.18,     # High burn rate
        'warrior': 0.28,   # 50s Finisher
        'abandon': 0.45    # Critical Cliff
    }
    coeff = decay_coeffs.get(tier_key, 0.28)
    # The 'Master PPP Solution' logic: Decay relative to a 5000kJ ceiling
    degraded_ftp = fresh_ftp * (1 - (total_kj / 5000)**(1/coeff if coeff > 0 else 100))
    if tier_key == 'pogi': return fresh_ftp # Pogi is immune to standard decay
    return max(round(degraded_ftp), 0)

# --- DATA TIERS ---
TIERS = {
    "S-Tier (Elite: Tadej Pogačar)": {
        "key": "pogi", "vam": "1,845 m/h", "vamD": "Elite Pro. Shattered 126-year Roubaix record (5h 16m).",
        "decay": "Dynamic Reset", "decayD": "Recovered from 3 punctures. Peak Power >1,000W maintained.",
        "fuel": "120-140 g/hr", "fuelD": "Max metabolic uptake. 1:0.8 carb ratio.",
        "risk": "Immune", "riskD": "CNS stability maintained despite 'Spaghetti Legs' threshold."
    },
    "Specialist (Giant-Killer: Andrew Feather)": {
        "key": "feather", "vam": "1,610 m/h", "vamD": "Specialist Peak. 6.2 W/kg (44 min) anchor.",
        "decay": "-2.5%", "decayD": "Zero decay for efforts < 60 mins.",
        "fuel": "45 g/hr", "fuelD": "Intense load. Pre-loading focus.",
        "risk": "Niche", "riskD": "Limited to specific climbing windows."
    },
    "Warrior (Endurance: 50y 3 Peaks Finisher)": {
        "key": "warrior", "vam": "740 m/h", "vamD": "Endurance anchor. 68kg/50y profile.",
        "decay": "-14.8%", "decayD": "Standard drift post-200km expenditure.",
        "fuel": "75 g/hr", "fuelD": "Balanced intake for 13hr survival.",
        "risk": "Safe", "riskD": "Paced for Back of Falls finish."
    },
    "Masters (Safety Limit: 50s Abandon Tier)": {
        "key": "abandon", "vam": "610 m/h", "vamD": "Masters Limit. 188km / 5,000 kJ cliff.",
        "decay": "CRITICAL", "decayD": "Metabolic cliff triggers 'Monument Hangover'.",
        "fuel": "95 g/hr", "fuelD": "Over-fuel early to buffer CNS deficit.",
        "risk": "DNF ALERT", "riskD": "Predicts abandon @ Anglers Rest foot."
    }
}

# --- UI LAYOUT ---
st.title("Apex Performance Master Summary")
st.caption("Universal PPP Engine • 360° Human Resilience Map")

selected_tier_name = st.selectbox("Select Athlete Profile", list(TIERS.keys()))
tier_data = TIERS[selected_tier_name]

# Live RAP Calculator Sidebar
st.sidebar.header("Real-Time RAP Engine")
fresh_ftp = st.sidebar.number_input("Fresh FTP (W)", value=300 if tier_data['key'] != 'pogi' else 415)
current_kj = st.sidebar.slider("Accumulated Work (kJ)", 0, 6000, 2500)

rap_value = calculate_rap(fresh_ftp, current_kj, tier_data['key'])

# --- DASHBOARD GRID ---
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown(f"""<div class="metric-card"><span class="metric-label">VAM Anchor</span><div class="metric-value">{tier_data['vam']}</div><div class="insight-box">{tier_data['vamD']}</div></div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card"><span class="metric-label">Metabolic Decay</span><div class="metric-value">{tier_data['decay']}</div><div class="insight-box">{tier_data['decayD']}</div></div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card"><span class="metric-label">Fuelling Target</span><div class="metric-value">{tier_data['fuel']}</div><div class="insight-box">{tier_data['fuelD']}</div></div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card"><span class="metric-label">Pacing Risk Profile</span><div class="metric-value">{tier_data['risk']}</div><div class="insight-box">{tier_data['riskD']}</div></div>""", unsafe_allow_html=True)

# Display RAP Result
st.divider()
st.subheader(f"Current Resilience-Adjusted Power (RAP): {rap_value}W")
st.progress(min(rap_value / fresh_ftp, 1.0))
