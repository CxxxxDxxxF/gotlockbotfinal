"""Stub Google Sheets client for testing."""

_watchlist = []
_picks = []
_linewatch_logs = []


def get_count_of_type(sheet_id: str, pick_type: str) -> int:
    return sum(1 for p in _picks if p.get('type') == pick_type)


def append_pick_to_sheet(sheet_id: str, row: list):
    _picks.append({'type': row[1], 'Units': row[-1], 'Payout': 0, 'Result': 'W'})


def append_watchlist_row(row: list) -> int:
    row_id = len(_watchlist) + 1
    entry = {
        'RowID': row_id,
        'UserID': row[0],
        'Team': row[1],
        'Opponent': row[2],
        'Threshold': row[3],
        'ChannelID': row[4],
        'LastLine': row[5],
        'GameDate': row[6],
    }
    _watchlist.append(entry)
    return row_id


def get_watchlist():
    return list(_watchlist)


def append_linewatch_log(row: list):
    _linewatch_logs.append({
        'DateTime': row[0],
        'Team': row[1],
        'OldLine': row[2],
        'NewLine': row[3],
        'Difference': row[4],
        'GameDate': row[5],
    })


def update_watchlist_last_line(row_id: int, new_line: int):
    for e in _watchlist:
        if e['RowID'] == row_id:
            e['LastLine'] = new_line
            break


def get_recent_linewatch_logs(hours: int):
    return list(_linewatch_logs)


def get_all_picks_for_user(user_id: int):
    return [p for p in _picks if p.get('UserID') == user_id]


def open_sheet(sheet_id: str, name: str):
    return None
