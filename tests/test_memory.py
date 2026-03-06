import os
import sys

# Lägg till src i path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from agents.memory import get_stress_level, update_stress_level, init_db

def test_m1_adk_state():
    print("Testar ADK State Management...")
    
    # Test DB init
    init_db()
    
    import uuid
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    
    # Test read default
    level = get_stress_level(user_id)
    assert level == 5, f"Förväntade default 5, fick {level}"
    
    # Test update
    success = update_stress_level(user_id, 8)
    assert success == True, "Kunde inte uppdatera stress_level"
    
    # Test read updated
    new_level = get_stress_level(user_id)
    assert new_level == 8, f"Förväntade uppdaterad 8, fick {new_level}"
    
    # Test API Key
    from dotenv import load_dotenv
    load_dotenv()
    assert os.getenv("GEMINI_API_KEY") is not None, "Saknar GEMINI_API_KEY i .env"

    print("✅ Alla tester för Milestone 1 passerade.")

if __name__ == "__main__":
    test_m1_adk_state()
