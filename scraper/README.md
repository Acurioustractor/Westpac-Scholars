# Westpac Scholars Scraper

This is a web scraper for the Westpac Scholars website that extracts information about scholars and performs data analysis.

## Features

- Scrapes scholar profiles from the Westpac Scholars website
- Extracts detailed information from individual scholar pages
- Performs sentiment analysis on scholar bios and descriptions
- Identifies themes and topics using Latent Dirichlet Allocation (LDA)
- Analyzes distributions of scholarship types, institutions, and years
- Exports data to CSV and JSON formats

## Requirements

- Python 3.8+
- Chrome browser (for Selenium WebDriver)

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Scraper

To run the scraper and extract data from the Westpac Scholars website:

```
python westpac_scholars_scraper.py
```

This will:
- Scrape scholar profiles from the website
- Save the data to `data/westpac_scholars.csv` and `data/westpac_scholars.json`

### Running the Analysis

To analyze the scraped data:

```
python analyze_data.py
```

This will:
- Perform sentiment analysis on scholar bios and descriptions
- Extract themes using topic modeling
- Analyze distributions of scholarship types, institutions, and years
- Save the analysis results to `analysis/analysis_results.json`

## Output

The scraper and analysis scripts generate the following output files:

- `data/westpac_scholars.csv`: CSV file containing scholar information
- `data/westpac_scholars.json`: JSON file containing scholar information
- `analysis/analysis_results.json`: JSON file containing analysis results

## Project Structure

```
scraper/
├── westpac_scholars_scraper.py  # Main scraper script
├── analyze_data.py              # Data analysis script
├── requirements.txt             # Python dependencies
├── data/                        # Directory for scraped data
│   ├── westpac_scholars.csv     # CSV output
│   └── westpac_scholars.json    # JSON output
└── analysis/                    # Directory for analysis results
    └── analysis_results.json    # Analysis output
```

## Notes

- The scraper uses Selenium with Chrome WebDriver to handle JavaScript-rendered content
- The analysis uses NLTK for sentiment analysis and scikit-learn for topic modeling
- The scraper may need adjustments if the website structure changes 