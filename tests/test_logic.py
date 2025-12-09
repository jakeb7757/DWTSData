import sys
import os
import pandas as pd

# Add the parent directory to sys.path to import code.data_processing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_processing import load_and_process_data, get_contestant_data

def test_should_have_placed():
    print("Testing 'should have placed' logic...")
    
    # Create a dummy CSV for testing
    data = {
        'celebrity_name': ['Alice', 'Bob', 'Charlie', 'David'],
        'season': [1, 1, 1, 2],
        'ballroom_partner': ['P1', 'P2', 'P3', 'P4'],
        'placement': ['1st', '2nd', '3rd', '1st'],
        'week1_avg_judge_score': [10, 8, 9, 10],
        'week1_total_judge_score': [30, 24, 27, 30],
        'week2_avg_judge_score': [10, 8, 8, 0], # David didn't dance week 2
        'week2_total_judge_score': [30, 24, 24, 0]
    }
    
    test_csv_path = 'test_data.csv'
    pd.DataFrame(data).to_csv(test_csv_path, index=False)
    
    try:
        df = load_and_process_data(test_csv_path)
        
        # Season 1:
        # Alice: (10+10)/2 = 10.0
        # Bob: (8+8)/2 = 8.0
        # Charlie: (9+8)/2 = 8.5
        # Ranks (descending avg): Alice (1), Charlie (2), Bob (3)
        
        alice = get_contestant_data(df, 'Alice')[0]
        bob = get_contestant_data(df, 'Bob')[0]
        charlie = get_contestant_data(df, 'Charlie')[0]
        
        print(f"Alice: Avg={alice['average_score']}, Should={alice['should_have_placed']}")
        print(f"Bob: Avg={bob['average_score']}, Should={bob['should_have_placed']}")
        print(f"Charlie: Avg={charlie['average_score']}, Should={charlie['should_have_placed']}")
        
        assert alice['should_have_placed'] == 1
        assert charlie['should_have_placed'] == 2
        assert bob['should_have_placed'] == 3
        
        print("Season 1 logic passed!")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

if __name__ == "__main__":
    test_should_have_placed()
