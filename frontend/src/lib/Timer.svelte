<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";

    export let duration = 300; // in seconds
    export let taskName = "Uppgift";

    const dispatch = createEventDispatcher();

    let timeLeft = duration;
    let timerInterval;

    // För ljud
    let audioCtx = null;
    let oscillator = null;
    let gainNode = null;

    $: progressPercentage = (timeLeft / duration) * 100;

    $: barColor =
        progressPercentage > 80
            ? "#4A6741"
            : progressPercentage > 50
              ? "#7CB342"
              : progressPercentage > 20
                ? "#FF9800"
                : "#D16D64";

    const totalDots = 24;
    $: dotsToShow = Math.ceil((progressPercentage / 100) * totalDots);

    $: minutes = Math.floor(timeLeft / 60);
    $: seconds = timeLeft % 60;
    $: formattedTime = `${minutes}:${seconds.toString().padStart(2, "0")}`;

    function playAlertSound() {
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();

            oscillator.type = "sine";
            oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // A4
            oscillator.frequency.exponentialRampToValueAtTime(
                880,
                audioCtx.currentTime + 0.5,
            ); // A5

            gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
            gainNode.gain.linearRampToValueAtTime(
                0.3,
                audioCtx.currentTime + 0.1,
            );
            gainNode.gain.linearRampToValueAtTime(
                0,
                audioCtx.currentTime + 1.5,
            );

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 1.5);
        } catch (e) {
            console.warn("Web Audio inte tillgängligt:", e);
        }
    }

    onMount(() => {
        timerInterval = setInterval(() => {
            if (timeLeft > 0) {
                timeLeft -= 1;
            } else {
                clearInterval(timerInterval);
                playAlertSound();
                dispatch("timeup", { task: taskName });
            }
        }, 1000);
    });

    onDestroy(() => {
        if (timerInterval) clearInterval(timerInterval);
        if (audioCtx) audioCtx.close();
    });

    function cancelTimer() {
        if (timerInterval) clearInterval(timerInterval);
        dispatch("cancel");
    }
</script>

<div class="timer-container" class:urgent={timeLeft > 0 && timeLeft <= 60}>
    <div class="timer-header">
        <div class="task-info">
            <span class="timer-icon">⏱️</span>
            <span class="task-name">{taskName}</span>
        </div>
        <div class="time-left">
            <span class="digits" style="color: {barColor}">{formattedTime}</span
            >
            <button class="cancel-btn" on:click={cancelTimer} title="Avbryt"
                >✕</button
            >
        </div>
    </div>

    <div class="timstock-track">
        {#each Array(totalDots) as _, i}
            <div
                class="timstock-dot"
                class:active={i < dotsToShow}
                style="background-color: {i < dotsToShow
                    ? barColor
                    : 'rgba(0,0,0,0.05)'};"
            ></div>
        {/each}
    </div>
</div>

<style>
    .timer-container {
        background: var(--bg-primary, #fdfbf7);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border-left: 4px solid var(--accent-calm, #4a6741);
        animation: slideDown 0.3s ease-out;
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .timer-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }

    .task-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .timer-icon {
        font-size: 1.1rem;
    }

    .task-name {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-dark);
    }

    .time-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .digits {
        font-size: 1.4rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        transition: color 0.5s ease;
    }

    .cancel-btn {
        background: transparent;
        border: none;
        color: var(--text-muted);
        font-size: 1rem;
        cursor: pointer;
        padding: 0.2rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }

    .cancel-btn:hover {
        background: rgba(0, 0, 0, 0.05);
        color: #d16d64;
    }

    .timstock-track {
        display: flex;
        gap: 4px;
        width: 100%;
        height: 20px;
        padding: 4px;
        background: rgba(0, 0, 0, 0.03);
        border-radius: 8px;
        border: 1px solid rgba(0, 0, 0, 0.04);
    }

    .timstock-dot {
        flex: 1;
        height: 100%;
        border-radius: 4px;
        transition:
            background-color 0.4s ease,
            opacity 0.4s ease;
        opacity: 0.3;
    }

    .timstock-dot.active {
        opacity: 1;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15);
    }

    .timer-container.urgent .timstock-dot.active {
        animation: blink 1.5s infinite alternate;
    }

    @keyframes blink {
        from {
            opacity: 1;
        }
        to {
            opacity: 0.6;
        }
    }
</style>
