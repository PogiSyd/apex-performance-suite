import streamlit as st
import pandas as pd
import json
from streamlit_gsheets import GSheetsConnection
import CoachLauncher, WKO_AddonLauncher, RouteAnalysisLauncher, WeatherAnalysisLauncher

# --- 1. DASHBOARD CONFIG ---
st.set_page_config(page_title="Apex Performance Suite", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the "Cycling Master Suite" Aesthetic
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #0b0e14; color: #ffffff; }
    
    /* Metric Card Styling (Bento Box Style) */
    [data-testid="stMetric"] {
        background-color: #1c222d;
        border: 1px solid #2d343f;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    
    /* Metric Typography */
    [data-testid="stMetricLabel"] { color: #8e949e !important; font-size: 0.85rem !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    
    /* Custom Section Headers */
    .section-header {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 35px 0 15px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid #2d343f;
    }

    /* Input Area Styling */
    .stFileUploader { background-color: #1c222d; border-radius: 12px; border: 1px dashed #4e545e; }
    .stTextArea textarea { background-color: #1c222d !important; color: white !important; border: 1px solid #2d343f !important; }
</style>
""", unsafe_allow_html=True)

def export_to_google_drive(all_cards, user_notes):
    """Syncs the session metrics to the centralized Google Sheet log"""
    try:
        stats = {c['title']: c['value'] for c in all_cards if c['type'] == 'stat'}
        stats['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        stats['Notes'] = user_notes 
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(worksheet="Performance_Log")
        updated_df = pd.concat([existing_data, pd.DataFrame([stats])], ignore_index=True)
        conn.update(worksheet="Performance_Log", data=updated_df)
        st.sidebar.success("✅ Cloud Sync Complete")
    except Exception as e:
        st.sidebar.error(f"Sync failed: {e}")

# --- 2. HEADER & INPUTS ---
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>Cycling Master Suite</h1>", unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])
with col_a:
    uploaded_file = st.file_uploader("Select .FIT Data", type=["fit"])
with col_b:
    user_notes = st.text_area("Ride Insights", placeholder="Notes for performance review...")

if uploaded_file:
    with open("temp_ride.fit", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Processing High-Resolution Data..."):
        # Gather data from all specialized engines
        all_cards = []
        all_cards.extend(CoachLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(WKO_AddonLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(RouteAnalysisLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(WeatherAnalysisLauncher.get_cards("temp_ride.fit"))

        # Optional: Sync to Sheets
        # export_to_google_drive(all_cards, user_notes)

        # --- 3. RENDERING ENGINE (V3.0 SPEC) ---

        # A. Key Metric Matrix (3-Column Grid)
        stat_cards = [c for c in all_cards if c['type'] == 'stat']
        if stat_cards:
            st.markdown("<div class='section-header'>Key Performance Indicators</div>", unsafe_allow_html=True)
            for i in range(0, len(stat_cards), 3):
                cols = st.columns(3)
                for idx, card in enumerate(stat_cards[i:i+3]):
                    with cols[idx]:
                        st.metric(label=card['title'], value=card['value'], delta=card.get('trend'))

        # B. Tables, Charts, and Visualization
        for card in all_cards:
            if card['type'] == 'table':
                # FIXED: Added missing quote here
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(card['rows'], columns=card['columns']), use_container_width=True)

            elif card['type'] == 'chart_line':
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                chart_data = pd.DataFrame({d['label']: d['data'] for d in card['datasets']})
                st.line_chart(chart_data)

            elif card['type'] == 'chart_scatter':
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                scatter_df = pd.DataFrame(card['points'])
                st.scatter_chart(scatter_df, x='x', y='y')

            elif card['type'] == 'interactive_route':
                st.markdown(f"<div class='section-header'>Spatial Analysis</div>", unsafe_allow_html=True)
                st.map(pd.DataFrame(card['path'], columns=['lat', 'lon']))

st.markdown("<p style='text-align: center; color: #4e545e; margin-top: 50px; font-size: 0.8rem;'>ANALYSIS COMPLETE | APEX PERFORMANCE SUITE v3.0</p>", unsafe_allow_html=True)
