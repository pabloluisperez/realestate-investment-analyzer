# Real Estate Investment Analysis System

This system consists of two main components:

1. **Python Web Scraper**: Extracts property data from Spanish real estate websites, stores it in MongoDB, tracks changes, and uses machine learning to identify investment opportunities.

2. **Java PrimeFaces Frontend**: Displays investment opportunities on interactive maps based on selected regions.

## Components

- **Scraper Module**: Python scrapers for real estate websites (idealista.com, fotocasa.es)
- **API Module**: Flask API for accessing property data and investment analysis
- **Frontend Module**: Java PrimeFaces web application

## Features

- Web scraping with anti-detection techniques
- Property listing tracking (new/modified)
- Investment opportunity analysis
- Interactive maps with property locations
- Filtering by city, neighborhood, price, etc.
