#!/usr/bin/env python3
"""
Monte Carlo Investment Calculator - Production Runner

Production-ready runner script with proper configuration management,
logging, and error handling.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

# Configuration
class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'monte-carlo-investment-calculator-2024')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'monte_carlo.log')


def setup_logging():
    """Setup application logging."""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set werkzeug logging level
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'flask', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'pandas', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements-advanced.txt")
        return False
    
    return True


def print_startup_info():
    """Print application startup information."""
    print("🚀 Monte Carlo Investment Calculator")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: http://{Config.HOST}:{Config.PORT}")
    print(f"🐛 Debug mode: {'ON' if Config.DEBUG else 'OFF'}")
    print(f"📊 Log level: {Config.LOG_LEVEL}")
    print("=" * 50)
    print("📱 Open the URL in your browser to start using the calculator!")
    print("🛑 Press Ctrl+C to stop the server")
    print()


def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Configure Flask app
        app.config.from_object(Config)
        
        # Print startup information
        if not Config.DEBUG:
            print_startup_info()
        
        # Log startup
        logger.info(f"Starting Monte Carlo Calculator on {Config.HOST}:{Config.PORT}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        
        # Start the application
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Monte Carlo Calculator...")
        logger.info("Application shutdown by user")
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        logger.error(f"Application startup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()