document.addEventListener("DOMContentLoaded", function () {

    const amountInput = document.getElementById("currency-amount");
    const fromSelect = document.getElementById("currency-from");
    const toSelect = document.getElementById("currency-to");

    const convertedAmount = document.getElementById("converted-amount");
    const convertedCurrency = document.getElementById("converted-currency");
    const exchangeRate = document.getElementById("exchange-rate");
    const rateDate = document.getElementById("rate-date");

    const swapButton = document.getElementById("swap-currencies");


    async function convertCurrency() {

        const amount = parseFloat(amountInput.value) || 0;

        const from = fromSelect.value;
        const to = toSelect.value;


        // Same currency
        if (from === to) {

            convertedAmount.textContent = formatNumber(amount);
            convertedCurrency.textContent = to;

            exchangeRate.textContent = `1 ${from} = 1 ${to}`;
            rateDate.textContent = "";

            return;
        }


        convertedAmount.textContent = "Loading...";
        convertedCurrency.textContent = "";


        try {

            const response = await fetch(
                `https://api.frankfurter.dev/v2/rate/${from}/${to}`
            );


            if (!response.ok) {
                throw new Error("Unable to retrieve exchange rate.");
            }


            const data = await response.json();

            const rate = Number(data.rate);

            const result = amount * rate;


            convertedAmount.textContent = formatNumber(result);
            convertedCurrency.textContent = to;


            exchangeRate.textContent =
                `1 ${from} = ${formatRate(rate)} ${to}`;


            if (data.date) {
                rateDate.textContent = `Rate date: ${data.date}`;
            } else {
                rateDate.textContent = "Latest available exchange rate";
            }

        }

        catch (error) {

            console.error(error);

            convertedAmount.textContent = "Unavailable";
            convertedCurrency.textContent = "";

            exchangeRate.textContent =
                "Unable to retrieve the exchange rate.";

            rateDate.textContent = "";

        }

    }


    function formatNumber(value) {

        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value);

    }


    function formatRate(value) {

        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 6,
        }).format(value);

    }


    // Amount changes
    amountInput.addEventListener("input", convertCurrency);

    // Currency changes
    fromSelect.addEventListener("change", convertCurrency);
    toSelect.addEventListener("change", convertCurrency);


    // Swap currencies
    swapButton.addEventListener("click", function () {

        const from = fromSelect.value;

        fromSelect.value = toSelect.value;
        toSelect.value = from;

        convertCurrency();

    });


    // Initial conversion
    convertCurrency();

});
