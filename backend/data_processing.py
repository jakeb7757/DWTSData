import pandas as pd
import numpy as np

def load_and_process_data(filepath):
    """
    Loads the DWTS dataset and performs necessary cleaning and feature engineering.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        return None

    # --- Data Cleaning ---
    
    # Convert score columns to numeric, coercing errors to NaN
    score_cols = [col for col in df.columns if 'score' in col]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Ensure placement and season are numeric
    df['placement'] = pd.to_numeric(df['placement'], errors='coerce')
    df['season'] = pd.to_numeric(df['season'], errors='coerce')

    # Fill NaN in score columns with 0 (assuming N/A means no dance/score)
    # Be careful with averages, but for raw scores 0 might be appropriate if they didn't dance.
    # However, for "should have placed", we want average of *actual* dances.
    
    # --- Feature Engineering ---

    # Calculate average score per contestant (across all weeks where they danced)
    # We'll look for columns like 'weekX_total_judge_score' or calculate from judge scores if needed.
    # The dataset seems to have 'weekX_avg_judge_score'. Let's use those for a more robust average.
    
    week_avg_cols = [col for col in df.columns if 'avg_judge_score' in col and 'week' in col]
    
    # Calculate overall average for each contestant, ignoring 0s (which likely mean didn't dance)
    # We do this row-wise.
    def calculate_contestant_avg(row):
        scores = [row[col] for col in week_avg_cols if row[col] > 0]
        return np.mean(scores) if scores else 0

    df['average_score'] = df.apply(calculate_contestant_avg, axis=1)
    
    # Calculate highest score
    # We can look at 'weekX_total_judge_score' but scales might differ (30 vs 40).
    # Let's stick to the provided columns. If 'weekX_total_judge_score' exists, use max of that.
    # Actually, let's look at individual judge scores to see if we can find the max total for a dance.
    # The dataset has 'weekX_total_judge_score'.
    total_score_cols = [col for col in df.columns if 'total_judge_score' in col and 'week' in col]
    df['highest_score'] = df[total_score_cols].max(axis=1)

    # --- "Should Have Placed" Logic ---
    
    # Rank by average score within each season
    df['should_have_placed'] = df.groupby('season')['average_score'].rank(ascending=False, method='min')

    return df

def get_contestant_names(df, query):
    """
    Returns a list of contestant names matching the query.
    """
    if df is None:
        return []
    
    # Case-insensitive partial match
    match = df[df['celebrity_name'].str.contains(query, case=False, na=False)]
    
    if match.empty:
        return []
        
    return match['celebrity_name'].tolist()

def get_contestant_data(df, name_query):
    """
    Searches for a contestant and returns their details.
    """
    if df is None:
        return None
        
    # Case-insensitive partial match
    match = df[df['celebrity_name'].str.contains(name_query, case=False, na=False)]
    
    if match.empty:
        return None
    
    # Return the first match (or list of matches - for now let's assume unique enough or return list)
    # Let's return a list of matches to be safe
    results = []
    for _, row in match.iterrows():
        contestant = {
            'name': row['celebrity_name'],
            'season': int(row['season']),
            'partner': row['ballroom_partner'],
            'average_score': round(row['average_score'], 2),
            'highest_score': row['highest_score'],
            'actual_placement': row['placement'], # Assuming 'placement' column exists and is clean
            'should_have_placed': int(row['should_have_placed']),
            'dances': []
        }
        
        # Extract dance scores
        # We'll iterate through weeks to structure the dance data
        # Assuming structure: week1_judge1_score, ..., week1_total_judge_score
        # We need to know how many weeks. Let's just iterate through columns.
        
        for i in range(1, 12): # Assuming max 11-12 weeks based on file view
            week_prefix = f'week{i}_'
            total_col = f'{week_prefix}total_judge_score'
            
            if total_col in df.columns and row[total_col] > 0:
                dance_data = {
                    'week': i,
                    'total_score': row[total_col],
                    'judges_scores': [] # We could add individual judge scores if needed
                }
                # Try to find individual judge scores
                for j in range(1, 5):
                    judge_col = f'{week_prefix}judge{j}_score'
                    if judge_col in df.columns and pd.notna(row[judge_col]):
                         dance_data['judges_scores'].append(row[judge_col])
                
                contestant['dances'].append(dance_data)
        
        results.append(contestant)
        
    return results

def get_pros_data(df):
    """
    Aggregates data by professional partner to calculate stats.
    """
    if df is None:
        return []

    # Group by partner
    # We need to be careful about duplicates if a pro danced with multiple partners in the same season (rare but possible?)
    # or just standard grouping.
    # The dataset has one row per couple per season.
    
    pros_stats = []
    
    # Get unique partners
    partners = df['ballroom_partner'].unique()
    
    for partner in partners:
        partner_df = df[df['ballroom_partner'] == partner]
        
        # Wins: Placement is 1 (or "1st Place" if string, but we saw "Eliminated..." and "3rd Place")
        # Let's check how placement is stored. The CSV view showed "Eliminated Week 2", "3rd Place".
        # We need to parse placement to numbers if not already done, or handle the strings.
        # The CSV view showed a 'placement' column at the end which looked numeric (6.00, 5.00, 4.00, 3.00).
        # Let's assume the 'placement' column is the numeric one we saw.
        
        wins = len(partner_df[partner_df['placement'] == 1])
        
        # Average Placement
        avg_placement = partner_df['placement'].mean()
        
        # Should Have Won
        # Count where the couple's 'should_have_placed' is 1
        should_have_won = len(partner_df[partner_df['should_have_placed'] == 1])
        
        pros_stats.append({
            'name': partner,
            'wins': wins,
            'average_placement': round(avg_placement, 2) if not pd.isna(avg_placement) else 0,
            'should_have_won': should_have_won,
            'seasons_count': len(partner_df)
        })
        
    # Sort by wins descending, then average placement ascending
    pros_stats.sort(key=lambda x: (-x['wins'], x['average_placement']))
    
    return pros_stats

def get_pro_names(df, query):
    """
    Returns a list of pro names matching the query.
    """
    if df is None:
        return []
    
    # Get unique partners
    partners = df['ballroom_partner'].unique()
    
    # Filter by query (case-insensitive)
    matches = [p for p in partners if query.lower() in p.lower()]
    
    return matches

def get_pro_details(df, name_query):
    """
    Searches for a pro and returns their aggregated stats and season history.
    """
    if df is None:
        return []
        
    # Find matching pros (usually just one, but handle partial matches)
    partners = df['ballroom_partner'].unique()
    matches = [p for p in partners if name_query.lower() in p.lower()]
    
    if not matches:
        return []
        
    results = []
    for pro_name in matches:
        pro_df = df[df['ballroom_partner'] == pro_name]
        
        # Calculate stats
        wins = len(pro_df[pro_df['placement'] == 1])
        avg_placement = pro_df['placement'].mean()
        should_have_won = len(pro_df[pro_df['should_have_placed'] == 1])
        
        # Season History
        seasons = []
        for _, row in pro_df.iterrows():
            seasons.append({
                'season': int(row['season']),
                'partner': row['celebrity_name'],
                'average_score': round(row['average_score'], 2),
                'placement': row['placement'], # Numeric
                'placement_text': row['results'], # "Eliminated Week X" or "3rd Place" etc.
                'should_have_placed': int(row['should_have_placed']) # Add this line
            })
            
        # Sort seasons by season number
        seasons.sort(key=lambda x: x['season'])
        
        results.append({
            'name': pro_name,
            'wins': wins,
            'average_placement': round(avg_placement, 2) if not pd.isna(avg_placement) else 0,
            'should_have_won': should_have_won,
            'seasons_count': len(pro_df),
            'seasons': seasons
        })
        
    return results


