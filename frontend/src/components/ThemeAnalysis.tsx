import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

// Import interfaces from DataService
import { Scholar, Theme } from '../services/DataService';

interface ThemeAnalysisProps {
  themes: Theme[];
  scholars: Scholar[];
}

const COLORS = ['#d5002b', '#2b0a3d', '#1f1f1f', '#6d6e71', '#87005b', '#1e22aa', '#ff585d', '#ffca05', '#0078cb', '#ff8200', '#00af3f'];

const ThemeAnalysis: React.FC<ThemeAnalysisProps> = ({ themes, scholars }) => {
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const handleThemeClick = (theme: Theme) => {
    setSelectedTheme(theme);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  // Filter themes based on search term
  const filteredThemes = themes.filter(theme => 
    theme.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    theme.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Get scholars associated with the selected theme
  const getScholarsForTheme = (themeId: number) => {
    return scholars.filter(scholar => 
      scholar.themes?.some(theme => theme.theme_id === themeId)
    ).sort((a, b) => {
      const scoreA = a.themes?.find(t => t.theme_id === themeId)?.score || 0;
      const scoreB = b.themes?.find(t => t.theme_id === themeId)?.score || 0;
      return scoreB - scoreA; // Sort by score descending
    });
  };

  // Prepare data for pie chart
  const pieChartData = themes.map(theme => ({
    name: theme.name,
    value: theme.weight
  }));

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>Theme Analysis</Typography>
        <Typography variant="body1" paragraph>
          This analysis identifies common themes across scholar profiles using natural language processing.
          Click on a theme to see which scholars are associated with it.
        </Typography>
      </Box>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search themes or keywords"
          variant="outlined"
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Theme Distribution</Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`Weight: ${value.toFixed(2)}`, 'Theme Weight']} 
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%', overflowY: 'auto', maxHeight: 400 }}>
            <Typography variant="h6" gutterBottom>Theme Catalog</Typography>
            <Grid container spacing={1}>
              {filteredThemes.length > 0 ? filteredThemes.map((theme) => (
                <Grid item xs={12} sm={6} md={4} key={theme.id}>
                  <Card 
                    variant="outlined"
                    sx={{ 
                      bgcolor: selectedTheme?.id === theme.id ? 'rgba(213, 0, 43, 0.1)' : 'inherit',
                      border: selectedTheme?.id === theme.id ? '1px solid #d5002b' : undefined
                    }}
                  >
                    <CardActionArea onClick={() => handleThemeClick(theme)}>
                      <CardContent>
                        <Typography variant="h6" component="div" gutterBottom noWrap>
                          {theme.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Weight: {theme.weight.toFixed(2)}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {theme.keywords.slice(0, 3).map((keyword, index) => (
                            <Chip 
                              key={index} 
                              label={keyword} 
                              size="small" 
                              variant="outlined"
                            />
                          ))}
                          {theme.keywords.length > 3 && (
                            <Chip 
                              label={`+${theme.keywords.length - 3}`} 
                              size="small" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
              )) : (
                <Grid item xs={12}>
                  <Typography variant="body1">No themes match your search criteria.</Typography>
                </Grid>
              )}
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {selectedTheme ? `Scholars Associated with "${selectedTheme.name}" Theme` : 'Select a Theme to See Associated Scholars'}
            </Typography>
            
            {selectedTheme ? (
              <>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" paragraph>
                    The following scholars have a strong association with this theme. 
                    Scholars are ranked by the strength of their association with the theme.
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    <Typography variant="body2" fontWeight="bold">Keywords: </Typography>
                    {selectedTheme.keywords.map((keyword, index) => (
                      <Chip 
                        key={index} 
                        label={keyword} 
                        size="small" 
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
                
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Scholar</TableCell>
                        <TableCell>Scholarship Type</TableCell>
                        <TableCell>Year</TableCell>
                        <TableCell>Institution</TableCell>
                        <TableCell>Theme Score</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {getScholarsForTheme(selectedTheme.id).slice(0, 10).map((scholar) => (
                        <TableRow key={scholar.id}>
                          <TableCell>{scholar.name}</TableCell>
                          <TableCell>{scholar.scholarship_type}</TableCell>
                          <TableCell>{scholar.year}</TableCell>
                          <TableCell>{scholar.university}</TableCell>
                          <TableCell>
                            {(scholar.themes?.find(t => t.theme_id === selectedTheme.id)?.score || 0).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : (
              <Typography variant="body1">
                Click on a theme in the catalog to see associated scholars.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ThemeAnalysis; 