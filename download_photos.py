#!/usr/bin/env python3
"""
Download Westpac Scholar Profile Photos

This script downloads all scholar profile photos from the URLs in the CSV file.
It includes retry logic, alternative URL patterns, and robust error handling.
"""

import os
import csv
import requests
import pandas as pd
import time
import re
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("photo_download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = "data/all_westpac_scholars.csv"
OUTPUT_DIR = "scholar_photos"
MAX_WORKERS = 5  # Reduced number of simultaneous downloads to avoid overwhelming the server
MAX_RETRIES = 3  # Number of retries for failed downloads
RETRY_BACKOFF = 2  # Exponential backoff factor
TIMEOUT = 15  # Connection timeout in seconds
ALTERNATIVE_BASE_URLS = [
    "https://scholars.westpac.com.au",
    "https://www.westpac.com.au/about-westpac/sustainability/initiatives-for-you/westpac-scholars",
    "https://www.westpac.com.au/content/dam/public/wsch/images"
]

def ensure_output_dir(directory):
    """Ensure the output directory exists."""
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured output directory exists: {directory}")

def create_session():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def generate_alternative_urls(url, scholar_id, year):
    """Generate alternative URLs for the image based on different patterns."""
    if not url:
        return []
    
    alternatives = []
    
    # Original URL
    alternatives.append(url)
    
    # Try different base URLs
    for base_url in ALTERNATIVE_BASE_URLS:
        parsed = urlparse(url)
        path = parsed.path
        if path.startswith('/'):
            path = path[1:]
        alternatives.append(urljoin(base_url + '/', path))
    
    # Try different year patterns
    if year and scholar_id:
        for base_url in ALTERNATIVE_BASE_URLS:
            # Pattern 1: /year/wsch_scholarhs_id_480x480.jpg
            alternatives.append(f"{base_url}/{year}/wsch_scholarhs_{scholar_id}_480x480.jpg")
            # Pattern 2: /scholars_{year}/profile_{scholar_id}.jpg
            alternatives.append(f"{base_url}/scholars_{year}/profile_{scholar_id}.jpg")
            # Pattern 3: /scholars/profile_{year}_{scholar_id}.jpg
            alternatives.append(f"{base_url}/scholars/profile_{year}_{scholar_id}.jpg")
    
    return list(set(alternatives))  # Remove duplicates

def download_image(row):
    """Download an image from a URL with retry logic and alternative URLs."""
    url = row.get('image_url', '')
    scholar_id = row.get('id', '')
    name = row.get('name', 'unknown')
    year = row.get('year', '')
    
    if not url or not isinstance(url, str) or url.strip() == '':
        logger.warning(f"No image URL for scholar: {name}")
        return None
    
    # Create a filename from the scholar's ID and name
    name_clean = re.sub(r'[^\w\s-]', '', name).replace(' ', '_')
    file_extension = '.jpg'  # Default to jpg
    
    # Try to get extension from URL
    parsed_url = urlparse(url)
    path_ext = os.path.splitext(parsed_url.path)[1]
    if path_ext:
        file_extension = path_ext
    
    filename = f"{scholar_id}_{name_clean}{file_extension}"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Check if file already exists
    if os.path.exists(filepath):
        logger.info(f"Image already exists for {name}, skipping download")
        return filepath
    
    # Generate alternative URLs
    urls_to_try = generate_alternative_urls(url, scholar_id, year)
    
    # Create a session with retry logic
    session = create_session()
    
    # Try each URL
    for i, current_url in enumerate(urls_to_try):
        try:
            logger.info(f"Attempting to download image for {name} from {current_url} (attempt {i+1}/{len(urls_to_try)})")
            
            response = session.get(current_url, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Check if the response is actually an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL {current_url} returned non-image content type: {content_type}")
                continue
            
            # Save the image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded image for {name}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to download from {current_url} for {name}: {e}")
            # Continue to the next URL
    
    logger.error(f"All download attempts failed for {name}")
    return None

def create_airtable_csv(input_csv, image_map, output_csv):
    """Create a CSV file that includes local image paths for Airtable."""
    try:
        df = pd.read_csv(input_csv)
        
        # Add a column with local image paths
        df['local_image_path'] = df.apply(lambda row: image_map.get(row['id'], ''), axis=1)
        
        # Add a column indicating if the image was successfully downloaded
        df['image_downloaded'] = df['local_image_path'].apply(lambda x: 'Yes' if x else 'No')
        
        # Save to CSV
        df.to_csv(output_csv, index=False)
        logger.info(f"Created Airtable CSV: {output_csv}")
        
        # Generate some statistics
        total = len(df)
        downloaded = df['image_downloaded'].value_counts().get('Yes', 0)
        failed = df['image_downloaded'].value_counts().get('No', 0)
        
        logger.info(f"Download Statistics: Total: {total}, Downloaded: {downloaded}, Failed: {failed}")
        
    except Exception as e:
        logger.error(f"Error creating Airtable CSV: {e}")

def main():
    """Main function to run the photo downloader."""
    start_time = time.time()
    logger.info("Starting Westpac Scholar photo downloader")
    
    # Ensure output directory exists
    ensure_output_dir(OUTPUT_DIR)
    
    # Load scholar data
    try:
        df = pd.read_csv(INPUT_CSV)
        logger.info(f"Loaded {len(df)} scholar records from {INPUT_CSV}")
    except Exception as e:
        logger.error(f"Error loading data from {INPUT_CSV}: {e}")
        return
    
    # Download images in parallel with a smaller number of workers
    image_map = {}  # Map scholar IDs to local image paths
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_row = {executor.submit(download_image, row): row for _, row in df.iterrows()}
        
        for future in future_to_row:
            row = future_to_row[future]
            filepath = future.result()
            if filepath:
                image_map[row['id']] = filepath
    
    # Create Airtable CSV
    create_airtable_csv(INPUT_CSV, image_map, "westpac_scholars_airtable.csv")
    
    # Calculate and log execution time
    execution_time = time.time() - start_time
    logger.info(f"Photo downloader completed in {execution_time:.2f} seconds")
    logger.info(f"Downloaded {len(image_map)} images out of {len(df)} records")

if __name__ == "__main__":
    main() 