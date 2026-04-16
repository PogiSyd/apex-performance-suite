import streamlit as st
import pandas as pd
import json
import plotly.express as px  # Required for the interactive map
from streamlit_gsheets import GSheetsConnection
import CoachLauncher, WKO_AddonLauncher, RouteAnalysisLauncher, WeatherAnalysisLauncher

# --- 1. DASHBOARD CONFIG ---
st.set_page_config(page_title="Apex Performance Suite", layout="wide", initial_sidebar_state="collapsed")

# Professional Dark Mode CSS
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    [data-testid="stMetric"] {
        background-color: #1c222d;
        border: 1px solid #2d343f;
        padding: 15px;
        border-radius: 10px;
    }
    [data-testid="stMetricLabel"] { color: #8e949e !important; font-size: 0.8rem !important; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-family: monospace; }
    .section-header {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 30px 0 15px 0;
        border-bottom: 1px solid #2d343f;
        padding-bottom: 5px;
    }
    /* Style the Lap Analysis Table */
    .stDataFrame { background-color: #1c222d; border-radius: 10px; }
    
    /* Input Styling */
    .stTextArea textarea { background-color: #1c222d !important; color: white !important; border: 1px solid #2d343f !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER & INPUTS ---
st.markdown("<h1 style='text-align: center;'>Cycling Master Suite</h1>", unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])
with col_a:
    uploaded_file = st.file_uploader("Select .FIT File", type=["fit"])
with col_b:
    user_notes = st.text_area("Ride Insights", placeholder="Notes for Coach analysis...")

if uploaded_file:
    with open("temp_ride.fit", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Decoding High-Resolution Matrices..."):
        # Collect data from all 4 Launchers
        all_cards = []
        try:
            all_cards.extend(CoachLauncher.get_cards("temp_ride.fit"))
            all_cards.extend(WKO_AddonLauncher.get_cards("temp_ride.fit"))
            all_cards.extend(RouteAnalysisLauncher.get_cards("temp_ride.fit"))
            all_cards.extend(WeatherAnalysisLauncher.get_cards("temp_ride.fit"))
        except Exception as e:
            st.error(f"Launcher Error: {e}")

        # --- 3. RENDERING ENGINE (FULL SPEC RECOVERY) ---

        # A. KPI Metrics Matrix (Top of Page)
        stat_cards = [c for c in all_cards if c.get('type') == 'stat']
        if stat_cards:
            st.markdown("<div class='section-header'>Key Performance Indicators</div>", unsafe_allow_html=True)
            for i in range(0, len(stat_cards), 3):
                cols = st.columns(3)
                for idx, card in enumerate(stat_cards[i:i+3]):
                    with cols[idx]:
                        st.metric(label=card['title'], value=card['value'], delta=card.get('trend'))

        # B. Detailed Analysis (Iterating through all generated cards)
        for card in all_cards:
            card_type = card.get('type')
            title = card.get('title', 'Analysis')

            if card_type == 'table':
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                df = pd.DataFrame(card['rows'], columns=card['columns'])
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif card_type == 'chart_line':
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                chart_data = pd.DataFrame({d['label']: d['data'] for d in card['datasets']})
                st.line_chart(chart_data)

            elif card_type == 'chart_scatter':
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                scatter_df = pd.DataFrame(card['points'])
                st.scatter_chart(scatter_df, x='x', y='y')

            elif card_type == 'bar_chart':
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                bar_df = pd.DataFrame({"Value": card['data']}, index=card['labels'])
                st.bar_chart(bar_df)

            elif card_type == 'interactive_route':
                st.markdown("<div class='section-header'>Interactive Spatial Analysis</div>", unsafe_allow_html=True)
                
                # Convert path data to a DataFrame
                df_map = pd.DataFrame(card['path'])
                
                # Check if data exists to prevent plotting errors
                if not df_map.empty:
                    # Create the interactive Mapbox plot
                    fig = px.scatter_mapbox(
                        df_map, 
                        lat="lat", 
                        lon="lon",
                        color="pwr" if "pwr" in df_map.columns else None, 
                        size_max=15,
                        zoom=12,
                        # Defines what shows up on touch/hover
                        hover_data={
                            "lat": False, 
                            "lon": False,
                            "pwr": ":.0f W" if "pwr" in df_map.columns else False,
                            "hr": ":.0f bpm" if "hr" in df_map.columns else False,
                            "grad": ":.1f %" if "grad" in df_map.columns else False,
                            "wind": ":.1f kph" if "wind" in df_map.columns else False,
                            "temp": ":.1f °C" if "temp" in df_map.columns else False
                        },
                        color_continuous_scale=px.colors.sequential.Plasma
                    )

                    # Apply the "Cycling Master Suite" dark styling to the map
                    fig.update_layout(
                        mapbox_style="carto-darkmatter",
                        margin={"r":0,"t":0,"l":0,"b":0},
                        paper_bgcolor="#1c222d",
                        plot_bgcolor="#1c222d",
                        font_color="white",
                        coloraxis_showscale=False # Keeps it clean like a native iPad app
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No path data available for mapping.")

st.markdown("<p style='text-align: center; color: #4e545e; margin-top: 50px;'>ANALYSIS COMPLETE | APEX PERFORMANCE SUITE v3.0</p>", unsafe_allow_html=True)
