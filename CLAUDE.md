# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sophisticated Monte Carlo investment calculator web application built with Flask and advanced scientific computing libraries. The application provides comprehensive financial modeling including accumulation phase planning, withdrawal phase analysis (Entsparphase), and full lifecycle investment strategy comparison.

## Key Commands

### Development & Running
```bash
# Quick start (recommended for development)
./start.sh

# Docker deployment (production-ready)
./init.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-advanced.txt
python run.py

# Access application at http://localhost:5000 (local) or http://localhost:5001 (Docker)
```

### Docker Commands
```bash
# Build and run with Docker Compose
docker-compose up --build -d

# View logs
docker-compose logs web

# Stop services
docker-compose down
```

## Architecture Overview

### Core Components

**Backend (Flask)**
- `app.py` - Main Flask application with API endpoints and 5 investment presets
- `advanced_calculator.py` - Monte Carlo calculation engine with parallel processing
- `run.py` - Production-ready application runner with logging and validation

**Frontend**
- `templates/index.html` - Single-page application with Russian localization
- `static/js/app.js` - ES6+ JavaScript application with real-time validation
- `static/css/style.css` - Custom responsive styling

### Calculation Modes

1. **Accumulation Phase** - Traditional investment growth with monthly deposits
2. **Withdrawal Phase (Entsparphase)** - Safe Withdrawal Rate analysis with sequence risk
3. **Mixed Lifecycle** - Combined accumulation and withdrawal analysis

### Investment Presets
- Conservative (4.5% avg, 7% vol), Moderate (7.5% avg, 15% vol)
- Aggressive (9.5% avg, 25% vol), Retirement (30yr), FIRE Strategy (15yr accumulation)

### API Endpoints

**Core Calculations**
- `POST /api/calculate` - Main calculation with mode detection
- `POST /api/calculate-advanced` - Advanced multi-mode calculations
- `GET /api/presets` - Investment strategy presets

**Visualization & Export**
- `GET /api/chart/<chart_type>` - Dynamic chart generation (histogram, boxplot, percentiles)
- `GET /api/export/<format>` - Data export (JSON, CSV)

**Advanced Features**
- `POST /api/compare` - Strategy comparison
- `POST /api/goal-planning` - Goal-based planning
- `POST /api/portfolio-rebalancing` - Rebalancing simulation

## Technical Details

### Monte Carlo Engine Features
- **Parallel processing** with joblib for performance
- **Beta distributions** for realistic market modeling
- **Autocorrelation modeling** (0.1 factor) for market trends
- **Inflation and tax modeling** (German Abgeltungssteuer system supported)
- **Risk metrics**: VaR, CVaR, downside deviation, sequence risk

### Parameter Ranges
- **Interest rates**: Support negative returns (-50% to +100%)
- **Monte Carlo iterations**: 1,000 to 50,000 (configurable)
- **Time horizons**: 1-50 years for both accumulation and withdrawal phases
- **Multiple currencies** (Euro-focused)

### Data Flow
1. Frontend validates parameters and sends to Flask API
2. Advanced calculator runs parallel Monte Carlo simulations
3. Results aggregated and statistical analysis performed
4. Charts generated server-side with Matplotlib/Seaborn
5. Data returned as JSON with base64-encoded images

## Development Notes

### Key Dependencies
- **Scientific computing**: NumPy, SciPy, Pandas for calculations
- **Visualization**: Matplotlib, Seaborn for server-side chart generation
- **Performance**: Joblib for parallel processing
- **Web framework**: Flask 2.3+ with modern Python 3.8+

### Parameter Validation
- Real-time frontend validation in JavaScript
- Backend validation with proper error messages in Russian
- Range constraints enforced for all financial parameters

### Localization
- Primary language: Russian (UI text, error messages, chart labels)
- Secondary support: German (tax system terminology)
- Easily extensible for additional languages

### Performance Considerations
- Simulations limited to 1000 results sent to frontend (full calculations cached)
- Parallel processing automatically scales to available CPU cores
- Server-side chart rendering reduces client computational load

### Special Features
- **Export functionality** for external analysis (JSON/CSV)
- **Preset system** with visual indicators and one-click application
- **Comparison tools** for side-by-side strategy analysis
- **Goal-based planning** with reverse calculation capabilities
- **Professional risk metrics** suitable for financial advisory use

## File Structure Notes

- **Templates**: Single main template (`index.html`) with progressive disclosure UI
- **Static assets**: Organized by type (js/, css/, images/ if added)
- **Configuration**: Environment-based with sensible defaults
- **Docker**: Production-ready with health checks and security practices

This is a production-grade financial application suitable for both personal finance planning and professional investment analysis.