import os
import logging
from typing import Literal
from google import genai
from google.genai import types

from src.agents.dr_phil import DrPhilAgent
from src.agents.task_manager import TaskManagerAgent
from src.agents.utils import format_conversation_history
from src.agents.exceptions import ConfigError, GeminiAPIError, RoutingError

# Konfigurera loggning
logger = logging.getLogger(__name__)

def get_gemini_client():
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ConfigError("GEMINI_API_KEY saknas i miljön.", missing_key="GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

class ChiefContextOfficer:
    """
    Chief Context Officer är den primära agenten som bedömer användarens inmatning
    och delegerar till rätt sub-agent. Den är designad för snabb routing (intent recognition).
    """
    def __init__(self):
        self.client = get_gemini_client()
        # Vi använder en snabb och billig modell för intent recognition
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Initiera sub-agenter
        self.dr_phil = DrPhilAgent()
        self.task_manager = TaskManagerAgent()
    
    def route_input(self, user_input: str) -> str:
        """
        Klassificerar användarens input för att bestämma vilken agent som ska ta över.
        """
        prompt = f"""Du är en Chief Context Officer för Jeeves, en virtuell ADHD-butler.
Din enda uppgift är att klassificera användarens inmatning i en av tre kategorier:
1. "Dr_Phil" - Välj detta om användaren uttrycker stress, ångest, oro, överväldigande känslor, behöver peppning, eller pratar om sitt mående ("jag känner mig stressad", "jag orkar inte", "allt är för mycket").
2. "Task_Manager" - Välj detta om användaren pratar om sysslor, kalender, planering, "todo list", lägga till saker att göra, tider, scheman eller struktur ("vad ska jag göra", "lägg in tvätt", "möte imorgon").
3. "General" - Välj detta BARA om inmatningen är en allmän hälsning eller en fråga som absolut inte är en uppgift eller emotionellt uttryck (t.ex. "Hej, läget?", "Vem är du?", "God morgon").

Svara BARA med kategori-namnet exakt som skrivet ovan ("Dr_Phil", "Task_Manager", eller "General").

Användarens inmatning: "{user_input}"
Kategori:"""

        try:
            response = self.client.models.generate_content(
                 model=self.model,
                 contents=prompt,
                 config=types.GenerateContentConfig(
                    temperature=0.1, 
                    max_output_tokens=100
                 )
            )
            
            if not response.text:
                return "General"
                
            result = response.text.strip().replace('"', '')
            if result in ["Dr_Phil", "Task_Manager", "General"]:
                return result
            
            if "Dr_Phil" in result: return "Dr_Phil"
            if "Task_Manager" in result: return "Task_Manager"
            return "General"
            
        except Exception as e:
            logger.error(f"[Chief] Fel vid routing: {e}", exc_info=True)
            return "General"  # Graceful degradation: faller tillbaka till General

    def route_request(self, user_input: str, tool_context=None) -> str:
        """
        Orkestrerar hela flödet: Klassificera -> Delegerera -> Returnera svar.
        """
        # Kolla om det är en mood-trigger från slidern
        if user_input.startswith("[MOOD_CHANGE]"):
            return self.handle_mood_change(user_input, tool_context)
        
        category = self.route_input(user_input)
        logger.info(f"[Chief] Delegerar till: {category}")
        
        if category == "Dr_Phil":
            return self.dr_phil.handle_request(user_input, tool_context)
        elif category == "Task_Manager":
            return self.task_manager.handle_request(user_input, tool_context)
        else:
            # Allmänt svar för General/Hälsningar
            return self.handle_general(user_input, tool_context)

    def handle_mood_change(self, user_input: str, tool_context=None) -> str:
        """
        Hanterar proaktiv respons när användaren ändrar humGet i slidern.
        Erbjuder konkreta förslag baserat på stressnivån.
        """
        stress_level = 5
        if tool_context:
            stress_level = getattr(tool_context, 'stress_level', 5)

        common_rules = (
            "REGLER FÖR VARATION: Variera alltid din hälsning. "
            "Använd en kombination av ett konstaterande (statement) och en fråga. "
            "Undvik att låta som en robot eller att upprepa samma fras varje gång. "
            "Använd ett varmt, mänskligt och ADHD-anpassat språk."
        )

        if stress_level >= 8:
            prompt = (
                f"Användaren har just markerat hög stress ({stress_level}/10). "
                "Hälsa mjukt och bekräftande, variera hur du uttrycker detta. "
                "Erbjud sedan TRE numrerade alternativ (1-3) för att sänka tröskeln: "
                "1) 5-minuters fokustimer, 2) Andningsövning, 3) Prioriteringshjälp. "
                f"{common_rules} Max 2 inledande meningar."
            )
        elif stress_level <= 3:
            prompt = (
                f"Användaren känner sig lugn/har energi ({stress_level}/10). "
                "Hälsa piggt och varierat. Använd ett statement om deras energi och ställ en öppen fråga "
                "om vad de vill fokusera på eller rida på för våg just nu. "
                f"{common_rules} Max 2 meningar."
            )
        else:
            prompt = (
                f"Användaren har landat på en mellan-nivå ({stress_level}/10). "
                "Hälsa balanserat. Bekräfta läget med en kort reflektion och fråga "
                "hur du bäst kan assistera just nu för att hålla flowet. "
                f"{common_rules} Max 2 meningar."
            )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.8) # Högre temperatur för mer variation
            )
            return response.text.strip() if response.text else "Jag ser att du har uppdaterat hur du mår. Hur kan jag hjälpa?"
        except Exception as e:
            logger.error(f"[Chief] Mood change error: {e}", exc_info=True)
            return "Jag ser hur du mår. Vill du ha hjälp med något?"

    def handle_general(self, user_input: str, tool_context=None) -> str:
        # Hämtar arkitektur-kontext från den globala text-RAG-laddaren
        notebook_context = ""
        try:
            from src.agents.rag_loader import get_rag_info
            context_text = get_rag_info(query_topic="arch")
            if context_text:
                # Vi skickar med en relevant sammanfattning av RAG-texten
                notebook_context = f"\n\nKONTEXT FRÅN PROJEKT-ARKITEKTUREN:\n{context_text[:10000]}"
        except Exception as e:
            logger.error(f"[Chief] RAG-laddning misslyckades: {e}")

        prompt = (
            f"Du är Jeeves, en personlig ADHD-butler. {notebook_context}\n\n"
        )
        
        # Om historik finns, lägg till den! (Undviker guldfisk-minne)
        if tool_context and hasattr(tool_context, 'history') and tool_context.history:
            prompt += format_conversation_history(tool_context.history) + "\n\n"
            
        prompt += (
            f"Användaren säger nu: '{user_input}'. "
            "Svara varmt och konversationellt baserat på historiken. "
            "REGLER FÖR VARATION: Variera alltid din hälsning/svar. "
            "Använd en kombination av ett konstaterande (statement) och en fråga. "
            "Undvik att låta som en robot. Max 2 meningar. "
            "Om konversationen stannar av, ställ en kort följdfråga."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.8) # Högre temperatur för mer mänsklig variation
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"[Chief] Fel i handle_general: {e}")
            return "Hej! Kul att höra från dig. Vad är det viktigaste jag kan hjälpa dig med just nu?"


if __name__ == "__main__":
    chief = ChiefContextOfficer()
    print("Test routing + svar:", chief.route_request("Jag känner mig superstressad!"))
