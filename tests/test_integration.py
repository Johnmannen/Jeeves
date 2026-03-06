import os
import sys

# Lägg till src i path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from agents.chief import ChiefContextOfficer
from agents.memory import update_stress_level
from agents.context import ToolContext

def test_end_to_end():
    print("Startar End-to-End Test (Input -> Chief -> Memory -> SubAgent)...")
    
    chief = ChiefContextOfficer()
    user_id = "e2e_test_user_999"
    
    # --- Scenario 1: Dr Phil (Hög stress) ---
    print("\n--- Scenario 1: Emotionellt stöd (Hög stress) ---")
    update_stress_level(user_id, 9)
    ctx_high = ToolContext(user_id=user_id, stress_level=9)
    input_text = "Allt är för mycket, jag orkar ingenting idag."
    
    # 1. Kolla om routing fungerar korrekt
    category = chief.route_input(input_text)
    assert category == "Dr_Phil", f"Förväntade Dr_Phil, fick {category}"
    print("[PASS] Routing klassificerade rätt kategori (Dr_Phil)")
    
    # 2. Testa hela flödet
    response = chief.route_request(input_text, ctx_high)
    assert response is not None and len(response) > 0, "Fick tomt svar"
    print(f"Jeeves svarar:\n{response}")
    print("[PASS] End-to-End slutfört för Dr Phil")

    # --- Scenario 2: Task Manager (Låg stress) ---
    print("\n--- Scenario 2: Struktur och Planering (Låg stress) ---")
    update_stress_level(user_id, 2)
    ctx_low = ToolContext(user_id=user_id, stress_level=2)
    input_text = "Vad ska jag göra nu? Behöver lägga in tvätt."
    
    # 1. Kolla routing
    category = chief.route_input(input_text)
    assert category == "Task_Manager", f"Förväntade Task_Manager, fick {category}"
    print("[PASS] Routing klassificerade rätt kategori (Task_Manager)")
    
    # 2. Testa hela flödet
    response = chief.route_request(input_text, ctx_low)
    assert response is not None and len(response) > 0, "Fick tomt svar"
    print(f"Jeeves svarar:\n{response}")
    print("[PASS] End-to-End slutfört för Task Manager")

    print("\n✅ [SUCCESS] Alla End-to-End tester passerade!")

if __name__ == "__main__":
    test_end_to_end()
