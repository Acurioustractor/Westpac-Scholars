#!/usr/bin/env python3
"""
Check Westpac Scholars Website Status

This script checks the status of the Westpac Scholars website and verifies the URLs
before attempting to download images. It helps diagnose connectivity issues and
identifies the correct URL patterns to use.
"""

import requests
import pandas as pd
import json
import logging
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_status.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = "data/all_westpac_scholars.csv"
MAX_WORKERS = 5
TIMEOUT = 15
MAX_RETRIES = 2

# URLs to check
URLS_TO_CHECK = [
    "https://scholars.westpac.com.au",
    "https://www.westpac.com.au/about-westpac/sustainability/initiatives-for-you/westpac-scholars",
    "https://www.westpac.com.au/content/dam/public/wsch/images",
    "https://www.westpac.com.au/about-westpac/westpac-scholars-trust",
    "https://www.westpac.com.au/about-westpac/our-foundations/westpac-scholars"
]

def create_session():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def check_url(url):
    """Check if a URL is accessible."""
    session = create_session()
    try:
        # First try a HEAD request (faster, doesn't download content)
        response = session.head(url, timeout=TIMEOUT)
        status_code = response.status_code
        content_type = response.headers.get('Content-Type', 'Unknown')
        
        # If HEAD request fails, try a GET request
        if status_code >= 400:
            response = session.get(url, timeout=TIMEOUT, stream=True)
            status_code = response.status_code
            content_type = response.headers.get('Content-Type', 'Unknown')
            # Don't download the full content
            response.close()
        
        return {
            'url': url,
            'status_code': status_code,
            'content_type': content_type,
            'accessible': 200 <= status_code < 400,
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': None,
            'content_type': None,
            'accessible': False,
            'error': str(e)
        }

def check_image_url(row):
    """Check if an image URL from the dataset is accessible."""
    url = row.get('image_url', '')
    scholar_id = row.get('id', '')
    name = row.get('name', 'Unknown')
    
    if not url or not isinstance(url, str) or url.strip() == '':
        return {
            'scholar_id': scholar_id,
            'name': name,
            'url': url,
            'accessible': False,
            'error': 'No URL provided'
        }
    
    result = check_url(url)
    return {
        'scholar_id': scholar_id,
        'name': name,
        'url': url,
        'accessible': result['accessible'],
        'status_code': result['status_code'],
        'content_type': result['content_type'],
        'error': result['error']
    }

def check_website_status():
    """Check the status of the Westpac Scholars website."""
    logger.info("Checking Westpac Scholars website status...")
    
    results = []
    for url in URLS_TO_CHECK:
        logger.info(f"Checking URL: {url}")
        result = check_url(url)
        results.append(result)
        
        if result['accessible']:
            logger.info(f"✅ URL {url} is accessible (Status: {result['status_code']}, Content-Type: {result['content_type']})")
        else:
            logger.warning(f"❌ URL {url} is NOT accessible: {result['error'] or f'Status: {result['status_code']}'}")
        
        # Add a small delay between requests
        time.sleep(1)
    
    return results

def check_image_urls_from_csv():
    """Check the image URLs from the CSV file."""
    try:
        df = pd.read_csv(INPUT_CSV)
        logger.info(f"Loaded {len(df)} scholar records from {INPUT_CSV}")
        
        # Take a sample of records to check (to avoid checking all records)
        sample_size = min(50, len(df))
        sample_df = df.sample(n=sample_size)
        
        logger.info(f"Checking {sample_size} sample image URLs...")
        
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_row = {executor.submit(check_image_url, row): row for _, row in sample_df.iterrows()}
            
            for future in future_to_row:
                result = future.result()
                results.append(result)
                
                if result['accessible']:
                    logger.info(f"✅ Image for {result['name']} is accessible")
                else:
                    logger.warning(f"❌ Image for {result['name']} is NOT accessible: {result['error'] or f'Status: {result.get('status_code')}'}")
        
        # Calculate statistics
        total = len(results)
        accessible = sum(1 for r in results if r['accessible'])
        not_accessible = total - accessible
        
        logger.info(f"Image URL Statistics: Total: {total}, Accessible: {accessible}, Not Accessible: {not_accessible}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error checking image URLs: {e}")
        return []

def suggest_fixes(website_results, image_results):
    """Suggest fixes based on the check results."""
    logger.info("Analyzing results and suggesting fixes...")
    
    suggestions = []
    
    # Check if the main website is accessible
    main_site_accessible = any(r['accessible'] for r in website_results if 'scholars.westpac.com.au' in r['url'])
    
    if not main_site_accessible:
        suggestions.append("The main Westpac Scholars website appears to be inaccessible. This could be due to:")
        suggestions.append("1. The website might have been moved or renamed")
        suggestions.append("2. There might be network connectivity issues")
        suggestions.append("3. The website might be temporarily down for maintenance")
        
        # Check if alternative URLs are accessible
        alternative_accessible = [r for r in website_results if r['accessible']]
        if alternative_accessible:
            suggestions.append("\nAlternative accessible URLs:")
            for r in alternative_accessible:
                suggestions.append(f"- {r['url']} (Status: {r['status_code']})")
            
            suggestions.append("\nRecommendations:")
            suggestions.append("1. Update the scraper to use the alternative URLs")
            suggestions.append("2. Modify the image URL patterns in the download_photos.py script")
        else:
            suggestions.append("\nNone of the alternative URLs are accessible. Recommendations:")
            suggestions.append("1. Check your network connection")
            suggestions.append("2. Try again later")
            suggestions.append("3. Contact Westpac to confirm the current website URLs")
    
    # Check image URL patterns
    if image_results:
        accessible_images = [r for r in image_results if r['accessible']]
        if accessible_images:
            suggestions.append("\nSome image URLs are accessible. Example patterns that work:")
            for r in accessible_images[:3]:  # Show up to 3 examples
                suggestions.append(f"- {r['url']}")
        
        # Analyze URL patterns
        url_patterns = {}
        for r in image_results:
            parsed = urlparse(r['url'])
            domain = parsed.netloc
            path_pattern = '/'.join(parsed.path.split('/')[:3])  # Get the first 3 path components
            
            key = f"{domain}{path_pattern}"
            if key not in url_patterns:
                url_patterns[key] = {'count': 0, 'accessible': 0, 'example': r['url']}
            
            url_patterns[key]['count'] += 1
            if r['accessible']:
                url_patterns[key]['accessible'] += 1
        
        suggestions.append("\nURL pattern analysis:")
        for pattern, stats in url_patterns.items():
            success_rate = stats['accessible'] / stats['count'] * 100 if stats['count'] > 0 else 0
            suggestions.append(f"- Pattern: {pattern}")
            suggestions.append(f"  Success rate: {success_rate:.1f}% ({stats['accessible']}/{stats['count']})")
            suggestions.append(f"  Example: {stats['example']}")
    
    return suggestions

def main():
    """Main function to run the website status checker."""
    start_time = time.time()
    logger.info("Starting Westpac Scholars website status checker")
    
    # Check website status
    website_results = check_website_status()
    
    # Check image URLs from CSV
    image_results = check_image_urls_from_csv()
    
    # Suggest fixes
    suggestions = suggest_fixes(website_results, image_results)
    
    # Save results to JSON
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'website_results': website_results,
        'image_results': image_results,
        'suggestions': suggestions
    }
    
    with open('website_status_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print suggestions
    logger.info("\n=== SUGGESTIONS ===")
    for suggestion in suggestions:
        logger.info(suggestion)
    
    # Calculate and log execution time
    execution_time = time.time() - start_time
    logger.info(f"Website status check completed in {execution_time:.2f} seconds")

if __name__ == "__main__":
    main() 