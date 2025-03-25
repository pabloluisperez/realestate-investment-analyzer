"""
Spider for scraping property data from fotocasa.es
"""

import scrapy
import json
import logging
import re
from datetime import datetime
from ..items import PropertyItem
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class FotocasaSpider(scrapy.Spider):
    name = "fotocasa"
    allowed_domains = ["fotocasa.es"]
    
    # Base URL for searches
    base_url = "https://www.fotocasa.es"
    
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
            sale_url = f"{self.base_url}/venta/viviendas/{city}/"
            yield scrapy.Request(url=sale_url, callback=self.parse_search_results, meta={'city': city, 'operation_type': 'sale'})
            
            # Also get rental listings
            rent_url = f"{self.base_url}/alquiler/viviendas/{city}/"
            yield scrapy.Request(url=rent_url, callback=self.parse_search_results, meta={'city': city, 'operation_type': 'rent'})
    
    def parse_search_results(self, response):
        """Parse the search results page and follow pagination and property links"""
        city = response.meta.get('city')
        operation_type = response.meta.get('operation_type')
        
        # Extract property links - Update selectors based on Fotocasa's structure
        property_links = response.css('a.re-CardPackPremium-info::attr(href), a.re-Card-link::attr(href)').getall()
        
        for link in property_links:
            full_url = urljoin(self.base_url, link)
            yield scrapy.Request(url=full_url, callback=self.parse_property_details,
                                meta={'city': city, 'operation_type': operation_type})
        
        # Follow pagination
        next_page = response.css('a.sui-LinkBasic[title="Siguiente"]::attr(href)').get()
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
            item['title'] = response.css('h1.re-DetailHeader-propertyTitle::text').get('').strip()
            descriptions = response.css('div.fc-DetailDescription p::text').getall()
            item['description'] = ' '.join(descriptions).strip()
            
            # Price
            price_text = response.css('span.re-DetailHeader-price::text').get('').strip()
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
            item['city'] = response.meta.get('city', location_data.get('city', ''))
            item['province'] = location_data.get('province', '')
            item['postal_code'] = location_data.get('postal_code', '')
            
            # Try to extract coordinates
            coords = self._extract_coordinates(response)
            if coords:
                item['latitude'] = coords[0]
                item['longitude'] = coords[1]
            
            return item
        except Exception as e:
            logger.error(f"Error parsing property {response.url}: {str(e)}")
            return None
    
    def _extract_property_id(self, url):
        """Extract the property ID from the URL"""
        match = re.search(r'/(\d+)/', url)
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
        type_text = response.css('ul.re-DetailFeaturesList li:contains("Tipo") span::text').get('')
        type_text = type_text.lower() if type_text else ''
        
        if 'piso' in type_text:
            return 'apartment'
        elif 'casa' in type_text or 'chalet' in type_text:
            return 'house'
        elif 'ático' in type_text:
            return 'penthouse'
        elif 'estudio' in type_text:
            return 'studio'
        else:
            # Try to get from breadcrumbs
            breadcrumbs = ' '.join(response.css('ol.breadcrumb li::text').getall()).lower()
            if 'pisos' in breadcrumbs:
                return 'apartment'
            elif 'casas' in breadcrumbs or 'chalets' in breadcrumbs:
                return 'house'
            else:
                return 'other'
    
    def _extract_size(self, response):
        """Extract the size in square meters"""
        # Try to find size in the features list
        size_text = response.css('ul.re-DetailFeaturesList li:contains("Superficie") span::text').get()
        if size_text:
            return self._extract_number(size_text)
        
        # Try alternate approach with basic features
        size_text = response.css('ul.re-DetailHeader-features li:contains("m²") span::text').get()
        if size_text:
            return self._extract_number(size_text)
            
        return None
    
    def _extract_rooms(self, response):
        """Extract the number of rooms"""
        # Try to find rooms in the features list
        rooms_text = response.css('ul.re-DetailFeaturesList li:contains("Habitaciones") span::text').get()
        if rooms_text:
            return self._extract_number(rooms_text)
        
        # Try alternate approach with basic features
        rooms_text = response.css('ul.re-DetailHeader-features li:contains("hab.") span::text').get()
        if rooms_text:
            return self._extract_number(rooms_text)
            
        return None
    
    def _extract_bathrooms(self, response):
        """Extract the number of bathrooms"""
        # Try to find bathrooms in the features list
        bath_text = response.css('ul.re-DetailFeaturesList li:contains("Baños") span::text').get()
        if bath_text:
            return self._extract_number(bath_text)
        
        # Try alternate approach with basic features
        bath_text = response.css('ul.re-DetailHeader-features li:contains("baño") span::text').get()
        if bath_text:
            return self._extract_number(bath_text)
            
        return None
    
    def _extract_floor(self, response):
        """Extract the floor number"""
        # Try to find floor in the features list
        floor_text = response.css('ul.re-DetailFeaturesList li:contains("Planta") span::text').get()
        if floor_text:
            floor_text = floor_text.lower()
            if 'bajo' in floor_text:
                return 0
            elif 'sótano' in floor_text:
                return -1
            elif 'entreplanta' in floor_text:
                return 0
            else:
                match = re.search(r'([0-9]+)', floor_text)
                if match:
                    return int(match.group(1))
        
        return None
    
    def _has_elevator(self, response):
        """Check if the property has an elevator"""
        # Look for elevator indicators in features or equipment section
        features = ' '.join(response.css('ul.re-DetailFeaturesList li span::text, ul.re-DetailCharacteristicsList li span::text').getall()).lower()
        return 'ascensor' in features
    
    def _get_condition(self, response):
        """Determine the condition of the property"""
        # Look for condition indicators in features or description
        features = ' '.join(response.css('ul.re-DetailFeaturesList li span::text, ul.re-DetailCharacteristicsList li span::text').getall()).lower()
        description = ' '.join(response.css('div.fc-DetailDescription p::text').getall()).lower()
        
        all_text = features + ' ' + description
        
        if 'nuevo' in all_text or 'a estrenar' in all_text:
            return 'new'
        elif 'buen estado' in all_text:
            return 'good'
        elif 'para reformar' in all_text or 'necesita reforma' in all_text:
            return 'needs_renovation'
        else:
            return 'unknown'
    
    def _extract_year_built(self, response):
        """Extract the year the property was built"""
        # Try to find year built in the features list
        year_text = response.css('ul.re-DetailFeaturesList li:contains("Año construcción") span::text').get()
        if year_text:
            match = re.search(r'(\d{4})', year_text)
            if match:
                return int(match.group(1))
        
        # Try to find in the description
        description = ' '.join(response.css('div.fc-DetailDescription p::text').getall())
        year_match = re.search(r'construido en (\d{4})', description.lower())
        if year_match:
            return int(year_match.group(1))
            
        return None
    
    def _extract_features(self, response):
        """Extract all features and amenities"""
        features = []
        
        # Get all features from feature lists
        feature_sections = response.css('ul.re-DetailFeaturesList, ul.re-DetailCharacteristicsList')
        for section in feature_sections:
            items = section.css('li span::text').getall()
            features.extend([item.strip() for item in items if item.strip()])
        
        return features
    
    def _extract_energy_cert(self, response):
        """Extract energy certification"""
        # Look for energy certificate indicators
        cert_text = response.css('ul.re-DetailFeaturesList li:contains("Certificado energético") span::text').get()
        if cert_text:
            match = re.search(r'([A-G])', cert_text.upper())
            if match:
                return match.group(1)
        
        # Try to find energy certificate in the images
        energy_img = response.css('img[alt*="Eficiencia"]::attr(alt)').get()
        if energy_img:
            match = re.search(r'([A-G])', energy_img.upper())
            if match:
                return match.group(1)
        
        return None
    
    def _extract_location(self, response):
        """Extract location details"""
        location_data = {}
        
        # Try to get location from breadcrumbs
        breadcrumbs = response.css('ol.breadcrumb li a::text').getall()
        if len(breadcrumbs) >= 2:
            location_data['province'] = breadcrumbs[0].strip()
            location_data['city'] = breadcrumbs[1].strip()
            
            if len(breadcrumbs) >= 3:
                location_data['district'] = breadcrumbs[2].strip()
            
            if len(breadcrumbs) >= 4:
                location_data['neighborhood'] = breadcrumbs[3].strip()
        
        # Try to get address from header
        address_text = response.css('h1.re-DetailHeader-propertyTitle + p::text').get()
        if address_text:
            location_data['address'] = address_text.strip()
            
            # Try to extract postal code
            postal_match = re.search(r'\b(\d{5})\b', address_text)
            if postal_match:
                location_data['postal_code'] = postal_match.group(1)
        
        return location_data
    
    def _extract_coordinates(self, response):
        """Extract latitude and longitude coordinates"""
        # Try to find coordinates in script tags
        scripts = response.css('script::text').getall()
        for script in scripts:
            # Look for latitude and longitude patterns
            lat_match = re.search(r'latitude\s*[:=]\s*[\'"]?([0-9.-]+)[\'"]?', script)
            lng_match = re.search(r'longitude\s*[:=]\s*[\'"]?([0-9.-]+)[\'"]?', script)
            
            if lat_match and lng_match:
                try:
                    lat = float(lat_match.group(1))
                    lng = float(lng_match.group(1))
                    return (lat, lng)
                except ValueError:
                    pass
            
            # Try to find in JSON-like data
            coords_match = re.search(r'"coordinates"\s*:\s*{[^}]*"latitude"\s*:\s*([0-9.-]+)[^}]*"longitude"\s*:\s*([0-9.-]+)', script)
            if coords_match:
                try:
                    lat = float(coords_match.group(1))
                    lng = float(coords_match.group(2))
                    return (lat, lng)
                except ValueError:
                    pass
                
            # Try Google Maps format
            maps_match = re.search(r'new\s+google\.maps\.LatLng\(([0-9.-]+),\s*([0-9.-]+)\)', script)
            if maps_match:
                try:
                    lat = float(maps_match.group(1))
                    lng = float(maps_match.group(2))
                    return (lat, lng)
                except ValueError:
                    pass
        
        return None
