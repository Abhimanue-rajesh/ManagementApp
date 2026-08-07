document.addEventListener("DOMContentLoaded", function () {
    function renderTaskStatusChart() {
        const chartEl = document.getElementById("task-status-chart");

        if (!chartEl || typeof ApexCharts === "undefined") {
            return;
        }

        if (chartEl.dataset.rendered === "true") {
            return;
        }

        const parseChartData = (elementId) => {
            const element = document.getElementById(elementId);

            if (!element) {
                return [];
            }

            try {
                return JSON.parse(element.textContent);
            } catch (error) {
                console.error(`Invalid chart data: ${elementId}`, error);
                return [];
            }
        };

        const labels = parseChartData("task-chart-labels");
        const notStarted = parseChartData("task-not-started-counts");
        const inProgress = parseChartData("task-in-progress-counts");
        const waiting = parseChartData("task-waiting-counts");
        const closed = parseChartData("task-closed-counts");
        const terminated = parseChartData("task-terminated-counts");

        const isDarkMode = document.documentElement.classList.contains("dark");

        const options = {
            series: [
                {
                    name: "Not Started",
                    data: notStarted,
                },
                {
                    name: "In Progress",
                    data: inProgress,
                },
                {
                    name: "Waiting for Approval",
                    data: waiting,
                },
                {
                    name: "Completed",
                    data: closed,
                },
                {
                    name: "Terminated",
                    data: terminated,
                },
            ],

            colors: [
                "#ef4444", // Not Started
                "#3b82f6", // In Progress
                "#f59e0b", // Waiting for Approval
                "#22c55e", // Completed
                "#6b7280", // Terminated
            ],

            chart: {
                type: "bar",
                height: 340,
                stacked: true,
                fontFamily: "Inter, sans-serif",
                background: "transparent",
                toolbar: {
                    show: true,
                },
            },

            theme: {
                mode: isDarkMode ? "dark" : "light",
            },

            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: "55%",
                    borderRadius: 5,
                    borderRadiusApplication: "end",
                },
            },

            dataLabels: {
                enabled: false,
            },

            xaxis: {
                categories: labels,
                axisBorder: {
                    show: false,
                },
                axisTicks: {
                    show: false,
                },
            },

            yaxis: {
                min: 0,
                forceNiceScale: true,
                labels: {
                    formatter: function (value) {
                        return Math.floor(value);
                    },
                },
            },

            grid: {
                borderColor: isDarkMode ? "#374151" : "#e5e7eb",
                strokeDashArray: 4,
            },

            legend: {
                position: "top",
                horizontalAlign: "right",
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

    renderTaskStatusChart();

    document.body.addEventListener("htmx:afterSwap", function () {
        renderTaskStatusChart();
    });
});
