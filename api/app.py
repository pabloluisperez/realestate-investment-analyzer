"""
Flask application for the Real Estate Investment Analysis API.
Provides endpoints for accessing property data and investment analysis.
"""

import os
import logging
from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from api.models import Property, InvestmentOpportunity
from api.services.property_service import PropertyService
from api.services.analysis_service import AnalysisService
from api.utils.db import get_db_connection

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Enable CORS for all routes
CORS(app)

# Initialize services
property_service = PropertyService()
analysis_service = AnalysisService()


@app.route('/')
def index():
    """Render the dashboard page"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/api/properties')
def get_properties():
    """Get properties with optional filtering"""
    try:
        # Parse query parameters
        city = request.args.get('city')
        neighborhood = request.args.get('neighborhood')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        property_type = request.args.get('property_type')
        operation_type = request.args.get('operation_type')
        min_size = request.args.get('min_size')
        max_size = request.args.get('max_size')
        min_rooms = request.args.get('min_rooms')
        
        # Convert numeric parameters
        if min_price:
            min_price = float(min_price)
        if max_price:
            max_price = float(max_price)
        if min_size:
            min_size = float(min_size)
        if max_size:
            max_size = float(max_size)
        if min_rooms:
            min_rooms = int(min_rooms)
        
        # Get properties from service
        properties = property_service.get_properties(
            city=city,
            neighborhood=neighborhood,
            min_price=min_price,
            max_price=max_price,
            property_type=property_type,
            operation_type=operation_type,
            min_size=min_size,
            max_size=max_size,
            min_rooms=min_rooms
        )
        
        return jsonify(properties)
    except Exception as e:
        logger.error(f"Error in get_properties: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/properties/<property_id>')
def get_property(property_id):
    """Get a specific property by ID"""
    try:
        source = request.args.get('source')
        property_data = property_service.get_property_by_id(property_id, source)
        
        if property_data:
            return jsonify(property_data)
        else:
            return jsonify({"error": "Property not found"}), 404
    except Exception as e:
        logger.error(f"Error in get_property: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/properties/map')
def get_properties_for_map():
    """Get properties with coordinates for map display"""
    try:
        # Parse query parameters
        city = request.args.get('city')
        neighborhood = request.args.get('neighborhood')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        property_type = request.args.get('property_type')
        operation_type = request.args.get('operation_type')
        
        # Convert numeric parameters
        if min_price:
            min_price = float(min_price)
        if max_price:
            max_price = float(max_price)
        
        # Only get properties with coordinates
        properties = property_service.get_properties_with_coordinates(
            city=city,
            neighborhood=neighborhood,
            min_price=min_price,
            max_price=max_price,
            property_type=property_type,
            operation_type=operation_type
        )
        
        return jsonify(properties)
    except Exception as e:
        logger.error(f"Error in get_properties_for_map: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cities')
def get_cities():
    """Get a list of all cities"""
    try:
        cities = property_service.get_cities()
        return jsonify(cities)
    except Exception as e:
        logger.error(f"Error in get_cities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/neighborhoods')
def get_neighborhoods():
    """Get neighborhoods for a city"""
    try:
        city = request.args.get('city')
        if not city:
            return jsonify({"error": "City parameter is required"}), 400
            
        neighborhoods = property_service.get_neighborhoods(city)
        return jsonify(neighborhoods)
    except Exception as e:
        logger.error(f"Error in get_neighborhoods: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/investment/opportunities')
def get_investment_opportunities():
    """Get investment opportunities based on analysis"""
    try:
        # Parse query parameters
        city = request.args.get('city')
        neighborhood = request.args.get('neighborhood')
        min_score = request.args.get('min_score')
        property_type = request.args.get('property_type')
        operation_type = request.args.get('operation_type')
        
        # Convert numeric parameters
        if min_score:
            min_score = float(min_score)
        else:
            min_score = 70  # Default to high score threshold
        
        # Get opportunities from service
        opportunities = analysis_service.get_investment_opportunities(
            city=city,
            neighborhood=neighborhood,
            min_score=min_score,
            property_type=property_type,
            operation_type=operation_type
        )
        
        return jsonify(opportunities)
    except Exception as e:
        logger.error(f"Error in get_investment_opportunities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/investment/analysis/<property_id>')
def get_property_analysis(property_id):
    """Get detailed investment analysis for a specific property"""
    try:
        source = request.args.get('source')
        analysis = analysis_service.analyze_property(property_id, source)
        
        if analysis:
            return jsonify(analysis)
        else:
            return jsonify({"error": "Property not found"}), 404
    except Exception as e:
        logger.error(f"Error in get_property_analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error="Server error"), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
