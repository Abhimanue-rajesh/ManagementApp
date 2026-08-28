document.addEventListener("DOMContentLoaded", function () {
    const ignoreSelector =
        "a, button, input, select, textarea, label, option, svg, " +
        "[role='button'], [role='combobox'], [role='listbox'], [role='option'], " +
        ".select2, .select2-container, .select2-selection, " +
        ".choices, .choices__inner, .choices__list, " +
        "[data-controller], [data-action]";

    document.querySelectorAll("tbody tr").forEach((row) => {
        const editButton = row.querySelector(".quickcopy-edit-btn");

        if (!editButton) {
            return;
        }

        const drawerUrl = editButton.dataset.drawerUrl;

        if (!drawerUrl) {
            return;
        }

        row.style.cursor = "pointer";

        row.addEventListener("click", function (event) {
            if (event.target.closest(ignoreSelector)) {
                return;
            }

            if (typeof window.openQuickCopyDrawer !== "function") {
                console.error("openQuickCopyDrawer is not available.");
                return;
            }

            window.openQuickCopyDrawer(drawerUrl);
        });
    });
});
