document.addEventListener("DOMContentLoaded", function () {

    const drawer = document.getElementById(
        "quickcopy-drawer"
    );

    const backdrop = document.getElementById(
        "quickcopy-drawer-backdrop"
    );

    const content = document.getElementById(
        "quickcopy-drawer-content"
    );

    const closeButton = document.getElementById(
        "quickcopy-drawer-close"
    );


    if (!drawer || !backdrop || !content) {
        return;
    }


    function openDrawer() {

        backdrop.style.display = "block";

        drawer.style.transform =
            "translateX(0)";

        document.body.style.overflow =
            "hidden";
    }


    function closeDrawer() {

        drawer.style.transform =
            "translateX(100%)";

        backdrop.style.display =
            "none";

        document.body.style.overflow =
            "";

        content.innerHTML = "";
    }


    closeButton?.addEventListener(
        "click",
        closeDrawer
    );


    backdrop.addEventListener(
        "click",
        closeDrawer
    );


    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {
                closeDrawer();
            }

        }
    );


    window.openQuickCopyDrawer =
        async function (url) {

            openDrawer();

            content.innerHTML = `
                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    padding:60px 20px;
                    color:#6b7280;
                ">
                    Loading...
                </div>
            `;

            try {

                const response = await fetch(
                    url,
                    {
                        headers: {
                            "X-Requested-With":
                                "XMLHttpRequest"
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        "Unable to load Quick Copy."
                    );
                }

                content.innerHTML =
                    await response.text();

                setupForm(url);

            } catch (error) {

                console.error(error);

                content.innerHTML = `
                    <div style="color:#dc2626;">
                        Unable to load Quick Copy.
                    </div>
                `;

            }

        };


    function setupForm(url) {

        const form = document.getElementById(
            "quickcopy-drawer-form"
        );

        if (!form) {
            return;
        }


        const cancelButton =
            document.getElementById(
                "quickcopy-drawer-cancel"
            );


        cancelButton?.addEventListener(
            "click",
            closeDrawer
        );


        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const saveButton =
                    document.getElementById(
                        "quickcopy-drawer-save"
                    );


                if (saveButton) {

                    saveButton.disabled = true;
                    saveButton.textContent =
                        "Saving...";

                }


                try {

                    const response = await fetch(
                        url,
                        {
                            method: "POST",
                            body: new FormData(form),

                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest"
                            }
                        }
                    );


                    const contentType =
                        response.headers.get(
                            "content-type"
                        ) || "";


                    if (
                        contentType.includes(
                            "application/json"
                        )
                    ) {

                        const data =
                            await response.json();


                        if (data.success) {

                            closeDrawer();

                            window.location.reload();

                            return;
                        }

                    }


                    /*
                     * Form contains validation
                     * errors. Django returns
                     * HTML again.
                     */

                    content.innerHTML =
                        await response.text();

                    setupForm(url);


                } catch (error) {

                    console.error(error);

                    alert(
                        "Unable to save Quick Copy."
                    );


                } finally {

                    const currentButton =
                        document.getElementById(
                            "quickcopy-drawer-save"
                        );

                    if (currentButton) {

                        currentButton.disabled =
                            false;

                        currentButton.textContent =
                            "Save changes";
                    }

                }

            }
        );

    }

});

document.addEventListener(
    "click",
    function (event) {

        const button = event.target.closest(
            ".quickcopy-edit-btn"
        );

        if (!button) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const url =
            button.dataset.drawerUrl;

        if (!url) {
            return;
        }

        window.openQuickCopyDrawer(url);

    }
);
