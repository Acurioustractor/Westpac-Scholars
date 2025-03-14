import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  CssBaseline, 
  ThemeProvider, 
  createTheme,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Paper,
  AppBar,
  Toolbar
} from '@mui/material';

// Import components
import ScholarsTable from './components/ScholarsTable';
import ThemeAnalysis from './components/ThemeAnalysis';
import SentimentAnalysis from './components/SentimentAnalysis';
import DistributionCharts from './components/DistributionCharts';

// Import data service
import { loadScholarData, AnalysisData } from './services/DataService';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#d5002b', // Westpac red
    },
    secondary: {
      main: '#000000', // Black
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Arial", "Helvetica", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [tabIndex, setTabIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const analysisData = await loadScholarData();
        setData(analysisData);
        setLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabIndex(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
              Westpac Scholars Analysis
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h4" gutterBottom>
              Westpac Scholars Dashboard
            </Typography>
            <Typography variant="body1" paragraph>
              This dashboard provides analysis of Westpac Scholars data, including sentiment analysis, 
              theme extraction, and distribution visualizations.
            </Typography>
          </Paper>

          <Paper sx={{ width: '100%' }}>
            <Tabs
              value={tabIndex}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
            >
              <Tab label="Scholars" />
              <Tab label="Themes" />
              <Tab label="Sentiment" />
              <Tab label="Distributions" />
            </Tabs>

            <Box sx={{ p: 3 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Typography color="error">{error}</Typography>
              ) : (
                <>
                  {tabIndex === 0 && data && <ScholarsTable scholars={data.scholars} />}
                  {tabIndex === 1 && data && <ThemeAnalysis themes={data.themes} scholars={data.scholars} />}
                  {tabIndex === 2 && data && <SentimentAnalysis scholars={data.scholars} />}
                  {tabIndex === 3 && data && (
                    <DistributionCharts 
                      scholarshipDistribution={data.scholarship_distribution}
                      institutionDistribution={data.institution_distribution}
                      yearDistribution={data.year_distribution}
                    />
                  )}
                </>
              )}
            </Box>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
