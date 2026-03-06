import os
import sys

# Lägg till src i path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from api.index import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_history_truncation():
    from dotenv import load_dotenv
    load_dotenv()
    print("Testar begränsning av chatthistorik (Stage 3.1)...")
    
    # Skapa en gigantisk historik (12 meddelanden)
    large_history = [{"role": "user", "text": f"Meddelande {i}"} for i in range(12)]
    
    payload = {
        "message": "En sista fråga",
        "user_id": "history_test_user",
        "history": large_history
    }
    
    # Vi kan inte direkt testa `api/index.py` interna state, men vi kan verifiera 
    # att anropet lyckas utan att krascha och vi kan kolla loggarna om vi vill.
    # För unittest-syfte här verifierar vi bara att API:et svarar.
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    
    print("✅ API:et hanterade stor historik utan problem.")

if __name__ == "__main__":
    test_history_truncation()
