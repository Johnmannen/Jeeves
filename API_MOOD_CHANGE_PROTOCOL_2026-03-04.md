# Protokoll för Humörändringar (Mood Change)
**Dokument-ID:** JEEVES_MOOD_PROTOCOL_v1.0
**Projekt:** Jeeves ADHD-Butlern
**Datum:** 2026-03-04

## Översikt
För att Jeeves ska kunna reagera proaktivt när användaren ändrar sin stressnivå i gränssnittet (via humör-slidern), används ett specifikt prefix i meddelandet till `/chat`-endpointen.

## Protokollet

### Meddelandeformat
När en humörändring sker ska frontend skicka en POST till `/chat` med följande format på `message`:
`[MOOD_CHANGE] {ny_stress_nivå}`

**Exempel:**
`[MOOD_CHANGE] 9`

### Backend-hantering
`ChiefContextOfficer` identifierar prefixet och delegerar anropet till `handle_mood_change`.
1. **Stressnivå 8-10 (Hög):** Jeeves svarar med lugnande bekräftelse och erbjuder tre konkreta, lågtröskliga alternativ (Timer, Andning, Prioritering).
2. **Stressnivå 4-7 (Normal):** Jeeves bekräftar och frågar om något specifikt behövs.
3. **Stressnivå 0-3 (Låg/Lugn):** Jeeves bekräftar energin och frågar vad som ska hända härnäst.

### Förväntad Respons
Svaret från Jeeves är en sträng (text) som är neuro-kalibrerad för att matcha stressnivån. Vid hög stress undviks listor och krav, istället presenteras numrerade alternativ för enkel interaktion.

---

**Notis:** Detta protokoll är synkront. För en ännu smidigare upplevelse kan framtida versioner använda WebSockets eller Server-Sent Events (SSE).
