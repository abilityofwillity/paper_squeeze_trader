# save as update_daily_picks.py
from paper_squeeze_trader_claude2 import generate_daily_picks, PICKS_FILE
import json
from datetime import date

def main():
    picks = generate_daily_picks()
    picks_data = {"date": date.today().isoformat(), "picks": picks}
    with open(PICKS_FILE, "w") as f:
        json.dump(picks_data, f, indent=2)

if __name__ == "__main__":
    main()
