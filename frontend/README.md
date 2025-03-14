# Westpac Scholars Dashboard

This is a React-based dashboard for visualizing and analyzing data from the Westpac Scholars website.

## Features

- Interactive data tables for exploring scholar information
- Theme analysis with visualization of extracted themes
- Sentiment analysis with charts and statistics
- Distribution visualizations for scholarship types, institutions, and years
- Responsive design for desktop and mobile viewing

## Technologies Used

- React with TypeScript
- Material UI for component styling
- Recharts for data visualization
- Axios for API requests

## Getting Started

### Prerequisites

- Node.js 14+ and npm

### Installation

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. Build for production:
   ```
   npm run build
   ```

## Project Structure

```
frontend/
├── public/                # Static files
├── src/                   # Source code
│   ├── components/        # React components
│   │   ├── ScholarsTable.tsx       # Table of scholars
│   │   ├── ThemeAnalysis.tsx       # Theme visualization
│   │   ├── SentimentAnalysis.tsx   # Sentiment analysis
│   │   └── DistributionCharts.tsx  # Distribution charts
│   ├── App.tsx            # Main application component
│   └── index.tsx          # Application entry point
└── package.json           # Project dependencies
```

## Usage

The dashboard is organized into tabs:

1. **Scholars**: Browse and search through the scholar data
2. **Themes**: Explore themes extracted from scholar descriptions
3. **Sentiment**: View sentiment analysis of scholar content
4. **Distributions**: Visualize distributions of scholarship types, institutions, and years

## Data Source

The dashboard displays data scraped from the Westpac Scholars website and processed by the analysis scripts in the `scraper` directory.

## Notes

- For development purposes, the application uses mock data
- In a production environment, you would connect to a backend API to fetch the real data
