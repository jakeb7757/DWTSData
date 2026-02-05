from flask import Flask, render_template, jsonify, request
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.data_processing import load_and_process_data, get_contestant_data, get_contestant_names, get_pros_data, get_pro_names, get_pro_details
from backend.dwts_analytics import get_analytics_summary
import os
import secrets

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Rate limiting to prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Define CSP to allow Google Fonts and local resources
csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'script-src': ["'self'"],
    'img-src': ["'self'", 'data:'],
    'connect-src': ["'self'"]
}

# Only enforce HTTPS in production
force_https = os.environ.get('FLASK_ENV') == 'production'
Talisman(app, content_security_policy=csp, force_https=force_https)

# Load data once at startup
DATA_PATH = os.path.join(os.path.dirname(__file__), 'dancing_with_the_stars_dataset.csv')
df = load_and_process_data(DATA_PATH)

@app.route('/')
def index():
    return render_template('index.html', active_page='stars')

@app.route('/pros')
def pros():
    return render_template('pros.html', active_page='pros')

@app.route('/analytics')
@app.route('/analytics/<category>')
def analytics(category='all'):
    valid_categories = ['robbed', 'overachievers', 'hall_of_fame', 'seasons']
    if category != 'all' and category not in valid_categories:
        # Fallback for invalid categories
        category = 'all'
    
    return render_template('analytics.html', category=category, active_page='analytics')

@app.route('/api/analytics')
def get_analytics():
    results = get_analytics_summary(df)
    return jsonify(results)

@app.route('/api/search')
@limiter.limit("30 per minute")
def search():
    query = request.args.get('q', '').strip()
    if not query or len(query) > 100:
        return jsonify([])
    
    results = get_contestant_data(df, query)
    if results:
        return jsonify(results)
    else:
        return jsonify([])

@app.route('/api/names')
@limiter.limit("60 per minute")
def names():
    query = request.args.get('q', '').strip()
    if not query or len(query) > 100:
        return jsonify([])
    
    results = get_contestant_names(df, query)
    return jsonify(results)

@app.route('/api/pros')
def get_pros():
    results = get_pros_data(df)
    return jsonify(results)

@app.route('/api/pros/names')
@limiter.limit("60 per minute")
def pro_names():
    query = request.args.get('q', '').strip()
    if not query or len(query) > 100:
        return jsonify([])
    
    results = get_pro_names(df, query)
    return jsonify(results)

@app.route('/api/pros/search')
@limiter.limit("30 per minute")
def pro_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) > 100:
        return jsonify([])
    
    results = get_pro_details(df, query)
    return jsonify(results)

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    # NEVER use debug=True in production
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
