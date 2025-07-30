import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import ApplicationsAnalytics from './pages/ApplicationsAnalytics';
import NetworkingAnalytics from './pages/NetworkingAnalytics';
import AIInsights from './pages/AIInsights';
import ResumeAnalytics from './pages/ResumeAnalytics';
import CompanyAnalytics from './pages/CompanyAnalytics';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar />
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <Header />
            <Box sx={{ flexGrow: 1, p: 3, backgroundColor: 'background.default' }}>
              <Routes>
                <Route path="/" element={<ExecutiveDashboard />} />
                <Route path="/dashboard" element={<ExecutiveDashboard />} />
                <Route path="/applications" element={<ApplicationsAnalytics />} />
                <Route path="/networking" element={<NetworkingAnalytics />} />
                <Route path="/ai-insights" element={<AIInsights />} />
                <Route path="/resume" element={<ResumeAnalytics />} />
                <Route path="/companies" element={<CompanyAnalytics />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
