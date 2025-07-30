import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Work as WorkIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface ApplicationMetrics {
  total_applications: number;
  response_rate: number;
  interview_rate: number;
  offer_rate: number;
  avg_response_time: number;
  top_companies: Array<{
    company: string;
    applications: number;
    response_rate: number;
  }>;
  application_status_breakdown: Record<string, number>;
  monthly_trends: Array<{
    month: string;
    applications: number;
    interviews: number;
    offers: number;
  }>;
}

const ApplicationsAnalytics: React.FC = () => {
  const [metrics, setMetrics] = useState<ApplicationMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplicationMetrics();
  }, []);

  const fetchApplicationMetrics = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/applications
      const mockMetrics: ApplicationMetrics = {
        total_applications: 47,
        response_rate: 0.234,
        interview_rate: 0.185,
        offer_rate: 0.064,
        avg_response_time: 8.5,
        top_companies: [
          { company: "TechCorp", applications: 5, response_rate: 0.4 },
          { company: "InnovateLabs", applications: 4, response_rate: 0.25 },
          { company: "DataSystems", applications: 3, response_rate: 0.33 },
          { company: "CloudWorks", applications: 3, response_rate: 0.0 },
          { company: "AI Solutions", applications: 2, response_rate: 0.5 },
        ],
        application_status_breakdown: {
          "Applied": 28,
          "Under Review": 8,
          "Interview Scheduled": 5,
          "Interview Completed": 3,
          "Offer Received": 2,
          "Rejected": 1,
        },
        monthly_trends: [
          { month: "April", applications: 12, interviews: 2, offers: 0 },
          { month: "May", applications: 18, interviews: 3, offers: 1 },
          { month: "June", applications: 17, interviews: 3, offers: 1 },
        ],
      };

      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch application metrics:', error);
      setLoading(false);
    }
  };

  const statusColors = {
    "Applied": "#2196f3",
    "Under Review": "#ff9800",
    "Interview Scheduled": "#9c27b0",
    "Interview Completed": "#673ab7",
    "Offer Received": "#4caf50",
    "Rejected": "#f44336",
  };

  const statusChartData = metrics ? {
    labels: Object.keys(metrics.application_status_breakdown),
    datasets: [
      {
        data: Object.values(metrics.application_status_breakdown),
        backgroundColor: Object.keys(metrics.application_status_breakdown).map(
          status => statusColors[status as keyof typeof statusColors] || '#757575'
        ),
        borderWidth: 0,
      },
    ],
  } : null;

  const trendsChartData = metrics ? {
    labels: metrics.monthly_trends.map(trend => trend.month),
    datasets: [
      {
        label: 'Applications',
        data: metrics.monthly_trends.map(trend => trend.applications),
        backgroundColor: '#1976d2',
        borderColor: '#1976d2',
        borderWidth: 1,
      },
      {
        label: 'Interviews',
        data: metrics.monthly_trends.map(trend => trend.interviews),
        backgroundColor: '#4caf50',
        borderColor: '#4caf50',
        borderWidth: 1,
      },
      {
        label: 'Offers',
        data: metrics.monthly_trends.map(trend => trend.offers),
        backgroundColor: '#ff9800',
        borderColor: '#ff9800',
        borderWidth: 1,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading application analytics...
        </Typography>
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Failed to load application metrics
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Applications Analytics
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WorkIcon sx={{ mr: 2, color: '#1976d2' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.total_applications}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Applications
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ mr: 2, color: '#4caf50' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.response_rate * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Response Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircleIcon sx={{ mr: 2, color: '#9c27b0' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.interview_rate * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Interview Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ScheduleIcon sx={{ mr: 2, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.avg_response_time.toFixed(1)}d
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Response Time
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Application Status Breakdown
              </Typography>
              {statusChartData && (
                <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                  <Doughnut 
                    data={statusChartData} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Monthly Trends
              </Typography>
              {trendsChartData && (
                <Box sx={{ height: 300 }}>
                  <Bar 
                    data={trendsChartData} 
                    options={{
                      ...chartOptions,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Top Companies Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Top Target Companies
          </Typography>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Company</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Applications</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Response Rate</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {metrics.top_companies.map((company, index) => (
                  <TableRow key={index}>
                    <TableCell>{company.company}</TableCell>
                    <TableCell align="right">{company.applications}</TableCell>
                    <TableCell align="right">
                      {(company.response_rate * 100).toFixed(1)}%
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={company.response_rate > 0.3 ? 'High' : company.response_rate > 0.1 ? 'Medium' : 'Low'}
                        color={company.response_rate > 0.3 ? 'success' : company.response_rate > 0.1 ? 'warning' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ApplicationsAnalytics;
