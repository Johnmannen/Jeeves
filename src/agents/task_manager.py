import os
import logging
from google import genai
from google.genai import types

from src.agents.utils import format_conversation_history
from src.agents.exceptions import ConfigError

# Konfigurera loggning
logger = logging.getLogger(__name__)

class TaskManagerAgent:
    """
    Sub-agent som fokuserar på struktur, planering och sysslor.
    För MVP kan vi mocka ADK tool integrationen för Notion/Calendar.
    """
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigError("GEMINI_API_KEY saknas i miljön.", missing_key="GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        self.base_persona = (
            "Du är Jeeves 'Task Manager', din personliga ADHD-protes. "
            "REGLER: Svara i MAX 2-3 korta meningar. Max 3 punkter i listor. "
            "Bryt ner mål i mikrosteg. Sänk tröskeln till handling. Aldrig dömande. "
            "OM du föreslår en tidsbegränsad uppgift (t.ex. städa i 5 minuter), "
            "MÅSTE du lägga till taggen [TIMER:sekunder] i slutet av ditt svar. "
            "Exempel: 'Då kör vi 5 minuter plock! [TIMER:300]'"
        )

    def handle_request(self, user_input: str, tool_context=None) -> str:
        """
        Svarar på strukturella förfrågningar och simulerar användning av verktyg.
        """
        stress_level = 5
        if tool_context:
            stress_level = getattr(tool_context, 'stress_level', 5)
            
        # Anpassa instruktionerna baserat på energi (Stressnivå i state)
        state_instruction = ""
        if stress_level >= 8:
            state_instruction = (
                "AKUT REAKTION: Användaren är överväldigad. Ge BARA ETT ENDA (1) löjligt litet steg åt gången (Atomic Action). "
                "T.ex. 'Vi börjar med att bara öppna fönstret en stund'. \n"
                "VISA INGA LISTOR ÖVERHUVUDTAGET."
            )
        elif stress_level <= 3:
            state_instruction = (
                "Användaren har hög energi. Du kan ge en djupt strukturerad och inspirerande lista på nästa steg. "
                "Här kan vi titta på lite större block för att rida på energin."
            )
        else:
            state_instruction = "Håll stödet på en balanserad nivå. Bryt ner saker i ca 2-3 konkreta mikrosteg."

        history_str = ""
        if tool_context and hasattr(tool_context, 'history') and tool_context.history:
            history_str = format_conversation_history(tool_context.history)
            
        system_prompt = f"{self.base_persona}\n\n{state_instruction}\n{history_str}"

        # Här framöver kan vi lägga till Tools för att anropa ex. Google Calendar API eller Notion API
        # tools=[notion_create_task, google_cal_get_events]

        try:
            response = self.client.models.generate_content(
                 model=self.model,
                 contents=f"Användarens inmatning: {user_input}\nSvara som Task Manager:",
                 config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3 # Lågt för att hålla sig strukturerad/konkret
                 )
            )
            if not response.text:
                return "Jag har uppdaterat schemat. Något mer jag kan strukturera upp åt dig?"
            return response.text.strip()
        except Exception as e:
            logger.error(f"[TaskManager] Fel vid generering: {e}", exc_info=True)
            return "Jag hade problem med att hämta schemat. Förlåt för det."

if __name__ == "__main__":
    from src.agents.context import ToolContext
    agent = TaskManagerAgent()
            
    print("--- Test Normal ---")
    print(agent.handle_request("Vad borde jag börja med idag?", ToolContext(user_id="test", stress_level=5)))
