#!/usr/bin/env python3
"""
Simple Westpac Scholars Web Scraper

This script scrapes scholar information from the Westpac Scholars website
using requests and BeautifulSoup, without Selenium.
"""

import os
import csv
import json
import logging
import requests
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup

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
BASE_URL = "https://scholars.westpac.com.au/scholars/"
SCHOLARS_PAGE = "https://scholars.westpac.com.au/scholars/our-scholars.html"
OUTPUT_DIR = "data"
SCHOLARS_CSV = os.path.join(OUTPUT_DIR, "westpac_scholars.csv")
SCHOLARS_JSON = os.path.join(OUTPUT_DIR, "westpac_scholars.json")
DEBUG_HTML = os.path.join(OUTPUT_DIR, "page_structure.html")

def scrape_scholar_profiles() -> List[Dict[str, Any]]:
    """
    Scrape scholar profiles from the Westpac Scholars website.
    
    Returns:
        List of dictionaries containing scholar information
    """
    logger.info(f"Requesting {SCHOLARS_PAGE}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    response = requests.get(SCHOLARS_PAGE, headers=headers)
    response.raise_for_status()
    
    # Save the HTML for debugging
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(DEBUG_HTML, 'w', encoding='utf-8') as f:
        f.write(response.text)
    logger.info(f"Saved HTML to {DEBUG_HTML} for debugging")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print some debug info about the page structure
    logger.info(f"Page title: {soup.title.text if soup.title else 'No title found'}")
    
    # Log all div elements with class attributes to help identify patterns
    class_patterns = {}
    for div in soup.find_all(['div', 'article', 'section']):
        if 'class' in div.attrs:
            class_name = ' '.join(div['class'])
            if class_name not in class_patterns:
                class_patterns[class_name] = 0
            class_patterns[class_name] += 1
    
    logger.info("Common class patterns found:")
    for class_name, count in sorted(class_patterns.items(), key=lambda x: x[1], reverse=True)[:20]:
        logger.info(f"  {class_name}: {count} occurrences")
    
    # Try various selectors based on the image
    selectors_to_try = [
        ".scholar-card", 
        ".profile-card", 
        "article", 
        ".card",
        ".scholar",
        ".profile",
        ".scholar-profile",
        ".scholar-item",
        ".profile-item",
        ".grid-item",
        ".col-md-3",  # Common Bootstrap grid class that might contain cards
        ".col-sm-6",
        ".col-lg-4"
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        logger.info(f"Selector '{selector}' found {len(elements)} elements")
    
    # Based on the image, look for scholar cards
    scholar_elements = soup.select(".scholar-card, .profile-card, article, .card")
    
    if not scholar_elements:
        # Try more generic selectors if specific ones don't work
        logger.info("No scholar elements found with specific selectors, trying more generic ones")
        scholar_elements = soup.select("article, .card, .profile, .scholar, div[class*='scholar'], div[class*='profile']")
    
    if not scholar_elements:
        # Try even more generic approach - look for divs containing images and headings
        logger.info("Still no elements found, trying to identify scholar cards by structure")
        potential_cards = []
        
        # Find all images that might be profile pictures
        for img in soup.find_all('img'):
            # Get the parent container that might be a card
            parent = img.find_parent(['div', 'article', 'section'])
            if parent and parent.find(['h1', 'h2', 'h3', 'h4', 'strong']):
                potential_cards.append(parent)
        
        scholar_elements = potential_cards
    
    logger.info(f"Found {len(scholar_elements)} scholar elements")
    
    scholars = []
    for element in scholar_elements:
        try:
            scholar = {}
            
            # Log the HTML of this element to help debug
            logger.info(f"Processing element: {element.name} with classes: {element.get('class', [])}")
            
            # Extract name (based on image, this is a prominent heading in each card)
            name_element = element.select_one("h2, h3, h4, .name, .title, strong")
            if name_element:
                scholar["name"] = name_element.text.strip()
                logger.info(f"Found name: {scholar['name']}")
            
            # Extract scholarship type (shown as "Social Change Fellowship" in the image)
            scholarship_element = element.select_one(".scholarship-type, .fellowship, .category, .type")
            if scholarship_element:
                scholar["scholarship_type"] = scholarship_element.text.strip()
            
            # Extract year (shown as "2025" in the image)
            year_element = element.select_one(".year, .cohort, .date")
            if year_element:
                scholar["year"] = year_element.text.strip()
            
            # Extract institution (shown as "N/A" in some cards in the image)
            institution_element = element.select_one(".institution, .university, .org")
            if institution_element:
                scholar["institution"] = institution_element.text.strip()
            
            # Extract state/location (shown as "Queensland", "New South Wales", etc. in the image)
            location_element = element.select_one(".state, .location, .region")
            if location_element:
                scholar["location"] = location_element.text.strip()
            
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
                    if img_src.startswith("/"):
                        img_src = f"https://scholars.westpac.com.au{img_src}"
                    else:
                        img_src = f"https://scholars.westpac.com.au/{img_src}"
                scholar["image_url"] = img_src
            
            # Extract LinkedIn URL (shown as LinkedIn icon in the image)
            linkedin_element = element.select_one("a[href*='linkedin.com']")
            if linkedin_element and linkedin_element.has_attr("href"):
                scholar["linkedin_url"] = linkedin_element["href"]
            
            # Extract profile URL (likely the "Explore more" link in the image)
            profile_link = element.select_one("a:not([href*='linkedin.com'])")
            if profile_link and profile_link.has_attr("href"):
                profile_url = profile_link["href"]
                # Make absolute URL if relative
                if not profile_url.startswith(("http://", "https://")):
                    if profile_url.startswith("/"):
                        profile_url = f"https://scholars.westpac.com.au{profile_url}"
                    else:
                        profile_url = f"https://scholars.westpac.com.au/{profile_url}"
                scholar["profile_url"] = profile_url
                
                # Try to get more details from the profile page
                try:
                    detailed_info = scrape_scholar_detail(profile_url)
                    scholar.update(detailed_info)
                except Exception as e:
                    logger.error(f"Error scraping profile details for {profile_url}: {e}")
            
            # Only add scholars with at least a name
            if scholar.get("name"):
                scholars.append(scholar)
                logger.info(f"Scraped scholar: {scholar.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error scraping scholar: {e}")
    
    return scholars

def scrape_scholar_detail(profile_url: str) -> Dict[str, Any]:
    """
    Scrape detailed information from a scholar's profile page.
    
    Args:
        profile_url: URL of the scholar's profile page
        
    Returns:
        Dictionary containing detailed scholar information
    """
    logger.info(f"Requesting profile: {profile_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    response = requests.get(profile_url, headers=headers)
    response.raise_for_status()
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    details = {}
    
    # Extract detailed information
    try:
        # Better quality profile image from the details page
        img_element = soup.select_one(".profile-image img, .scholar-image img, .avatar img, .hero img")
        if img_element and img_element.has_attr("src"):
            img_src = img_element["src"]
            # Make absolute URL if relative
            if not img_src.startswith(("http://", "https://")):
                if img_src.startswith("/"):
                    img_src = f"https://scholars.westpac.com.au{img_src}"
                else:
                    img_src = f"https://scholars.westpac.com.au/{img_src}"
            details["image_url_large"] = img_src
        
        # Research/project title
        title_element = soup.select_one(".project-title, .research-title, h1")
        if title_element:
            details["project_title"] = title_element.text.strip()
        
        # Full bio
        full_bio_element = soup.select_one(".full-bio, .biography, .description, .about")
        if full_bio_element:
            details["full_bio"] = full_bio_element.text.strip()
        
        # Research/project description
        description_element = soup.select_one(".project-description, .research-description, .project")
        if description_element:
            details["project_description"] = description_element.text.strip()
        
        # Areas of interest/expertise
        interests_element = soup.select_one(".interests, .expertise, .areas, .focus-area")
        if interests_element:
            details["interests"] = interests_element.text.strip()
        
        # Social media links
        social_links = {}
        social_elements = soup.select("a[href*='linkedin.com'], a[href*='twitter.com'], a[href*='instagram.com']")
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
    
    try:
        scholars = scrape_scholar_profiles()
        
        if scholars:
            save_to_csv(scholars, SCHOLARS_CSV)
            save_to_json(scholars, SCHOLARS_JSON)
            logger.info(f"Successfully scraped {len(scholars)} scholar profiles")
        else:
            logger.warning("No scholar data was scraped")
            
    except Exception as e:
        logger.error(f"Error in scraper: {e}", exc_info=True)
    
    logger.info("Scraper completed")

if __name__ == "__main__":
    main() 