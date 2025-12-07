#!/usr/bin/env python3
"""
Run the Flask backend server.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the app
from backend.main import app
import os

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting BIST Analyst API on port {port}")
    print(f"   Debug mode: {debug}")
    print(f"   CORS enabled for localhost:3000, localhost:3001")
    print(f"   Health check: http://localhost:{port}/api/health")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
