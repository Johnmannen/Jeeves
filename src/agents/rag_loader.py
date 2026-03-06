import logging
import os

# Konfigurera loggning
logger = logging.getLogger(__name__)

# Denna fil laddar in hela JEEVES RAG-texten en gång så att alla agenter kan använda den snabbt.
# För V1 i molnet (Vercel) läser vi från den extraherade textfilen.

def load_rag_context():
    rag_file = os.path.join(os.path.dirname(__file__), "rag_context.txt")
    if not os.path.exists(rag_file):
        logger.warning("[RAG Loader] RAG-fil saknas (rag_context.txt). Använder minimalistisk fallback.")
        return "Jeeves är din personliga ADHD-butler. Fokusera på samreglering och skamfri hjälp."
    
    try:
        with open(rag_file, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"[RAG Loader] Laddade RAG-kontext ({len(content)} tecken).")
            return content
    except Exception as e:
        logger.error(f"[RAG Loader] Error loading context: {e}")
        return "Jeeves är din personliga ADHD-butler. Fokusera på samreglering och skamfri hjälp."

# Singleton för att undvika att läsa filen vid varje anrop
GLOBAL_RAG_CONTEXT = load_rag_context()

def get_rag_info(query_topic: str = ""):
    """Hämtar relevant kontext. Just nu returneras hela (pga liten storlek), 
    men kan utökas med sökning senare."""
    return GLOBAL_RAG_CONTEXT
