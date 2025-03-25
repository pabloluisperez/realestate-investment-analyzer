"""
Main entry point for the Real Estate Investment Analysis API.
This file imports the Flask app from the api module.
"""

from api.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)