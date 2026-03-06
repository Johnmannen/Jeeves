from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ToolContext:
    """
    Kontext-objekt som skickas genom hela agent-kedjan.
    Ersätter spridda dictionarys och inkonsekventa klasser.
    """
    user_id: str = "john_doe"
    stress_level: int = 5
    history: List[Dict[str, Any]] = field(default_factory=list)
