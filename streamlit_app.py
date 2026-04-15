import streamlit as st
import pandas as pd
import json
from streamlit_gsheets import GSheetsConnection
import CoachLauncher, WKO_AddonLauncher, RouteAnalysisLauncher, WeatherAnalysisLauncher

# --- DASHBOARD CONFIG ---
st.set_page_config(page_title="Apex Performance Suite", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the "Universal Look and Feel"
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #007aff; font-family: monospace; }
    .section-header {
        color: #007aff;
        letter-spacing: 2px;
        font-weight: bold;
        text-transform: uppercase;
        border-left: 4px solid #007aff;
        padding-left: 15px;
        margin: 30px 0 15px 0;
    }
</style>
""", unsafe_allow_html=True)

def export_to_google_drive(all_cards, user_notes):
    """Refined sync with Column Mapping and User Notes"""
    try:
        # Extract title and value from stat cards
        stats = {c['title']: c['value'] for c in all_cards if c['type'] == 'stat'}
        stats['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        stats['Notes'] = user_notes 
        
        # Connect to GSheets (requires st.secrets configuration)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read existing data to append correctly
        existing_data = conn.read(worksheet="Performance_Log")
        df_new_row = pd.DataFrame([stats])
        updated_df = pd.concat([existing_data, df_new_row], ignore_index=True)
        
        conn.update(worksheet="Performance_Log", data=updated_df)
        st.sidebar.success("✅ Logged to Google Sheets")
    except Exception as e:
        st.sidebar.error(f"Sync failed: {e}")

# --- MAIN UI ---
st.title("🚴‍♂️ Apex Performance Suite")

# 1. Capture User Input First
col_a, col_b = st.columns([1, 2])
with col_a:
    uploaded_file = st.file_uploader("Upload .FIT File", type=["fit"])
with col_b:
    user_notes = st.text_area("Ride Insights (Subjective Feel)", placeholder="e.g., Legs felt heavy after Omeo climb...")

if uploaded_file:
    # Save temp file for the launchers to read
    with open("temp_ride.fit", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Analyzing performance data..."):
        # 1. Run all launchers to get card arrays
        all_cards = []
        all_cards.extend(CoachLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(WKO_AddonLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(RouteAnalysisLauncher.get_cards("temp_ride.fit"))
        all_cards.extend(WeatherAnalysisLauncher.get_cards("temp_ride.fit"))

        # 2. Export Stats AND Notes to Google Sheets
        export_to_google_drive(all_cards, user_notes)

        # 3. Render the Universal Grid
        # Create a grid for stat cards
        stat_cards = [c for c in all_cards if c['type'] == 'stat']
        if stat_cards:
            cols = st.columns(len(stat_cards))
            for idx, card in enumerate(stat_cards):
                with cols[idx]:
                    st.metric(label=card['title'], value=card['value'], delta=card.get('trend'))

        # Render other components (Tables, Charts, Maps)
        for card in all_cards:
            if card['type'] == 'table':
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(card['rows'], columns=card['columns']), use_container_width=True)

            elif card['type'] == 'chart_line':
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                st.line_chart(card['datasets'][0]['data'])

            elif card['type'] == 'interactive_route':
                st.markdown(f"<div class='section-header'>{card['title']}</div>", unsafe_allow_html=True)
                st.map(pd.DataFrame(card['path'], columns=['lat', 'lon']))

st.sidebar.info("v3.1 Standardized Protocol Active")
