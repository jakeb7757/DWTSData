import pandas as pd

# Load the dataset
df = pd.read_csv('C:\\Users\\jquie\\Documents\\DWTS_Data\\dancing_with_the_stars_dataset.csv')

# Identify week average score columns
week_cols = [col for col in df.columns if col.startswith('week') and col.endswith('_avg_judge_score')]

# Function to get the max week for a season (highest week with any non-zero score)
def get_max_week(season_df):
    for col in reversed(week_cols):
        if (season_df[col] > 0).any():
            return int(col.replace('week', '').replace('_avg_judge_score', ''))
    return 0

# List to store full-season contestants
full_season_contestants = []

# Process each season
for season, season_df in df.groupby('season'):
    max_week = get_max_week(season_df)
    if max_week == 0:
        continue  # Skip if no weeks
    
    # Check each contestant in the season
    for _, row in season_df.iterrows():
        # Check if they have scores >0 in all weeks up to max_week
        full_season = True
        scores = []
        for w in range(1, max_week + 1):
            col = f'week{w}_avg_judge_score'
            score = row[col]
            if score <= 0:
                full_season = False
                break
            scores.append(score)
        
        if full_season:
            avg_score = sum(scores) / len(scores)
            full_season_contestants.append({
                'celebrity_name': row['celebrity_name'],
                'season': season,
                'average_score': avg_score,
                'weeks_completed': max_week,
                'placement': row['placement']  # Add placement
            })

# Convert to DataFrame and sort by average_score descending
if full_season_contestants:
    results_df = pd.DataFrame(full_season_contestants).sort_values(by='average_score', ascending=False)
    
    # Print top 10
    print("Top 10 Contestants with Highest Full Season Average Scores:")
    print(results_df.head(10).to_string(index=False))
else:
    print("No contestants completed a full season in the dataset.")