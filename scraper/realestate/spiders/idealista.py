"""
Spider for scraping property data from idealista.com
"""

import scrapy
import json
import logging
import re
from datetime import datetime
from ..items import PropertyItem
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class IdealistaSpider(scrapy.Spider):
    name = "idealista"
    allowed_domains = ["idealista.com"]
    
    # Base URL for searches
    base_url = "https://www.idealista.com"
    
    # Cities to scrape (can be extended)
    cities = [
        "madrid",
        "barcelona",
        "valencia",
        "sevilla",
        "zaragoza",
        "malaga",
        "murcia",
        "palma-de-mallorca",
        "las-palmas-de-gran-canaria",
        "bilbao",
        "alicante",
    ]
    
    def start_requests(self):
        """Generate initial requests for each city"""
        for city in self.cities:
            # Start with for-sale listings
            sale_url = f"{self.base_url}/venta-viviendas/{city}/"
            yield scrapy.Request(url=sale_url, callback=self.parse_search_results, meta={'city': city, 'operation_type': 'sale'})
            
            # Also get rental listings
            rent_url = f"{self.base_url}/alquiler-viviendas/{city}/"
            yield scrapy.Request(url=rent_url, callback=self.parse_search_results, meta={'city': city, 'operation_type': 'rent'})
    
    def parse_search_results(self, response):
        """Parse the search results page and follow pagination and property links"""
        city = response.meta.get('city')
        operation_type = response.meta.get('operation_type')
        
        # Extract property links
        property_links = response.css('article.item a.item-link::attr(href)').getall()
        
        for link in property_links:
            full_url = urljoin(self.base_url, link)
            yield scrapy.Request(url=full_url, callback=self.parse_property_details,
                                meta={'city': city, 'operation_type': operation_type})
        
        # Follow pagination
        next_page = response.css('a.icon-arrow-right-after::attr(href)').get()
        if next_page:
            next_page_url = urljoin(self.base_url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse_search_results,
                               meta={'city': city, 'operation_type': operation_type})
    
    def parse_property_details(self, response):
        """Extract detailed information about a property listing"""
        try:
            item = PropertyItem()
            
            # Extract property ID from URL
            property_id = self._extract_property_id(response.url)
            item['id'] = property_id
            item['url'] = response.url
            item['source'] = self.name
            
            # Basic details
            item['title'] = response.css('h1.main-info__title::text').get('').strip()
            item['description'] = ' '.join(response.css('div.comment p::text').getall()).strip()
            
            # Price
            price_text = response.css('span.info-data-price::text').get('').strip()
            item['price'] = self._extract_number(price_text)
            
            # Property type
            item['property_type'] = self._get_property_type(response)
            item['operation_type'] = response.meta.get('operation_type')
            
            # Physical characteristics
            item['size'] = self._extract_size(response)
            item['rooms'] = self._extract_rooms(response)
            item['bathrooms'] = self._extract_bathrooms(response)
            item['floor'] = self._extract_floor(response)
            item['has_elevator'] = self._has_elevator(response)
            item['condition'] = self._get_condition(response)
            item['year_built'] = self._extract_year_built(response)
            
            # Features and amenities
            item['features'] = self._extract_features(response)
            item['energy_cert'] = self._extract_energy_cert(response)
            
            # Location data
            location_data = self._extract_location(response)
            item['address'] = location_data.get('address', '')
            item['neighborhood'] = location_data.get('neighborhood', '')
            item['district'] = location_data.get('district', '')
            item['city'] = response.meta.get('city', '')
            item['province'] = location_data.get('province', '')
            item['postal_code'] = location_data.get('postal_code', '')
            
            # Try to extract coordinates
            coords = self._extract_coordinates(response)
            if coords:
                item['latitude'] = coords[0]
                item['longitude'] = coords[1]
            
            # Metadata is handled by the pipeline
            
            return item
        except Exception as e:
            logger.error(f"Error parsing property {response.url}: {str(e)}")
            return None
    
    def _extract_property_id(self, url):
        """Extract the property ID from the URL"""
        match = re.search(r'/inmueble/(\d+)/', url)
        if match:
            return match.group(1)
        return None
    
    def _extract_number(self, text):
        """Extract a number from text, handling currency symbols and separators"""
        if not text:
            return None
        # Remove currency symbols, dots as thousand separators, and replace comma with dot for decimals
        clean_text = re.sub(r'[€\$£\.a-zA-Z\s]', '', text).replace(',', '.')
        try:
            return float(clean_text)
        except ValueError:
            return None
    
    def _get_property_type(self, response):
        """Determine the property type"""
        # Look for property type indicators in the breadcrumbs or detail sections
        breadcrumbs = ' '.join(response.css('ol.breadcrumb li::text').getall()).lower()
        detail_text = ' '.join(response.css('div.details-property li::text').getall()).lower()
        
        if 'piso' in breadcrumbs or 'piso' in detail_text:
            return 'apartment'
        elif 'casa' in breadcrumbs or 'casa' in detail_text or 'chalet' in breadcrumbs or 'chalet' in detail_text:
            return 'house'
        elif 'ático' in breadcrumbs or 'ático' in detail_text:
            return 'penthouse'
        elif 'estudio' in breadcrumbs or 'estudio' in detail_text:
            return 'studio'
        else:
            return 'other'
    
    def _extract_size(self, response):
        """Extract the size in square meters"""
        size_text = response.css('div.details-property-feature-one li span::text').get()
        if size_text:
            return self._extract_number(size_text)
        return None
    
    def _extract_rooms(self, response):
        """Extract the number of rooms"""
        rooms_text = response.css('div.details-property-feature-one li:nth-child(1) span::text').get()
        if rooms_text:
            return self._extract_number(rooms_text)
        return None
    
    def _extract_bathrooms(self, response):
        """Extract the number of bathrooms"""
        bath_text = response.css('div.details-property-feature-one li:nth-child(2) span::text').get()
        if bath_text:
            return self._extract_number(bath_text)
        return None
    
    def _extract_floor(self, response):
        """Extract the floor number"""
        floor_text = None
        # Check various selectors where floor info might be found
        detail_items = response.css('div.details-property li::text').getall()
        for item in detail_items:
            if 'planta' in item.lower():
                floor_text = item
                break
        
        if floor_text:
            # Extract floor number
            match = re.search(r'([0-9]+)[ºª]?\s*planta', floor_text.lower())
            if match:
                return int(match.group(1))
            
            # Check for specific floor types
            if 'bajo' in floor_text.lower():
                return 0
            elif 'sótano' in floor_text.lower():
                return -1
            elif 'entreplanta' in floor_text.lower():
                return 0
        
        return None
    
    def _has_elevator(self, response):
        """Check if the property has an elevator"""
        detail_items = ' '.join(response.css('div.details-property li::text').getall()).lower()
        return 'ascensor' in detail_items
    
    def _get_condition(self, response):
        """Determine the condition of the property"""
        detail_items = ' '.join(response.css('div.details-property li::text').getall()).lower()
        
        if 'nuevo' in detail_items or 'a estrenar' in detail_items:
            return 'new'
        elif 'buen estado' in detail_items:
            return 'good'
        elif 'para reformar' in detail_items or 'necesita reforma' in detail_items:
            return 'needs_renovation'
        else:
            return 'unknown'
    
    def _extract_year_built(self, response):
        """Extract the year the property was built"""
        detail_items = response.css('div.details-property li::text').getall()
        for item in detail_items:
            if 'año' in item.lower() and 'construc' in item.lower():
                match = re.search(r'(\d{4})', item)
                if match:
                    return int(match.group(1))
        return None
    
    def _extract_features(self, response):
        """Extract all features and amenities"""
        features = []
        # Check various sections for features
        feature_sections = response.css('div.details-property-feature, div.details-property')
        for section in feature_sections:
            items = section.css('li::text').getall()
            features.extend([item.strip() for item in items if item.strip()])
        
        return features
    
    def _extract_energy_cert(self, response):
        """Extract energy certification"""
        # Check for energy certificate information
        energy_text = None
        detail_items = response.css('div.details-property li::text').getall()
        for item in detail_items:
            if 'energética' in item.lower():
                energy_text = item
                break
        
        if energy_text:
            match = re.search(r'([A-G])', energy_text.upper())
            if match:
                return match.group(1)
        
        return None
    
    def _extract_location(self, response):
        """Extract location details"""
        location_data = {}
        
        # Try to extract location from breadcrumbs
        breadcrumbs = response.css('ol.breadcrumb li a::text').getall()
        if len(breadcrumbs) >= 3:
            location_data['province'] = breadcrumbs[1].strip()
            location_data['city'] = breadcrumbs[2].strip()
            
            if len(breadcrumbs) >= 4:
                location_data['district'] = breadcrumbs[3].strip()
            
            if len(breadcrumbs) >= 5:
                location_data['neighborhood'] = breadcrumbs[4].strip()
        
        # Try to extract address from title or description
        title = response.css('h1.main-info__title::text').get('').strip()
        description = ' '.join(response.css('div.comment p::text').getall()).strip()
        
        # Look for address patterns in the title
        address_match = re.search(r'en\s+([^,]+),\s*([^,]+)', title)
        if address_match:
            location_data['address'] = address_match.group(1).strip()
            if 'neighborhood' not in location_data:
                location_data['neighborhood'] = address_match.group(2).strip()
        
        # Look for postal code
        postal_match = re.search(r'\b(\d{5})\b', description)
        if postal_match:
            location_data['postal_code'] = postal_match.group(1)
        
        return location_data
    
    def _extract_coordinates(self, response):
        """Extract latitude and longitude coordinates"""
        # Try to find coordinates in script tags
        scripts = response.css('script::text').getall()
        for script in scripts:
            # Look for latitude and longitude patterns
            lat_match = re.search(r'latitude["\s:]+([0-9.-]+)', script)
            lng_match = re.search(r'longitude["\s:]+([0-9.-]+)', script)
            
            if lat_match and lng_match:
                try:
                    lat = float(lat_match.group(1))
                    lng = float(lng_match.group(1))
                    return (lat, lng)
                except ValueError:
                    pass
            
            # Try to find Google Maps coordinates
            maps_match = re.search(r'google.maps.LatLng\(([0-9.-]+),\s*([0-9.-]+)\)', script)
            if maps_match:
                try:
                    lat = float(maps_match.group(1))
                    lng = float(maps_match.group(2))
                    return (lat, lng)
                except ValueError:
                    pass
        
        return None
