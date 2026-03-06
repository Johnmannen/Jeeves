<script>
  import "./app.css";
  import { onMount, tick } from "svelte";
  import Timeline from "./lib/Timeline.svelte";
  import WakeUpScreen from "./lib/WakeUpScreen.svelte";
  import Timer from "./lib/Timer.svelte";

  let messages = [
    {
      id: 1,
      role: "jeeves",
      text: "Hej John. Jag är här. Hur mår du just nu?",
    },
  ];
  // API Konfiguration för Vercel/Lokal drift
  const API_BASE = import.meta.env.VITE_API_BASE || "/api";
  let userInput = "";
  let chatWindow;
  let isThinking = false;
  let stressLevel = 5;
  let userId = "John";
  let calendarEvents = [];
  let connectionError = "";

  // Timeout-konfiguration (ms)
  const FETCH_TIMEOUT = 30000; // 30 sekunder max

  // Väckarklocka
  let showWakeUp = false;
  let wakeUpMessage = "";

  // TTS
  let ttsEnabled = true;

  // Timer
  let activeTimer = null; // { duration, taskName }

  // Röstinmatning
  let isListening = false;
  let recognition = null;

  const stressOptions = [
    { label: "Lugn 😊", value: 2, class: "low" },
    { label: "Okej 😐", value: 5, class: "med" },
    { label: "Stressad 🤯", value: 9, class: "high" },
  ];

  function speakText(text) {
    if (!ttsEnabled || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();

    // Rensa bort eventuella [TIMER:xxx] -taggar före uppläsning
    const cleanText = text.replace(/\[TIMER:\d+\]/g, "").trim();

    const utt = new SpeechSynthesisUtterance(cleanText);
    utt.lang = "sv-SE";
    utt.rate = 0.9;
    const voices = window.speechSynthesis.getVoices();
    const svVoice = voices.find((v) => v.lang.startsWith("sv"));
    if (svVoice) utt.voice = svVoice;
    window.speechSynthesis.speak(utt);
  }

  // Initiera Web Speech API för röstinmatning
  function initSpeechRecognition() {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.lang = "sv-SE";
      recognition.interimResults = true; // För att se text formulerar sig

      recognition.onstart = () => {
        isListening = true;
      };

      recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        userInput = transcript; // Live-uppdatera input-fältet
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        isListening = false;
        if (
          event.error === "not-allowed" ||
          event.error === "service-not-allowed"
        ) {
          alert(
            "Kunde inte starta mikrofonen. Har du gett tillåtelse? (På mobil måste du ofta använda HTTPS)",
          );
        }
      };

      recognition.onend = () => {
        isListening = false;
        // Skicka automatiskt när användaren slutar prata om vi har text
        if (userInput.trim().length > 0) {
          sendMessage();
        }
      };
    } else {
      console.warn("Speech Recognition API stöds inte av denna webbläsare.");
    }
  }

  function toggleListening() {
    if (!recognition) return;
    if (isListening) {
      recognition.stop();
    } else {
      userInput = ""; // Rensa innan ny lyssning
      recognition.start();
    }
  }

  async function fetchCalendar() {
    try {
      const response = await fetch(`${API_BASE}/calendar?max_results=5`);
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      calendarEvents = data.events;
      connectionError = "";
    } catch (e) {
      console.error("Kunde inte hämta kalender:", e);
      connectionError = "⚠️ Kunde inte ansluta till Jeeves-servern.";
    }
  }

  onMount(() => {
    fetchCalendar();
    window.speechSynthesis?.getVoices();
    initSpeechRecognition();
  });

  async function scrollToBottom() {
    await tick();
    if (chatWindow) {
      chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
    }
  }

  async function sendMessage() {
    if (!userInput.trim()) return;
    const text = userInput;
    userInput = "";
    messages = [...messages, { id: Date.now(), role: "user", text }];
    scrollToBottom();
    isThinking = true;

    // Avbryt Jeeves om han redan pratar
    window.speechSynthesis?.cancel();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);

      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          stress_level: stressLevel,
          user_id: userId,
          history: messages.slice(-10),
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server svarade med status ${response.status}`);
      }

      const data = await response.json();
      let reply = data.reply;

      // Kolla efter timer-kommandon i svaret: ex "[TIMER:300]"
      const timerMatch = reply.match(/\[TIMER:(\d+)\]/);
      if (timerMatch) {
        const durationSec = parseInt(timerMatch[1], 10);
        activeTimer = { duration: durationSec, taskName: "Aktivitet" };
        reply = reply.replace(timerMatch[0], "").trim(); // Städa texten utåt
      }

      messages = [
        ...messages,
        { id: Date.now() + 1, role: "jeeves", text: reply },
      ];
      speakText(reply);
    } catch (e) {
      console.error("Chat-fel:", e);
      const errorMsg = e.name === 'AbortError'
        ? "Förlåt, jag hann inte svara i tid. Försök igen!"
        : "Förlåt, min kontakt med nätverket svajade. Jag är kvar.";
      messages = [
        ...messages,
        {
          id: Date.now() + 1,
          role: "jeeves",
          text: errorMsg,
        },
      ];
    } finally {
      isThinking = false;
      scrollToBottom();
    }
  }

  // .. Väcknings-logik (oförändrad) ...
  async function triggerWakeUp() {
    isThinking = true;
    try {
      const response = await fetch(
        `${API_BASE}/wake-up?stress_level=${stressLevel}&user_id=${userId}`,
      );
      const data = await response.json();
      wakeUpMessage = data.greeting;
      showWakeUp = true;
      fetchCalendar();
    } catch (e) {
      console.error(e);
    } finally {
      isThinking = false;
    }
  }

  async function handleSnooze() {
    try {
      const response = await fetch(
        `${API_BASE}/wake-up?stress_level=${stressLevel}&user_id=${userId}`,
      );
      const data = await response.json();
      wakeUpMessage = data.greeting;
    } catch (e) {
      console.error(e);
    }
  }

  function handleWakeUpDismiss() {
    showWakeUp = false;
    messages = [
      ...messages,
      {
        id: Date.now(),
        role: "jeeves",
        text: "☀️ Bra jobbat att du vaknade! Jag finns här om du behöver mig.",
      },
    ];
    scrollToBottom();
  }

  function toggleTts() {
    ttsEnabled = !ttsEnabled;
    if (!ttsEnabled) window.speechSynthesis?.cancel();
  }

  let moodChangeTimer = null;
  async function handleMoodChange() {
    // Debounce: vänta 800ms efter att slidern slutat röra sig
    clearTimeout(moodChangeTimer);
    moodChangeTimer = setTimeout(async () => {
      const moodLabel =
        stressLevel <= 3 ? "Lugn" : stressLevel <= 6 ? "Okej" : "Stressad";
      // Skicka bara trigger om Jeeves inte redan tänker
      if (isThinking) return;
      isThinking = true;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);

        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: `[MOOD_CHANGE] Humöret är nu: ${moodLabel} (${stressLevel}/10)`,
            stress_level: stressLevel,
            user_id: userId,
            history: messages.slice(-10),
          }),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`Server svarade med status ${response.status}`);
        }

        const data = await response.json();
        let reply = data.reply;
        const timerMatch = reply.match(/\[TIMER:(\d+)\]/);
        if (timerMatch) {
          const durationSec = parseInt(timerMatch[1], 10);
          activeTimer = { duration: durationSec, taskName: "Aktivitet" };
          reply = reply.replace(timerMatch[0], "").trim();
        }
        messages = [
          ...messages,
          { id: Date.now() + 1, role: "jeeves", text: reply },
        ];
        speakText(reply);
        scrollToBottom();
      } catch (e) {
        console.error("Mood change error:", e);
      } finally {
        isThinking = false;
      }
    }, 800);
  }

  function handleTimerDone(event) {
    activeTimer = null;
    messages = [
      ...messages,
      {
        id: Date.now(),
        role: "jeeves",
        text: `Tiden är ute! Bra kämpat. Hur kändes det?`,
      },
    ];
    speakText("Tiden är ute! Bra kämpat.");
    scrollToBottom();
  }
</script>

{#if showWakeUp}
  <WakeUpScreen
    message={wakeUpMessage}
    onDismiss={handleWakeUpDismiss}
    onSnooze={handleSnooze}
  />
{/if}

<div class="app-container">
  <header>
    <div class="avatar-container">
      <img src="/avatar.png" alt="Jeeves" class="avatar-img" />
      <div class="status-indicator"></div>
    </div>
    <div class="info" style="flex: 1;">
      <h2 style="margin:0; font-size: 1.15rem; font-weight: 700;">
        Jeeves <span
          style="font-size: 0.7rem; color: var(--accent-warn); font-weight: 400;"
          >(ALFA)</span
        >
      </h2>
      <input
        type="text"
        bind:value={userId}
        style="border:none; background:transparent; font-size: 0.85rem; color: var(--text-muted); outline: none; width: 100px;"
        title="Byt användar-ID för test"
      />
    </div>
    <button
      on:click={toggleTts}
      class="tts-btn"
      title={ttsEnabled ? "Stäng av röst" : "Sätt på röst"}
    >
      {ttsEnabled ? "🔊" : "🔇"}
    </button>
    <button
      on:click={triggerWakeUp}
      style="background: var(--bg-secondary); border: 1px solid rgba(0,0,0,0.1); padding: 0.5rem; border-radius: 8px; font-size: 0.7rem; cursor: pointer;"
    >
      ⏰ Väckning
    </button>
  </header>

  <Timeline events={calendarEvents} />

  {#if connectionError}
    <div
      style="color: red; padding: 0.5rem; text-align: center; font-size: 0.8rem; background: #fff0f0; margin: 0 1rem 0.5rem; border-radius: 8px;"
    >
      {connectionError}
    </div>
  {/if}

  <div class="stress-section">
    <div class="stress-header">
      <span class="stress-label">Mående</span>
      <span
        class="stress-text"
        style="color: {stressLevel <= 3
          ? '#4A6741'
          : stressLevel <= 6
            ? '#D68C45'
            : '#D16D64'}"
      >
        {stressLevel <= 3
          ? "Lugn 😊"
          : stressLevel <= 6
            ? "Okej 😐"
            : "Stressad 🤯"}
      </span>
    </div>
    <div class="slider-container">
      <span class="slider-arrow left">◀</span>
      <div class="slider-track">
        <input
          type="range"
          min="1"
          max="10"
          bind:value={stressLevel}
          class="stress-slider"
          style="--val: {(stressLevel - 1) / 9}"
          on:change={handleMoodChange}
        />
        <div class="slider-labels">
          <span>Lugn</span>
          <span>Okej</span>
          <span>Stressad</span>
        </div>
      </div>
      <span class="slider-arrow right">▶</span>
    </div>
  </div>

  <main
    class="chat-window"
    bind:this={chatWindow}
    on:click={() => window.speechSynthesis?.cancel()}
    title="Klicka för att avbryta uppläsning"
  >
    {#if activeTimer}
      <Timer
        duration={activeTimer.duration}
        taskName={activeTimer.taskName}
        on:timeup={handleTimerDone}
        on:cancel={() => {
          activeTimer = null;
        }}
      />
    {/if}

    {#each messages as msg (msg.id)}
      <div class="message {msg.role}">
        {msg.text}
      </div>
    {/each}

    {#if isThinking}
      <div class="message jeeves">
        <div class="typing">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    {/if}
  </main>

  <div class="input-area">
    <input
      type="text"
      bind:value={userInput}
      placeholder={isListening
        ? "Lyssnar... pratar nu"
        : "Berätta vad som händer..."}
      on:keydown={(e) => e.key === "Enter" && !isListening && sendMessage()}
      disabled={isListening}
    />
    {#if recognition}
      <button
        class="voice-btn mic-btn"
        class:listening={isListening}
        on:click={toggleListening}
        title="Prata"
      >
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          ><path
            d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"
          /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line
            x1="12"
            y1="19"
            x2="12"
            y2="22"
          /></svg
        >
      </button>
    {/if}
    <button class="voice-btn send-btn" on:click={sendMessage} title="Skicka">
      <svg
        width="22"
        height="22"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        ><line x1="22" y1="2" x2="11" y2="13" /><polygon
          points="22 2 15 22 11 13 2 9 22 2"
        /></svg
      >
    </button>
  </div>
</div>

<style>
  /* Extra styling för röstinmatning läggs i app.css. Vi lägger in klasserna direkt i DOMen här. */
</style>
