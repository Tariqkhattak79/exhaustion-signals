import pypsx_toolkit as pt
import pandas as pd
import os

os.makedirs('data', exist_ok=True)

# Read symbols from the root folder
if os.path.exists('symbols.txt'):
    with open('symbols.txt', 'r') as f:
        syms = [line.strip() for line in f if line.strip()]
        
    for sym in syms:
        try:
            df = pt.download(sym, period="400d")
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(-1)
                df = df.reset_index()
                df.columns = [c.lower() for c in df.columns]
                df.to_csv(f"data/{sym}.csv", index=False)
        except:
            pass
