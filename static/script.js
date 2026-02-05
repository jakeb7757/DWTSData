document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');
    const autocompleteList = document.getElementById('autocomplete-list');

    let currentFocus = -1;

    // Detect mode based on URL
    const isProsPage = window.location.pathname === '/pros';

    const SEARCH_URL = isProsPage ? '/api/pros/search' : '/api/search';
    const NAMES_URL = isProsPage ? '/api/pros/names' : '/api/names';

    /**
     * Sanitize a string for safe text display (prevents XSS).
     */
    function escapeHTML(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }

    /**
     * Create a text node or set textContent instead of innerHTML where possible.
     */

    async function performSearch(queryOverride) {
        const query = queryOverride || searchInput.value.trim();
        if (!query) return;

        // Close autocomplete list
        closeAllLists();

        resultsContainer.innerHTML = '<div style="text-align:center; color: #a0a0a0;">Searching...</div>';

        try {
            const response = await fetch(`${SEARCH_URL}?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            resultsContainer.innerHTML = '';

            if (data.length === 0) {
                resultsContainer.innerHTML = '<div style="text-align:center; color: #a0a0a0;">No results found.</div>';
                return;
            }

            data.forEach(item => {
                const card = isProsPage ? createProCard(item) : createContestantCard(item);
                resultsContainer.appendChild(card);
            });

        } catch (error) {
            console.error('Error fetching data:', error);
            resultsContainer.innerHTML = '<div style="text-align:center; color: #ff6b6b;">An error occurred. Please try again.</div>';
        }
    }

    function createContestantCard(data) {
        const card = document.createElement('div');
        card.className = 'contestant-card';

        // Format placement text
        const placementText = escapeHTML(data.actual_placement);

        // Build dances rows (sanitized)
        const dancesRows = data.dances.map(dance => `
            <tr>
                <td>Week ${escapeHTML(dance.week)}</td>
                <td>${escapeHTML(dance.total_score)}</td>
                <td style="color: #a0a0a0; font-size: 0.9em;">${dance.judges_scores.map(s => escapeHTML(s)).join(' / ')}</td>
            </tr>
        `).join('');

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="contestant-name">${escapeHTML(data.name)}</div>
                    <div class="season-info">Season ${escapeHTML(data.season)} • Partner: ${escapeHTML(data.partner)}</div>
                </div>
                <div class="placement-badge">${placementText}</div>
            </div>

            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Average Score</div>
                    <div class="stat-value">${escapeHTML(data.average_score)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Highest Score</div>
                    <div class="stat-value">${escapeHTML(data.highest_score)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Should Have Placed</div>
                    <div class="stat-value should-have-placed">${getOrdinal(data.should_have_placed)}</div>
                </div>
            </div>

            <h3 style="color: var(--primary-gold); margin-bottom: 1rem; font-family: 'Playfair Display', serif;">Dance History</h3>
            <div style="overflow-x: auto;">
                <table class="dances-table">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Total Score</th>
                            <th>Judges' Breakdown</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dancesRows}
                    </tbody>
                </table>
            </div>
        `;

        return card;
    }

    function createProCard(data) {
        const card = document.createElement('div');
        card.className = 'contestant-card';

        // Build season history rows (sanitized)
        const historyRows = data.seasons.map(season => `
            <tr>
                <td>Season ${escapeHTML(season.season)}</td>
                <td>${escapeHTML(season.partner)}</td>
                <td>${escapeHTML(season.average_score)}</td>
                <td>${escapeHTML(season.placement_text)}</td>
                <td style="color: #4caf50;">${getOrdinal(season.should_have_placed)}</td>
            </tr>
        `).join('');

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="contestant-name">${escapeHTML(data.name)}</div>
                    <div class="season-info">${escapeHTML(data.seasons_count)} Seasons</div>
                </div>
                <div class="placement-badge">${escapeHTML(data.wins)} Wins</div>
            </div>

            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Wins</div>
                    <div class="stat-value">${escapeHTML(data.wins)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Placement</div>
                    <div class="stat-value">${escapeHTML(data.average_placement)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Should Have Won</div>
                    <div class="stat-value should-have-placed">${escapeHTML(data.should_have_won)}</div>
                </div>
            </div>

            <h3 style="color: var(--primary-gold); margin-bottom: 1rem; font-family: 'Playfair Display', serif;">Season History</h3>
            <div style="overflow-x: auto;">
                <table class="dances-table">
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Partner</th>
                            <th>Avg Score</th>
                            <th>Result</th>
                            <th>Should Have Placed</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${historyRows}
                    </tbody>
                </table>
            </div>
        `;

        return card;
    }

    function getOrdinal(n) {
        const s = ["th", "st", "nd", "rd"];
        const v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    }

    // --- Autocomplete Logic ---
    searchInput.addEventListener('input', async function (e) {
        const val = this.value;
        closeAllLists();
        if (!val) return false;
        currentFocus = -1;

        try {
            const response = await fetch(`${NAMES_URL}?q=${encodeURIComponent(val)}`);
            const names = await response.json();

            if (names.length === 0) return;

            // Limit suggestions to top 5 to avoid clutter
            const suggestions = names.slice(0, 5);

            suggestions.forEach(name => {
                const item = document.createElement('div');
                item.textContent = name;
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.value = name;
                item.appendChild(hiddenInput);

                item.addEventListener('click', function (e) {
                    searchInput.value = this.getElementsByTagName('input')[0].value;
                    closeAllLists();
                    performSearch();
                });
                autocompleteList.appendChild(item);
            });

        } catch (error) {
            console.error("Error fetching names:", error);
        }
    });

    searchInput.addEventListener('keydown', function (e) {
        let x = autocompleteList.getElementsByTagName('div');
        if (e.keyCode == 40) { // Down
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) { // Up
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            } else {
                performSearch();
            }
        }
    });

    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add('autocomplete-active');
    }

    function removeActive(x) {
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove('autocomplete-active');
        }
    }

    function closeAllLists(elmnt) {
        while (autocompleteList.firstChild) {
            autocompleteList.removeChild(autocompleteList.firstChild);
        }
    }

    document.addEventListener('click', function (e) {
        closeAllLists(e.target);
    });

    searchBtn.addEventListener('click', () => performSearch());

    // Check for query parameter on load
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
        searchInput.value = query;
        performSearch(query);
    }
});


