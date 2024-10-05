document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the ids and selectedId from the hidden script element
    //var dataElement = document.getElementById('data');
    //var data = JSON.parse(dataElement.textContent);

    //var ids = data.ids;
    //var selectedId = data.selected_id;

    // Populate the dropdown
    var select = document.getElementById('id');
    //ids.forEach(function(id) {
       // var option = document.createElement('option');
        //option.value = id;
        //option.textContent = id;
        //if (id == selectedId) {
        //    option.selected = true;
        //}
        //select.appendChild(option);
    //});

    // Update the XZ plot image source
    var xzPlotImg = document.getElementById('xzPlot');
    //if (selectedId) {
    //    xzPlotImg.src = '/static/plots/plot_' + selectedId + '.png';
    //} else {
    //    xzPlotImg.src = '/static/plots/plot_1.png'; // Default image
    //}
});

document.getElementById('selectionForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    var id = document.getElementById('id').value;
    var xzPlotImg = document.getElementById('xzPlot');

    // Update the XZ plot image source
    xzPlotImg.src = '/static/plots/plot_' + id + '.png';
});

document.addEventListener('DOMContentLoaded', function() {
    loadLeaderboard();

    // Function to load leaderboard data
    function loadLeaderboard() {
        fetch('/leaderboard')
            .then(response => response.json())
            .then(data => {
                const leaderboardDiv = document.getElementById('leaderboard');
                leaderboardDiv.innerHTML = ''; // Clear previous content

                if (data.error) {
                    leaderboardDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                    return;
                }

                if (data.length === 0) {
                    leaderboardDiv.innerHTML = '<p>No leaderboard data available.</p>';
                    return;
                }

                // Create and append leaderboard entries
                data.forEach((entry, index) => {
                    const entryDiv = document.createElement('div');
                    entryDiv.className = 'leaderboard-entry';
                    entryDiv.innerHTML = `<strong>${index + 1}. ${entry.player_name}</strong>: ${entry.completion_time}s`;
                    leaderboardDiv.appendChild(entryDiv);
                });
            })
            .catch(error => {
                console.error('Error loading leaderboard data:', error);
                const leaderboardDiv = document.getElementById('leaderboard');
                leaderboardDiv.innerHTML = `<p>Error loading leaderboard data.</p>`;
            });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    loadStats();

    // Function to load stats data
    function loadStats() {
        fetch('/get_statistics')
            .then(response => response.json())
            .then(data => {
                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = ''; // Clear previous content

                if (data.error) {
                    statsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                    return;
                }

                // Display X position stats
                const xStatsDiv = document.createElement('div');
                xStatsDiv.className = 'stats-section';
                xStatsDiv.innerHTML = `
                    <h3>X Position Stats</h3>
                    <p>Min: ${data.x_stats.min}</p>
                    <p>Max: ${data.x_stats.max}</p>
                    <p>Avg: ${data.x_stats.avg.toFixed(2)}</p>
                `;
                statsDiv.appendChild(xStatsDiv);

                // Display Z position stats
                const zStatsDiv = document.createElement('div');
                zStatsDiv.className = 'stats-section';
                zStatsDiv.innerHTML = `
                    <h3>Z Position Stats</h3>
                    <p>Min: ${data.z_stats.min}</p>
                    <p>Max: ${data.z_stats.max}</p>
                    <p>Avg: ${data.z_stats.avg.toFixed(2)}</p>
                `;
                statsDiv.appendChild(zStatsDiv);
            })
            .catch(error => {
                console.error('Error loading stats data:', error);
                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = `<p>Error loading stats data.</p>`;
            });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const llmForm = document.getElementById('llmForm');
    const responseText = document.getElementById('responseText');
    const pageSummary = document.getElementById('pageSummary'); // Make sure this exists in your HTML

    // Handle form submission for the LLM input
    llmForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const userInput = document.getElementById('userInput').value;
        responseText.textContent = 'Loading...'; // Show loading text

        try {
            const response = await fetch('/query_llm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: userInput })
            });

            const result = await response.json();
            if (response.ok) {
                responseText.textContent = result.response; // Display AI's answer
            } else {
                responseText.textContent = `Error: ${result.error || 'Something went wrong'}`;
            }
        } catch (error) {
            responseText.textContent = 'Network error: Unable to query the LLM';
        }
    });

    // Send a request to get the page summary from the LLM
    async function getPageSummary() {
        const pageContent = document.body.innerText;  // Send the page content as a string
        try {
            const response = await fetch('/query_llm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: `Summarize the following page: ${pageContent}` })
            });

            const result = await response.json();
            if (response.ok) {
                pageSummary.textContent = result.response;
            } else {
                pageSummary.textContent = `Error: ${result.error || 'Something went wrong'}`;
            }
        } catch (error) {
            pageSummary.textContent = 'Network error: Unable to fetch page summary';
        }
    }

    // Call the function to get the page summary on page load
    getPageSummary();
});
