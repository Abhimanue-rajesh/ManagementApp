document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("email-input");
    const output = document.getElementById("email-output");

    const extractButton = document.getElementById("extract-btn");
    const copyButton = document.getElementById("copy-btn");
    const clearButton = document.getElementById("clear-btn");

    const countElement = document.getElementById("email-count");
    const copyStatus = document.getElementById("copy-status");

    const emailRegex =
        /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;

    function extractEmails() {
        const text = input.value;

        if (!text.trim()) {
            output.value = "";
            updateCount(0);
            copyButton.disabled = true;
            return;
        }

        /*
         * Capture only:
         * From:
         * Cc:
         *
         * Ignore:
         * To:
         * Subject:
         * Body/content
         */

        const lines = text.split(/\r?\n/);

        let currentField = null;
        let relevantText = [];

        for (const line of lines) {
            const trimmedLine = line.trim();

            const headerMatch = trimmedLine.match(
                /^(from|to|cc|bcc|subject):\s*(.*)$/i
            );

            if (headerMatch) {
                const field = headerMatch[1].toLowerCase();
                const value = headerMatch[2];

                currentField = field;

                if (field === "from" || field === "cc") {
                    relevantText.push(value);
                }

                continue;
            }

            /*
             * Handles wrapped Cc/From lines such as:
             *
             * Cc: user1@example.com;
             *     user2@example.com;
             *     user3@example.com
             */
            if (
                (currentField === "from" || currentField === "cc") &&
                trimmedLine
            ) {
                relevantText.push(trimmedLine);
            }
        }

        const matches =
            relevantText.join(" ").match(emailRegex) || [];

        // Normalize and remove duplicates
        const emails = [
            ...new Set(
                matches.map(email =>
                    email.toLowerCase()
                )
            ),
        ];

        output.value = emails.join("\n");

        updateCount(emails.length);

        copyButton.disabled = emails.length === 0;

        copyStatus.classList.add("hidden");
    }

    function updateCount(count) {
        countElement.textContent =
            `${count} ${count === 1 ? "email" : "emails"}`;
    }

    async function copyEmails() {
        const text = output.value;

        if (!text) {
            return;
        }

        try {
            await navigator.clipboard.writeText(text);

            copyStatus.textContent = "Copied to clipboard.";
            copyStatus.classList.remove("hidden");

            setTimeout(() => {
                copyStatus.classList.add("hidden");
            }, 2000);
        } catch (error) {
            output.select();
            document.execCommand("copy");

            copyStatus.textContent = "Copied to clipboard.";
            copyStatus.classList.remove("hidden");
        }
    }

    function clearFields() {
        input.value = "";
        output.value = "";

        updateCount(0);

        copyButton.disabled = true;
        copyStatus.classList.add("hidden");

        input.focus();
    }

    extractButton.addEventListener("click", extractEmails);
    copyButton.addEventListener("click", copyEmails);
    clearButton.addEventListener("click", clearFields);

    /*
     * Ctrl + Enter = Extract
     */
    input.addEventListener("keydown", event => {
        if (event.ctrlKey && event.key === "Enter") {
            extractEmails();
        }
    });
});
