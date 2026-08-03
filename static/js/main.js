function initializeWorldClock() {
    const clocks = [
        {
            id: "india-time",
            timezone: "Asia/Kolkata",
        },
        {
            id: "uae-time",
            timezone: "Asia/Dubai",
        },
        {
            id: "ksa-time",
            timezone: "Asia/Riyadh",
        },
    ];

    function updateClock() {
        const now = new Date();

        const desktopDateElement = document.getElementById("current-date");
        const mobileDateElement = document.getElementById(
            "current-date-mobile"
        );

        // Desktop: 03 Aug 2026
        if (desktopDateElement) {
            desktopDateElement.textContent = now.toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric",
            });
        }

        // Mobile: 03 Aug
        if (mobileDateElement) {
            mobileDateElement.textContent = now.toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
            });
        }

        clocks.forEach((clock) => {
            const element = document.getElementById(clock.id);

            if (!element) return;

            element.textContent = now.toLocaleTimeString("en-IN", {
                timeZone: clock.timezone,
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
            });
        });
    }

    updateClock();

    // Seconds are not displayed, so updating every 30 seconds is enough.
    setInterval(updateClock, 30000);
}

document.addEventListener("DOMContentLoaded", initializeWorldClock);
