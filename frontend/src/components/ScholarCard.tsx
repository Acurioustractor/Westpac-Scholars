import React from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  CardActions,
  Button,
  Chip,
  Box,
  Link
} from '@mui/material';
import { Scholar } from '../services/DataService';

interface ScholarCardProps {
  scholar: Scholar;
  onClick?: (scholar: Scholar) => void;
}

const ScholarCard: React.FC<ScholarCardProps> = ({ scholar, onClick }) => {
  // Default image if none available
  const defaultImage = '/placeholder-profile.jpg';
  
  // Determine image source
  const getImageSource = () => {
    // First try local image path if available
    if (scholar.local_image_path) {
      // Convert path to relative URL
      const fileName = scholar.local_image_path.split('/').pop();
      return `/scholar_photos/${fileName}`;
    }
    
    // Then try web URL
    if (scholar.image_url) {
      return scholar.image_url;
    }
    
    // Fall back to default image
    return defaultImage;
  };

  // Handle image loading errors
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.src = defaultImage;
  };

  return (
    <Card sx={{ 
      maxWidth: 345, 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-5px)',
        boxShadow: 6
      }
    }}>
      <CardMedia
        component="img"
        height="200"
        image={getImageSource()}
        alt={`Photo of ${scholar.name}`}
        onError={handleImageError}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h5" component="div">
          {scholar.name}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Chip 
            label={scholar.scholarship_type} 
            color="primary" 
            size="small" 
            sx={{ mr: 1, mb: 1 }} 
          />
          <Chip 
            label={scholar.year} 
            color="secondary" 
            size="small" 
            sx={{ mb: 1 }} 
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {scholar.university}
          {scholar.state && `, ${scholar.state}`}
        </Typography>
        
        {scholar.focus_area && (
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Focus:</strong> {scholar.focus_area}
          </Typography>
        )}
        
        {scholar.quote && (
          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', mb: 2 }}>
            "{scholar.quote.slice(0, 100)}{scholar.quote.length > 100 ? '...' : ''}"
          </Typography>
        )}
        
        {/* Show passions if available */}
        {(scholar.passion_1 || scholar.passion_2 || scholar.passion_3) && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Passions:</strong>
            </Typography>
            <Box>
              {scholar.passion_1 && <Chip label={scholar.passion_1} size="small" sx={{ mr: 0.5, mb: 0.5 }} />}
              {scholar.passion_2 && <Chip label={scholar.passion_2} size="small" sx={{ mr: 0.5, mb: 0.5 }} />}
              {scholar.passion_3 && <Chip label={scholar.passion_3} size="small" sx={{ mr: 0.5, mb: 0.5 }} />}
              {scholar.passion_4 && <Chip label={scholar.passion_4} size="small" sx={{ mr: 0.5, mb: 0.5 }} />}
              {scholar.passion_5 && <Chip label={scholar.passion_5} size="small" sx={{ mb: 0.5 }} />}
            </Box>
          </Box>
        )}
      </CardContent>
      
      <CardActions>
        {onClick && (
          <Button size="small" onClick={() => onClick(scholar)}>
            View Details
          </Button>
        )}
        
        {scholar.linkedin_url && (
          <Button 
            size="small" 
            component={Link} 
            href={scholar.linkedin_url} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            LinkedIn
          </Button>
        )}
      </CardActions>
    </Card>
  );
};

export default ScholarCard; 