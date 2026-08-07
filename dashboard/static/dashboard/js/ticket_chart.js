document.addEventListener("DOMContentLoaded", function () {
    function renderTicketChart() {
        const chartEl = document.getElementById("ticket-column-chart");

        if (!chartEl || typeof ApexCharts === "undefined") {
            return;
        }

        if (chartEl.dataset.rendered === "true") {
            return;
        }

        const getBrandColor = () => {
            const computedStyle = getComputedStyle(document.documentElement);
            return computedStyle.getPropertyValue("--color-fg-brand").trim() || "#9810fa";
        };

        const getBrandSecondaryColor = () => {
            const computedStyle = getComputedStyle(document.documentElement);
            return computedStyle.getPropertyValue("--color-fg-brand-subtle").trim() || "#3d0466";
        };

        const labels = JSON.parse(document.getElementById("ticket-chart-labels").textContent);
        const created = JSON.parse(document.getElementById("ticket-created-counts").textContent);

        const createdSeries = labels.map((label, index) => ({
            x: label,
            y: created[index],
        }));

        const options = {
            colors: [getBrandColor()],
            series: [
                {
                    name: "Created Tickets",
                    data: createdSeries,
                },
            ],
            chart: {
                type: "bar",
                height: 320,
                fontFamily: "Inter, sans-serif",
                toolbar: {
                    show: true,
                },
                background: "transparent",
            },
            theme: {
                mode: "dark"
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: "50%",
                    borderRadius: 8,
                    borderRadiusApplication: "end",
                },
            },
            dataLabels: {
                enabled: true,
            },
            legend: {
                show: false,
            },
            xaxis: {
                type: "category",
                axisBorder: {
                    show: false,
                },
                axisTicks: {
                    show: false,
                },
            },
            yaxis: {
                show: true,
                min: 0,
                forceNiceScale: true,
            },
            grid: {
                show: false,
            },
            tooltip: {
                shared: true,
                intersect: false,
            },
            fill: {
                opacity: 1,
            },
        };

        const chart = new ApexCharts(chartEl, options);
        chart.render();

        chartEl.dataset.rendered = "true";
    }

    renderTicketChart();

    document.body.addEventListener("htmx:afterSwap", function () {
        renderTicketChart();
    });
});
