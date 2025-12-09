# Dancing With the Stars - Contestant Archive

A Flask-based web application for exploring and analyzing Dancing With the Stars (DWTS) contestant data across 32 seasons. Search for celebrities and professional dancers, view detailed performance statistics, and discover how contestants "should have placed" based purely on their judge scores.

## Features

### Celebrity Search
- Search for any DWTS contestant by name with autocomplete
- View detailed performance statistics including:
  - Average score across all weeks
  - Highest single-week score
  - Actual placement vs. "should have placed" (score-based ranking)
  - Week-by-week dance history with individual judge scores

### Professional Dancers Statistics
- Comprehensive stats for all DWTS pro dancers
- Track wins, average placements, and "should have won" metrics
- Season-by-season history showing:
  - Celebrity partners
  - Average scores per season
  - Actual results vs. score-based rankings

### Analytics Features
- Score-based ranking system that shows where contestants "should have placed" based on average judge scores
- Eliminates voting bias to reveal pure performance rankings
- Aggregated statistics across multiple seasons for pros

## Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Data Processing**: pandas, NumPy
- **Deployment**: Docker, Gunicorn (WSGI server)
- **Security**: Flask-Talisman (HTTPS enforcement, security headers)
- **Frontend**: Vanilla JavaScript, CSS3 with Google Fonts

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jakeb7757/DWTSData.git
   cd DWTSData