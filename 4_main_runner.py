import os
import json
from importlib import import_module

logic = import_module("2_exhaustion_logic")
emailer = import_module("3_send_email")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

def run_app():
    print("Starting Exhaustion Setup Scan...")
    results = []
    
    if not os.path.exists(DATA_FOLDER):
        print("Data folder missing!")
        return
        
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    print(f"Found {len(files)} files to scan.")
    
    for filename in files:
        sym = filename.replace(".csv", "")
        path = os.path.join(DATA_FOLDER, filename)
        
        signal_data = logic.check_exhaustion_setup(path)
        
        if signal_data:
            signal_data["symbol"] = sym
            results.append(signal_data)
            
    print(f"Scan complete. Found {len(results)} signals.")
    
    with open("live_scan.json", "w") as f: 
        json.dump(results, f, indent=4)
        
    emailer.send_signals_email(results)

if __name__ == "__main__":
    run_app()
