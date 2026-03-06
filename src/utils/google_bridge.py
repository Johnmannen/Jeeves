import os
import pickle
import logging
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scopes som krävs för Jeeves
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

class GoogleBridge:
    def __init__(self):
        self.creds = None
        # Dynamiska sökvägar som fungerar både i Windows och Vercel (Linux)
        base_dir = os.getcwd()
        self.token_path = os.path.join(base_dir, 'token.pickle')
        self.secret_path = os.path.join(base_dir, 'client_secret.json')
        self._authenticate()

    def _authenticate(self):
        """Hanterar OAuth2-autentisering."""
        # 1. Försök läsa från ENV (för Molndrift/Vercel)
        import base64
        env_token = os.getenv("GOOGLE_TOKEN_PICKLE_BASE64")
        if env_token:
            # Rensa eventuella mellanslag/radbrytningar från kopieringen
            env_token = env_token.strip()
            logger.info("[GoogleBridge] Försöker ladda token från miljövariabel...")
            try:
                # Base64 padding-fix (måste vara multipel av 4)
                missing_padding = len(env_token) % 4
                if missing_padding:
                    env_token += '=' * (4 - missing_padding)
                
                self.creds = pickle.loads(base64.b64decode(env_token))
                logger.info("[GoogleBridge] Token framgångsrikt laddad från miljövariabel!")
            except Exception as e:
                logger.error(f"[GoogleBridge] Fel vid avkodning/laddning av ENV-token: {e}")
                self.creds = None

        # 2. Försök läsa från lokal fil
        if not self.creds and os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # 3. Validera och re-autha om möjligt
        # Kolla om creds saknas, är ogiltiga eller saknar vissa scopes
        if not self.creds or not self.creds.valid or not all(s in getattr(self.creds, "scopes", []) for s in SCOPES):
            if self.creds and self.creds.expired and self.creds.refresh_token and all(s in getattr(self.creds, "scopes", []) for s in SCOPES):
                self.creds.refresh(Request())
            elif os.getenv("VERCEL"):
                logger.warning("[GoogleBridge] VARNING: Saknar giltiga Google-creds i Vercel-miljö!")
                return
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Spara ner för lokal framtida användning (ej i molnet)
            if not os.getenv("VERCEL") and self.creds:
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

    def list_calendars(self):
        """Listar alla tillgängliga kalendrar."""
        service = build('calendar', 'v3', credentials=self.creds)
        calendar_list = service.calendarList().list().execute()
        return calendar_list.get('items', [])

    def get_upcoming_events(self, calendar_id='primary', max_results=10):
        """Hämtar kommande kalenderhändelser."""
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                "start": start,
                "summary": event.get('summary', '(Ingen rubrik)')
            })
        return formatted_events

if __name__ == "__main__":
    bridge = GoogleBridge()
    print("--- TILLGÄNGLIGA KALENDRAR ---")
    for cal in bridge.list_calendars():
        print(f"Namn: {cal['summary']} (ID: {cal['id']})")
    
    print("\n--- TEST PRIMARY ---")
    for e in bridge.get_upcoming_events():
        print(f"{e['start']}: {e['summary']}")
