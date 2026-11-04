import streamlit as st
import os
import pandas as pd
from importlib import import_module

# Import our logic
logic = import_module("2_exhaustion_logic")

# Set page config for mobile
st.set_page_config(page_title="Exhaustion Setup", layout="centered")

# Custom CSS to match your screenshot
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .signal-card { background-color: #1E232E; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #FF9800; }
    .cat-a { background-color: #00E676; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .cat-b { background-color: #FFC107; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .entry-box { background-color: #004D40; padding: 10px; border-radius: 5px; text-align: center; }
    .stop-box { background-color: #B71C1C; padding: 10px; border-radius: 5px; text-align: center; }
    .target-box { background-color: #1A237E; padding: 10px; border-radius: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🔥 Live 3PM Scan")

# Scan Data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

@st.cache_data(ttl=60)
def get_signals():
    results = []
    if not os.path.exists(DATA_FOLDER): return results
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    
    for filename in files:
        sym = filename.replace(".csv", "")
        path = os.path.join(DATA_FOLDER, filename)
        signal = logic.check_exhaustion_setup(path)
        if signal:
            signal["symbol"] = sym
            results.append(signal)
    results.sort(key=lambda x: (x["category"] != "CAT A", -x["drop_pct"]))
    return results

with st.spinner("Scanning 278 stocks..."):
    signals = get_signals()

st.markdown(f"### ! {len(signals)} LIVE 3PM SIGNALS")

# Display Cards
for s in signals:
    cat_class = "cat-a" if s["category"] == "CAT A" else "cat-b"
    
    st.markdown(f"""
    <div class="signal-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: white;">{s['symbol']}</h3>
            <span class="{cat_class}">{s['category']}</span>
        </div>
        <p style="color: #A0AAB5; font-size: 14px; margin-top: 10px;">
            Yesterday Vol: <b>{s['prev_vol']:,}</b> | Today Vol: <b>{s['today_vol']:,}</b><br>
            Context: Dropped <b>{s['drop_pct']}%</b> over {s['drop_days']} days.
        </p>
        <div style="display: flex; justify-content: space-between; margin-top: 15px; gap: 10px;">
            <div class="entry-box" style="flex: 1;">
                <div style="font-size: 10px; color: #A0AAB5;">ENTRY</div>
                <div style="font-size: 18px; font-weight: bold; color: #00E676;">{s['entry']}</div>
            </div>
            <div class="stop-box" style="flex: 1;">
                <div style="font-size: 10px; color: #A0AAB5;">STOP</div>
                <div style="font-size: 18px; font-weight: bold; color: #FF5252;">{s['stop']}</div>
            </div>
            <div class="target-box" style="flex: 1;">
                <div style="font-size: 10px; color: #A0AAB5;">TARGET</div>
                <div style="font-size: 18px; font-weight: bold; color: #448AFF;">{s['target']}</div>
            </div>
        </div>
        <p style="color: #FF9800; font-size: 12px; margin-top: 10px; font-style: italic;">
            Exhaustion Bounce: Green today on drastically lower volume after a major downtrend.
        </p>
    </div>
    """, unsafe_allow_html=True)
