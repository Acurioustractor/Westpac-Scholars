import axios from 'axios';
import * as Papa from 'papaparse';

// Define interfaces for data types
export interface Scholar {
  id: string;
  name: string;
  scholarship_type: string;
  year: string;
  university: string;
  state: string;
  focus_area: string;
  quote: string;
  about: string;
  linkedin_url: string;
  image_url: string;
  local_image_path?: string;
  passion_1?: string;
  passion_2?: string;
  passion_3?: string;
  passion_4?: string;
  passion_5?: string;
  sentiment?: {
    compound: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  themes?: {
    theme_id: number;
    score: number;
  }[];
}

export interface Theme {
  id: number;
  name: string;
  keywords: string[];
  weight: number;
}

export interface Distribution {
  name: string;
  count: number;
}

export interface YearDistribution {
  year: string;
  count: number;
}

export interface AnalysisData {
  scholars: Scholar[];
  themes: Theme[];
  scholarship_distribution: Distribution[];
  institution_distribution: Distribution[];
  year_distribution: YearDistribution[];
}

// Function to load CSV data
const loadCSV = async (filePath: string): Promise<any[]> => {
  try {
    // Use process.env.PUBLIC_URL to ensure paths work on GitHub Pages
    const publicUrl = process.env.PUBLIC_URL || '';
    const response = await axios.get(`${publicUrl}${filePath}`);
    return new Promise((resolve, reject) => {
      Papa.parse(response.data, {
        header: true,
        complete: (results) => {
          resolve(results.data);
        },
        error: (error) => {
          reject(error);
        }
      });
    });
  } catch (error) {
    console.error(`Error loading CSV from ${filePath}:`, error);
    throw error;
  }
};

// Function to extract themes from scholar data
const extractThemes = (scholars: Scholar[]): Theme[] => {
  // This is a simplified theme extraction process
  // In a real application, you'd use more sophisticated NLP techniques
  
  const focusAreas = scholars
    .map(scholar => scholar.focus_area)
    .filter(area => area && area.trim() !== '')
    .reduce((acc: {[key: string]: number}, area) => {
      acc[area] = (acc[area] || 0) + 1;
      return acc;
    }, {});
  
  // Convert to themes
  return Object.entries(focusAreas)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)  // Take top 10 themes
    .map((entry, index) => ({
      id: index + 1,
      name: entry[0],
      keywords: entry[0].split(' '),
      weight: entry[1]
    }));
};

// Function to calculate distributions
const calculateDistributions = (scholars: Scholar[]): {
  scholarship_distribution: Distribution[];
  institution_distribution: Distribution[];
  year_distribution: YearDistribution[];
} => {
  // Calculate scholarship type distribution
  const scholarship_counts: { [key: string]: number } = {};
  scholars.forEach(scholar => {
    const type = scholar.scholarship_type || 'Unknown';
    scholarship_counts[type] = (scholarship_counts[type] || 0) + 1;
  });

  const scholarship_distribution = Object.entries(scholarship_counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  // Calculate institution distribution
  const institution_counts: { [key: string]: number } = {};
  scholars.forEach(scholar => {
    const institution = scholar.university || 'Unknown';
    institution_counts[institution] = (institution_counts[institution] || 0) + 1;
  });

  const institution_distribution = Object.entries(institution_counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);  // Take top 10 institutions

  // Calculate year distribution
  const year_counts: { [key: string]: number } = {};
  scholars.forEach(scholar => {
    const year = scholar.year || 'Unknown';
    year_counts[year] = (year_counts[year] || 0) + 1;
  });

  const year_distribution = Object.entries(year_counts)
    .map(([year, count]) => ({ year, count }))
    .sort((a, b) => a.year.localeCompare(b.year));

  return {
    scholarship_distribution,
    institution_distribution,
    year_distribution
  };
};

// Main function to load and process scholar data
export const loadScholarData = async (): Promise<AnalysisData> => {
  try {
    // In a production environment, these would be API calls
    // For this demo, we'll load the CSV file directly
    const scholars = await loadCSV('/data/all_westpac_scholars.csv') as Scholar[];
    
    // Extract themes from the scholar data
    const themes = extractThemes(scholars);
    
    // Calculate distributions
    const distributions = calculateDistributions(scholars);
    
    // Add mock sentiment analysis
    // In a real application, this would come from a backend API
    const scholarsWithSentiment = scholars.map(scholar => ({
      ...scholar,
      sentiment: {
        compound: Math.random() * 2 - 1, // Random value between -1 and 1
        positive: Math.random(),
        negative: Math.random() * 0.5,
        neutral: Math.random()
      },
      themes: themes
        .filter(() => Math.random() > 0.5) // Randomly associate themes
        .map(theme => ({
          theme_id: theme.id,
          score: Math.random()
        }))
    }));

    return {
      scholars: scholarsWithSentiment,
      themes,
      ...distributions
    };
  } catch (error) {
    console.error('Error loading scholar data:', error);
    throw error;
  }
}; 