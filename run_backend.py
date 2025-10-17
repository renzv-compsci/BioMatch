"""
Main entry point for BioMatch backend server.
Run this file from the project root directory.
"""

import os
import sys

if __name__ == "__main__":
    # Ensure we're running from the project root
    if not os.path.exists(os.path.join(os.getcwd(), 'backend')):
        print("Error: Please run this script from the project root directory (BioMatch)")
        print("Current directory:", os.getcwd())
        sys.exit(1)
    
    # Import and run the Flask app
    from backend.app import app
    app.run(debug=True)
