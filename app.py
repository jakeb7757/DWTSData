from flask import Flask, render_template, jsonify, request
from flask_talisman import Talisman
from backend.data_processing import load_and_process_data, get_contestant_data, get_contestant_names, get_pros_data, get_pro_names, get_pro_details
import os

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = get_contestant_data(df, query)
    if results:
        return jsonify(results)
    else:
        return jsonify([])

@app.route('/api/names')
def names():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = get_contestant_names(df, query)
    return jsonify(results)

@app.route('/pros')
def pros():
    return render_template('pros.html')

@app.route('/api/pros')
def get_pros():
    results = get_pros_data(df)
    return jsonify(results)

@app.route('/api/pros/names')
def pro_names():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = get_pro_names(df, query)
    return jsonify(results)

@app.route('/api/pros/search')
def pro_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = get_pro_details(df, query)
    return jsonify(results)

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    # NEVER use debug=True in production
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

FLASK_ENV ='production'
