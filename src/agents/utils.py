from typing import List, Dict, Any

def format_conversation_history(history: List[Dict[str, Any]]) -> str:
    """
    Standardiserar formateringen av chat-historik för alla agenter.
    """
    if not history:
        return ""
        
    history_lines = [
        f"{msg.get('role', 'Okänd').upper()}: {msg.get('text', '')}" 
        for msg in history
    ]
    
    return (
        "\n[CHATT-HISTORIK BÖRJAR]\n" + 
        "\n".join(history_lines) + 
        "\n[CHATT-HISTORIK SLUTAR]\n"
        "(Fortsätt konversationen naturligt ifrån detta och bemöt vad användaren just sa)"
    )
