# 🏗️ Implementation Plan: Jeeves ADHD-Butlern
**Version:** V1 | **Datum:** 2026-02-28 | **Status:** APPROVED
**Arkitekt:** John Garp | 🔒 **IMMUTABLE: ORIGINAL PLAN**

> [!IMPORTANT]
> **Denna V1-plan är oföränderlig.** Alla uppdateringar sker i nya versioner (V2, V3...).
> V1 finns alltid tillgänglig som fallback-referens (Se Global Regel R6).

---

## 📊 Projektöversikt
**Total Progress:** [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0%
**Milestones:** 4 | **Tasks:** 6

### 💰 Kostnadsammanfattning
- **Estimerad total kostnad:** 0 SEK
- **Antal gratis-alternativ funna:** 5
- **Kräver godkännande:** ✅ NEJ
- **GCP Fallback (Credits):** ❌ Behövs ej

---

## 🛣️ Milestones & Tasks

### 🔴 M1: Core Infrastructure & RAG Integration
**Prio:** 🔴 CRITICAL | **Status:** NOT_STARTED | **Progress:** [░░░░░░░░░░░░░░░░░░░░] 0%
> Lägg grunden med RAG-databasen för Vibe & Tone, samt den gemensamma 'Local Log' för agenterna.

> [!TIP]
> **Agentens Challenge/Mönster:**
> Testa att låta 'Gemma'-agenten inte bara skriva loggar utan också generera 'State of Mind' headers som andra agenter läser först.

*Sektions-test Config: Auto-Test ✅ | Auto-Fix ✅*

#### Tasks
- [   ] **T1.1 — Koppla RAG-databasen för Personlighet** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Agenten kan hämta definierad 'framtoning' från RAG., Fallback finns om RAG är oåtkomlig.
  - 🔸 S1.1.1: Koppla Gemini API Key (`.env`) 🔴
- [   ] **T1.2 — Lokal 'Log/Memory' System (Gemma)** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Alla agenter kan läsa/skriva till en gemensam JSON/lokal databas., Loggen rensas/komprimeras dagligen (Short-term memory).
  - 🔸 S1.2.1: Skapa Memory Manager (`src/agents/memory.py`) 🔴

---

### 🔴 M2: Chief Context Officer (Routing Agent)
**Prio:** 🔴 CRITICAL | **Status:** NOT_STARTED | **Progress:** [░░░░░░░░░░░░░░░░░░░░] 0%
**Beroenden:** M1
> Bygg Huvudagenten ('Ansiktet utåt') som bedömer användarens input och delegerar internt.

> [!TIP]
> **Agentens Challenge/Mönster:**
> Håll Chief Agent otroligt lättviktig (snabb) — all tänkande kraft ska ligga i under-agenterna.

*Sektions-test Config: Auto-Test ✅ | Auto-Fix ✅*

#### Tasks
- [   ] **T2.1 — Intent Recognition & Routing** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Korrekt routing vid 'Jag känner mig överväldigad' (Dr Phil)., Korrekt routing vid 'Vad står på schemat' (Task Manager).
  - 🔸 S2.1.1: Bygg Routing Module (`src/agents/chief.py`) 🔴

---

### 🔴 M3: Sub-Agenter (Dr Phil & Task Manager)
**Prio:** 🟡 HIGH | **Status:** NOT_STARTED | **Progress:** [░░░░░░░░░░░░░░░░░░░░] 0%
**Beroenden:** M2
> Implementera de specialiserade agenterna.

*Sektions-test Config: Auto-Test ✅ | Auto-Fix ✅*

#### Tasks
- [   ] **T3.1 — Dr. Phil Light Agent** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Hämtar ton från RAG (M1)., Genererar korta, ej dömande svar (ADHD-fokus).
- [   ] **T3.2 — Calendar/Task Agent** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Bryter ner stora uppgifter (Executive Dysfunction Support).

---

### 🔴 M4: Mobil Anpassad UX/UI (Web App)
**Prio:** 🟢 MEDIUM | **Status:** NOT_STARTED | **Progress:** [░░░░░░░░░░░░░░░░░░░░] 0%
**Beroenden:** M3
> Minimum Viable Product gränssnitt, anpassat för mobiler (som en riktig app).

*Sektions-test Config: Auto-Test ✅ | Auto-Fix ✅*

#### Tasks
- [   ] **T4.1 — Chat Interface MVP** 🔴 *(Kostnad: 0 SEK)*
  - **AC:** Mobile-first CSS (Inga onödiga intryck)., Stöd för röstinmatning (viktigt för ADHD).

---
