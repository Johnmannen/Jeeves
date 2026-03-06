import os
import sys

# Lägg till src i path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from agents.dr_phil import DrPhilAgent
from agents.task_manager import TaskManagerAgent
from agents.memory import update_stress_level
from agents.context import ToolContext

def test_subagents():
    print("Testar Sub-Agenter för Milestone 3...")
    
    # Initiera agenter
    dr_phil = DrPhilAgent()
    task_manager = TaskManagerAgent()
    
    # Kör Dr Phil med Hög Stress (Nivå 9)
    print("\n[M3] Testar Dr_Phil med Hög Stress (Nivå 9)...")
    test_user_high = "test_user_drphil_high"
    update_stress_level(test_user_high, 9)
    ctx_high = ToolContext(user_id=test_user_high, stress_level=9)
    response_phil = dr_phil.handle_request("Mitt huvud exploderar av allt jag måste göra!!", ctx_high)
    assert response_phil is not None and len(response_phil) > 0, "Dr Phil returnerade ett tomt svar"
    print(f"Svar: {response_phil}")
    print("PASS: Dr Phil genererade ett svar")
    
    # Kör Task Manager med Låg Stress (Nivå 2)
    print("\n[M3] Testar Task_Manager med Låg Stress (Nivå 2)...")
    test_user_low = "test_user_taskmgr_low"
    update_stress_level(test_user_low, 2)
    ctx_low = ToolContext(user_id=test_user_low, stress_level=2)
    response_task = task_manager.handle_request("Vad borde jag börja med idag?", ctx_low)
    assert response_task is not None and len(response_task) > 0, "Task Manager returnerade ett tomt svar"
    print(f"Svar: {response_task}")
    print("PASS: Task Manager genererade ett svar")

    print("\n[SUCCESS] Alla tester för Milestone 3 passerade med riktiga agentanrop!")

if __name__ == "__main__":
    run_m3_tests()
