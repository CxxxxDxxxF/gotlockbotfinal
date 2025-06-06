"""Wrapper around the gspread client."""

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SheetsClient:
    def __init__(self, creds_path: str):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        self.client = gspread.authorize(creds)

    def get_sheet(self, name: str):
        return self.client.open(name).sheet1
