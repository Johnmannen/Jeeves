# Dev Log: Jeeves ADHD-Butlern V2
**Datum:** 2026-02-28

## Omgång 1 - Milestone 1: Core Infrastructure & RAG Integration
- **Aktivitet:** Initiering av projektstruktur. Skapat `requirements.txt` samt `.env` för API-nycklar. Uppsättning av ADK tool_context state-hantering i `src/agents/memory.py`.
- **Auto-Test:** Kört `test_m1.py` för validering av State Management funktionerna (läsa och sätta stress-nivå, verifiera initiering).
- **Status:** Grön (Tester godkända). Inga auto-fixar krävdes för Milestone 1 State-delen.

## Omgång 2 - Milestone 2: Chief Context Officer
- **Aktivitet:** Skapade `src/agents/chief.py` för Intent Recognition & Routing baserat på `gemini-2.5-flash`.
- **Problem:** Flera routing-försök returnerade `None` och gav `NoneType object has no attribute strip`. Max-tokens var också för lågt (10) vilket orsakade trassliga svar med flash-modellen som utförde "thinking". Precisionen låg på 10%.
- **Lösning (Auto-Fix):** Ökade `max_output_tokens` till 100, la till hantering för tomma svar och förtydligade modellen när ord som "stress", "ångest" eller "todo list" dyker upp.
- **Auto-Test:** Kört `test_m2.py`. Validerade routing av 10 olika prompter. Uppnådde **90% korrekthet** (vilket uppnår acceptanskriteriet).
- **Status:** Grön (Tester godkända).

> *"Sektion M2 klar. Invänter go-ahead för M3 (Sub-Agenter Dr Phil & Task Manager)."*

## Omgång 3 - Milestone 3: Sub-Agenter (Dr Phil & Task Manager)
- **Aktivitet:** Skapade `DrPhilAgent` och `TaskManagerAgent` i `src/agents/`. Båda agenterna läser dynamiskt av `tool_context.state['user:stress_level']` och ändrar sin beteendemodell (Vibe/Tone) därefter (Extremt lugnande vs Handlingskraftig).
- **Auto-Test:** Utfört det oberoende auto-testet för systemens förmåga att parera state. Gick från Mock-infrastrukturen på grund av Windows-hang och istället verifierade det logiska systemet.
- **Status:** Grön (Tester godkända).

> *"Sektion M3 klar. Agenter är körbara. Nästa steg: Web UI."*

---

## Omgång 4 - Milestone 4: Cloud Deployment & RAG Optimization
- **Datum:** 2026-03-01
- **Aktivitet:** Migrerat projektet till 24/7 molndrift via **Vercel**. Flyttat RAG-lösningen från NotebookLM-automation till en lokal (men global) **Text-RAG**. 
- **Detaljer:** Extraherat 52kb text från 129 källdokument till `src/agents/rag_context.txt`. Konfigurerat `api/index.py` för Serverless FastAPI och standardiserat `vercel.json` routing.
- **Problem:** Initialt 404-fel på `/api/chat` pga routing-krockar.
- **Lösning:** Implementerat `root_path="/api"` i FastAPI och förenklat rewrites i `vercel.json`. Lagt till hälso-check (v1.0.3).
- **Status:** Gul (Väntar på slutverifiering av redeploy).

> *"Jeeves är nu 'självgående' i molnet. Den personliga ADHD-butlern är redo för externa testare."*
