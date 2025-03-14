#!/usr/bin/env python3
"""
Comprehensive Westpac Scholars Scraper

This script fetches scholar information from all available years from the Westpac Scholars JSON API
and saves the combined data to CSV and JSON files.
"""

import os
import csv
import json
import logging
import requests
import time
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://scholars.westpac.com.au"
OUTPUT_DIR = "data"
ALL_SCHOLARS_CSV = os.path.join(OUTPUT_DIR, "all_westpac_scholars.csv")
ALL_SCHOLARS_JSON = os.path.join(OUTPUT_DIR, "all_westpac_scholars.json")
YEAR_SCHOLARS_FORMAT = os.path.join(OUTPUT_DIR, "westpac_scholars_{}.json")

# We'll try to scrape scholars from 2015 to present year
current_year = datetime.now().year
YEARS_TO_SCRAPE = list(range(2015, current_year + 1))
JSON_URL_FORMAT = "https://scholars.westpac.com.au/content/dam/public/wsch/profile/Scholars_{}.json"

def fetch_scholar_data_for_year(year: int) -> List[Dict[str, Any]]:
    """
    Fetch scholar data for a specific year from the JSON API.
    
    Args:
        year: The year to fetch data for
        
    Returns:
        List of dictionaries containing scholar information for that year
    """
    json_url = JSON_URL_FORMAT.format(year)
    logger.info(f"Requesting scholar data for year {year} from {json_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    try:
        response = requests.get(json_url, headers=headers)
        response.raise_for_status()
        
        # Save raw response for debugging
        debug_json = os.path.join(OUTPUT_DIR, f"raw_response_{year}.json")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(debug_json, 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info(f"Saved raw JSON response to {debug_json} for debugging")
        
        # Parse the JSON response
        data = response.json()
        
        # Try different possible structures for the JSON data
        scholars = []
        if isinstance(data, dict):
            # Check for 'data' field which might contain 'profiles' or 'scholars'
            if 'data' in data and isinstance(data['data'], dict):
                if 'profiles' in data['data']:
                    scholars = data['data']['profiles']
                elif 'scholars' in data['data']:
                    scholars = data['data']['scholars']
            # Check if scholars are directly in the root
            elif 'profiles' in data:
                scholars = data['profiles']
            elif 'scholars' in data:
                scholars = data['scholars']
        
        logger.info(f"Found {len(scholars)} scholars for year {year}")
        return scholars, year
    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch data for year {year}: {e}")
        return [], year

def process_scholar_data(scholars: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
    """
    Process the raw scholar data to create a more structured format.
    
    Args:
        scholars: List of raw scholar data from the JSON API
        year: The year the data was fetched from
        
    Returns:
        List of processed scholar dictionaries
    """
    processed_scholars = []
    
    for scholar in scholars:
        processed_scholar = {
            'id': scholar.get('uniqueId', ''),
            'name': scholar.get('fullName', ''),
            'scholarship_type': scholar.get('scholarshipCategory', ''),
            'year': scholar.get('scholarshipYear', '') or str(year),
            'university': scholar.get('university', ''),
            'state': scholar.get('state', ''),
            'focus_area': scholar.get('focusArea', ''),
            'quote': scholar.get('quote', ''),
            'about': scholar.get('aboutYou', ''),
            'linkedin_url': scholar.get('linkedInURL', ''),
            'passions': [
                scholar.get('passion1', ''),
                scholar.get('passion2', ''),
                scholar.get('passion3', ''),
                scholar.get('passion4', ''),
                scholar.get('passion5', '')
            ],
            'data_source_year': year  # Add the year we fetched this data from
        }
        
        # Process image URL
        image_id = scholar.get('image', '')
        if image_id:
            if image_id.startswith('/'):
                # Already a full path
                processed_scholar['image_url'] = f"{BASE_URL}{image_id}"
            else:
                # Just an ID, construct the URL - pattern might change across years
                processed_scholar['image_url'] = f"{BASE_URL}/content/dam/public/wsch/images/{year}/wsch_scholarhs_{image_id}_480x480.jpg"
        
        processed_scholars.append(processed_scholar)
        logger.info(f"Processed scholar: {processed_scholar['name']} ({processed_scholar['year']})")
    
    return processed_scholars

def save_to_csv(scholars: List[Dict[str, Any]], filename: str):
    """Save scholar data to a CSV file."""
    if not scholars:
        logger.warning("No scholar data to save to CSV")
        return
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Flatten the passions list
    flattened_scholars = []
    for scholar in scholars:
        flat_scholar = scholar.copy()
        passions = flat_scholar.pop('passions', [])
        for i, passion in enumerate(passions, 1):
            if passion:
                flat_scholar[f'passion_{i}'] = passion
        flattened_scholars.append(flat_scholar)
    
    # Get all possible keys
    all_keys = set()
    for scholar in flattened_scholars:
        all_keys.update(scholar.keys())
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flattened_scholars)
    
    logger.info(f"Saved {len(scholars)} scholar records to {filename}")

def save_to_json(scholars: List[Dict[str, Any]], filename: str):
    """Save scholar data to a JSON file."""
    if not scholars:
        logger.warning("No scholar data to save to JSON")
        return
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(scholars, jsonfile, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(scholars)} scholar records to {filename}")

def main():
    """Main function to run the scraper."""
    logger.info("Starting Comprehensive Westpac Scholars scraper")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_scholars = []
    
    try:
        # Fetch scholar data from all years
        for year in YEARS_TO_SCRAPE:
            raw_scholars, year_fetched = fetch_scholar_data_for_year(year)
            
            if raw_scholars:
                # Process the raw scholar data
                processed_scholars = process_scholar_data(raw_scholars, year_fetched)
                
                # Save the processed data for this year
                year_json = YEAR_SCHOLARS_FORMAT.format(year_fetched)
                save_to_json(processed_scholars, year_json)
                
                # Add to the combined list
                all_scholars.extend(processed_scholars)
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
        
        # Save the combined data
        if all_scholars:
            save_to_csv(all_scholars, ALL_SCHOLARS_CSV)
            save_to_json(all_scholars, ALL_SCHOLARS_JSON)
            logger.info(f"Successfully scraped a total of {len(all_scholars)} scholar profiles across all years")
        else:
            logger.warning("No scholar data was scraped from any year")
            
    except Exception as e:
        logger.error(f"Error in scraper: {e}", exc_info=True)
    
    logger.info("Scraper completed")

if __name__ == "__main__":
    main() 