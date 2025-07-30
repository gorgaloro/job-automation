import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
} from '@mui/material';
import {
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  LinkedIn as LinkedInIcon,
  Message as MessageIcon,
} from '@mui/icons-material';
import { Line, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
);

interface NetworkingMetrics {
  total_contacts: number;
  active_connections: number;
  response_rate: number;
  network_growth_rate: number;
  top_connections: Array<{
    name: string;
    company: string;
    role: string;
    relationship_strength: number;
    last_interaction: string;
  }>;
  industry_breakdown: Record<string, number>;
  monthly_growth: Array<{
    month: string;
    new_connections: number;
    interactions: number;
  }>;
  engagement_metrics: {
    messages_sent: number;
    messages_received: number;
    meetings_scheduled: number;
    referrals_received: number;
  };
}

const NetworkingAnalytics: React.FC = () => {
  const [metrics, setMetrics] = useState<NetworkingMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNetworkingMetrics();
  }, []);

  const fetchNetworkingMetrics = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/networking
      const mockMetrics: NetworkingMetrics = {
        total_contacts: 134,
        active_connections: 89,
        response_rate: 0.67,
        network_growth_rate: 0.152,
        top_connections: [
          {
            name: "Sarah Chen",
            company: "TechCorp",
            role: "Senior Engineering Manager",
            relationship_strength: 0.85,
            last_interaction: "2025-07-22T10:30:00Z"
          },
          {
            name: "Michael Rodriguez",
            company: "InnovateLabs",
            role: "VP of Engineering",
            relationship_strength: 0.78,
            last_interaction: "2025-07-20T14:15:00Z"
          },
          {
            name: "Emily Johnson",
            company: "DataSystems",
            role: "Tech Lead",
            relationship_strength: 0.72,
            last_interaction: "2025-07-19T09:45:00Z"
          },
        ],
        industry_breakdown: {
          "Technology": 45,
          "Finance": 23,
          "Healthcare": 18,
          "Consulting": 15,
          "Startups": 33,
        },
        monthly_growth: [
          { month: "April", new_connections: 12, interactions: 45 },
          { month: "May", new_connections: 18, interactions: 67 },
          { month: "June", new_connections: 15, interactions: 52 },
        ],
        engagement_metrics: {
          messages_sent: 156,
          messages_received: 104,
          meetings_scheduled: 23,
          referrals_received: 8,
        },
      };

      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch networking metrics:', error);
      setLoading(false);
    }
  };

  const growthChartData = metrics ? {
    labels: metrics.monthly_growth.map(growth => growth.month),
    datasets: [
      {
        label: 'New Connections',
        data: metrics.monthly_growth.map(growth => growth.new_connections),
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Interactions',
        data: metrics.monthly_growth.map(growth => growth.interactions),
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
      },
    ],
  } : null;

  const industryRadarData = metrics ? {
    labels: Object.keys(metrics.industry_breakdown),
    datasets: [
      {
        label: 'Network Distribution',
        data: Object.values(metrics.industry_breakdown),
        backgroundColor: 'rgba(25, 118, 210, 0.2)',
        borderColor: '#1976d2',
        borderWidth: 2,
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
          Loading networking analytics...
        </Typography>
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Failed to load networking metrics
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Networking Analytics
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PeopleIcon sx={{ mr: 2, color: '#1976d2' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.total_contacts}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Contacts
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
                    {(metrics.network_growth_rate * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Growth Rate
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
                <MessageIcon sx={{ mr: 2, color: '#9c27b0' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.response_rate * 100).toFixed(0)}%
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
                <LinkedInIcon sx={{ mr: 2, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.active_connections}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Connections
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Network Growth Trends
              </Typography>
              {growthChartData && (
                <Box sx={{ height: 300 }}>
                  <Line 
                    data={growthChartData} 
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

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Industry Distribution
              </Typography>
              {industryRadarData && (
                <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                  <Radar 
                    data={industryRadarData} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Engagement Metrics and Top Connections */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Engagement Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                      {metrics.engagement_metrics.messages_sent}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Messages Sent
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#4caf50' }}>
                      {metrics.engagement_metrics.messages_received}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Messages Received
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#9c27b0' }}>
                      {metrics.engagement_metrics.meetings_scheduled}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Meetings Scheduled
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#ff9800' }}>
                      {metrics.engagement_metrics.referrals_received}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Referrals Received
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Top Connections
              </Typography>
              <List>
                {metrics.top_connections.map((connection, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: '#1976d2' }}>
                        {connection.name.split(' ').map(n => n[0]).join('')}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {connection.name}
                          </Typography>
                          <Chip
                            label={`${(connection.relationship_strength * 100).toFixed(0)}%`}
                            size="small"
                            color="primary"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {connection.role} at {connection.company}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Last interaction: {new Date(connection.last_interaction).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NetworkingAnalytics;
