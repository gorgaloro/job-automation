import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Chip,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';

const Header: React.FC = () => {
  const currentTime = new Date().toLocaleString();

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        backgroundColor: 'white',
        borderBottom: '1px solid #e0e0e0',
        color: 'text.primary'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#1976d2' }}>
            AI Job Search Analytics
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Real-time insights across 8 integrated platform features
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={<TrendingUpIcon />}
            label="Live Data"
            color="success"
            variant="outlined"
            size="small"
          />
          
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {currentTime}
          </Typography>

          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
