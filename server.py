"""
Jeeves ADHD Butler — Lokal startfil
===================================
Shadow-API borttaget (2026-03-06).
Denna fil pekar nu enkom på Vercel-routern (`api/index.py`) för att garantera
att lokal utveckling kör EXAKT samma kod som moln-miljön.
"""

import uvicorn
import os
import sys

# Säkerställ att api och src syns i mappen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importera den gemensamma källan till sanning (Routern)
from api.index import app

if __name__ == "__main__":
    print("-" * 50)
    print("🚀 Startar Jeeves Lokalt via api/index.py (Unified Mode)")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)

