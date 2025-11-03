import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('C:\\Users\\jquie\\Documents\\DWTS_Data\\dancing_with_the_stars_dataset.csv')

print(df.head(20))

print(df.info())

# Identify the week average score columns (dynamically, in case of future changes)
week_cols = [col for col in df.columns if col.startswith('week') and col.endswith('_avg_judge_score')]

# Group by 'season' and compute the mean for each week column, excluding 0.00 scores
season_week_averages = df.groupby('season')[week_cols].apply(lambda x: x[x > 0].mean())

# Rename columns for clarity (remove '_avg_judge_score' suffix)
season_week_averages.columns = [col.replace('_avg_judge_score', '') for col in season_week_averages.columns]

# Print the resulting DataFrame
print("\nAverage Scores per Week per Season (excluding 0.00 scores):")
print(season_week_averages)

# Export to CSV
season_week_averages.to_csv('season_week_averages.csv')
print("\nDataFrame exported to 'season_week_averages.csv' in the current directory.")

# Plot the results: Line plot of average scores per week per season
plt.figure(figsize=(10, 6))  # Set figure size for readability
for season in season_week_averages.index:
    plt.plot(season_week_averages.columns, season_week_averages.loc[season], label=f'Season {int(season)}', marker='o')

plt.title('Average Scores per Week per Season')
plt.xlabel('Week')
plt.ylabel('Average Score')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot as an image file
plt.savefig('season_scores_plot.png')
print("\nPlot saved as 'season_scores_plot.png' in the current directory.")

# Optional: Show the plot in a window (comment out if not needed)
# plt.show()
