"""
Jeeves ADHD Butler — Custom Exception Hierarchy
================================================
Skapad som del av felhanteringsanalys (error-handling-patterns skill).
Ger specifik felhantering istället för generiska except Exception.
"""
from datetime import datetime
from typing import Optional, Dict, Any


class JeevesError(Exception):
    """Basexception för alla Jeeves-fel."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def __str__(self):
        base = super().__str__()
        if self.code:
            return f"[{self.code}] {base}"
        return base


class ConfigError(JeevesError):
    """Fel relaterat till konfiguration (API-nycklar, miljövariabler)."""
    def __init__(self, message: str, missing_key: Optional[str] = None):
        super().__init__(
            message,
            code="CONFIG_ERROR",
            details={"missing_key": missing_key} if missing_key else {}
        )
        self.missing_key = missing_key


class GeminiAPIError(JeevesError):
    """Fel vid kommunikation med Gemini API."""
    def __init__(self, message: str, agent: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(
            message,
            code="GEMINI_API_ERROR",
            details={"agent": agent}
        )
        self.agent = agent
        self.original_error = original_error


class RoutingError(JeevesError):
    """Fel vid routing av användarinput till rätt sub-agent."""
    def __init__(self, message: str, user_input: Optional[str] = None):
        super().__init__(
            message,
            code="ROUTING_ERROR",
            details={"user_input": user_input[:100] if user_input else None}
        )


class MemoryDBError(JeevesError):
    """Fel relaterat till databas/minne (SQLite/Turso)."""
    def __init__(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None):
        super().__init__(
            message,
            code="MEMORY_ERROR",
            details={"operation": operation, "user_id": user_id}
        )
        self.operation = operation


class RAGError(JeevesError):
    """Fel vid laddning/sökning i RAG-kontexten."""
    def __init__(self, message: str, source: Optional[str] = None):
        super().__init__(
            message,
            code="RAG_ERROR",
            details={"source": source}
        )


class GoogleBridgeError(JeevesError):
    """Fel vid kommunikation med Google-tjänster (Calendar, Drive)."""
    def __init__(self, message: str, service: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(
            message,
            code="GOOGLE_BRIDGE_ERROR",
            details={"service": service}
        )
        self.service = service
        self.original_error = original_error


class ValidationError(JeevesError):
    """Fel vid validering av input-data."""
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": str(value)[:50] if value else None}
        )
        self.field = field
