"""
Flask application entry point with CORS and module blueprints.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

# Import blueprints
from backend.modules.screener.routes import screener_bp
from backend.modules.market_data.routes import market_data_bp

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",  # Main app (development)
                "http://localhost:3001",  # Screener app (development)
                os.getenv("FRONTEND_URL", "http://localhost:3000")
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(screener_bp)
    app.register_blueprint(market_data_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'bist-analyst-api',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information."""
        return jsonify({
            'message': 'BIST Analyst API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'screener': '/api/screener/*',
                'market_data': '/api/market-data/*'
            }
        }), 200
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting BIST Analyst API on port {port}")
    print(f"   Debug mode: {debug}")
    print(f"   CORS enabled for localhost:3000, localhost:3001")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
