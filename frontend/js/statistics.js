async function loadStatistics() {

    const response = await fetch(
        "https://credibility-intelligence-api.onrender.com/api/claims/statistics/"
    );

    const data = await response.json();

    // Total
    document.getElementById("total").innerText = data.total_claims;

    // Label chart
    const labelCtx = document.getElementById("labelChart");

    new Chart(labelCtx, {
        type: "bar",
        data: {
            labels: Object.keys(data.by_label),
            datasets: [{
                label: "Claims by Label",
                data: Object.values(data.by_label)
            }]
        }
    });

    // Split chart
    const splitCtx = document.getElementById("splitChart");

    new Chart(splitCtx, {
        type: "pie",
        data: {
            labels: Object.keys(data.by_split),
            datasets: [{
                label: "Dataset Split",
                data: Object.values(data.by_split)
            }]
        }
    });

}

loadStatistics();