import pandas as pd

from backend.data_processing import load_and_process_data, get_contestant_data, get_contestant_names
from backend.dwts_analytics import get_analytics_summary


def test_score_ranking_excludes_missing_weeks_and_preserves_ties(tmp_path):
    path = tmp_path / 'contestants.csv'
    pd.DataFrame({
        'celebrity_name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'season': [1, 1, 1, 2, 1],
        'ballroom_partner': ['P1', 'P2', 'P3', 'P4', 'P5'],
        'placement': [1, 2, 3, 1, 4],
        'week1_avg_judge_score': [10, 8, 9, 10, 10],
        'week1_total_judge_score': [30, 24, 27, 30, 30],
        'week2_avg_judge_score': [10, 8, 8, 0, None],
        'week2_total_judge_score': [30, 24, 24, 0, None],
    }).to_csv(path, index=False)
    df = load_and_process_data(path)
    assert df['average_score'].tolist() == [10, 8, 8.5, 10, 10]
    assert df['should_have_placed'].tolist() == [1, 4, 3, 1, 1]
    assert get_contestant_data(df, 'David')[0]['dances'] == [
        {'week': 1, 'total_score': 30, 'judges_scores': []}
    ]


def test_name_search_is_literal_and_suggestions_are_unique():
    df = pd.DataFrame({'celebrity_name': ['A. Star', 'A. Star', 'Another Star']})
    assert get_contestant_names(df, '.') == ['A. Star']
    assert get_contestant_names(df, 'STAR') == ['A. Star', 'Another Star']
    assert get_contestant_names(df, '[') == []
    assert get_contestant_data(df, '[') is None


def test_analytics_does_not_mutate_shared_data():
    df = pd.DataFrame({
        'celebrity_name': ['Alice', 'Bob'], 'ballroom_partner': ['P1', 'P2'],
        'season': [1, 1], 'placement': [1, 2],
        'average_score': [8, 9], 'should_have_placed': [2, 1],
    })
    original = df.copy(deep=True)
    summary = get_analytics_summary(df)
    pd.testing.assert_frame_equal(df, original)
    assert summary['robbed'][0]['name'] == 'Bob'
    assert summary['season_stats'][0]['winner'] == 'Alice'
    assert summary['season_stats'][0]['top_star'] == 'Bob'
