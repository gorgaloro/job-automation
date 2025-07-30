import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Alert,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Work as WorkIcon,
  People as PeopleIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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
  Title,
  Tooltip,
  Legend
);

interface KPI {
  kpi_id: string;
  name: string;
  current_value: number;
  target_value?: number;
  unit: string;
  status: string;
  improvement_suggestions: string[];
}

interface DashboardData {
  kpis: Record<string, KPI>;
  quick_stats: {
    total_applications: number;
    interview_rate: number;
    network_size: number;
    ai_accuracy: number;
  };
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
  }>;
  alerts: Array<{
    type: string;
    message: string;
    priority: string;
  }>;
}

const ExecutiveDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/dashboard/summary
      const mockData: DashboardData = {
        kpis: {
          total_applications: {
            kpi_id: "total_applications",
            name: "Total Applications",
            current_value: 47,
            target_value: 100,
            unit: "applications",
            status: "good",
            improvement_suggestions: [
              "Increase daily application target to 3-4 applications",
              "Focus on high-compatibility opportunities (>80% match)"
            ]
          },
          interview_conversion_rate: {
            kpi_id: "interview_conversion_rate",
            name: "Interview Conversion Rate",
            current_value: 18.5,
            target_value: 25.0,
            unit: "percentage",
            status: "warning",
            improvement_suggestions: [
              "Optimize resume for higher ATS compatibility",
              "Use AI scoring to focus on best-fit opportunities"
            ]
          },
          network_growth_rate: {
            kpi_id: "network_growth_rate",
            name: "Network Growth Rate",
            current_value: 15.2,
            target_value: 20.0,
            unit: "percentage",
            status: "good",
            improvement_suggestions: [
              "Increase LinkedIn outreach frequency",
              "Attend more industry networking events"
            ]
          },
          ai_recommendation_accuracy: {
            kpi_id: "ai_recommendation_accuracy",
            name: "AI Recommendation Accuracy",
            current_value: 87.3,
            target_value: 90.0,
            unit: "percentage",
            status: "excellent",
            improvement_suggestions: [
              "Continue refining personal brand profile",
              "Provide feedback on AI recommendations"
            ]
          }
        },
        quick_stats: {
          total_applications: 47,
          interview_rate: 0.185,
          network_size: 134,
          ai_accuracy: 0.873
        },
        recent_activity: [
          {
            type: "application",
            description: "Applied to Senior Engineer at TechCorp",
            timestamp: "2025-07-24T20:30:00Z"
          },
          {
            type: "networking",
            description: "Connected with Sarah Chen on LinkedIn",
            timestamp: "2025-07-24T18:15:00Z"
          }
        ],
        alerts: [
          {
            type: "opportunity",
            message: "3 new high-scoring job opportunities available",
            priority: "high"
          },
          {
            type: "networking",
            message: "Follow up with 5 pending LinkedIn connections",
            priority: "medium"
          }
        ]
      };

      setDashboardData(mockData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#4caf50';
      case 'good': return '#2196f3';
      case 'warning': return '#ff9800';
      case 'critical': return '#f44336';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
      case 'good':
        return <TrendingUpIcon sx={{ color: getStatusColor(status) }} />;
      case 'warning':
        return <TrendingFlatIcon sx={{ color: getStatusColor(status) }} />;
      case 'critical':
        return <TrendingDownIcon sx={{ color: getStatusColor(status) }} />;
      default:
        return <TrendingFlatIcon sx={{ color: getStatusColor(status) }} />;
    }
  };

  const getKPIIcon = (kpiId: string) => {
    switch (kpiId) {
      case 'total_applications': return <WorkIcon />;
      case 'interview_conversion_rate': return <AssessmentIcon />;
      case 'network_growth_rate': return <PeopleIcon />;
      case 'ai_recommendation_accuracy': return <PsychologyIcon />;
      default: return <AssessmentIcon />;
    }
  };

  const chartData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Applications',
        data: [8, 12, 15, 12],
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Interviews',
        data: [1, 2, 3, 2],
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Job Search Progress Trend',
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
          Loading analytics dashboard...
        </Typography>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="error">
        Failed to load dashboard data. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Executive Dashboard
      </Typography>

      {/* Alerts */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {dashboardData.alerts.map((alert, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Alert 
              severity={alert.priority === 'high' ? 'warning' : 'info'}
              sx={{ borderRadius: 2 }}
            >
              {alert.message}
            </Alert>
          </Grid>
        ))}
      </Grid>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {Object.entries(dashboardData.kpis).map(([key, kpi]) => (
          <Grid item xs={12} sm={6} md={3} key={key}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: 2, 
                    backgroundColor: getStatusColor(kpi.status) + '20',
                    mr: 2 
                  }}>
                    {getKPIIcon(kpi.kpi_id)}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {kpi.current_value}
                      {kpi.unit === 'percentage' && '%'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {kpi.name}
                    </Typography>
                  </Box>
                  {getStatusIcon(kpi.status)}
                </Box>

                {kpi.target_value && (
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Progress</Typography>
                      <Typography variant="body2">
                        {Math.round((kpi.current_value / kpi.target_value) * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((kpi.current_value / kpi.target_value) * 100, 100)}
                      sx={{ 
                        height: 8, 
                        borderRadius: 4,
                        backgroundColor: '#f0f0f0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getStatusColor(kpi.status),
                        }
                      }}
                    />
                  </Box>
                )}

                <Chip
                  label={kpi.status.toUpperCase()}
                  size="small"
                  sx={{
                    backgroundColor: getStatusColor(kpi.status) + '20',
                    color: getStatusColor(kpi.status),
                    fontWeight: 600,
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts and Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Performance Trends
              </Typography>
              <Line data={chartData} options={chartOptions} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Recent Activity
              </Typography>
              {dashboardData.recent_activity.map((activity, index) => (
                <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: index < dashboardData.recent_activity.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {activity.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(activity.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExecutiveDashboard;
