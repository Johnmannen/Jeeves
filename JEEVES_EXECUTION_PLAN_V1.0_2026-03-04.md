# Exekveringsplan & Master ToDo: Jeeves ADHD-Butlern
**Dokument-ID:**# JEEVES EXECUTION PLAN v1.1 - COMPLETE
**Projekt:** Refining Agentic Structure (ADHD-Butler)
**Status:** ✅ ALL STAGES COMPLETE & TESTED
**Datum:** 2026-03-04

Detta dokument fungerar som vår Master ToDo och strategiska planering för att åtgärda och förbättra den nuvarande arkitekturen baserat på vår senaste analys (AGENTIC_STRUCTURE_ANALYSIS_REPORT.md).

---

## 🏗️ Stage 1: Kritiska Blockeringar (Testing & Memory Layer)
*Fokus: Få alla tester att passera ärligt och säkerställa att grundläggande tillståndshantering (state management) fungerar.*

- [x] **1.1: Fixa `test_m1.py` (Memory Layer)**
  - Omdöp/rätta importen från `init_goodmem()` till `init_db()`.
  - Uppdatera API-anrop så strängar (`user_id`) används istället för kontextobjekt.
  - Lägg till faktiska assertions för att verifiera att stressnivåer sparas och hämtas korrekt.
- [x] **1.2: Koda om `test_m3.py` (Sub-Agents)**
  - Ersätt mockade print-satser med faktiska agentanrop till t.ex. `Dr_Phil` och `Task_Manager`.
  - Implementera validering (assertions) på svarsinnehåll baserat på olika stressnivåer.
- [x] **1.3: E2E Integrationstest (End-to-End)**
  - Bygg ett komplett flöde: "Input → Route (Chief) → Läs Stressnivå → Generera Svar (SubAgent)".

*Efter Stage 1 testar vi hela flödet och felsöker potentiella buggar.*

---

## 🧱 Stage 2: Arkitektonisk Struktur & Underhåll
*Fokus: Minska kodduplicering och skapa en förutsägbar datakälla för systemet.*

- [x] **2.1: Centralisera State Management (Stressnivå)**
  - Skapa en dedikerad hantering (t.ex. `StateManager`) så att man inte sätter "hardcodade" defaultvärden i varje enskild agent.
- [x] **2.2: Standardisera `ToolContext`**
  - Definiera ett tydligt kontext-interface (dataclass/Pydantic-modell) så att kontraktet förblir konsekvent över hela applikationen.
- [x] **2.3: Typificera Historikhantering & Formatering**
  - Extrahera koden för historik-formatering ("CHATT-HISTORIK BÖRJAR...") till en gemensam utility-funktion.
- [x] **2.4: Förenhetliga Loggning**
  - Ersätt `print()` med standard `logging` i alla agenter (kritiskt för molnmiljöer/Vercel).

*Efter Stage 2 testar vi hela flödet och felsöker potentiella buggar.*

---

## 🛡️ Stage 3: Robusthet & Felhantering
*Fokus: Skydda applikationen mot kraschar och minnesläckor i produktion.*

- [x] **3.1: Historikbegränsning (Token Management)**
  - Inför maxgräns för konversationshistoriken via API:et (Paginering eller "Sliding Window") för att förhindra token overflow.
- [x] **3.2: RAG-fil & Deployment Validering**
  - Säkerställ korrekta molnsökvägar för `rag_context.txt` och implementera tydliga loggningar om systemet måste "falla tillbaka" på standardprompter.
- [x] **3.3: Omfattande Edge Case-testning**
  - Simulera API-key-bortbortfall, korrupt databas och felaktiga stressnivå-inputs (t.ex. negativa värden eller `null`).
- [x] **3.4: Databasstrategi för Vercel**
  - Utvärdera och implementera en lösning för ihållande databas (SQLite i molnet återställs vid varje deployment, vi behöver en "persistence"-strategi).

*Efter Stage 3 testar vi hela flödet och felsöker potentiella buggar.*

---

## 🚀 Stage 4: "Polish", Prestanda & Produktion
*Fokus: Finjustering av UX och CI/CD-pipeline.*

- [x] **4.1: Dokumentera Mood Change-protokollet**
  - Skapa specifikationer för hur `[MOOD_CHANGE]`-integrationen ska samspela med frontend.
- [x] **4.2: Migrera till Pytest**
  - Lägg till konfigurationsfiler och konvertera råa testscript för enklare CI/CD-automation.
- [x] **4.3: Prestandamätning & Temperaturkalibrering**
  - Logga svarstider (latency), token-användning och A/B-testa temperaturinställningarna för optimal balans mellan seriositet (Task Manager) och empati (Dr. Phil).

*Efter Stage 4 genomfördes en fullständig slutvalidering med Pytest (5/5 tester passerade).*

---

## 🔮 Framtida Utveckling (Pattern Suggestion)
**Challenge:** Nu när vi har en robust `StateManager` och en bra bas för personlighet, bör vi titta på **"Hjärnsläpps"-funktionen (Brain Dump)**. 

**Mönster:** Istället för att bara spara text, föreslår jag ett **"Associative Memory"-mönster**. När användaren pratar om något nytt, kraschar vi inte bara in det i databasen, utan låter Jeeves (via StateManager) försöka länka det till befintlig kontext för att proaktivt påminna användaren senare. (T.ex. om användaren sa "mjölken är slut" vid hög stress, kan Jeeves vänta tills stressen är låg nästa morgon för att föreslå en handling).
