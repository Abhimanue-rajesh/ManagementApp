document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("meeting-date");
    const hourInput = document.getElementById("meeting-hour");
    const minuteInput = document.getElementById("meeting-minute");
    const timezoneInput = document.getElementById("source-timezone");

    const amButton = document.getElementById("am-button");
    const pmButton = document.getElementById("pm-button");

    const resultsContainer = document.getElementById("timezone-results");
    const description = document.getElementById("conversion-description");

    let selectedPeriod = "AM";


    const timezones = [
        {
            name: "UAE",
            timezone: "Asia/Dubai",
            short: "UAE",
        },
        {
            name: "KSA",
            timezone: "Asia/Riyadh",
            short: "KSA",
        },
        {
            name: "India",
            timezone: "Asia/Kolkata",
            short: "IND",
        },
        {
            name: "Qatar",
            timezone: "Asia/Qatar",
            short: "QAT",
        },
        {
            name: "Oman",
            timezone: "Asia/Muscat",
            short: "OMN",
        },
        {
            name: "United Kingdom",
            timezone: "Europe/London",
            short: "UK",
        },
    ];


    function updatePeriodButtons() {

        const activeClasses = [
            "text-primary-600",
            "shadow-sm",
            "dark:bg-base-700",
            "dark:text-primary-400",
        ];

        const inactiveClasses = [
            "text-font-subtle-light",
            "dark:text-font-subtle-dark",
        ];


        [amButton, pmButton].forEach(function (button) {

            activeClasses.forEach(cls => button.classList.remove(cls));
            inactiveClasses.forEach(cls => button.classList.remove(cls));


            if (button.dataset.period === selectedPeriod) {

                activeClasses.forEach(
                    cls => button.classList.add(cls)
                );

            } else {

                inactiveClasses.forEach(
                    cls => button.classList.add(cls)
                );

            }

        });

    }


    function get24HourTime() {

        if (!hourInput.value) {
            return null;
        }

        let hour = parseInt(hourInput.value, 10);
        const minute = minuteInput.value;


        if (selectedPeriod === "AM") {

            if (hour === 12) {
                hour = 0;
            }

        } else {

            if (hour !== 12) {
                hour += 12;
            }

        }


        return {
            hour: hour,
            minute: parseInt(minute, 10),
        };

    }


    function getTimezoneOffset(date, timezone) {

        const formatter = new Intl.DateTimeFormat(
            "en-US",
            {
                timeZone: timezone,
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hourCycle: "h23",
            }
        );


        const parts = formatter.formatToParts(date);
        const values = {};


        parts.forEach(function (part) {

            if (part.type !== "literal") {
                values[part.type] = part.value;
            }

        });


        const asUTC = Date.UTC(
            parseInt(values.year),
            parseInt(values.month) - 1,
            parseInt(values.day),
            parseInt(values.hour),
            parseInt(values.minute),
            parseInt(values.second)
        );


        return asUTC - date.getTime();

    }


    function zonedTimeToUtc(
        dateString,
        hour,
        minute,
        timezone
    ) {

        const [year, month, day] = dateString
            .split("-")
            .map(Number);


        const utcGuess = new Date(
            Date.UTC(
                year,
                month - 1,
                day,
                hour,
                minute,
                0
            )
        );


        let offset = getTimezoneOffset(
            utcGuess,
            timezone
        );


        let utcDate = new Date(
            utcGuess.getTime() - offset
        );


        const secondOffset = getTimezoneOffset(
            utcDate,
            timezone
        );


        if (secondOffset !== offset) {

            utcDate = new Date(
                utcGuess.getTime() - secondOffset
            );

        }


        return utcDate;

    }


    function formatTime(date, timezone) {

        return new Intl.DateTimeFormat(
            "en-US",
            {
                timeZone: timezone,
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
            }
        ).format(date);

    }


    function formatDate(date, timezone) {

        return new Intl.DateTimeFormat(
            "en-GB",
            {
                timeZone: timezone,
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        ).format(date);

    }


    function formatDay(date, timezone) {

        return new Intl.DateTimeFormat(
            "en-US",
            {
                timeZone: timezone,
                weekday: "long",
            }
        ).format(date);

    }


    function createCard(location, utcDate, sourceTimezone) {

        const convertedTime = formatTime(
            utcDate,
            location.timezone
        );

        const convertedDate = formatDate(
            utcDate,
            location.timezone
        );

        const convertedDay = formatDay(
            utcDate,
            location.timezone
        );


        const isSource =
            location.timezone === sourceTimezone;


        return `
            <div
                class="
                    rounded-default
                    border
                    p-5
                    transition
                    ${isSource
                ? "border-primary-500 dark:border-primary-600 dark:bg-primary-950/20"
                : "border-base-200 dark:border-base-800 dark:bg-base-900"
            }
                "
            >

                <div class="mb-5 flex items-start justify-between">

                    <div>

                        <div class="flex items-center gap-2">

                            <p
                                class="
                                    text-sm font-semibold
                                    text-font-important-light
                                    dark:text-font-important-dark
                                "
                            >
                                ${location.name}
                            </p>

                            ${isSource
                ? `
                                        <span
                                            class="
                                                rounded-default
                                                bg-primary-100
                                                px-2 py-0.5
                                                text-xs font-medium
                                                text-primary-700
                                                dark:bg-primary-900
                                                dark:text-primary-300
                                            "
                                        >
                                            Source
                                        </span>
                                    `
                : ""
            }

                        </div>

                        <p
                            class="
                                mt-1 text-xs
                                text-font-subtle-light
                                dark:text-font-subtle-dark
                            "
                        >
                            ${location.short}
                        </p>

                    </div>

                    <span
                        class="
                            material-symbols-outlined
                            text-base-400
                        "
                    >
                        schedule
                    </span>

                </div>


                <div
                    class="
                        text-3xl font-semibold
                        tracking-tight
                        text-font-important-light
                        dark:text-font-important-dark
                    "
                >
                    ${convertedTime}
                </div>


                <div
                    class="
                        mt-2 text-sm
                        text-font-subtle-light
                        dark:text-font-subtle-dark
                    "
                >
                    ${convertedDay}, ${convertedDate}
                </div>

            </div>
        `;

    }


    function updateTimes() {

        const selectedDate = dateInput.value;
        const selectedTimezone = timezoneInput.value;
        const selectedTime = get24HourTime();


        if (!selectedDate || !selectedTime) {

            resultsContainer.innerHTML = "";

            description.textContent =
                "Select a date and meeting time to view conversions.";

            return;

        }


        try {

            const utcDate = zonedTimeToUtc(
                selectedDate,
                selectedTime.hour,
                selectedTime.minute,
                selectedTimezone
            );


            resultsContainer.innerHTML = "";


            timezones.forEach(function (location) {

                resultsContainer.insertAdjacentHTML(
                    "beforeend",
                    createCard(
                        location,
                        utcDate,
                        selectedTimezone
                    )
                );

            });


            const sourceLocation = timezones.find(
                location =>
                    location.timezone === selectedTimezone
            );


            const sourceTime = formatTime(
                utcDate,
                selectedTimezone
            );


            description.textContent =
                `${sourceTime} in ${sourceLocation.name}`;

        } catch (error) {

            console.error(
                "Time conversion error:",
                error
            );

            description.textContent =
                "Unable to convert the selected time.";

        }

    }


    function setPeriod(period) {

        selectedPeriod = period;

        updatePeriodButtons();
        updateTimes();

    }


    amButton.addEventListener(
        "click",
        function () {
            setPeriod("AM");
        }
    );


    pmButton.addEventListener(
        "click",
        function () {
            setPeriod("PM");
        }
    );


    dateInput.addEventListener(
        "change",
        updateTimes
    );

    hourInput.addEventListener(
        "change",
        updateTimes
    );

    minuteInput.addEventListener(
        "change",
        updateTimes
    );

    timezoneInput.addEventListener(
        "change",
        updateTimes
    );


    // Default today's date
    const today = new Date();

    const year = today.getFullYear();

    const month = String(
        today.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        today.getDate()
    ).padStart(2, "0");


    dateInput.value =
        `${year}-${month}-${day}`;


    // Better defaults
    hourInput.value = "9";
    minuteInput.value = "00";

    updatePeriodButtons();
    updateTimes();

});
