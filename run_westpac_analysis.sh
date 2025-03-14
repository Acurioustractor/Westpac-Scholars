#!/bin/bash
# Westpac Scholars Analysis Pipeline
# This script runs the entire analysis pipeline from scraping to visualizing the data.

# Set up error handling
set -e
trap 'echo "An error occurred. Exiting..."; exit 1' ERR

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  Westpac Scholars Analysis Pipeline ${NC}"
echo -e "${GREEN}====================================${NC}"

# Create necessary directories if they don't exist
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p data scholar_photos frontend/public/data

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "\n${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# 1. Run the scholar scraper
echo -e "\n${YELLOW}Step 1: Running the Westpac Scholars scraper...${NC}"
python comprehensive_scraper.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Error running scholar scraper. Exiting.${NC}"
    exit 1
fi
echo -e "${GREEN}Scholar scraping completed.${NC}"

# 2. Run the photo downloader
echo -e "\n${YELLOW}Step 2: Downloading scholar photos...${NC}"
python download_photos.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Photo downloading completed with errors. Continuing anyway.${NC}"
else
    echo -e "${GREEN}Photo downloading completed.${NC}"
fi

# 3. Copy data to frontend public directory
echo -e "\n${YELLOW}Step 3: Copying data to frontend...${NC}"
cp data/all_westpac_scholars.csv frontend/public/data/
cp -r scholar_photos frontend/public/
echo -e "${GREEN}Data copying completed.${NC}"

# 4. Install frontend dependencies if needed
echo -e "\n${YELLOW}Step 4: Setting up frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing frontend dependencies. Exiting.${NC}"
        exit 1
    fi
fi

# 5. Start frontend development server
echo -e "\n${YELLOW}Step 5: Starting frontend development server...${NC}"
echo -e "${GREEN}All steps completed. Starting the application...${NC}"
npm start

# Script end
echo -e "\n${GREEN}Analysis pipeline completed.${NC}" 