<script>
    import { onMount, onDestroy } from "svelte";

    export let message = "";
    export let onDismiss = () => {};
    export let onSnooze = () => {};

    let phase = "waking"; // waking | challenge | dismissed
    let challengeAnswer = "";
    let challengeQuestion = "";
    let correctAnswer = "";
    let challengeError = false;
    let snoozeTimer = null;
    let audioCtx = null;
    let oscillator = null;
    let gainNode = null;

    // Generera en enkel kognitiv fråga
    function generateChallenge() {
        const today = new Date();
        const days = [
            "Söndag",
            "Måndag",
            "Tisdag",
            "Onsdag",
            "Torsdag",
            "Fredag",
            "Lördag",
        ];
        const months = [
            "januari",
            "februari",
            "mars",
            "april",
            "maj",
            "juni",
            "juli",
            "augusti",
            "september",
            "oktober",
            "november",
            "december",
        ];

        const challenges = [
            {
                q: "Vilken dag är det idag?",
                a: days[today.getDay()].toLowerCase(),
            },
            { q: `Vilken månad är det?`, a: months[today.getMonth()] },
            {
                q: `Vad är ${2 + Math.floor(Math.random() * 5)} + ${1 + Math.floor(Math.random() * 5)}?`,
                a: "",
            },
        ];

        // Beräkna mattetal om det valdes
        const pick = challenges[Math.floor(Math.random() * challenges.length)];
        if (!pick.a) {
            const match = pick.q.match(/(\d+) \+ (\d+)/);
            pick.a = String(Number(match[1]) + Number(match[2]));
        }

        challengeQuestion = pick.q;
        correctAnswer = pick.a;
    }

    // Mjukt ljud via Web Audio API
    function startSound() {
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();

            oscillator.type = "sine";
            oscillator.frequency.setValueAtTime(440, audioCtx.currentTime);

            // Mjuk puls: upp-ner i volym
            gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
            gainNode.gain.linearRampToValueAtTime(
                0.08,
                audioCtx.currentTime + 2,
            );
            gainNode.gain.linearRampToValueAtTime(
                0.02,
                audioCtx.currentTime + 3,
            );
            gainNode.gain.linearRampToValueAtTime(
                0.08,
                audioCtx.currentTime + 5,
            );
            gainNode.gain.linearRampToValueAtTime(
                0.02,
                audioCtx.currentTime + 6,
            );

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();

            // Stoppa efter 8 sekunder
            setTimeout(() => stopSound(), 8000);
        } catch (e) {
            console.warn("Web Audio inte tillgängligt:", e);
        }
    }

    function stopSound() {
        try {
            if (oscillator) {
                oscillator.stop();
                oscillator = null;
            }
            if (audioCtx) {
                audioCtx.close();
                audioCtx = null;
            }
        } catch (e) {
            /* ignore */
        }
    }

    // TTS – läs upp meddelandet
    function speak(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(text);
        utt.lang = "sv-SE";
        utt.rate = 0.9;
        utt.pitch = 1.0;

        // Försök hitta en svensk röst
        const voices = window.speechSynthesis.getVoices();
        const svVoice = voices.find((v) => v.lang.startsWith("sv"));
        if (svVoice) utt.voice = svVoice;

        window.speechSynthesis.speak(utt);
    }

    function tryDismiss() {
        const answer = challengeAnswer.trim().toLowerCase();
        if (answer === correctAnswer) {
            phase = "dismissed";
            stopSound();
            window.speechSynthesis?.cancel();
            clearInterval(snoozeTimer);
            onDismiss();
        } else {
            challengeError = true;
            setTimeout(() => (challengeError = false), 1500);
        }
    }

    function handleKeydown(e) {
        if (e.key === "Enter") tryDismiss();
    }

    onMount(() => {
        generateChallenge();
        startSound();

        // Vänta lite innan TTS (efter ljudet)
        setTimeout(() => speak(message), 3000);

        // Auto-snooze var 2:a minut
        snoozeTimer = setInterval(async () => {
            if (phase === "waking") {
                onSnooze(); // Hämta nytt meddelande
                startSound();
            }
        }, 120000);

        // Visa kognitiv challenge efter 10 sekunder
        setTimeout(() => {
            if (phase === "waking") phase = "challenge";
        }, 10000);
    });

    onDestroy(() => {
        stopSound();
        window.speechSynthesis?.cancel();
        if (snoozeTimer) clearInterval(snoozeTimer);
    });
</script>

<div class="wake-overlay">
    <div class="pulse-bg"></div>

    <div class="content">
        <div class="sun-icon">☀️</div>
        <h1>God morgon</h1>

        <div class="message-box">
            <p>{message}</p>
        </div>

        {#if phase === "challenge"}
            <div class="challenge-box" class:shake={challengeError}>
                <p class="challenge-label">Svara för att stänga av alarmet:</p>
                <p class="challenge-question">{challengeQuestion}</p>
                <input
                    type="text"
                    bind:value={challengeAnswer}
                    on:keydown={handleKeydown}
                    placeholder="Skriv ditt svar..."
                    autofocus
                />
                <button on:click={tryDismiss}>Jag är vaken! ☕</button>
            </div>
        {:else}
            <p class="waiting-text">Jeeves väntar tålmodigt på dig...</p>
        {/if}
    </div>
</div>

<style>
    .wake-overlay {
        position: fixed;
        inset: 0;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        overflow: hidden;
    }

    .pulse-bg {
        position: absolute;
        width: 300vmax;
        height: 300vmax;
        border-radius: 50%;
        background: radial-gradient(
            circle,
            rgba(255, 183, 77, 0.15) 0%,
            transparent 60%
        );
        animation: pulse 6s ease-in-out infinite;
    }

    @keyframes pulse {
        0%,
        100% {
            transform: scale(0.8);
            opacity: 0.4;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.8;
        }
    }

    .content {
        position: relative;
        z-index: 1;
        text-align: center;
        color: #f0e6d3;
        padding: 2rem;
        max-width: 400px;
        width: 100%;
    }

    .sun-icon {
        font-size: 4rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%,
        100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    h1 {
        font-size: 2rem;
        font-weight: 300;
        margin: 0 0 1.5rem;
        letter-spacing: 2px;
        color: #ffcc80;
    }

    .message-box {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }

    .message-box p {
        margin: 0;
        font-size: 1rem;
        line-height: 1.6;
        color: #e0d5c4;
    }

    .waiting-text {
        font-style: italic;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.9rem;
        animation: fadeInOut 3s ease-in-out infinite;
    }

    @keyframes fadeInOut {
        0%,
        100% {
            opacity: 0.3;
        }
        50% {
            opacity: 0.7;
        }
    }

    .challenge-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        animation: slideUp 0.4s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .challenge-label {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
        margin: 0 0 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .challenge-question {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffcc80;
        margin: 0 0 1rem;
    }

    .challenge-box input {
        width: 100%;
        padding: 0.8rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        background: rgba(0, 0, 0, 0.3);
        color: white;
        font-size: 1.1rem;
        text-align: center;
        outline: none;
        margin-bottom: 0.8rem;
        box-sizing: border-box;
    }

    .challenge-box input:focus {
        border-color: #ffcc80;
    }

    .challenge-box button {
        width: 100%;
        padding: 0.8rem;
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, #ffcc80, #ffab40);
        color: #1a1a2e;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .challenge-box button:active {
        transform: scale(0.97);
    }

    .shake {
        animation: shake 0.4s ease-in-out;
    }

    @keyframes shake {
        0%,
        100% {
            transform: translateX(0);
        }
        20% {
            transform: translateX(-8px);
        }
        40% {
            transform: translateX(8px);
        }
        60% {
            transform: translateX(-4px);
        }
        80% {
            transform: translateX(4px);
        }
    }
</style>
