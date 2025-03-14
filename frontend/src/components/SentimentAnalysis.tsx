import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  SelectChangeEvent,
  Slider,
  Chip
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell
} from 'recharts';

// Import Scholar interface from DataService
import { Scholar } from '../services/DataService';

interface SentimentAnalysisProps {
  scholars: Scholar[];
}

// Define sentiment ranges
const sentimentRanges = {
  veryPositive: { min: 0.6, max: 1.0, color: '#00af3f' },
  positive: { min: 0.2, max: 0.6, color: '#8bc34a' },
  neutral: { min: -0.2, max: 0.2, color: '#9e9e9e' },
  negative: { min: -0.6, max: -0.2, color: '#ff9800' },
  veryNegative: { min: -1.0, max: -0.6, color: '#d5002b' }
};

const SentimentAnalysis: React.FC<SentimentAnalysisProps> = ({ scholars }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [scholarshipFilter, setScholarshipFilter] = useState('All');
  const [sentimentRange, setSentimentRange] = useState<[number, number]>([-1, 1]);

  // Handle pagination
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle filters
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  const handleScholarshipChange = (event: SelectChangeEvent) => {
    setScholarshipFilter(event.target.value);
    setPage(0);
  };

  const handleSentimentRangeChange = (event: Event, newValue: number | number[]) => {
    setSentimentRange(newValue as [number, number]);
    setPage(0);
  };

  // Get unique scholarship types
  const scholarshipTypes = ['All', ...Array.from(new Set(scholars.map(scholar => scholar.scholarship_type).filter(Boolean)))];

  // Filter scholars based on search term, scholarship type, and sentiment range
  const filteredScholars = scholars.filter(scholar => {
    // Filter by search term
    const matchesSearch = !searchTerm || 
      (scholar.name && scholar.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (scholar.university && scholar.university.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (scholar.about && scholar.about.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Filter by scholarship type
    const matchesScholarship = scholarshipFilter === 'All' || 
      scholar.scholarship_type === scholarshipFilter;
    
    // Filter by sentiment range
    const sentiment = scholar.sentiment?.compound || 0;
    const matchesSentiment = sentiment >= sentimentRange[0] && sentiment <= sentimentRange[1];
    
    return matchesSearch && matchesScholarship && matchesSentiment;
  });

  // Sort by sentiment
  const sortedScholars = [...filteredScholars].sort((a, b) => 
    (b.sentiment?.compound || 0) - (a.sentiment?.compound || 0)
  );

  // Paginate
  const paginatedScholars = sortedScholars.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate sentiment distribution
  const sentimentDistribution = [
    { name: 'Very Positive', count: scholars.filter(s => (s.sentiment?.compound || 0) >= 0.6).length },
    { name: 'Positive', count: scholars.filter(s => (s.sentiment?.compound || 0) >= 0.2 && (s.sentiment?.compound || 0) < 0.6).length },
    { name: 'Neutral', count: scholars.filter(s => (s.sentiment?.compound || 0) > -0.2 && (s.sentiment?.compound || 0) < 0.2).length },
    { name: 'Negative', count: scholars.filter(s => (s.sentiment?.compound || 0) <= -0.2 && (s.sentiment?.compound || 0) > -0.6).length },
    { name: 'Very Negative', count: scholars.filter(s => (s.sentiment?.compound || 0) <= -0.6).length }
  ];

  // Create scatter plot data
  const scatterData = scholars.map(scholar => ({
    name: scholar.name,
    x: scholar.sentiment?.positive || 0,  // x-axis: positive sentiment
    y: scholar.sentiment?.negative || 0,  // y-axis: negative sentiment
    z: scholar.sentiment?.neutral || 0,   // z-axis (bubble size): neutral sentiment
    compound: scholar.sentiment?.compound || 0,
    scholarshipType: scholar.scholarship_type,
    university: scholar.university
  }));

  // Determine sentiment category and color for a compound score
  const getSentimentCategory = (compound: number): {category: string, color: string} => {
    if (compound >= sentimentRanges.veryPositive.min) return { category: 'Very Positive', color: sentimentRanges.veryPositive.color };
    if (compound >= sentimentRanges.positive.min) return { category: 'Positive', color: sentimentRanges.positive.color };
    if (compound >= sentimentRanges.neutral.min) return { category: 'Neutral', color: sentimentRanges.neutral.color };
    if (compound >= sentimentRanges.negative.min) return { category: 'Negative', color: sentimentRanges.negative.color };
    return { category: 'Very Negative', color: sentimentRanges.veryNegative.color };
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>Sentiment Analysis</Typography>
        <Typography variant="body1" paragraph>
          This analysis uses natural language processing to evaluate the sentiment in scholar bios and descriptions.
          Sentiment scores range from -1 (very negative) to 1 (very positive).
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Sentiment Distribution</Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={sentimentDistribution}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [value, 'Count']} />
                  <Legend />
                  <Bar dataKey="count" name="Scholars">
                    {sentimentDistribution.map((entry, index) => {
                      let color = sentimentRanges.neutral.color;
                      if (entry.name === 'Very Positive') color = sentimentRanges.veryPositive.color;
                      if (entry.name === 'Positive') color = sentimentRanges.positive.color;
                      if (entry.name === 'Negative') color = sentimentRanges.negative.color;
                      if (entry.name === 'Very Negative') color = sentimentRanges.veryNegative.color;
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Positive vs Negative Sentiment</Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                >
                  <CartesianGrid />
                  <XAxis type="number" dataKey="x" name="Positive" domain={[0, 1]} />
                  <YAxis type="number" dataKey="y" name="Negative" domain={[0, 1]} />
                  <ZAxis type="number" dataKey="z" range={[50, 500]} name="Neutral" />
                  <Tooltip 
                    formatter={(value: number) => value.toFixed(2)}
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        const sentiment = getSentimentCategory(data.compound);
                        return (
                          <Paper sx={{ p: 1, bgcolor: 'rgba(255, 255, 255, 0.9)' }}>
                            <Typography variant="subtitle2">{data.name}</Typography>
                            <Typography variant="body2">{data.scholarshipType}</Typography>
                            <Typography variant="body2">{data.university}</Typography>
                            <Box sx={{ mt: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
                              <Typography variant="body2">Sentiment:</Typography>
                              <Chip 
                                label={sentiment.category}
                                size="small"
                                sx={{ bgcolor: sentiment.color, color: '#fff' }}
                              />
                            </Box>
                            <Typography variant="body2">
                              Positive: {data.x.toFixed(2)}, Negative: {data.y.toFixed(2)}
                            </Typography>
                          </Paper>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend />
                  <Scatter 
                    name="Scholars" 
                    data={scatterData} 
                    fill="#d5002b"
                    shape="circle"
                  >
                    {scatterData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={getSentimentCategory(entry.compound).color} 
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Scholar Sentiment Details</Typography>
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Search"
                  variant="outlined"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  placeholder="Search by name, institution..."
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Scholarship Type</InputLabel>
                  <Select
                    value={scholarshipFilter}
                    label="Scholarship Type"
                    onChange={handleScholarshipChange}
                  >
                    {scholarshipTypes.map((type, index) => (
                      <MenuItem key={index} value={type}>{type}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography gutterBottom>Sentiment Range</Typography>
                <Slider
                  value={sentimentRange}
                  onChange={handleSentimentRangeChange}
                  valueLabelDisplay="auto"
                  min={-1}
                  max={1}
                  step={0.1}
                  marks={[
                    { value: -1, label: '-1' },
                    { value: 0, label: '0' },
                    { value: 1, label: '1' }
                  ]}
                />
              </Grid>
            </Grid>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Scholarship Type</TableCell>
                    <TableCell>Institution</TableCell>
                    <TableCell>Year</TableCell>
                    <TableCell>Sentiment</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paginatedScholars.map((scholar, index) => {
                    const compound = scholar.sentiment?.compound || 0;
                    const sentiment = getSentimentCategory(compound);
                    
                    return (
                      <TableRow key={scholar.id || index}>
                        <TableCell>{scholar.name}</TableCell>
                        <TableCell>{scholar.scholarship_type}</TableCell>
                        <TableCell>{scholar.university}</TableCell>
                        <TableCell>{scholar.year}</TableCell>
                        <TableCell>
                          <Chip 
                            label={`${sentiment.category} (${compound.toFixed(2)})`}
                            size="small"
                            sx={{ bgcolor: sentiment.color, color: '#fff' }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip 
                              label={`+ ${(scholar.sentiment?.positive || 0).toFixed(2)}`} 
                              size="small" 
                              color="success"
                              variant="outlined"
                            />
                            <Chip 
                              label={`- ${(scholar.sentiment?.negative || 0).toFixed(2)}`} 
                              size="small" 
                              color="error"
                              variant="outlined"
                            />
                            <Chip 
                              label={`n ${(scholar.sentiment?.neutral || 0).toFixed(2)}`} 
                              size="small" 
                              color="default"
                              variant="outlined"
                            />
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={filteredScholars.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SentimentAnalysis; 