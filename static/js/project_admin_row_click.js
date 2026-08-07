document.addEventListener("DOMContentLoaded", function () {
    const ignoreSelector =
        "a, button, input, select, textarea, label, option, svg, " +
        "[role='button'], [role='combobox'], [role='listbox'], [role='option'], " +
        ".select2, .select2-container, .select2-selection, " +
        ".choices, .choices__inner, .choices__list, " +
        "[data-controller], [data-action]";

    document.querySelectorAll("tbody tr").forEach((row) => {
        const projectData = row.querySelector(".project-row-data");

        if (!projectData) {
            return;
        }

        const projectId = projectData.dataset.projectId;

        if (!projectId) {
            return;
        }

        row.style.cursor = "pointer";

        row.addEventListener("click", function (e) {
            // Ignore Edit button, checkbox, dropdowns, etc.
            if (e.target.closest(ignoreSelector)) {
                return;
            }

            window.location.href =
                `/tasks/task/?project__id__exact=${projectId}`;
        });
    });
});
