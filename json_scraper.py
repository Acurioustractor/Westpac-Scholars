#!/usr/bin/env python3
"""
Westpac Scholars JSON Scraper

This script fetches scholar information directly from the Westpac Scholars JSON API
and saves it to CSV and JSON files.
"""

import os
import csv
import json
import logging
import requests
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
SCHOLARS_JSON_URL = "https://scholars.westpac.com.au/content/dam/public/wsch/profile/Scholars_2025.json"
OUTPUT_DIR = "data"
SCHOLARS_CSV = os.path.join(OUTPUT_DIR, "westpac_scholars.csv")
SCHOLARS_JSON = os.path.join(OUTPUT_DIR, "westpac_scholars.json")
DEBUG_JSON = os.path.join(OUTPUT_DIR, "raw_response.json")

def fetch_scholar_data() -> List[Dict[str, Any]]:
    """
    Fetch scholar data directly from the JSON API.
    
    Returns:
        List of dictionaries containing scholar information
    """
    logger.info(f"Requesting scholar data from {SCHOLARS_JSON_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    response = requests.get(SCHOLARS_JSON_URL, headers=headers)
    response.raise_for_status()
    
    # Save raw response for debugging
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(DEBUG_JSON, 'w', encoding='utf-8') as f:
        f.write(response.text)
    logger.info(f"Saved raw JSON response to {DEBUG_JSON} for debugging")
    
    # Parse the JSON response
    data = response.json()
    
    # Print the structure of the JSON response
    logger.info(f"JSON response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
    if isinstance(data, dict) and 'data' in data:
        logger.info(f"data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Not a dictionary'}")
    
    if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict) and 'profiles' in data['data']:
        scholars = data['data']['profiles']
        logger.info(f"Found {len(scholars)} scholars in the JSON data")
        return scholars
    else:
        logger.warning("No scholar data found in the JSON response")
        return []

def process_scholar_data(scholars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process the raw scholar data to create a more structured format.
    
    Args:
        scholars: List of raw scholar data from the JSON API
        
    Returns:
        List of processed scholar dictionaries
    """
    processed_scholars = []
    
    for scholar in scholars:
        processed_scholar = {
            'id': scholar.get('uniqueId', ''),
            'name': scholar.get('fullName', ''),
            'scholarship_type': scholar.get('scholarshipCategory', ''),
            'year': scholar.get('scholarshipYear', ''),
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
            ]
        }
        
        # Process image URL
        image_id = scholar.get('image', '')
        if image_id:
            if image_id.startswith('/'):
                # Already a full path
                processed_scholar['image_url'] = f"{BASE_URL}{image_id}"
            else:
                # Just an ID, construct the URL
                processed_scholar['image_url'] = f"{BASE_URL}/content/dam/public/wsch/images/2025/wsch_scholarhs_{image_id}_480x480.jpg"
        
        processed_scholars.append(processed_scholar)
        logger.info(f"Processed scholar: {processed_scholar['name']}")
    
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
    logger.info("Starting Westpac Scholars JSON scraper")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # Fetch scholar data from the JSON API
        raw_scholars = fetch_scholar_data()
        
        if raw_scholars:
            # Process the raw scholar data
            processed_scholars = process_scholar_data(raw_scholars)
            
            # Save the processed data
            save_to_csv(processed_scholars, SCHOLARS_CSV)
            save_to_json(processed_scholars, SCHOLARS_JSON)
            logger.info(f"Successfully scraped {len(processed_scholars)} scholar profiles")
        else:
            logger.warning("No scholar data was scraped")
            
    except Exception as e:
        logger.error(f"Error in scraper: {e}", exc_info=True)
    
    logger.info("Scraper completed")

if __name__ == "__main__":
    main() 