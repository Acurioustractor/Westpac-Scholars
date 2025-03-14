#!/usr/bin/env python3
"""
Westpac Scholars Web Scraper

This script scrapes scholar information from the Westpac Scholars website
and exports the data to a CSV file.
"""

import os
import time
import csv
import json
import logging
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

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
BASE_URL = "https://scholars.westpac.com.au/scholars/our-scholars.html"
OUTPUT_DIR = "data"
SCHOLARS_CSV = os.path.join(OUTPUT_DIR, "westpac_scholars.csv")
SCHOLARS_JSON = os.path.join(OUTPUT_DIR, "westpac_scholars.json")

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Try using the webdriver-manager with specific version and architecture
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.warning(f"Failed to use webdriver-manager: {e}")
        
        # Fallback to Safari WebDriver which is built into macOS
        logger.info("Falling back to Safari WebDriver")
        from selenium.webdriver.safari.service import Service as SafariService
        from selenium.webdriver.safari.options import Options as SafariOptions
        
        safari_options = SafariOptions()
        driver = webdriver.Safari(options=safari_options)
        return driver

def scrape_scholar_profiles(driver) -> List[Dict[str, Any]]:
    """
    Scrape scholar profiles from the Westpac Scholars website.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List of dictionaries containing scholar information
    """
    logger.info(f"Navigating to {BASE_URL}")
    driver.get(BASE_URL)
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".scholar-card, .scholar-profile, .scholar"))
    )
    
    # Get the page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all scholar cards/profiles
    scholar_elements = soup.select(".scholar-card, .scholar-profile, .scholar, .profile-card")
    
    scholars = []
    for element in scholar_elements:
        try:
            scholar = {}
            
            # Extract name
            name_element = element.select_one(".scholar-name, h2, h3, .name")
            if name_element:
                scholar["name"] = name_element.text.strip()
            
            # Extract scholarship type
            scholarship_element = element.select_one(".scholarship-type, .category, .scholar-type")
            if scholarship_element:
                scholar["scholarship_type"] = scholarship_element.text.strip()
            
            # Extract university/institution
            institution_element = element.select_one(".institution, .university")
            if institution_element:
                scholar["institution"] = institution_element.text.strip()
            
            # Extract year
            year_element = element.select_one(".year, .cohort")
            if year_element:
                scholar["year"] = year_element.text.strip()
            
            # Extract bio/description
            bio_element = element.select_one(".bio, .description, p")
            if bio_element:
                scholar["bio"] = bio_element.text.strip()
            
            # Extract image URL
            img_element = element.select_one("img")
            if img_element and img_element.has_attr("src"):
                img_src = img_element["src"]
                # Make absolute URL if relative
                if not img_src.startswith(("http://", "https://")):
                    img_src = f"https://scholars.westpac.com.au{img_src}"
                scholar["image_url"] = img_src
            
            # Extract profile URL if available
            profile_link = element.select_one("a")
            if profile_link and profile_link.has_attr("href"):
                scholar["profile_url"] = profile_link["href"]
                
                # If there's a profile URL, visit it to get more details
                if scholar.get("profile_url"):
                    detailed_info = scrape_scholar_detail(driver, scholar["profile_url"])
                    scholar.update(detailed_info)
            
            scholars.append(scholar)
            logger.info(f"Scraped scholar: {scholar.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error scraping scholar: {e}")
    
    return scholars

def scrape_scholar_detail(driver, profile_url: str) -> Dict[str, Any]:
    """
    Scrape detailed information from a scholar's profile page.
    
    Args:
        driver: Selenium WebDriver instance
        profile_url: URL of the scholar's profile page
        
    Returns:
        Dictionary containing detailed scholar information
    """
    # Check if the URL is absolute or relative
    if not profile_url.startswith("http"):
        profile_url = f"https://scholars.westpac.com.au{profile_url}"
    
    logger.info(f"Visiting profile: {profile_url}")
    driver.get(profile_url)
    
    # Wait for the page to load
    time.sleep(2)
    
    # Get the page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    details = {}
    
    # Extract detailed information
    try:
        # Better quality profile image from the details page
        img_element = soup.select_one(".profile-image img, .scholar-image img, .avatar img")
        if img_element and img_element.has_attr("src"):
            img_src = img_element["src"]
            # Make absolute URL if relative
            if not img_src.startswith(("http://", "https://")):
                img_src = f"https://scholars.westpac.com.au{img_src}"
            details["image_url_large"] = img_src
        
        # Research/project title
        title_element = soup.select_one(".project-title, .research-title, h1")
        if title_element:
            details["project_title"] = title_element.text.strip()
        
        # Full bio
        full_bio_element = soup.select_one(".full-bio, .biography, .description")
        if full_bio_element:
            details["full_bio"] = full_bio_element.text.strip()
        
        # Research/project description
        description_element = soup.select_one(".project-description, .research-description")
        if description_element:
            details["project_description"] = description_element.text.strip()
        
        # Areas of interest/expertise
        interests_element = soup.select_one(".interests, .expertise, .areas")
        if interests_element:
            details["interests"] = interests_element.text.strip()
        
        # Social media links
        social_links = {}
        social_elements = soup.select(".social-links a, .social-media a, .social a")
        for link in social_elements:
            href = link.get("href", "")
            if "linkedin.com" in href:
                social_links["linkedin"] = href
            elif "twitter.com" in href:
                social_links["twitter"] = href
            elif "instagram.com" in href:
                social_links["instagram"] = href
        
        if social_links:
            details["social_links"] = social_links
            
    except Exception as e:
        logger.error(f"Error scraping profile details: {e}")
    
    return details

def save_to_csv(scholars: List[Dict[str, Any]], filename: str):
    """Save scholar data to a CSV file."""
    if not scholars:
        logger.warning("No scholar data to save to CSV")
        return
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Flatten the social_links dictionary if it exists
    flattened_scholars = []
    for scholar in scholars:
        flat_scholar = scholar.copy()
        if "social_links" in flat_scholar:
            for platform, url in flat_scholar["social_links"].items():
                flat_scholar[f"social_{platform}"] = url
            del flat_scholar["social_links"]
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
    logger.info("Starting Westpac Scholars scraper")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    driver = None
    try:
        driver = setup_driver()
        scholars = scrape_scholar_profiles(driver)
        
        if scholars:
            save_to_csv(scholars, SCHOLARS_CSV)
            save_to_json(scholars, SCHOLARS_JSON)
            logger.info(f"Successfully scraped {len(scholars)} scholar profiles")
        else:
            logger.warning("No scholar data was scraped")
            
    except Exception as e:
        logger.error(f"Error in scraper: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")
    
    logger.info("Scraper completed")

if __name__ == "__main__":
    main() 