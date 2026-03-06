import os
import pickle
import datetime
from googleapiclient.discovery import build

class GoogleDiag:
    def __init__(self):
        self.token_path = r'C:\Jeeves_ADHD_Butlern\token.pickle'
        with open(self.token_path, 'rb') as token:
            self.creds = pickle.load(token)
        self.service = build('calendar', 'v3', credentials=self.creds)

    def run_diag(self):
        print(f"--- DIAGNOSTIK: {datetime.datetime.now()} ---")
        
        # 1. Vilka kalendrar ser vi?
        cals = self.service.calendarList().list().execute().get('items', [])
        print(f"\nAntal kalendrar hittade: {len(cals)}")
        for cal in cals:
            print(f"- {cal['summary']} (ID: {cal['id']})")
            if cal.get('primary'):
                print("  [DETTA ÄR DIN HUVUDKALENDER]")

        # 2. Hämta händelser från huvudkalendern
        print("\n--- HÄNDELSER I HUVUDKALENDERN (Primary) ---")
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        if not events:
            print("Inga kommande händelser hittades i primary.")
        else:
            for e in events:
                start = e['start'].get('dateTime', e['start'].get('date'))
                status = e.get('status', 'unknown')
                print(f"[{start}] Status: {status} | Rubrik: {e.get('summary')}")

if __name__ == "__main__":
    diag = GoogleDiag()
    diag.run_diag()
