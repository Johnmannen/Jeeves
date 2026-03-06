<script>
    export let events = [];

    // Filtrera till bara dagens händelser
    $: todayEvents = events.filter((e) => isToday(e.start));
    $: nextEvent = events.find((e) => !isToday(e.start));

    function formatTime(isoString) {
        if (!isoString) return "";
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString("sv-SE", {
                hour: "2-digit",
                minute: "2-digit",
            });
        } catch (e) {
            return isoString.substring(11, 16) || "";
        }
    }

    function formatDate(isoString) {
        if (!isoString) return "";
        const date = new Date(isoString);
        return date.toLocaleDateString("sv-SE", {
            weekday: "long",
            day: "numeric",
            month: "long",
        });
    }

    function isToday(isoString) {
        const date = new Date(isoString);
        const today = new Date();
        return (
            date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear()
        );
    }
</script>

<div class="timeline-container">
    <h3>📅 Idag</h3>

    {#if todayEvents.length === 0}
        <p class="empty-state">Inga möten idag — andas ut! 🌿</p>
        {#if nextEvent}
            <p class="next-hint">
                Nästa: {nextEvent.summary} · {formatDate(nextEvent.start)}
            </p>
        {/if}
    {:else}
        <div class="events-list">
            {#each todayEvents as event}
                <div class="event-card today">
                    <div class="time-box">
                        <span class="time">{formatTime(event.start)}</span>
                    </div>
                    <div class="info-box">
                        <span class="summary">{event.summary}</span>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .timeline-container {
        background: var(--bg-primary, #fdfbf7);
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin: 0.5rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    h3 {
        margin: 0 0 0.6rem;
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .empty-state {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 0;
    }

    .next-hint {
        color: var(--accent-calm, #4a6741);
        font-size: 0.8rem;
        margin: 0.4rem 0 0;
        opacity: 0.7;
    }

    .events-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .event-card {
        display: flex;
        align-items: center;
        padding: 0.7rem 0.8rem;
        background: var(--bg-secondary, #f4f1ea);
        border-radius: 10px;
        border-left: 3px solid var(--accent-calm, #4a6741);
    }

    .time-box {
        min-width: 50px;
        font-weight: 700;
        font-size: 0.85rem;
        color: var(--accent-calm, #4a6741);
    }

    .info-box {
        display: flex;
        flex-direction: column;
    }

    .summary {
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
</style>
