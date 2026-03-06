# Strategi för Persistent Lagring i Molnet (Vercel)
**Dokument-ID:** JEEVES_CLOUD_STATE_STRATEGY_v1.0
**Projekt:** Jeeves ADHD-Butlern
**Datum:** 2026-03-04

## Bakgrund
Nuvarande arkitektur använder **SQLite** (`jeeves_memory.db`) som lagras lokalt eller i `/tmp/` på Vercel. 
**Problemet:** Vercel är "stateless" och serverless-funktioner har ett skrivskyddat filsystem. Allt i `/tmp/` raderas när funktionen avslutas eller startas om. Detta innebär att stressnivåer och minnen raderas vid varje deployment eller när sessionen går ner.

> [!IMPORTANT]
> Alla rekommenderade lösningar nedan är valda för att de har generösa **Gratis-nivåer (Free Tiers)**. För ett projekt som Jeeves, med dagsformslagring för en eller ett fåtal användare, kommer dessa lösningar i praktiken vara helt gratis för dig.

## Rekommenderade Lösningar (Prioritetsordning)

### 1. Turso (SQLite in the Cloud) - REKOMMENDERAS (✅ IMPLEMENTERAD)
Turso är en distribuerad databas byggd på libSQL (en SQLite-fork). Vi har nu implementerat logik i `memory.py` som per automatik använder Turso om miljövariablerna hittas!
- **Fördelar:** Minimal kodändring, blixtsnabb respons, gratisnivå finns.
- **Implementering:** `sqlite3` är nu kompatibelt med `libsql_client` via unified executor.

### 2. Vercel KV (Redis)
Ett key-value-storage som är inbyggt i Vercel.
- **Fördelar:** Ingen extra setup, extremt enkelt för att lagra just `user_id -> stress_level`.
- **Nackdelar:** Inte en relationsdatabas, svårare om vi vill spara komplexa minnen/brain-dumps senare.

### 3. Supabase (PostgreSQL)
En fullfjädrad backend-as-a-service.
- **Fördelar:** Väldigt kraftfullt, bra för framtida expansion (auth, filer, etc).
- **Nackdelar:** Kräver mer kodändring (SQL-dialekt och bibliotek).

## Kortsiktig Åtgärd (Bulletproof Mode)
För att förhindra krascher i molnet har vi nu implementerat:
1. **Clamped inputs:** Stressnivåer valideras alltid (0-10).
2. **Graceful Failures:** Om databasen inte går att skriva till (t.ex. pga skrivskydd), loggas felet men applikationen fortsätter fungera med default-värden (Stressnivå 5).

---

**Nästa steg:** John, vilken av ovanstående lösningar föredrar du för vår persistenta lagring? Jag rekommenderar **Turso** om du vill fortsätta med SQLite-känslan.
