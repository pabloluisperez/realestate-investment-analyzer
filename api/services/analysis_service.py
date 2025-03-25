"""
Service for analyzing property data and identifying investment opportunities.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json

# Importaciones condicionales para evitar errores cuando las librerías no estén disponibles
try:
    from bson.json_util import dumps, loads
except ImportError:
    # Implementaciones simples como fallback 
    def dumps(obj):
        return json.dumps(str(obj))
    def loads(obj):
        try:
            return json.loads(obj)
        except:
            return obj

try:
    import numpy as np
except ImportError:
    pass

from api.utils.db import get_db_connection
from api.models import InvestmentOpportunity
from api.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for analyzing property data and identifying investment opportunities"""
    
    def __init__(self):
        """Initialize the analysis service"""
        self.db = get_db_connection()
        self.collection = self.db['properties']
        self.notification_service = NotificationService()
    
    def get_investment_opportunities(self, city=None, neighborhood=None, min_score=70,
                                    property_type=None, operation_type=None,
                                    limit=50, notify_bargains=False) -> List[Dict[str, Any]]:
        """
        Get investment opportunities based on analysis
        
        Args:
            city: Filter by city
            neighborhood: Filter by neighborhood
            min_score: Minimum investment score (0-100)
            property_type: Type of property (apartment, house, etc.)
            operation_type: Type of operation (sale, rent)
            limit: Maximum number of properties to return
            notify_bargains: Si se deben enviar notificaciones para los chollos encontrados
            
        Returns:
            List of investment opportunities
        """
        try:
            # Build query filter
            query_filter = {
                'investment_score': {'$exists': True, '$gte': min_score},
                'price': {'$exists': True, '$ne': None},
                'size': {'$exists': True, '$ne': None}
            }
            
            if city:
                query_filter['city'] = city
            
            if neighborhood:
                query_filter['neighborhood'] = neighborhood
            
            if property_type:
                query_filter['property_type'] = property_type
            
            if operation_type:
                query_filter['operation_type'] = operation_type
            
            # Query database
            try:
                cursor = self.collection.find(query_filter).sort('investment_score', -1).limit(limit)
                # Convert to list of dictionaries
                properties = loads(dumps(list(cursor)))
            except Exception as e:
                logger.warning(f"Error querying database: {str(e)}, returning empty list")
                properties = []
            
            # Enhance with additional analysis
            opportunities = []
            bargains = []
            
            for prop in properties:
                opportunity = self._create_opportunity(prop)
                opportunities.append(opportunity)
                
                # Separar los chollos para posibles notificaciones
                if opportunity.get('is_bargain'):
                    bargains.append(opportunity)
            
            # Si se solicita, notificar a los usuarios sobre los chollos
            if notify_bargains and bargains:
                # Procesamiento en segundo plano para no bloquear la respuesta
                asyncio.create_task(self._notify_bargains(bargains))
            
            return opportunities
        except Exception as e:
            logger.error(f"Error getting investment opportunities: {str(e)}")
            return []
    
    async def _notify_bargains(self, bargains: List[Dict[str, Any]]) -> None:
        """
        Notificar a los usuarios sobre chollos inmobiliarios
        
        Args:
            bargains: Lista de oportunidades de inversión consideradas chollos
        """
        try:
            for bargain in bargains:
                # Convertir el diccionario a la clase InvestmentOpportunity para el servicio de notificaciones
                opportunity = InvestmentOpportunity(
                    property_id=bargain.get('property_id', ''),
                    source=bargain.get('source', ''),
                    title=bargain.get('title', ''),
                    price=bargain.get('price', 0),
                    size=bargain.get('size', 0),
                    city=bargain.get('city', ''),
                    neighborhood=bargain.get('neighborhood'),
                    property_type=bargain.get('property_type'),
                    operation_type=bargain.get('operation_type'),
                    investment_score=bargain.get('investment_score', 0),
                    price_per_sqm=bargain.get('price_per_sqm'),
                    avg_area_price_per_sqm=bargain.get('avg_area_price_per_sqm'),
                    price_difference=bargain.get('price_difference'),
                    estimated_roi=bargain.get('estimated_roi'),
                    latitude=bargain.get('latitude'),
                    longitude=bargain.get('longitude'),
                    url=bargain.get('url'),
                    is_bargain=True
                )
                
                # Notificar a los usuarios que coinciden con esta oportunidad
                notify_count = await self.notification_service.notify_matching_users(opportunity)
                
                if notify_count > 0:
                    logger.info(f"Notificados {notify_count} usuarios sobre el chollo: {opportunity.title}")
        except Exception as e:
            logger.error(f"Error al notificar chollos: {str(e)}")
    
    def analyze_property(self, property_id: str, source: str) -> Optional[Dict[str, Any]]:
        """
        Perform detailed investment analysis on a specific property
        
        Args:
            property_id: The property ID
            source: The source website (e.g., 'idealista', 'fotocasa')
            
        Returns:
            Dictionary with analysis results or None if property not found
        """
        try:
            # Get the property
            property_data = self.collection.find_one({'id': property_id, 'source': source})
            
            if not property_data:
                return None
            
            # Convert MongoDB document to dictionary
            property_dict = loads(dumps(property_data))
            
            # Get comparison data for the area
            area_data = self._get_area_comparison_data(property_dict)
            
            # Calculate price insights
            price_insights = self._calculate_price_insights(property_dict, area_data)
            
            # Calculate investment metrics
            investment_metrics = self._calculate_investment_metrics(property_dict, area_data)
            
            # Get similar properties
            similar_properties = self._get_similar_properties(property_dict)
            
            # Prepare analysis result
            analysis = {
                'property': property_dict,
                'area_data': area_data,
                'price_insights': price_insights,
                'investment_metrics': investment_metrics,
                'similar_properties': similar_properties
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing property: {str(e)}")
            return None
    
    def _create_opportunity(self, property_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an investment opportunity object from a property dictionary
        
        Args:
            property_dict: Property dictionary
            
        Returns:
            Investment opportunity dictionary
        """
        try:
            # Basic property data
            opportunity = {
                'property_id': property_dict.get('id'),
                'source': property_dict.get('source'),
                'title': property_dict.get('title'),
                'price': property_dict.get('price'),
                'size': property_dict.get('size'),
                'city': property_dict.get('city'),
                'neighborhood': property_dict.get('neighborhood'),
                'property_type': property_dict.get('property_type'),
                'operation_type': property_dict.get('operation_type'),
                'investment_score': property_dict.get('investment_score'),
                'price_per_sqm': property_dict.get('price_per_sqm'),
                'latitude': property_dict.get('latitude'),
                'longitude': property_dict.get('longitude'),
                'url': property_dict.get('url')
            }
            
            # Get area average price per sqm
            avg_price_per_sqm = self._get_area_avg_price_per_sqm(
                city=opportunity['city'],
                neighborhood=opportunity['neighborhood'],
                property_type=opportunity['property_type'],
                operation_type=opportunity['operation_type']
            )
            
            opportunity['avg_area_price_per_sqm'] = avg_price_per_sqm
            
            # Calculate price difference from area average
            if opportunity['price_per_sqm'] and avg_price_per_sqm:
                price_diff = ((avg_price_per_sqm - opportunity['price_per_sqm']) / avg_price_per_sqm) * 100
                opportunity['price_difference'] = round(price_diff, 2)
                
                # Determinar si es un chollo (precio al menos 15% por debajo de la media del área)
                opportunity['is_bargain'] = price_diff >= 15.0 and opportunity['investment_score'] >= 70.0
            else:
                opportunity['is_bargain'] = False
            
            # Calculate estimated ROI (simple version)
            if opportunity['operation_type'] == 'sale' and opportunity['price'] and avg_price_per_sqm:
                # Estimate that price will eventually reach area average
                estimated_future_price = opportunity['size'] * avg_price_per_sqm
                
                # Adjust if property needs renovation (estimated at 500€/m²)
                renovation_cost = 0
                if opportunity.get('condition') == 'needs_renovation':
                    renovation_cost = opportunity['size'] * 500
                
                # Calculate ROI
                roi = ((estimated_future_price - opportunity['price'] - renovation_cost) / 
                       (opportunity['price'] + renovation_cost)) * 100
                opportunity['estimated_roi'] = round(roi, 2)
                
                # Un ROI alto también puede ser considerado un chollo
                if opportunity['estimated_roi'] >= 25.0 and opportunity['investment_score'] >= 75.0:
                    opportunity['is_bargain'] = True
            
            # Get count of comparable properties
            opportunity['comparable_count'] = len(property_dict.get('comparable_properties', []))
            
            return opportunity
        except Exception as e:
            logger.error(f"Error creating opportunity: {str(e)}")
            # Return basic opportunity with error flag
            return {
                'property_id': property_dict.get('id'),
                'source': property_dict.get('source'),
                'title': property_dict.get('title'),
                'price': property_dict.get('price'),
                'investment_score': property_dict.get('investment_score'),
                'error': str(e)
            }
    
    def _get_area_avg_price_per_sqm(self, city: str, neighborhood: Optional[str] = None,
                                  property_type: Optional[str] = None,
                                  operation_type: Optional[str] = None) -> Optional[float]:
        """
        Calculate the average price per square meter for an area
        
        Args:
            city: The city
            neighborhood: The neighborhood (optional)
            property_type: Type of property (optional)
            operation_type: Type of operation (optional)
            
        Returns:
            Average price per square meter or None if not enough data
        """
        try:
            # Build query filter
            query_filter = {
                'city': city,
                'price_per_sqm': {'$exists': True, '$ne': None}
            }
            
            if neighborhood:
                query_filter['neighborhood'] = neighborhood
            
            if property_type:
                query_filter['property_type'] = property_type
            
            if operation_type:
                query_filter['operation_type'] = operation_type
            
            # Query database
            pipeline = [
                {'$match': query_filter},
                {'$group': {
                    '_id': None,
                    'avg_price_per_sqm': {'$avg': '$price_per_sqm'},
                    'count': {'$sum': 1}
                }}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result and result[0]['count'] >= 5:  # Only use if we have enough data
                return round(result[0]['avg_price_per_sqm'], 2)
            elif result:  # Not enough data, try without neighborhood
                if neighborhood and property_type:
                    return self._get_area_avg_price_per_sqm(
                        city=city,
                        neighborhood=None,
                        property_type=property_type,
                        operation_type=operation_type
                    )
                elif property_type:
                    return self._get_area_avg_price_per_sqm(
                        city=city,
                        neighborhood=None,
                        property_type=None,
                        operation_type=operation_type
                    )
                else:
                    return None
            else:
                return None
        except Exception as e:
            logger.error(f"Error calculating area average price: {str(e)}")
            return None
    
    def _get_area_comparison_data(self, property_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comparison data for the area where the property is located
        
        Args:
            property_dict: Property dictionary
            
        Returns:
            Dictionary with area comparison data
        """
        try:
            city = property_dict.get('city')
            neighborhood = property_dict.get('neighborhood')
            property_type = property_dict.get('property_type')
            operation_type = property_dict.get('operation_type')
            
            # Build query filter for the area
            area_filter = {'city': city}
            if neighborhood:
                area_filter['neighborhood'] = neighborhood
            
            # Calculate average price per sqm in the area
            price_per_sqm_pipeline = [
                {'$match': {
                    **area_filter,
                    'price_per_sqm': {'$exists': True, '$ne': None},
                    'property_type': property_type,
                    'operation_type': operation_type
                }},
                {'$group': {
                    '_id': None,
                    'avg_price_per_sqm': {'$avg': '$price_per_sqm'},
                    'min_price_per_sqm': {'$min': '$price_per_sqm'},
                    'max_price_per_sqm': {'$max': '$price_per_sqm'},
                    'count': {'$sum': 1}
                }}
            ]
            
            price_result = list(self.collection.aggregate(price_per_sqm_pipeline))
            
            # Calculate average time on market
            time_pipeline = [
                {'$match': {
                    **area_filter,
                    'days_listed': {'$exists': True, '$ne': None},
                    'property_type': property_type,
                    'operation_type': operation_type
                }},
                {'$group': {
                    '_id': None,
                    'avg_days_listed': {'$avg': '$days_listed'},
                    'count': {'$sum': 1}
                }}
            ]
            
            time_result = list(self.collection.aggregate(time_pipeline))
            
            # Calculate property type distribution
            type_pipeline = [
                {'$match': {
                    **area_filter,
                    'property_type': {'$exists': True, '$ne': None},
                    'operation_type': operation_type
                }},
                {'$group': {
                    '_id': '$property_type',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            
            type_result = list(self.collection.aggregate(type_pipeline))
            
            # Prepare result
            area_data = {
                'city': city,
                'neighborhood': neighborhood,
                'property_count': self.collection.count_documents(area_filter),
                'price_per_sqm': price_result[0] if price_result else None,
                'time_on_market': time_result[0] if time_result else None,
                'property_types': type_result
            }
            
            return area_data
        except Exception as e:
            logger.error(f"Error getting area comparison data: {str(e)}")
            return {}
    
    def _calculate_price_insights(self, property_dict: Dict[str, Any], 
                                area_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate price insights for a property
        
        Args:
            property_dict: Property dictionary
            area_data: Area comparison data
            
        Returns:
            Dictionary with price insights
        """
        try:
            price_insights = {}
            
            # Get property data
            price = property_dict.get('price')
            size = property_dict.get('size')
            price_per_sqm = property_dict.get('price_per_sqm')
            
            # Get area data
            area_price_data = area_data.get('price_per_sqm', {})
            if area_price_data:
                avg_price_per_sqm = area_price_data.get('avg_price_per_sqm')
                min_price_per_sqm = area_price_data.get('min_price_per_sqm')
                max_price_per_sqm = area_price_data.get('max_price_per_sqm')
                
                if avg_price_per_sqm and price_per_sqm:
                    # Calculate price difference from area average
                    price_diff = ((avg_price_per_sqm - price_per_sqm) / avg_price_per_sqm) * 100
                    price_insights['price_difference'] = round(price_diff, 2)
                    price_insights['price_difference_label'] = (
                        'below average' if price_diff > 0 else 'above average'
                    )
                    
                    # Calculate where this property sits in the price range
                    price_range = max_price_per_sqm - min_price_per_sqm
                    if price_range > 0:
                        percentile = ((price_per_sqm - min_price_per_sqm) / price_range) * 100
                        price_insights['price_percentile'] = round(percentile, 2)
            
            # Calculate price history insights if available
            price_history = property_dict.get('price_history', [])
            if price_history and price:
                # Sort by date
                price_history.sort(key=lambda x: x.get('date', ''))
                
                # Calculate price changes
                initial_price = price_history[0].get('price') if price_history else price
                price_change = ((price - initial_price) / initial_price) * 100 if initial_price else 0
                price_insights['price_change'] = round(price_change, 2)
                
                # Calculate price change frequency
                if len(price_history) > 1:
                    price_insights['price_changes_count'] = len(price_history)
            
            return price_insights
        except Exception as e:
            logger.error(f"Error calculating price insights: {str(e)}")
            return {}
    
    def _calculate_investment_metrics(self, property_dict: Dict[str, Any],
                                     area_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate investment metrics for a property
        
        Args:
            property_dict: Property dictionary
            area_data: Area comparison data
            
        Returns:
            Dictionary with investment metrics
        """
        try:
            metrics = {}
            
            # Get property data
            price = property_dict.get('price')
            size = property_dict.get('size')
            price_per_sqm = property_dict.get('price_per_sqm')
            investment_score = property_dict.get('investment_score')
            operation_type = property_dict.get('operation_type')
            condition = property_dict.get('condition')
            
            # Basic metrics
            metrics['investment_score'] = investment_score
            
            # Get area data
            area_price_data = area_data.get('price_per_sqm', {})
            area_time_data = area_data.get('time_on_market', {})
            
            if area_price_data and price and size and operation_type == 'sale':
                avg_price_per_sqm = area_price_data.get('avg_price_per_sqm')
                
                # Calculate potential value after renovation
                if condition == 'needs_renovation':
                    renovation_cost_per_sqm = 500  # Estimated renovation cost per sqm
                    renovation_cost = size * renovation_cost_per_sqm
                    
                    # Estimate market value after renovation
                    market_value = size * avg_price_per_sqm
                    
                    # Calculate ROI for renovation
                    if market_value > (price + renovation_cost):
                        renovation_roi = ((market_value - price - renovation_cost) / 
                                         (price + renovation_cost)) * 100
                        metrics['renovation_roi'] = round(renovation_roi, 2)
                        metrics['renovation_cost'] = renovation_cost
                        metrics['estimated_market_value'] = market_value
                
                # Calculate general investment metrics
                if avg_price_per_sqm:
                    # Estimate market value based on area average
                    market_value = size * avg_price_per_sqm
                    
                    # Price to market value ratio (lower is better)
                    price_to_value = price / market_value if market_value > 0 else 1
                    metrics['price_to_value_ratio'] = round(price_to_value, 2)
                    
                    # Potential appreciation
                    if price < market_value:
                        potential_appreciation = ((market_value - price) / price) * 100
                        metrics['potential_appreciation'] = round(potential_appreciation, 2)
            
            # Rental yield calculation (if operation_type is sale)
            if operation_type == 'sale' and price and size:
                # Estimate monthly rental price based on city averages
                # This is a simplified calculation and should be refined with real data
                city = property_dict.get('city')
                property_type = property_dict.get('property_type')
                
                # Get average rental price per sqm in the same city
                rental_price_per_sqm = self._get_area_avg_price_per_sqm(
                    city=city,
                    property_type=property_type,
                    operation_type='rent'
                )
                
                if rental_price_per_sqm:
                    # Estimate monthly rental income
                    monthly_rent = size * rental_price_per_sqm
                    annual_rent = monthly_rent * 12
                    
                    # Calculate gross rental yield
                    rental_yield = (annual_rent / price) * 100
                    metrics['estimated_monthly_rent'] = round(monthly_rent, 2)
                    metrics['estimated_rental_yield'] = round(rental_yield, 2)
            
            # Liquidity metric based on average time on market
            if area_time_data:
                avg_days_listed = area_time_data.get('avg_days_listed')
                if avg_days_listed:
                    # Liquidity score (0-100, higher is more liquid)
                    liquidity_score = 100 * (1 - min(1, avg_days_listed / 180))
                    metrics['liquidity_score'] = round(liquidity_score, 2)
                    metrics['avg_days_on_market'] = round(avg_days_listed, 2)
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating investment metrics: {str(e)}")
            return {}
    
    def _get_similar_properties(self, property_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get similar properties to the given property
        
        Args:
            property_dict: Property dictionary
            
        Returns:
            List of similar properties
        """
        try:
            # Get property data
            city = property_dict.get('city')
            neighborhood = property_dict.get('neighborhood')
            property_type = property_dict.get('property_type')
            operation_type = property_dict.get('operation_type')
            size = property_dict.get('size')
            price = property_dict.get('price')
            property_id = property_dict.get('id')
            source = property_dict.get('source')
            
            if not city or not size or not price:
                return []
            
            # Define size and price ranges
            size_range = (size * 0.8, size * 1.2)
            price_range = (price * 0.8, price * 1.2)
            
            # Build query filter
            query_filter = {
                'city': city,
                'size': {'$gte': size_range[0], '$lte': size_range[1]},
                'price': {'$gte': price_range[0], '$lte': price_range[1]},
                'id': {'$ne': property_id},  # Exclude the current property
                'source': {'$ne': source},  # Different source
                'operation_type': operation_type
            }
            
            if neighborhood:
                query_filter['neighborhood'] = neighborhood
            
            if property_type:
                query_filter['property_type'] = property_type
            
            # Query database
            cursor = self.collection.find(query_filter, {
                'id': 1, 'source': 1, 'title': 1, 'price': 1, 'size': 1,
                'price_per_sqm': 1, 'url': 1, 'days_listed': 1,
                'neighborhood': 1, 'investment_score': 1
            }).limit(10)
            
            # Convert to list of dictionaries
            similar_properties = loads(dumps(list(cursor)))
            
            # Sort by similarity (using Euclidean distance of normalized price and size)
            if similar_properties:
                for prop in similar_properties:
                    # Calculate similarity score (0-100, higher is more similar)
                    size_diff = abs(prop.get('size', 0) - size) / size if size > 0 else 1
                    price_diff = abs(prop.get('price', 0) - price) / price if price > 0 else 1
                    
                    # Convert to similarity score (inverse of difference)
                    similarity = 100 * (1 - (size_diff * 0.5 + price_diff * 0.5))
                    prop['similarity_score'] = round(max(0, similarity), 2)
                
                # Sort by similarity score
                similar_properties.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            return similar_properties
        except Exception as e:
            logger.error(f"Error getting similar properties: {str(e)}")
            return []
