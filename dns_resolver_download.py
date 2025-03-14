#!/usr/bin/env python3
"""
Download Westpac Scholar Photos using Alternative DNS Servers

This script attempts to download scholar profile photos using alternative DNS servers
to get around DNS resolution issues.
"""

import os
import pandas as pd
import logging
import time
import dns.resolver
import socket
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dns_download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = "data/all_westpac_scholars.csv"
OUTPUT_DIR = "scholar_photos_dns"
MAX_WORKERS = 5
TIMEOUT = 15

# Alternative DNS servers to try
DNS_SERVERS = [
    ('Google DNS', ['8.8.8.8', '8.8.4.4']),
    ('Cloudflare DNS', ['1.1.1.1', '1.0.0.1']),
    ('OpenDNS', ['208.67.222.222', '208.67.220.220']),
    ('Quad9', ['9.9.9.9', '149.112.112.112']),
    ('Default DNS', None)  # Use system default
]

def ensure_output_dir(directory):
    """Ensure the output directory exists."""
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured output directory exists: {directory}")

def resolve_domain_with_dns(domain, dns_servers=None):
    """
    Resolve a domain using the specified DNS servers.
    
    Args:
        domain: Domain name to resolve
        dns_servers: List of DNS server IP addresses to use
        
    Returns:
        IP address as a string, or None if resolution failed
    """
    if dns_servers:
        try:
            # Create a new resolver using the specified DNS servers
            resolver = dns.resolver.Resolver()
            resolver.nameservers = dns_servers
            
            # Resolve the domain
            answers = resolver.resolve(domain, 'A')
            if answers:
                return str(answers[0])
        except Exception as e:
            logger.warning(f"Failed to resolve {domain} with custom DNS servers: {e}")
            return None
    else:
        # Use the system's default resolver
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except socket.gaierror as e:
            logger.warning(f"Failed to resolve {domain} with default DNS: {e}")
            return None

def download_with_custom_dns(url, output_path, dns_name, dns_servers):
    """
    Download a file using custom DNS resolution.
    
    Args:
        url: URL to download
        output_path: Path to save the downloaded file
        dns_name: Name of the DNS service (for logging)
        dns_servers: List of DNS server IP addresses
        
    Returns:
        True if download was successful, False otherwise
    """
    try:
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Resolve the domain using the specified DNS servers
        ip_address = resolve_domain_with_dns(domain, dns_servers)
        
        if not ip_address:
            logger.warning(f"Could not resolve {domain} using {dns_name}")
            return False
        
        logger.info(f"Resolved {domain} to {ip_address} using {dns_name}")
        
        # Modify the URL to use the IP address directly
        # We keep the original hostname in the Host header
        ip_url = url.replace(domain, ip_address)
        headers = {'Host': domain}
        
        # Download the file
        response = requests.get(ip_url, headers=headers, timeout=TIMEOUT, stream=True)
        
        if response.status_code != 200:
            logger.warning(f"Failed to download {url} using {dns_name}: HTTP {response.status_code}")
            return False
        
        # Check if the response is an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"URL {url} returned non-image content type: {content_type}")
            return False
        
        # Save the file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Successfully downloaded {url} using {dns_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error downloading {url} using {dns_name}: {e}")
        return False

def process_scholar(row):
    """
    Process a scholar record by attempting to download their profile photo
    using various DNS servers.
    
    Args:
        row: DataFrame row containing scholar information
        
    Returns:
        Dictionary with download results
    """
    url = row.get('image_url', '')
    scholar_id = row.get('id', '')
    name = row.get('name', 'unknown')
    
    if not url or url.strip() == '':
        logger.warning(f"No image URL for scholar: {name}")
        return {
            'scholar_id': scholar_id,
            'name': name,
            'success': False,
            'successful_dns': None
        }
    
    # Create a filename from the scholar's ID and name
    name_clean = name.replace(' ', '_').replace('.', '').replace(',', '')
    filename = f"{scholar_id}_{name_clean}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Check if file already exists
    if os.path.exists(filepath):
        logger.info(f"Image already exists for {name}, skipping download")
        return {
            'scholar_id': scholar_id,
            'name': name,
            'success': True,
            'successful_dns': 'Already downloaded'
        }
    
    # Try each DNS server
    for dns_name, dns_servers in DNS_SERVERS:
        logger.info(f"Attempting to download image for {name} using {dns_name}")
        
        success = download_with_custom_dns(url, filepath, dns_name, dns_servers)
        
        if success:
            return {
                'scholar_id': scholar_id,
                'name': name,
                'success': True,
                'successful_dns': dns_name
            }
    
    logger.error(f"All download attempts failed for {name}")
    return {
        'scholar_id': scholar_id,
        'name': name,
        'success': False,
        'successful_dns': None
    }

def main():
    """Main function to run the DNS resolver photo downloader."""
    start_time = time.time()
    logger.info("Starting Westpac Scholar photo downloader with alternative DNS servers")
    
    # Ensure output directory exists
    ensure_output_dir(OUTPUT_DIR)
    
    # Load scholar data
    try:
        df = pd.read_csv(INPUT_CSV)
        logger.info(f"Loaded {len(df)} scholar records from {INPUT_CSV}")
    except Exception as e:
        logger.error(f"Error loading data from {INPUT_CSV}: {e}")
        return
    
    # Process scholars in parallel
    results = []
    successful_downloads = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_scholar, row) for _, row in df.iterrows()]
        
        for future in futures:
            result = future.result()
            results.append(result)
            
            if result['success']:
                successful_downloads += 1
    
    # Generate report
    dns_statistics = {}
    for dns_name, _ in DNS_SERVERS:
        dns_statistics[dns_name] = sum(1 for r in results if r['successful_dns'] == dns_name)
    
    logger.info("=== DNS Download Statistics ===")
    for dns_name, count in dns_statistics.items():
        if count > 0:
            logger.info(f"{dns_name}: {count} successful downloads")
    
    # Calculate and log execution time
    execution_time = time.time() - start_time
    logger.info(f"Photo downloader completed in {execution_time:.2f} seconds")
    logger.info(f"Downloaded {successful_downloads} images out of {len(df)} records")
    
    # Save results to CSV
    result_df = pd.DataFrame(results)
    result_df.to_csv("dns_download_results.csv", index=False)
    logger.info("Saved download results to dns_download_results.csv")

if __name__ == "__main__":
    main() 