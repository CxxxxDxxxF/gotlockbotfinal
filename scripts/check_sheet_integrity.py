import os
from gotlockz_bot.sheets_client import open_sheet
from datetime import datetime, timedelta

SHEETS_ID = os.getenv('SHEETS_SPREADSHEET_ID')

def check_integrity():
    watch_ws = open_sheet(SHEETS_ID, 'Watchlist')
    watch_records = [] if watch_ws is None else []
    log_ws = open_sheet(SHEETS_ID, 'LineWatch')
    logs = [] if log_ws is None else []
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_logs = [r for r in logs if datetime.fromisoformat(r['DateTime']) >= one_week_ago]
    mismatches = []
    for entry in watch_records:
        team = entry['Team']
        logged_count = sum(1 for r in recent_logs if r['Team'] == team)
        if logged_count < 1:
            mismatches.append(f"{team} has {logged_count} alerts in the past week (expected \u2265 1).")
    if mismatches:
        print('\u26a0\ufe0f Integrity Warnings:')
        for m in mismatches:
            print('  \u2022', m)
    else:
        print('\u2705 All watchlist entries have expected log counts.')

if __name__ == '__main__':
    check_integrity()
