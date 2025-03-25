"""
Flask application for the Real Estate Investment Analysis API.
Provides endpoints for accessing property data and investment analysis.
"""

import os
import logging
from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from api.models import Property, InvestmentOpportunity, UserPreference, TelegramConfig
from api.services.property_service import PropertyService
from api.services.analysis_service import AnalysisService
from api.services.notification_service import NotificationService
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
notification_service = NotificationService()


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
        notify_bargains = request.args.get('notify_bargains', 'false').lower() == 'true'
        
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
            operation_type=operation_type,
            notify_bargains=notify_bargains
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


@app.route('/api/user/preferences', methods=['GET', 'POST'])
def handle_user_preferences():
    """Get or update user preferences for notifications"""
    try:
        if request.method == 'GET':
            # Obtener preferencias del usuario
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({"error": "User ID is required"}), 400
                
            preference = notification_service.get_user_preference(user_id)
            if preference:
                # Convertir el objeto UserPreference a diccionario
                return jsonify({
                    "user_id": preference.user_id,
                    "cities": preference.cities,
                    "neighborhoods": preference.neighborhoods,
                    "min_price": preference.min_price,
                    "max_price": preference.max_price,
                    "min_size": preference.min_size,
                    "min_rooms": preference.min_rooms,
                    "property_types": preference.property_types,
                    "operation_type": preference.operation_type,
                    "min_investment_score": preference.min_investment_score,
                    "bargain_threshold": preference.bargain_threshold,
                    "telegram_chat_id": preference.telegram_chat_id,
                    "notify_bargains": preference.notify_bargains,
                    "notify_new_listings": preference.notify_new_listings,
                    "last_notification": preference.last_notification.isoformat() if preference.last_notification else None
                })
            else:
                return jsonify({"error": "User preferences not found"}), 404
        else:  # POST
            # Actualizar o crear preferencias del usuario
            data = request.json
            
            if not data or 'user_id' not in data:
                return jsonify({"error": "User ID is required"}), 400
                
            # Crear objeto de preferencias
            preference = UserPreference(
                user_id=data['user_id'],
                cities=data.get('cities', []),
                neighborhoods=data.get('neighborhoods', []),
                min_price=data.get('min_price'),
                max_price=data.get('max_price'),
                min_size=data.get('min_size'),
                min_rooms=data.get('min_rooms'),
                property_types=data.get('property_types', []),
                operation_type=data.get('operation_type', 'sale'),
                min_investment_score=data.get('min_investment_score', 70.0),
                bargain_threshold=data.get('bargain_threshold', 15.0),
                telegram_chat_id=data.get('telegram_chat_id'),
                notify_bargains=data.get('notify_bargains', True),
                notify_new_listings=data.get('notify_new_listings', False)
            )
            
            # Guardar preferencias
            success = notification_service.save_user_preference(preference)
            if success:
                return jsonify({"success": True, "message": "Preferences saved successfully"})
            else:
                return jsonify({"error": "Failed to save preferences"}), 500
            
    except Exception as e:
        logger.error(f"Error in handle_user_preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/telegram/config', methods=['GET', 'POST'])
def handle_telegram_config():
    """Get or update Telegram bot configuration"""
    try:
        if request.method == 'GET':
            # Obtener la configuración actual
            config = notification_service.telegram_config
            
            # No devolver el token del bot por seguridad
            return jsonify({
                "username": config.bot_username,
                "enabled": config.enabled,
                "webhook_url": config.webhook_url
            })
        else:  # POST
            # Solo administradores deben poder actualizar la configuración
            # Aquí se debería verificar la autenticación del administrador
            
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            # Actualizar configuración en la base de datos
            success = notification_service.db["config"].update_one(
                {"name": "telegram"},
                {"$set": {
                    "bot_token": data.get('bot_token', ''),
                    "bot_username": data.get('bot_username', ''),
                    "webhook_url": data.get('webhook_url'),
                    "enabled": data.get('enabled', False)
                }},
                upsert=True
            )
            
            if success:
                # Reiniciar el servicio de notificaciones para aplicar la nueva configuración
                notification_service._setup_telegram_bot()
                return jsonify({"success": True, "message": "Telegram configuration updated"})
            else:
                return jsonify({"error": "Failed to update Telegram configuration"}), 500
                
    except Exception as e:
        logger.error(f"Error in handle_telegram_config: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/investment/notify', methods=['POST'])
def notify_bargain():
    """Notificar manualmente sobre una oportunidad de inversión a los usuarios interesados"""
    try:
        data = request.json
        if not data or 'property_id' not in data or 'source' not in data:
            return jsonify({"error": "Property ID and source are required"}), 400
        
        # Obtener la propiedad de la base de datos
        property_data = property_service.get_property_by_id(data['property_id'], data['source'])
        if not property_data:
            return jsonify({"error": "Property not found"}), 404
        
        # Crear una oportunidad de inversión
        opportunity = AnalysisService()._create_opportunity(property_data)
        
        # Verificar si es un chollo antes de notificar
        if not opportunity.get('is_bargain', False) and not data.get('force_notify', False):
            return jsonify({"error": "Property is not considered a bargain. Use force_notify=true to override."}), 400
        
        # Convertir a objeto InvestmentOpportunity para el servicio de notificaciones
        investment_opportunity = InvestmentOpportunity(
            property_id=opportunity.get('property_id', ''),
            source=opportunity.get('source', ''),
            title=opportunity.get('title', ''),
            price=opportunity.get('price', 0),
            size=opportunity.get('size', 0),
            city=opportunity.get('city', ''),
            neighborhood=opportunity.get('neighborhood'),
            property_type=opportunity.get('property_type'),
            operation_type=opportunity.get('operation_type'),
            investment_score=opportunity.get('investment_score', 0),
            price_per_sqm=opportunity.get('price_per_sqm'),
            avg_area_price_per_sqm=opportunity.get('avg_area_price_per_sqm'),
            price_difference=opportunity.get('price_difference'),
            estimated_roi=opportunity.get('estimated_roi'),
            latitude=opportunity.get('latitude'),
            longitude=opportunity.get('longitude'),
            url=opportunity.get('url'),
            is_bargain=True  # Forzar como chollo para notificación manual
        )
        
        # Notificar a los usuarios de forma asíncrona
        import asyncio
        notify_count = asyncio.run(notification_service.notify_matching_users(investment_opportunity))
        
        return jsonify({
            "success": True,
            "notified_users": notify_count,
            "message": f"Notified {notify_count} users about this investment opportunity"
        })
    except Exception as e:
        logger.error(f"Error in notify_bargain: {str(e)}")
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
