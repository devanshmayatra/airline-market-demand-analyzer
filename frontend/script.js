const API_BASE_URL = "https://airline-market-demand-analyzer-api.onrender.com";

const analyzeBtn = document.getElementById('analyzeBtn');
const originInput = document.getElementById('origin');
const destinationInput = document.getElementById('destination');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const insightsDiv = document.getElementById('insights');
const offersTableBody = document.querySelector('#offersTable tbody');

let trendsChartInstance = null; // To hold the chart instance

analyzeBtn.addEventListener('click', async () => {
    const origin = originInput.value.trim();
    const destination = destinationInput.value.trim();
    const source = document.getElementById('dataSource').value;

    if (!origin || !destination) {
        alert('Please enter both origin and destination.');
        return;
    }

    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    insightsDiv.innerHTML = '';
    offersTableBody.innerHTML = '';

    try {
        const analyzeUrl = `${API_BASE_URL}/api/analyze-route?origin=${origin}&destination=${destination}&source=${source}`;
        
        const response = await fetch(analyzeUrl);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch market data');
        }
        const data = await response.json();

        // Render the data we received (it might be empty)
        renderOffersTable(data.offers);
        renderTrendsChart(data.trends);

        // --- NEW GUARD CLAUSE ---
        // If there are no offers, don't call the AI. Set a manual message.
        if (data.offers.length === 0) {
            insightsDiv.innerText = "No flight data was found for the selected route and date. Unable to generate insights.";
        } else {
            // If we have data, THEN call the AI for insights.
            const insightsResponse = await fetch(`${API_BASE_URL}/api/generate-insights`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!insightsResponse.ok) {
                const errorData = await insightsResponse.json();
                throw new Error(errorData.detail || 'Failed to generate insights');
            }
            const insightsData = await insightsResponse.json();
            insightsDiv.innerText = insightsData.insights;
        }

        resultsDiv.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        alert(`An error occurred: ${error.message}`);
    } finally {
        loadingDiv.classList.add('hidden');
    }
});

function renderOffersTable(offers) {
    offersTableBody.innerHTML = '';
    if (!offers || offers.length === 0) {
        offersTableBody.innerHTML = '<tr><td colspan="4">No current offers found.</td></tr>';
        return;
    }
    offers.forEach(offer => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${offer.airline}</td>
            <td>₹${offer.price.toFixed(2)}</td>
            <td>${offer.departure}</td>
            <td>${offer.arrival}</td>
        `;
        offersTableBody.appendChild(row);
    });
}

function renderTrendsChart(trends) {
    const chartContainer = document.querySelector('.chart-container');

    if (trendsChartInstance) {
        trendsChartInstance.destroy(); 
    }

    // If there is no trend data, hide the entire chart section and stop.
    if (!trends || trends.length === 0) {
        chartContainer.style.display = 'none';
        return;
    }

    // If we have data, make sure the chart section is visible and then draw the chart.
    chartContainer.style.display = 'block';
    const ctx = document.getElementById('trendsChart').getContext('2d');

    const labels = trends.map(item => item.departureDate);
    const data = trends.map(item => parseFloat(item.price.total));

    trendsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cheapest Price (AUD)',
                data: data,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}