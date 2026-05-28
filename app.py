import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Match Highlights Core",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- HIGH-END DARK MODE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f4f4f5;
    }
    .stApp {
        background-color: #09090b; 
    }
    
    /* Make the top header invisible to blend with the dark background */
    [data-testid="stHeader"] {
        background-color: rgba(9, 9, 11, 0) !important;
    }

    /* Typography Magic */
    .mono-text {
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.5px;
    }

    /* Architecture Cards */
    .step-card {
        background-color: #18181b;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #27272a;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .step-card:hover { 
        transform: translateY(-4px);
        border-color: #3f3f46;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
    }
    
    .step-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #a1a1aa;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
    }
    .step-desc {
        color: #e4e4e7;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Accent Lines */
    .accent-cyan { border-top: 3px solid #06b6d4; }
    .accent-indigo { border-top: 3px solid #6366f1; }
    .accent-rose { border-top: 3px solid #f43f5e; }
    .accent-emerald { border-top: 3px solid #10b981; }
    .accent-amber { border-top: 3px solid #f59e0b; }
    .accent-violet { border-top: 3px solid #8b5cf6; }

    /* Override Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2.5rem !important;
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #d4d4d8 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid #27272a;
    }
    hr {
        border-color: #27272a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING UTILITIES ---


@st.cache_data
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


# --- DYNAMIC DATASET CONFIGURATION ---
# To add a new match, just add a new folder in 'assets' and update this dictionary.
AVAILABLE_MATCHES = {
    "ENG vs NZ T20I 2023": "assets/eng_nz_2023",
    "Sample Match 02": "assets/sample_02"
}

# --- THE SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px; margin-top: 1rem;'>NAVIGATION</p>", unsafe_allow_html=True)
    navigation = st.radio(
        "hidden_nav_label",
        ["Architecture Map", "Live Telemetry"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px;'>ACTIVE DATASET</p>", unsafe_allow_html=True)

    # Dropdown matches the dictionary keys
    selected_match_name = st.selectbox("hidden_dataset_label", list(
        AVAILABLE_MATCHES.keys()), label_visibility="collapsed")

    # Set the active paths based on the dropdown selection
    ACTIVE_DIR = AVAILABLE_MATCHES[selected_match_name]
    VIDEO_PATH = os.path.join(ACTIVE_DIR, "match_highlights_fast.mp4")
    MATCH_DATA_PATH = os.path.join(ACTIVE_DIR, "match_data.json")
    OCR_DATA_PATH = os.path.join(ACTIVE_DIR, "ocr_telemetry.json")
    AUDIO_DATA_PATH = os.path.join(ACTIVE_DIR, "audio_telemetry.json")

    st.markdown("---")

    # System Limitations
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px;'>SYSTEM LIMITATIONS</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style='font-size: 0.85rem; line-height: 1.6; color: #d4d4d8;'>
            <span style='color: #f43f5e;'>■</span> <b>UI Dependency:</b> The OCR engine relies on standard broadcast graphics. Custom scoreboards require recalibration.<br><br>
            <span style='color: #f43f5e;'>■</span> <b>Latency Shift:</b> The trailing-edge interpolation assumes a 6-12s TV broadcast delay. Variations can cause clipping.<br><br>
            <span style='color: #f43f5e;'>■</span> <b>Compute Overhead:</b> 1.0 FPS extraction limits scaling for real-time live broadcast integration.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Module Status
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px;'>MODULE UPLINK</p>", unsafe_allow_html=True)
    st.markdown("""
        <div class='mono-text' style='font-size: 0.85rem; line-height: 1.8; color: #e4e4e7;'>
            <span style='color: #10b981;'>[+]</span> JSON_PARSER   <span style='float:right; color: #a1a1aa;'>OK</span><br>
            <span style='color: #10b981;'>[+]</span> WHISPER_NLP   <span style='float:right; color: #a1a1aa;'>OK</span><br>
            <span style='color: #10b981;'>[+]</span> EASY_OCR      <span style='float:right; color: #a1a1aa;'>OK</span><br>
            <span style='color: #10b981;'>[+]</span> AUDIO_RMS     <span style='float:right; color: #a1a1aa;'>OK</span><br>
            <span style='color: #f59e0b;'>[-]</span> YOLO_VISION   <span style='float:right; color: #a1a1aa;'>IDLE</span>
        </div>
    """, unsafe_allow_html=True)

# --- VIEW 1: PROJECT ARCHITECTURE ---
if navigation == "Architecture Map":
    st.markdown("<h1 style='font-size: 3rem; font-weight: 800; margin-bottom: 0;'>SYSTEM ARCHITECTURE</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='color: #d4d4d8; font-size: 1.1rem; margin-bottom: 3rem;'>End-to-end data flow for the autonomous match highlight generator.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="step-card accent-indigo">
            <div class="step-number">01 // DATA INGESTION</div>
            <div class="step-title">Cricsheet JSON Parsing</div>
            <div class="step-desc">Ingests raw ball-by-ball metadata from Cricsheet APIs. Filters the entire dataset to extract only mathematically significant events (boundaries and wickets) to build the factual baseline.</div>
        </div>
        
        <div class="step-card accent-cyan">
            <div class="step-number">03 // VISION ENGINE</div>
            <div class="step-title">EasyOCR Frame Extraction</div>
            <div class="step-desc">Video is sliced at 1.0 FPS via OpenCV. An EasyOCR pipeline scans the physical pixels of the TV broadcast graphic to extract the current Innings, Over, and Ball.</div>
        </div>

        <div class="step-card accent-emerald">
            <div class="step-number">05 // SYNCHRONIZATION</div>
            <div class="step-title">Trailing Edge Interpolation</div>
            <div class="step-desc">Because TV graphics lag 5-10 seconds behind live action, the system algorithms anchor the video clip to the exact millisecond the <i>previous</i> graphic disappears, perfectly capturing the bowler's run-up.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="step-card accent-violet">
            <div class="step-number">02 // NLP PIPELINE</div>
            <div class="step-title">Whisper Commentary Mapping</div>
            <div class="step-desc">OpenAI's Whisper transcribes the broadcast audio track into timestamped blocks. These blocks are analyzed to confirm match narrative and filter out dead-ball commentary.</div>
        </div>
        
        <div class="step-card accent-rose">
            <div class="step-number">04 // SIGNAL PROCESSING</div>
            <div class="step-title">Librosa RMS Energy</div>
            <div class="step-desc">The audio waveform is analyzed using Librosa to calculate Root Mean Square (RMS) energy. This creates a quantifiable metric for "Crowd Roar", objectively measuring match excitement.</div>
        </div>
        
        <div class="step-card accent-amber">
            <div class="step-number">06 // MULTIMODAL FUSION</div>
            <div class="step-title">Confidence Matrix</div>
            <div class="step-desc">A final algorithmic pass combines the Cricsheet Priority, Audio Excitement (RMS), and Visual Anchors. Events scoring above the confidence threshold are passed to the FFmpeg renderer.</div>
        </div>
        """, unsafe_allow_html=True)

# --- VIEW 2: MATCH ANALYTICS DASHBOARD ---
else:
    st.markdown("<h1 style='font-size: 3rem; font-weight: 800; margin-bottom: 0;'>MATCH TELEMETRY</h1>",
                unsafe_allow_html=True)

    events = load_json(MATCH_DATA_PATH)
    ocr_telemetry = load_json(OCR_DATA_PATH)
    audio_telemetry = load_json(AUDIO_DATA_PATH)

    if not events:
        st.error(
            f"SYSTEM HALTED: Data not found in '{ACTIVE_DIR}'. Create this folder and add your JSON/MP4 files.")
        st.stop()

    # --- KPI METRICS ROW ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    df_events = pd.DataFrame(events)
    avg_conf = df_events['final_score'].mean() if not df_events.empty else 0
    total_time = (df_events['clip_end'] - df_events['clip_start']
                  ).sum() if not df_events.empty else 0

    m1.metric("HIGHLIGHTS EXTRACTED", f"{len(events)}")
    m2.metric("MEAN AI CONFIDENCE", f"{avg_conf:.2f}")
    m3.metric("REEL DURATION (SEC)", f"{total_time:.1f}")
    m4.metric("OCR ANCHORS FOUND",
              f"{len(ocr_telemetry) if ocr_telemetry else 0}")

    st.markdown("---")

    # --- DETAILED TABS ---
    tab_reel, tab_data, tab_charts = st.tabs([
        "VIDEO OUTPUT",
        "MASTER LEDGER",
        "WAVEFORM ANALYTICS"
    ])

    # TAB 1: VIDEO AND HIGHLIGHT COMPOSITION
    with tab_reel:
        st.markdown("<br>", unsafe_allow_html=True)
        v_col, d_col = st.columns([2, 1])

        with v_col:
            DROPBOX_STREAM_URL = "https://www.dropbox.com/scl/fi/svu4a2nb0lrlmb1dfsg65/match_highlights_fast.mp4?rlkey=yluk8r2ovr72ig3yv9rep2xyh&st=nicj6ag3&raw=1"

            try:
                st.video(DROPBOX_STREAM_URL)
            except Exception as e:
                st.error("UPLINK FAILED: Unable to establish secure stream.")

        with d_col:
            st.markdown(
                "<p style='font-size: 0.85rem; font-weight: 800; color: #a1a1aa; letter-spacing: 1px;'>HIGHLIGHT COMPOSITION</p>", unsafe_allow_html=True)

            # Replaced frames with an Event Type Donut Chart
            if not df_events.empty:
                event_counts = df_events['event_type'].value_counts(
                ).reset_index()
                event_counts.columns = ['Type', 'Count']
                event_counts['Type'] = event_counts['Type'].str.upper()

                fig_pie = px.pie(
                    event_counts,
                    names='Type',
                    values='Count',
                    hole=0.6,
                    color_discrete_sequence=[
                        '#06b6d4', '#6366f1', '#f43f5e', '#10b981']
                )
                fig_pie.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Inter",
                    margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom",
                                y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

                # Spotlighting the top highlight
                top_event = df_events.loc[df_events['final_score'].idxmax()]
                st.markdown(
                    "<p style='font-size: 0.85rem; font-weight: 800; color: #a1a1aa; letter-spacing: 1px; margin-top: 1rem;'>PEAK EVENT MATCH</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background-color: #18181b; border-left: 4px solid #10b981; padding: 16px; border-radius: 4px;'>
                    <p style='color: #10b981; font-weight: 800; margin: 0; font-size: 0.8rem;'>{top_event['event_type'].upper()} DETECTED</p>
                    <p style='color: #ffffff; font-weight: 700; font-size: 1.2rem; margin: 4px 0;'>Over {top_event['over']}.{top_event['ball']}</p>
                    <p style='color: #a1a1aa; font-size: 0.9rem; margin: 0;'>Confidence: {top_event['final_score']:.2f} | Audio RMS: {top_event['audio_score']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

    # TAB 2: DATA TABLE
    with tab_data:
        st.markdown("<br>", unsafe_allow_html=True)
        display_df = df_events[['innings', 'over', 'ball', 'event_type',
                                'final_score', 'audio_score', 'clip_start', 'clip_end']].copy()
        display_df.columns = ['INNINGS', 'OVER', 'BALL', 'EVENT TYPE',
                              'AI CONFIDENCE', 'RMS AUDIO', 'START (S)', 'END (S)']
        display_df['EVENT TYPE'] = display_df['EVENT TYPE'].str.upper()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "EVENT TYPE": st.column_config.TextColumn("EVENT TYPE"),
                "AI CONFIDENCE": st.column_config.ProgressColumn("FUSION CONFIDENCE", format="%.2f", min_value=0, max_value=1),
                "RMS AUDIO": st.column_config.NumberColumn("RMS ENERGY", format="%.2f"),
                "START (S)": st.column_config.NumberColumn(format="%.1f"),
                "END (S)": st.column_config.NumberColumn(format="%.1f"),
            }
        )

    # TAB 3: PLOTLY CHARTS
    with tab_charts:
        st.markdown("<br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown(
                "<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px;'>OCR TIMELINE PROGRESSION</p>", unsafe_allow_html=True)
            if ocr_telemetry:
                df_ocr = pd.DataFrame(ocr_telemetry)
                fig_ocr = px.scatter(df_ocr, x="timestamp", y="over_val")
                fig_ocr.update_traces(marker=dict(
                    size=5, color='#06b6d4', opacity=0.8))
                fig_ocr.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Inter",
                    xaxis_title="VIDEO ELAPSED (SEC)",
                    yaxis_title="MATCH OVERS",
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                fig_ocr.update_xaxes(
                    showgrid=True, gridwidth=1, gridcolor='#27272a')
                fig_ocr.update_yaxes(
                    showgrid=True, gridwidth=1, gridcolor='#27272a')
                st.plotly_chart(fig_ocr, use_container_width=True)

        with chart_col2:
            st.markdown(
                "<p style='font-size: 0.85rem; font-weight: 800; color: #e4e4e7; letter-spacing: 1px;'>STADIUM RMS ENERGY</p>", unsafe_allow_html=True)
            if audio_telemetry:
                df_audio = pd.DataFrame(audio_telemetry)
                fig_audio = go.Figure()
                fig_audio.add_trace(go.Scatter(
                    x=df_audio["time"], y=df_audio["energy"],
                    fill='tozeroy',
                    mode='lines',
                    line=dict(color='#f43f5e', width=1.5),
                    fillcolor='rgba(244, 63, 94, 0.15)'
                ))
                fig_audio.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Inter",
                    xaxis_title="VIDEO ELAPSED (SEC)",
                    yaxis_title="NORMALIZED RMS",
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                fig_audio.update_xaxes(
                    showgrid=True, gridwidth=1, gridcolor='#27272a')
                fig_audio.update_yaxes(
                    showgrid=True, gridwidth=1, gridcolor='#27272a')
                st.plotly_chart(fig_audio, use_container_width=True)
