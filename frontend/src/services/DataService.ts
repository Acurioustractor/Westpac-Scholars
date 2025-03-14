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
    const fullPath = `${publicUrl}${filePath}`;
    console.log(`Attempting to load CSV from: ${fullPath}`);
    
    let responseData: string;
    try {
      // First try with axios
      const response = await axios.get(fullPath);
      responseData = response.data;
    } catch (axiosError: any) {
      console.warn(`Axios failed to load CSV, trying fetch API instead:`, axiosError);
      
      // Try with plain fetch API as a fallback
      const response = await fetch(fullPath);
      if (!response.ok) {
        throw new Error(`Fetch failed with status: ${response.status}`);
      }
      responseData = await response.text();
    }
    
    console.log(`CSV data received, length: ${responseData.length} characters`);
    
    // Add extra check to make sure we got actual data
    if (!responseData || responseData.length < 100) {
      throw new Error(`Received invalid or too small CSV data: ${responseData}`);
    }
    
    return new Promise<any[]>((resolve, reject) => {
      Papa.parse(responseData, {
        header: true,
        skipEmptyLines: true,
        complete: (results: Papa.ParseResult<any>) => {
          console.log(`CSV parsing complete. Found ${results.data.length} rows.`);
          
          if (results.errors && results.errors.length > 0) {
            console.warn('CSV parsing completed with errors:', results.errors);
          }
          
          if (results.data.length === 0) {
            reject(new Error('CSV parsed successfully but contained no data rows'));
            return;
          }
          
          console.log(`First row sample:`, results.data[0]);
          resolve(results.data);
        },
        error: (error: any) => {
          console.error(`Error parsing CSV: ${error}`);
          reject(error);
        }
      });
    });
  } catch (error: any) {
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
    let scholars: Scholar[] = [];
    
    // Define data sources to try in order
    const publicUrl = process.env.PUBLIC_URL || '';
    const dataSources = [
      `${publicUrl}/data/all_westpac_scholars.csv`,
      `${publicUrl}/data/test_scholars.csv`
    ];
    
    let loadSuccess = false;
    let lastError: any = null;
    
    // Try each data source in order until one succeeds
    for (const dataPath of dataSources) {
      if (loadSuccess) break; // Skip if we already have data
      
      try {
        console.log(`Attempting to load data from: ${dataPath}`);
        
        const rawData = await loadCSV(dataPath);
        console.log(`Successfully loaded ${rawData.length} raw data records from ${dataPath}`);
        
        // Map the raw data to our Scholar interface
        const mappedScholars = rawData
          .filter((item: any) => item && (item.id || item.name)) // Ensure we have valid entries
          .map((item: any) => {
            const scholar: Scholar = {
              id: item.id || String(Math.random()).substring(2, 10), // Generate ID if missing
              name: item.name || 'Unknown Scholar',
              scholarship_type: item.scholarship_type || '',
              year: item.year || '',
              university: item.university || '',
              state: item.state || '',
              focus_area: item.focus_area || '',
              quote: item.quote || '',
              about: item.about || '',
              linkedin_url: item.linkedin_url || '',
              image_url: item.image_url || '/images/placeholder.jpg'
            };
            
            // Add optional fields if present
            if (item.passion_1) scholar.passion_1 = item.passion_1;
            if (item.passion_2) scholar.passion_2 = item.passion_2;
            if (item.passion_3) scholar.passion_3 = item.passion_3;
            if (item.passion_4) scholar.passion_4 = item.passion_4;
            if (item.passion_5) scholar.passion_5 = item.passion_5;
            
            return scholar;
          });
        
        console.log(`Mapped ${mappedScholars.length} scholars from ${dataPath}`);
        
        // If we have valid scholars after mapping, use them
        if (mappedScholars.length > 0) {
          scholars = mappedScholars;
          loadSuccess = true;
          console.log(`Successfully loaded data from ${dataPath}`);
        } else {
          console.warn(`Data source ${dataPath} returned 0 valid scholars after mapping`);
        }
      } catch (error: any) {
        console.warn(`Failed to load or parse data from ${dataPath}:`, error);
        lastError = error;
      }
    }
    
    // If all data sources failed, use fallback data
    if (!loadSuccess || scholars.length === 0) {
      console.warn('All data sources failed or returned no data, using fallback data:', lastError);
      scholars = [
        {
          id: '1',
          name: 'Jane Smith',
          scholarship_type: 'Future Leaders',
          year: '2023',
          university: 'University of Sydney',
          state: 'NSW',
          focus_area: 'Technology',
          quote: 'The future belongs to those who believe in the power of their dreams.',
          about: 'Jane is passionate about leveraging technology to solve social challenges.',
          linkedin_url: 'https://linkedin.com/in/janesmith',
          image_url: '/images/placeholder.jpg',
          passion_1: 'AI',
          passion_2: 'Healthcare',
          passion_3: 'Education'
        },
        {
          id: '2',
          name: 'John Doe',
          scholarship_type: 'Research Fellowship',
          year: '2022',
          university: 'University of Melbourne',
          state: 'VIC',
          focus_area: 'Climate Change',
          quote: 'Research is formalized curiosity. It is poking and prying with a purpose.',
          about: 'John focuses on sustainable agriculture methods that can withstand climate challenges.',
          linkedin_url: 'https://linkedin.com/in/johndoe',
          image_url: '/images/placeholder.jpg',
          passion_1: 'Sustainability',
          passion_2: 'Agriculture',
          passion_3: 'Research'
        },
        {
          id: '3',
          name: 'Emily Wong',
          scholarship_type: 'Social Innovation',
          year: '2021',
          university: 'UNSW',
          state: 'NSW',
          focus_area: 'Education',
          quote: 'Education is the most powerful weapon.',
          about: 'Emily works on improving access to education in underserved communities.',
          linkedin_url: 'https://linkedin.com/in/emilywong',
          image_url: '/images/placeholder.jpg',
          passion_1: 'Teaching',
          passion_2: 'Technology',
          passion_3: 'Policy'
        }
      ];
    }
    
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