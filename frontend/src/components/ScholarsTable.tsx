import React, { useState } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Typography,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Avatar
} from '@mui/material';

// Import the Scholar interface from DataService
import { Scholar } from '../services/DataService';

interface ScholarsTableProps {
  scholars: Scholar[];
}

type Order = 'asc' | 'desc';
type OrderBy = keyof Scholar | '';

const ScholarsTable: React.FC<ScholarsTableProps> = ({ scholars }) => {
  const [order, setOrder] = useState<Order>('asc');
  const [orderBy, setOrderBy] = useState<OrderBy>('name');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedScholar, setSelectedScholar] = useState<Scholar | null>(null);

  // Handle sorting
  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  // Handle pagination
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle search
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  // Handle scholar selection
  const handleScholarClick = (scholar: Scholar) => {
    setSelectedScholar(scholar);
  };

  const handleCloseDialog = () => {
    setSelectedScholar(null);
  };

  // Filter scholars based on search term
  const filteredScholars = scholars.filter((scholar) => {
    const searchFields = [
      scholar.name,
      scholar.scholarship_type,
      scholar.university, // Changed from institution to university
      scholar.year,
      scholar.about,     // Changed from bio to about
      scholar.focus_area // Added focus_area
    ].filter(Boolean);
    
    return searchFields.some(field => 
      field?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  // Sort scholars
  const sortedScholars = React.useMemo(() => {
    if (!orderBy) return filteredScholars;
    
    return [...filteredScholars].sort((a, b) => {
      // Handle special case for university since it replaces institution
      if (orderBy === 'university') {
        const aValue = a.university || '';
        const bValue = b.university || '';
        return order === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      const aValue = a[orderBy] || '';
      const bValue = b[orderBy] || '';
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return order === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      // Fallback for non-string values
      return order === 'asc'
        ? aValue < bValue ? -1 : 1
        : aValue > bValue ? -1 : 1;
    });
  }, [filteredScholars, order, orderBy]);

  // Paginate scholars
  const paginatedScholars = sortedScholars.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // If no scholars, show a message
  if (scholars.length === 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6">No scholar data available</Typography>
        <Typography variant="body1">
          Please run the scraper to collect data from the Westpac Scholars website.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          label="Search Scholars"
          variant="outlined"
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder="Search by name, university, scholarship type..."
        />
      </Box>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="scholars table">
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'name'}
                  direction={orderBy === 'name' ? order : 'asc'}
                  onClick={() => handleRequestSort('name')}
                >
                  Name
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'scholarship_type'}
                  direction={orderBy === 'scholarship_type' ? order : 'asc'}
                  onClick={() => handleRequestSort('scholarship_type')}
                >
                  Scholarship Type
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'university'}
                  direction={orderBy === 'university' ? order : 'asc'}
                  onClick={() => handleRequestSort('university')}
                >
                  Institution
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'year'}
                  direction={orderBy === 'year' ? order : 'asc'}
                  onClick={() => handleRequestSort('year')}
                >
                  Year
                </TableSortLabel>
              </TableCell>
              <TableCell>Bio</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedScholars.map((scholar, index) => (
              <TableRow 
                key={scholar.id || index}
                hover
                onClick={() => handleScholarClick(scholar)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell component="th" scope="row">
                  {scholar.name}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={scholar.scholarship_type || 'Unknown'} 
                    color="primary" 
                    variant="outlined" 
                    size="small" 
                  />
                </TableCell>
                <TableCell>{scholar.university || 'Unknown'}</TableCell>
                <TableCell>{scholar.year || 'Unknown'}</TableCell>
                <TableCell>
                  {scholar.about ? (
                    scholar.about.length > 100 
                      ? `${scholar.about.substring(0, 100)}...` 
                      : scholar.about
                  ) : scholar.quote ? (
                    scholar.quote.length > 100
                      ? `${scholar.quote.substring(0, 100)}...`
                      : scholar.quote
                  ) : 'No bio available'}
                </TableCell>
              </TableRow>
            ))}
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

      {/* Scholar Detail Dialog */}
      <Dialog
        open={!!selectedScholar}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedScholar && (
          <>
            <DialogTitle>
              {selectedScholar.name}
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                {/* Profile Photo */}
                {selectedScholar.image_url && (
                  <Grid item xs={12} sm={4} sx={{ display: 'flex', justifyContent: 'center' }}>
                    <Avatar
                      alt={selectedScholar.name}
                      src={selectedScholar.local_image_path || selectedScholar.image_url}
                      sx={{ width: 200, height: 200 }}
                    />
                  </Grid>
                )}
                
                <Grid item xs={12} sm={selectedScholar.image_url ? 8 : 12}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle1" fontWeight="bold">Scholarship Type</Typography>
                      <Typography variant="body1" paragraph>
                        {selectedScholar.scholarship_type || 'Unknown'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle1" fontWeight="bold">Institution</Typography>
                      <Typography variant="body1" paragraph>
                        {selectedScholar.university || 'Unknown'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle1" fontWeight="bold">Year</Typography>
                      <Typography variant="body1" paragraph>
                        {selectedScholar.year || 'Unknown'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle1" fontWeight="bold">State</Typography>
                      <Typography variant="body1" paragraph>
                        {selectedScholar.state || 'Unknown'}
                      </Typography>
                    </Grid>
                    {selectedScholar.focus_area && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle1" fontWeight="bold">Focus Area</Typography>
                        <Typography variant="body1" paragraph>
                          {selectedScholar.focus_area}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Grid>
                
                {selectedScholar.quote && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" fontWeight="bold">Quote</Typography>
                    <Typography variant="body1" paragraph sx={{ fontStyle: 'italic' }}>
                      "{selectedScholar.quote}"
                    </Typography>
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" fontWeight="bold">About</Typography>
                  <Typography variant="body1" paragraph>
                    {selectedScholar.about || 'No information available'}
                  </Typography>
                </Grid>
                
                {selectedScholar.linkedin_url && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" fontWeight="bold">LinkedIn</Typography>
                    <Typography variant="body1" paragraph>
                      <a href={selectedScholar.linkedin_url} target="_blank" rel="noopener noreferrer">
                        {selectedScholar.linkedin_url}
                      </a>
                    </Typography>
                  </Grid>
                )}
                
                {selectedScholar.sentiment && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" fontWeight="bold">Sentiment Analysis</Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                      <Chip 
                        label={`Positive: ${(selectedScholar.sentiment.positive * 100).toFixed(1)}%`} 
                        color="success" 
                        variant="outlined" 
                      />
                      <Chip 
                        label={`Negative: ${(selectedScholar.sentiment.negative * 100).toFixed(1)}%`} 
                        color="error" 
                        variant="outlined" 
                      />
                      <Chip 
                        label={`Neutral: ${(selectedScholar.sentiment.neutral * 100).toFixed(1)}%`} 
                        color="default" 
                        variant="outlined" 
                      />
                    </Box>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default ScholarsTable; 