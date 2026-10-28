import streamlit as st
import pandas as pd
import numpy as np
import os

# ==========================================
# LOGIC
# ==========================================
def calculate_volume_profile(df, bins=30):
    try:
        price_min = df["low"].min()
        price_max = df["high"].max()
        if price_max == price_min: return None, None
        bins_arr = np.linspace(price_min, price_max, bins + 1)
        df = df.copy()
        df["bin"] = pd.cut(df["close"], bins=bins_arr, labels=False)
        vol_profile = df.groupby("bin")["volume"].sum()
        poc_bin = vol_profile.idxmax()
        poc_price = (bins_arr[int(poc_bin)] + bins_arr[int(poc_bin) + 1]) / 2
        sorted_bins = vol_profile.sort_values(ascending=False)
        hvn_bin = sorted_bins.index[1] if len(sorted_bins) > 1 else poc_bin
        hvn_price = (bins_arr[int(hvn_bin)] + bins_arr[int(hvn_bin) + 1]) / 2
        return poc_price, hvn_price
    except:
        return None, None

def check_exhaustion_setup(file_path):
    MIN_DROP_PCT = 3.0     
    LOOKBACK_DAYS = 60     
    try:
        df = pd.read_csv(file_path)
        date_col = "time" if "time" in df.columns else "date"
        df = df.sort_values(date_col).reset_index(drop=True)
        if len(df) < 20: return None
            
        today = df.iloc[-1]
        yesterday = df.iloc[-2]
        
        prev_is_red = yesterday["close"] < yesterday["open"]
        is_green = today["close"] > today["open"]
        low_vol = today["volume"] < yesterday["volume"]
        
        lookback_window = df.tail(LOOKBACK_DAYS)
        high_idx = lookback_window["high"].idxmax()
        recent_high = df.loc[high_idx, "high"]
        drop_pct = ((recent_high - yesterday["low"]) / recent_high) * 100
        is_downtrend = drop_pct >= MIN_DROP_PCT
        days_since_high = len(df) - 1 - high_idx

        avg_vol20 = df["volume"].tail(20).mean()
        is_cat_a = (yesterday["volume"] > (avg_vol20 * 1.2)) and (today["volume"] < (yesterday["volume"] * 0.6))
        
        if prev_is_red and is_green and low_vol and is_downtrend:
            entry = round(today["close"], 2)
            drop_window = df.loc[high_idx:len(df)-2]
            poc, hvn = calculate_volume_profile(drop_window)
            
            if hvn and hvn < entry:
                stop = round(hvn * 0.99, 2) 
            else:
                calculated_stop = round(yesterday["low"] * 0.99, 2)
                stop = calculated_stop if calculated_stop < entry else round(entry * 0.98, 2)
                
            if poc and poc > entry:
                target = round(poc, 2)
            else:
                risk = entry - stop
                target = round(entry + (risk * 2), 2)
                
            category = "CAT A" if is_cat_a else "CAT B"
            return {
                "entry": entry, "stop": stop, "target": target,
                "today_vol": int(today["volume"]), "prev_vol": int(yesterday["volume"]),
                "drop_pct": round(drop_pct, 1), "drop_days": int(days_since_high),
                "category": category
            }
    except:
        pass
    return None

# ==========================================
# UI
# ==========================================
st.set_page_config(page_title="Exhaustion Signals", layout="centered")

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

st.title("🔥 Exhaustion Signals")

@st.cache_data(ttl=60)
def get_signals():
    results = []
    if not os.path.exists("data"): return results
    files = [f for f in os.listdir("data") if f.endswith(".csv")]
    
    for filename in files:
        sym = filename.replace(".csv", "")
        path = os.path.join("data", filename)
        signal = check_exhaustion_setup(path)
        if signal:
            signal["symbol"] = sym
            results.append(signal)
    return results

with st.spinner("Scanning stocks..."):
    signals = get_signals()

search_query = st.text_input("🔍 Search Symbol (e.g., PPL, ABL)", "").upper()

# Separate into CAT A and CAT B
cat_a_signals = [s for s in signals if s["category"] == "CAT A"]
cat_b_signals = [s for s in signals if s["category"] == "CAT B"]

# Filter by search
if search_query:
    cat_a_signals = [s for s in cat_a_signals if search_query in s['symbol']]
    cat_b_signals = [s for s in cat_b_signals if search_query in s['symbol']]

def render_card(s):
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
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# COLLAPSIBLE SECTIONS
# ==========================================
st.markdown(f"### ! {len(cat_a_signals) + len(cat_b_signals)} LIVE SIGNALS")

with st.expander(f"🟢 CAT A ({len(cat_a_signals)} Signals)", expanded=True):
    if not cat_a_signals:
        st.write("No CAT A signals today.")
    for s in cat_a_signals:
        render_card(s)

with st.expander(f"🟡 CAT B ({len(cat_b_signals)} Signals)", expanded=True):
    if not cat_b_signals:
        st.write("No CAT B signals today.")
    for s in cat_b_signals:
        render_card(s)
