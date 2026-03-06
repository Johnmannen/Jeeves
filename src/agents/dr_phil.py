import os
import logging
from google import genai
from google.genai import types

from src.agents.utils import format_conversation_history
from src.agents.exceptions import ConfigError, GeminiAPIError

# Konfigurera loggning
logger = logging.getLogger(__name__)

class DrPhilAgent:
    """
    Sub-agent som fokuserar på emotionellt stöd och uppmuntran.
    Använder RAG-instruktioner (hårdkodade för MVP) och ADK State
    för att anpassa sin ton efter användarens stressnivå.
    """
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigError("GEMINI_API_KEY saknas i miljön.", missing_key="GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash") # Stabil standardmodell för free tier
        
        # Simulerad RAG för "Vibe & Tone" (M1).
        # I framtiden hämtas detta via API från NotebookLM/Vector DB.
        self.base_persona = (
            "Du är Jeeves 'Dr Phil'-persona, ett empatiskt stöd för en person med ADHD. "
            "REGLER: Svara i MAX 2-3 korta meningar. Radikal Acceptans. Skamfri Design. "
            "När användaren är överväldigad, bekräfta känslan först."
        )

    def handle_request(self, user_input: str, tool_context=None) -> str:
        """
        Gör ett API-anrop till Gemini baserat på inmatning och nuvarande stressnivå.
        """
        stress_level = 5
        if tool_context:
            stress_level = getattr(tool_context, 'stress_level', 5)
            
        # Anpassa prompten efter state (Neuro-kalibrering)
        state_instruction = ""
        if stress_level >= 8:
            state_instruction = (
                "VARNING: Användaren är i ADHD-paralys/extrem stress (Nivå 8+). \n"
                "REGEL: Kräv absolut ingenting. Ge inga råd om vad som 'borde' göras. \n"
                "DIN ENDA UPPGIFT: Var en trygg hamn. Använd runda, mjuka meningar. "
                "Bekräfta t.ex. att det är okej att bara sitta i soffan en stund till."
            )
        elif stress_level <= 3:
            state_instruction = "Användaren har energi (Nivå 1-3). Du kan vara lite mer peppande och inspirerande, men behåll den skamfria tonen."
        else:
            state_instruction = "Användaren är på en normal nivå. Var stödjande, empatisk och lyssna aktivt."

        # Hämtar specifik ADHD-kontext från den globala text-RAG-laddaren (BUG-06/Vercel Cloud Support)
        notebook_context = ""
        try:
            from src.agents.rag_loader import get_rag_info
            context_text = get_rag_info(query_topic="adhd_strategy")
            if context_text:
                # Vi skickar med en relevant sammanfattning av RAG-texten
                notebook_context = f"\n\nDIN KUNSKAPSDATABAS (ADHD-PRINCIPER):\n{context_text[:15000]}" # Begränsa för att spara tokens
        except Exception as e:
            logger.warning(f"[DrPhil] RAG-laddning misslyckades (degraderar elegant): {e}")

        history_str = ""
        if tool_context and hasattr(tool_context, 'history') and tool_context.history:
            history_str = format_conversation_history(tool_context.history)
            
        system_prompt = f"{self.base_persona}\n\n{state_instruction}{notebook_context}\n{history_str}"

        try:
            response = self.client.models.generate_content(
                 model=self.model,
                 contents=user_input,
                 config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7 # Lite högre temperatur för mer empatisk variation
                 )
            )
            if not response.text:
                return "Jag förstår att det är mycket nu. Berätta hur jag kan hjälpa dig på bästa sätt."
            return response.text.strip()
        except Exception as e:
            logger.error(f"[DrPhil] Fel vid generering: {e}", exc_info=True)
            return "Förlåt, jag har lite svårt att tänka klart just nu, men jag är här för dig."

if __name__ == "__main__":
    from src.agents.context import ToolContext
    agent = DrPhilAgent()
    
    print("--- Test Låg Stress ---")
    print(agent.handle_request("Jag känner mig lite off idag.", ToolContext(user_id="test", stress_level=2)))
    print("\n--- Test Hög Stress ---")
    print(agent.handle_request("Mitt huvud exploderar av allt jag måste göra!!", ToolContext(user_id="test", stress_level=9)))
