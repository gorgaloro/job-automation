import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Work as WorkIcon,
  People as PeopleIcon,
  Psychology as PsychologyIcon,
  Description as DescriptionIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';

const drawerWidth = 280;

interface NavigationItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  description: string;
}

const navigationItems: NavigationItem[] = [
  {
    text: 'Executive Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
    description: 'Overview & KPIs'
  },
  {
    text: 'Applications',
    icon: <WorkIcon />,
    path: '/applications',
    description: 'Job applications analytics'
  },
  {
    text: 'Networking',
    icon: <PeopleIcon />,
    path: '/networking',
    description: 'Network growth & engagement'
  },
  {
    text: 'AI Insights',
    icon: <PsychologyIcon />,
    path: '/ai-insights',
    description: 'AI scoring & recommendations'
  },
  {
    text: 'Resume Analytics',
    icon: <DescriptionIcon />,
    path: '/resume',
    description: 'Resume optimization metrics'
  },
  {
    text: 'Company Intelligence',
    icon: <BusinessIcon />,
    path: '/companies',
    description: 'Market & company insights'
  },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#1a1a1a',
          color: 'white',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AnalyticsIcon sx={{ mr: 1, color: '#42a5f5' }} />
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
            Analytics Dashboard
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
          AI Job Search Platform
        </Typography>
      </Box>
      
      <Divider sx={{ borderColor: '#333' }} />
      
      <List sx={{ px: 2, py: 1 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: '#42a5f5',
                  '&:hover': {
                    backgroundColor: '#1976d2',
                  },
                },
                '&:hover': {
                  backgroundColor: '#333',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <Box>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: 500,
                  }}
                />
                <Typography variant="caption" sx={{ color: '#888', display: 'block' }}>
                  {item.description}
                </Typography>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Box sx={{ mt: 'auto', p: 2 }}>
        <Box sx={{ 
          backgroundColor: '#333', 
          borderRadius: 2, 
          p: 2,
          textAlign: 'center'
        }}>
          <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
            Epic 9: Analytics Dashboard
          </Typography>
          <Typography variant="caption" sx={{ color: '#42a5f5' }}>
            8 Epics Integrated
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
