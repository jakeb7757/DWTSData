document.addEventListener('DOMContentLoaded', async () => {
    const loading = document.getElementById('loading');
    const content = document.getElementById('analytics-content');

    if (!content) return; // Should not happen on analytics page

    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        // Hide loading, show content
        loading.style.display = 'none';
        content.style.display = 'block';

        const category = content.getAttribute('data-category');

        // Populate Robbed List
        const robbedList = document.getElementById('robbed-list');
        if (robbedList && (category === 'all' || category === 'robbed')) {
            data.robbed.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'rank-item';
                li.innerHTML = `
                    <div class="rank-number">${index + 1}</div>
                    <div class="rank-details">
                        <div class="rank-name"><a href="/?q=${encodeURIComponent(item.name)}" class="analytics-link">${item.name}</a></div>
                        <div class="rank-meta">Season ${item.season} • Partner: ${item.partner}</div>
                    </div>
                    <div class="rank-stat stat-highlight">
                        +${item.diff} Spots
                        <div style="font-size: 0.8em; color: var(--text-muted); font-weight: normal;">
                            Should: ${getOrdinal(item.should_have_placed)} / Actual: ${getOrdinal(item.actual_placement)}
                        </div>
                    </div>
                `;
                robbedList.appendChild(li);
            });
        }

        // Populate Overachievers List
        const overachieversList = document.getElementById('overachievers-list');
        if (overachieversList && (category === 'all' || category === 'overachievers')) {
            data.overachievers.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'rank-item';
                li.innerHTML = `
                    <div class="rank-number">${index + 1}</div>
                    <div class="rank-details">
                        <div class="rank-name"><a href="/?q=${encodeURIComponent(item.name)}" class="analytics-link">${item.name}</a></div>
                        <div class="rank-meta">Season ${item.season} • Partner: ${item.partner}</div>
                    </div>
                    <div class="rank-stat stat-negative">
                        ${item.diff} Spots
                        <div style="font-size: 0.8em; color: var(--text-muted); font-weight: normal;">
                            Should: ${getOrdinal(item.should_have_placed)} / Actual: ${getOrdinal(item.actual_placement)}
                        </div>
                    </div>
                `;
                overachieversList.appendChild(li);
            });
        }

        // Populate Hall of Fame
        const hofList = document.getElementById('hall-of-fame-list');
        if (hofList && (category === 'all' || category === 'hall_of_fame')) {
            data.hall_of_fame.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'rank-item';
                li.innerHTML = `
                    <div class="rank-number">${index + 1}</div>
                    <div class="rank-details">
                        <div class="rank-name"><a href="/?q=${encodeURIComponent(item.name)}" class="analytics-link">${item.name}</a></div>
                        <div class="rank-meta">Season ${item.season}</div>
                    </div>
                    <div class="rank-stat">
                        ${item.average_score} Avg
                    </div>
                `;
                hofList.appendChild(li);
            });
        }

        // Populate Season Stats
        const seasonBody = document.getElementById('season-stats-body');
        if (seasonBody && (category === 'all' || category === 'seasons')) {
            data.season_stats.forEach(season => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${season.season}</td>
                    <td>${season.average_score}</td>
                    <td><a href="/?q=${encodeURIComponent(season.winner)}" class="analytics-link">${season.winner}</a></td>
                    <td>
                        <a href="/?q=${encodeURIComponent(season.top_star)}" class="analytics-link">${season.top_star}</a>
                        <span style="font-size: 0.8em; color: var(--text-muted);">(${season.top_star_avg})</span>
                    </td>
                `;
                seasonBody.appendChild(tr);
            });
        }

    } catch (error) {
        console.error('Error fetching analytics:', error);
        if (loading) loading.textContent = 'Error loading analytics.';
    }

    function getOrdinal(n) {
        if (typeof n !== 'number') return n;
        const s = ["th", "st", "nd", "rd"];
        const v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    }
});
