import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def query_notebooklm(question: str, notebook_id: str = None) -> str:
    """
    Hjälpfunktion för att ställa frågor till NotebookLM via den globala skillen.
    """
    run_script = r"C:\Users\johnr\.gemini\antigravity\skills\notebooklm\scripts\run.py"
    ask_script = "ask_question.py"
    
    cmd = [
        "python", 
        run_script, 
        ask_script, 
        "--question", question
    ]
    
    if notebook_id:
        cmd.extend(["--notebook-id", notebook_id])
        
    try:
        logger.info(f"[NotebookLM] Frågar: {question[:50]}...")
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            check=False
        )
        
        if result.returncode == 0:
            # Extrahera svaret mellan separatorerna =============
            output = result.stdout
            if "============================================================" in output:
                parts = output.split("============================================================")
                if len(parts) >= 3:
                    answer = parts[2].strip()
                    logger.info("[GoogleBridge] Token framgångsrikt laddad från miljövariabel!")
                    # Ta bort follow-up reminder ifall den finns
                    if "EXTREMELY IMPORTANT: Is that ALL you need to know?" in answer:
                        answer = answer.split("EXTREMELY IMPORTANT:")[0].strip()
                    return answer
            return output.strip()
        else:
            logger.error(f"[NotebookLM] Fel: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"[NotebookLM] Exception: {e}", exc_info=True)
        return None
