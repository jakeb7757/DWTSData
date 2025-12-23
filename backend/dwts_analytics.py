import pandas as pd
import numpy as np

def get_analytics_summary(df):
    """
    Calculates deep dive statistics for the DWTS dataset.
    Returns a dictionary structure suitable for JSON serialization.
    """
    if df is None or df.empty:
        return {}

    # Calculate placement difference: Actual - Should Have (Positive = Robbed, Negative = Overachieved)
    # Example: Placed 5th, Should Have 1st. Diff = 4 (Robbed)
    # Example: Placed 1st, Should Have 5th. Diff = -4 (Overachieved)
    df['placement_diff'] = df['placement'] - df['should_have_placed']

    # --- Robbed List ---
    # Sort by difference descending
    robbed_df = df.sort_values(by='placement_diff', ascending=False).head(10)
    robbed_list = []
    for _, row in robbed_df.iterrows():
        robbed_list.append({
            'name': row['celebrity_name'],
            'season': int(row['season']),
            'partner': row['ballroom_partner'],
            'actual_placement': int(row['placement']) if pd.notna(row['placement']) else "N/A",
            'should_have_placed': int(row['should_have_placed']),
            'diff': int(row['placement_diff'])
        })

    # --- Overachievers List ---
    # Sort by difference ascending
    overachievers_df = df.sort_values(by='placement_diff', ascending=True).head(10)
    overachievers_list = []
    for _, row in overachievers_df.iterrows():
        overachievers_list.append({
            'name': row['celebrity_name'],
            'season': int(row['season']),
            'partner': row['ballroom_partner'],
            'actual_placement': int(row['placement']) if pd.notna(row['placement']) else "N/A",
            'should_have_placed': int(row['should_have_placed']),
            'diff': int(row['placement_diff'])
        })

    # --- Season Stats ---
    # Group by season
    season_stats = []
    season_groups = df.groupby('season')
    
    for season, group in season_groups:
        season_avg = group['average_score'].mean()
        # Find winner
        winner = group[group['placement'] == 1]
        winner_name = winner.iloc[0]['celebrity_name'] if not winner.empty else "Unknown"
        
        # highest avg in season
        best_avg_row = group.loc[group['average_score'].idxmax()]
        
        season_stats.append({
            'season': int(season),
            'average_score': round(season_avg, 2),
            'winner': winner_name,
            'top_star': best_avg_row['celebrity_name'],
            'top_star_avg': round(best_avg_row['average_score'], 2)
        })
    
    # Sort seasons by highest average score to see "Best Seasons"
    season_stats.sort(key=lambda x: x['average_score'], reverse=True)

    # --- Hall of Fame (Top 10 Averages All Time) ---
    top_avg_df = df.sort_values(by='average_score', ascending=False).head(10)
    hall_of_fame = []
    for _, row in top_avg_df.iterrows():
        hall_of_fame.append({
            'name': row['celebrity_name'],
            'season': int(row['season']),
            'average_score': round(row['average_score'], 2),
            'placement': int(row['placement']) if pd.notna(row['placement']) else "N/A"
        })

    return {
        'robbed': robbed_list,
        'overachievers': overachievers_list,
        'season_stats': season_stats,
        'hall_of_fame': hall_of_fame
    }
