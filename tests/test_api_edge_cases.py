import os
import sys

# Lägg till src i path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from api.index import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_edge_cases():
    from dotenv import load_dotenv
    load_dotenv()
    print("Testar Edge Cases (Stage 3.3)...")
    
    # Test 1: Ogiltig stressnivå (för hög)
    print(" - Testar stressnivå 99 (ska clampas till 10)")
    payload = {
        "message": "Hej",
        "user_id": "edge_tester",
        "stress_level": 99
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    
    # Verifiera via user-state att den blev 10
    state_res = client.get("/user-state/edge_tester")
    assert state_res.json()["stress_level"] == 10
    print("   ✅ Stressnivå clampades korrekt till 10.")

    # Test 2: Negativ stressnivå (ska clampas till 0)
    print(" - Testar stressnivå -5 (ska clampas till 0)")
    payload["stress_level"] = -5
    client.post("/chat", json=payload)
    state_res = client.get("/user-state/edge_tester")
    assert state_res.json()["stress_level"] == 0
    print("   ✅ Stressnivå clampades korrekt till 0.")

    print("\n✅ Alla Edge Case-tester passerade!")

if __name__ == "__main__":
    test_edge_cases()
