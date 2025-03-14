import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  TextField,
  Card,
  CardContent,
  Divider
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
  PieChart,
  Pie,
  Cell,
  Treemap
} from 'recharts';

// Import interfaces from DataService
import { Distribution, YearDistribution } from '../services/DataService';

interface DistributionChartsProps {
  scholarshipDistribution: Distribution[];
  institutionDistribution: Distribution[];
  yearDistribution: YearDistribution[];
}

interface TreemapContentProps {
  root?: any;
  depth?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  index?: number;
  payload?: any;
  colors?: any;
  rank?: any;
  name?: string;
}

const COLORS = ['#d5002b', '#2b0a3d', '#1f1f1f', '#6d6e71', '#87005b', '#1e22aa', '#ff585d', '#ffca05', '#0078cb', '#ff8200', '#00af3f'];

// Custom content component for Treemap
class CustomContent extends React.Component<TreemapContentProps> {
  render() {
    const { x, y, width, height, index, name, depth } = this.props;
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: COLORS[index! % COLORS.length],
            stroke: '#fff',
            strokeWidth: 2 / (depth! + 1e-10),
            strokeOpacity: 1 / (depth! + 1e-10),
          }}
        />
        {width! > 30 && height! > 30 && (
          <text
            x={x! + width! / 2}
            y={y! + height! / 2 + 7}
            textAnchor="middle"
            fill="#fff"
            fontSize={12}
          >
            {name}
          </text>
        )}
      </g>
    );
  }
}

// Add a type guard to safely access properties
function isYearDistribution(item: Distribution | YearDistribution): item is YearDistribution {
  return 'year' in item;
}

// A helper function to safely get property values
function getPropertyValue(item: Distribution | YearDistribution, key: string): string | number {
  if (isYearDistribution(item)) {
    if (key === 'year') return item.year;
    if (key === 'count') return item.count;
  } else {
    if (key === 'name') return item.name;
    if (key === 'count') return item.count;
  }
  return '';
}

const DistributionCharts: React.FC<DistributionChartsProps> = ({
  scholarshipDistribution,
  institutionDistribution,
  yearDistribution
}) => {
  const [chartType, setChartType] = useState<'bar' | 'pie' | 'treemap'>('bar');
  const [institutionLimit, setInstitutionLimit] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');

  // Handle chart type change
  const handleChartTypeChange = (event: SelectChangeEvent) => {
    setChartType(event.target.value as 'bar' | 'pie' | 'treemap');
  };

  // Handle institution limit change
  const handleInstitutionLimitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value);
    if (!isNaN(value) && value > 0) {
      setInstitutionLimit(value);
    }
  };

  // Handle search
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  // Filter institution distribution based on search term
  const filteredInstitutionDistribution = institutionDistribution.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, institutionLimit);

  // Calculate statistics
  const totalScholars = scholarshipDistribution.reduce((sum, item) => sum + item.count, 0);
  const totalInstitutions = institutionDistribution.length;
  const avgScholarsPerInstitution = totalInstitutions > 0 
    ? totalScholars / totalInstitutions 
    : 0;
  const topScholarshipType = scholarshipDistribution.length > 0 
    ? scholarshipDistribution[0].name 
    : 'None';

  // Helper function to render the appropriate chart
  const renderChart = (
    data: Distribution[] | YearDistribution[],
    dataKey: string,
    nameKey: string,
    title: string
  ) => {
    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={data}
              margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={nameKey} 
                angle={-45} 
                textAnchor="end" 
                height={100} 
                interval={0}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={dataKey} fill="#d5002b" name="Count">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );
      
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={100}
                fill="#d5002b"
                dataKey={dataKey}
                nameKey={nameKey}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [value, 'Count']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
      
      case 'treemap':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <Treemap
              data={data.map(item => ({
                name: getPropertyValue(item, nameKey),
                size: getPropertyValue(item, dataKey),
                value: getPropertyValue(item, dataKey)
              }))}
              dataKey="size"
              stroke="#fff"
              fill="#d5002b"
              content={<CustomContent />}
            />
          </ResponsiveContainer>
        );
      
      default:
        return null;
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>Distribution Analysis</Typography>
        <Typography variant="body1" paragraph>
          This analysis shows the distribution of scholars by different dimensions such as scholarship type, 
          institution, and year.
        </Typography>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {totalScholars}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Scholars
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {totalInstitutions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unique Institutions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {avgScholarsPerInstitution.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Scholars per Institution
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {topScholarshipType}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Most Common Scholarship
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Box sx={{ mb: 2 }}>
        <FormControl sx={{ minWidth: 120, mr: 2 }}>
          <InputLabel>Chart Type</InputLabel>
          <Select
            value={chartType}
            label="Chart Type"
            onChange={handleChartTypeChange}
            size="small"
          >
            <MenuItem value="bar">Bar Chart</MenuItem>
            <MenuItem value="pie">Pie Chart</MenuItem>
            <MenuItem value="treemap">Treemap</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Scholarship Type Distribution</Typography>
            {renderChart(scholarshipDistribution, 'count', 'name', 'Scholarship Type Distribution')}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Year Distribution</Typography>
            {renderChart(
              // Sort by year in ascending order
              [...yearDistribution].sort((a, b) => a.year.localeCompare(b.year)),
              'count',
              'year',
              'Year Distribution'
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" gutterBottom>Institution Distribution</Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="Max Institutions"
                  type="number"
                  value={institutionLimit}
                  onChange={handleInstitutionLimitChange}
                  size="small"
                  sx={{ width: 150 }}
                  InputProps={{ inputProps: { min: 1 } }}
                />
                <TextField
                  label="Search"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  size="small"
                  sx={{ width: 200 }}
                />
              </Box>
            </Box>
            <Divider sx={{ mb: 2 }} />
            {filteredInstitutionDistribution.length > 0 ? (
              renderChart(filteredInstitutionDistribution, 'count', 'name', 'Institution Distribution')
            ) : (
              <Typography>No institutions match your search criteria.</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DistributionCharts; 