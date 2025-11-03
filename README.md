# Dancing With the Stars Data Analysis

This project explores trends in the Dancing With the Stars (DWTS) dataset, focusing on contestant scores, seasonal averages, and performance metrics. It uses Python and pandas to analyze weekly judge scores, identify full-season participants, and visualize results.

## Features
- Load and inspect the DWTS dataset from a CSV file.
- Calculate average scores per week across seasons, excluding eliminations.
- Export seasonal averages to CSV and visualize as line plots.
- Identify contestants who completed full seasons and rank the top 10 by average score.
- Include placement data in outputs for context.

## Prerequisites
- Python 3.x installed.
- Required libraries: `pandas`, `matplotlib`. Install via `pip install pandas matplotlib`.

## Usage
1. Place the `dancing_with_the_stars_dataset.csv` file in the same directory as the scripts.
2. Run scripts from the command line in the DWTS_Data directory:
   - `python data_import.py`: Loads data, computes seasonal week averages, exports to CSV, and generates a plot.
   - `python full_season_averages.py`: Finds and ranks full-season contestants, prints top 10 with placements.
3. Outputs include printed results, CSV files (e.g., `season_week_averages.csv`), and PNG plots (e.g., `season_scores_plot.png`).

## Files
- `dancing_with_the_stars_dataset.csv`: The raw dataset with contestant details and weekly scores.
- `data_import.py`: Script for loading data, averaging scores, and basic visualization.
- `full_season_averages.py`: Script for identifying and ranking full-season contestants.
- `README.md`: This file.

## Notes
- Assumes "full season" means non-zero scores in every week up to the season's maximum.
- Visualizations are saved as images for easy viewing outside the terminal.
- Customize scripts for different analyses (e.g., adjust filters or add more plots).