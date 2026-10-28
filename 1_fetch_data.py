import pypsx_toolkit as pt
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE_DIR, "data")
SYMBOLS_FILE = os.path.join(BASE_DIR, "symbols.txt")

def download_data():
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(SYMBOLS_FILE):
        print("ERROR: symbols.txt not found!")
        return
    with open(SYMBOLS_FILE, "r") as f:
        syms = [line.strip() for line in f if line.strip()]
    print(f"Total count: {len(syms)}")
    
    ok, fail = 0, 0
    for sym in syms:
        try:
            df = pt.download(sym, period="400d")
            if df is None or df.empty:
                fail += 1
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(-1)
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            df.to_csv(os.path.join(OUT, f"{sym}.csv"), index=False)
            ok += 1
        except:
            fail += 1
    print(f"DONE ok={ok} fail={fail}")

if __name__ == "__main__":
    download_data()
