import os
import json
import logging
from google import genai
from google.genai import types

# Konfigurera loggning
logger = logging.getLogger(__name__)

from src.agents.exceptions import ConfigError

class ProactivityAgent:
    """
    Agent för proaktiva handlingar, såsom den 'Kreativa Väckarklockan'.
    Den analyseras kalenderdata och skapar ett personligt morgonmeddelande.
    """
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigError("GEMINI_API_KEY saknas i miljön.", missing_key="GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        
        # Initiera en säker mock-kalender för att förhindra krascher i molnet
        class MockBridge:
            def get_upcoming_events(self, max_results=5):
                return [{"summary": "Inga möten (Mock)", "start": "Idag"}]
        self.google = MockBridge()

    def generate_morning_greeting(self, stress_level=5):
        """
        Genererar en unik och peppande väckningsfras baserat på dagens händelser.
        """
        # Hämta RIKTIGA händelser från Google Kalender
        events = self.google.get_upcoming_events(max_results=5)
        events_str = json.dumps(events, indent=2)
        
        system_instruction = (
            "Du är Jeeves i din 'Kreativa Väckarklocka'-mode. "
            "DIN UPPGIFT: Skapa en varm och peppande morgonhälsning. "
            "DIN PRINCIP: Radikal Acceptans och Skamfri Design. "
            "REGLER FÖR VARIATION: Variera alltid din hälsning. "
            "Använd en kombination av ett konstaterande (statement) och en fråga. "
            "Undvik att låta som en robot eller att upprepa samma fras varje gång. "
            "ANVISNINGAR: \n"
            "1. MAX 3 KORTA MENINGAR. Ingen lång text. \n"
            "2. Om stressen är hög: BARA ett mikrosteg ('börja med att sätta på kaffet'). \n"
            "3. Om stressen är låg: nämn en rolig sak i kalendern. \n"
            "4. Aldrig dömande. Aldrig om att man sovit länge."
        )
        
        user_prompt = f"Stressnivå: {stress_level}/10. \nKalender: \n{events_str} \n\nSkriv morgonhälsningen (max 3 meningar):"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8 # Kreativitet är viktigt här
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"[Proactivity] Fel vid väckning: {e}", exc_info=True)
            return "God morgon John. Det är okej att ta det i din takt idag. Jag finns här när du är redo."

if __name__ == "__main__":
    agent = ProactivityAgent()
    print("--- Test Väckning (Hög Stress) ---")
    print(agent.generate_morning_greeting(stress_level=9))
    print("\n--- Test Väckning (Låg Stress) ---")
    print(agent.generate_morning_greeting(stress_level=3))
