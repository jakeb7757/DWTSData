from contextlib import contextmanager

import pytest
from flask import template_rendered

from app import app, limiter, SEASONS


@pytest.fixture
def client():
    app.config['TESTING'] = True
    limiter.reset()
    with app.test_client() as client:
        yield client


@contextmanager
def rendered_context():
    contexts = []

    def record(sender, template, context, **extra):
        contexts.append(context)

    with template_rendered.connected_to(record, app):
        yield contexts


@pytest.mark.parametrize('path, expected', [
    ('/', 'Every star has'),
    ('/?q=Charli', 'Charli D'),
    ('/?q=not-a-real-contestant', 'No stars found'),
    ('/pros', 'The professionals'),
    ('/pros?q=Derek', 'Every partnership. Every season.'),
    ('/pros?q=not-a-real-pro', 'No professionals found'),
    ('/analytics', 'Great scores. Earlier exits.'),
    ('/analytics/robbed', 'Great scores. Earlier exits.'),
    ('/analytics/overachievers', 'Beyond the scores'),
    ('/analytics/hall_of_fame', 'The high-score club'),
    ('/analytics/seasons', 'Season rankings'),
    ('/analytics/unknown', 'Great scores. Earlier exits.'),
])
def test_pages_render_content_without_javascript(client, path, expected):
    response = client.get(path)
    assert response.status_code == 200
    assert expected in response.get_data(as_text=True)
    assert "script-src 'self'" in response.headers['Content-Security-Policy']


@pytest.mark.parametrize('sort, column, reverse', [
    ('placement', 'placement', False),
    ('score', 'average_score', True),
    ('name', 'celebrity_name', False),
])
def test_season_filter_and_sort(client, sort, column, reverse):
    with rendered_context() as contexts:
        assert client.get(f'/?season=1&sort={sort}').status_code == 200
    people = contexts[0]['contestants']
    assert len(people) == 6
    assert all(person['season'] == 1 for person in people)
    values = [person[column] for person in people]
    assert values == sorted(values, reverse=reverse)


def test_invalid_filters_fall_back_to_latest_season(client):
    with rendered_context() as contexts:
        assert client.get('/?season=999&sort=invalid').status_code == 200
    assert contexts[0]['selected_season'] == max(SEASONS)
    assert contexts[0]['sort'] == 'placement'


def test_search_escapes_html_and_handles_regex_characters(client):
    response = client.get('/', query_string={'q': '<script>alert(1)</script>'})
    assert response.status_code == 200
    assert '<script>alert(1)</script>' not in response.get_data(as_text=True)
    assert '&lt;script&gt;' in response.get_data(as_text=True)
    for endpoint in ['/api/names', '/api/search']:
        response = client.get(endpoint, query_string={'q': '['})
        assert response.status_code == 200
        assert response.json == []


def test_existing_api_contracts_remain_available(client):
    assert client.get('/api/search', query_string={'q': "Charli D'Amelio"}).json[0]['should_have_placed'] == 1
    assert 'seasons' in client.get('/api/pros/search?q=Derek').json[0]
    assert client.get('/api/pros').json
    assert len(client.get('/api/analytics').json['season_stats']) == len(SEASONS)
