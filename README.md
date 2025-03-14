# Westpac Scholars Analysis

This project collects, analyzes, and visualizes data from the Westpac Scholars program, providing insights into scholar demographics, institutional distribution, and thematic analysis.

## Project Overview

The Westpac Scholars Analysis project consists of two main components:
1. **Data Collection Pipeline**: Python scripts to scrape scholar information and photos from the Westpac Scholars website
2. **Data Visualization Frontend**: React application to visualize and explore the collected data

## Features

- **Comprehensive Data Collection**: Gathers detailed information about all Westpac Scholars
- **Scholar Photo Collection**: Downloads profile photos for all scholars where available
- **Interactive Data Explorer**: Browse, filter, and search scholars
- **Distribution Analysis**: Visualize scholar distribution by institution, scholarship type, and year
- **Theme Analysis**: Explore common themes and focus areas across scholars
- **Sentiment Analysis**: Analyze sentiment patterns in scholar descriptions

## Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd westpac-scholars
```

2. Set up the Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

### Running the Full Pipeline

You can run the entire pipeline using the provided shell script:

```bash
chmod +x run_westpac_analysis.sh
./run_westpac_analysis.sh
```

### Manual Execution

#### Data Collection

1. Run the comprehensive scraper:
```bash
python comprehensive_scraper.py
```

2. Download scholar photos:
```bash
python download_photos.py
```
   
   If you encounter DNS issues, try the alternative:
```bash
python dns_resolver_download.py
```

#### Frontend Visualization

1. Ensure data files are in the correct location:
```bash
mkdir -p frontend/public/data
cp data/all_westpac_scholars.csv frontend/public/data/
cp -r scholar_photos frontend/public/
```

2. Start the development server:
```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## Project Structure

```
westpac-scholars/
├── data/                       # Scraped data storage
├── scholar_photos/             # Downloaded scholar photos
├── comprehensive_scraper.py    # Main scraping script
├── download_photos.py          # Photo downloader
├── dns_resolver_download.py    # Alternative photo downloader with DNS resolution
├── run_westpac_analysis.sh     # Full pipeline script
├── requirements.txt            # Python dependencies
├── frontend/                   # React visualization application
│   ├── public/                 # Static assets
│   │   ├── data/               # Data files for the frontend
│   │   └── scholar_photos/     # Photos for display
│   ├── src/                    # Source code
│   │   ├── components/         # React components
│   │   ├── services/           # Data services
│   │   └── App.tsx             # Main application component
│   ├── package.json            # Node.js dependencies
│   └── tsconfig.json           # TypeScript configuration
└── README.md                   # Project documentation
```

## Data Analysis Components

The frontend includes several analysis components:

- **ScholarsTable**: Browse, filter, and search all scholars
- **DistributionCharts**: Visualize scholar distribution by various dimensions
- **ThemeAnalysis**: Explore common themes and focus areas
- **SentimentAnalysis**: Analyze sentiment patterns in scholar descriptions

## License

[MIT License]

## Acknowledgements

- Westpac Scholars program for providing the inspiration and data
- All the scholars whose achievements make this analysis meaningful 