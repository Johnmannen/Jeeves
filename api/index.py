import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Konfigurera loggning
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Förbättrad sökvägshantering för Vercel
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_PATH)
sys.path.append(os.path.join(ROOT_PATH, 'src'))

# Tog bort root_path härifrån, vi specificerar rutterna exakt istället!
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globala instanser (Lazy Loading)  - skapas noll och intet vid start
_chief = None
_proactivity = None

def get_chief():
    global _chief
    if _chief is None:
        from src.agents.chief import ChiefContextOfficer
        _chief = ChiefContextOfficer()
    return _chief

def get_proactivity():
    global _proactivity
    if _proactivity is None:
        from src.agents.proactivity import ProactivityAgent
        _proactivity = ProactivityAgent()
    return _proactivity

class ChatRequest(BaseModel):
    message: str
    stress_level: Optional[int] = None
    user_id: str = "john_doe"
    history: Optional[list] = None

# Hälso-check som Vercel aldrig kan missa!
@app.get("/")
@app.get("/api")
@app.get("/api/")
@app.get("/health")
@app.get("/api/health")
def read_root(request: Request):
    return {
        "status": "Jeeves is Alive (Bulletproof Mode)",
        "version": "1.1.4",
        "env": "Vercel",
        "path": request.url.path
    }

@app.get("/test")
@app.get("/api/test")
def test():
    return {"message": "Jeeves test-rutt fungerar! (v1.1.4)"}

@app.post("/chat")
@app.post("/api/chat")
async def chat(request: ChatRequest, req: Request):
    # Validera miljö (Stage 3.3)
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY saknas i miljön!")
        raise HTTPException(status_code=500, detail="Konfigurationsfel: API-nyckel saknas.")

    try:
        from src.agents.memory import update_stress_level, get_stress_level
        
        # Validera stress_level (Stage 3.3: Edge Cases)
        if request.stress_level is not None:
            clamped_stress = max(0, min(10, request.stress_level))
            update_stress_level(request.user_id, clamped_stress)
            
        current_stress = get_stress_level(request.user_id)
        
        from src.agents.context import ToolContext
        
        # Begränsa historiken (Stage 3.1: Token/History Management)
        safe_history = request.history or []
        MAX_HISTORY_MESSAGES = 10
        if len(safe_history) > MAX_HISTORY_MESSAGES:
            safe_history = safe_history[-MAX_HISTORY_MESSAGES:]
            
        ctx = ToolContext(user_id=request.user_id, stress_level=current_stress, history=safe_history)
        reply = get_chief().route_request(request.message, ctx)
        return {"reply": reply, "user_id": request.user_id}
    except Exception as e:
        logger.exception(f"API Error in /chat: {e}")
        # FIX: Exponera inte interna feldetaljer till klienten
        return {"reply": "Jeeves laddar batterierna... Försök igen!", "error": "internal_error"}

@app.get("/calendar")
@app.get("/api/calendar")
async def get_calendar(max_results: int = 10):
    try:
        from src.utils.google_bridge import GoogleBridge
        google = GoogleBridge()
        events = google.get_upcoming_events(max_results=max_results)
        if events:
            return {"events": events}
    except Exception as e:
        logger.error(f"Calendar API Error (falling back to mock): {e}")

    # Fallback till mock-data om riktig auth saknas i Vercel
    return {
        "events": [
            {"summary": "✨ Fokuspass: 25 min", "start": {"dateTime": "2026-03-01T14:00:00Z"}},
            {"summary": "💧 Påminnelse: Vatten", "start": {"dateTime": "2026-03-01T15:30:00Z"}},
            {"summary": "🌿 Mikropaus", "start": {"dateTime": "2026-03-01T17:00:00Z"}}
        ]
    }

@app.get("/user-state/{user_id}")
@app.get("/api/user-state/{user_id}")
async def get_user_state(user_id: str):
    from src.agents.memory import get_stress_level
    stress = get_stress_level(user_id)
    return {"user_id": user_id, "stress_level": stress}

@app.get("/wake-up")
@app.get("/api/wake-up")
async def wake_up(stress_level: int = 5):
    try:
        morning_greeting = get_proactivity().generate_morning_greeting(stress_level)
        return {"greeting": morning_greeting}
    except Exception as e:
        logger.error(f"Wake-up error: {e}", exc_info=True)
        return {"greeting": "God morgon! Är du redo?"}

# Global catch-all
@app.api_route("/{path_name:path}", methods=["GET", "POST"])
async def catch_all(request: Request, path_name: str):
    return {
        "error": "Jeeves Route Not Found",
        "debug": {"path_name": path_name, "url_path": request.url.path}
    }
