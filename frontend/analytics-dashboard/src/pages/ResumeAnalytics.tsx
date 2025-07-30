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
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { Bar, Line } from 'react-chartjs-2';

interface ResumeMetrics {
  total_versions: number;
  avg_compatibility_score: number;
  optimization_improvement: number;
  ats_compatibility: number;
  version_performance: Array<{
    version_id: string;
    name: string;
    compatibility_score: number;
    applications_sent: number;
    response_rate: number;
    created_date: string;
  }>;
  keyword_analysis: Array<{
    keyword: string;
    frequency: number;
    importance: number;
    trend: string;
  }>;
  optimization_trends: Array<{
    date: string;
    score_before: number;
    score_after: number;
    improvement: number;
  }>;
}

const ResumeAnalytics: React.FC = () => {
  const [metrics, setMetrics] = useState<ResumeMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResumeMetrics();
  }, []);

  const fetchResumeMetrics = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/resume
      const mockMetrics: ResumeMetrics = {
        total_versions: 8,
        avg_compatibility_score: 0.782,
        optimization_improvement: 0.234,
        ats_compatibility: 0.891,
        version_performance: [
          {
            version_id: "v8",
            name: "Senior Engineer - Cloud Focus",
            compatibility_score: 0.89,
            applications_sent: 12,
            response_rate: 0.25,
            created_date: "2025-07-20T10:00:00Z"
          },
          {
            version_id: "v7", 
            name: "Full Stack Developer - Startup",
            compatibility_score: 0.84,
            applications_sent: 8,
            response_rate: 0.375,
            created_date: "2025-07-15T14:30:00Z"
          },
          {
            version_id: "v6",
            name: "Tech Lead - Enterprise",
            compatibility_score: 0.78,
            applications_sent: 15,
            response_rate: 0.133,
            created_date: "2025-07-10T09:15:00Z"
          },
        ],
        keyword_analysis: [
          { keyword: "React", frequency: 15, importance: 0.92, trend: "up" },
          { keyword: "TypeScript", frequency: 12, importance: 0.88, trend: "up" },
          { keyword: "AWS", frequency: 18, importance: 0.85, trend: "stable" },
          { keyword: "Docker", frequency: 10, importance: 0.82, trend: "up" },
          { keyword: "Kubernetes", frequency: 8, importance: 0.79, trend: "up" },
          { keyword: "Python", frequency: 14, importance: 0.76, trend: "stable" },
        ],
        optimization_trends: [
          { date: "2025-07-01", score_before: 0.65, score_after: 0.78, improvement: 0.13 },
          { date: "2025-07-08", score_before: 0.72, score_after: 0.84, improvement: 0.12 },
          { date: "2025-07-15", score_before: 0.76, score_after: 0.89, improvement: 0.13 },
          { date: "2025-07-22", score_before: 0.81, score_after: 0.91, improvement: 0.10 },
        ],
      };

      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch resume metrics:', error);
      setLoading(false);
    }
  };

  const optimizationChartData = metrics ? {
    labels: metrics.optimization_trends.map(trend => new Date(trend.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Score Before Optimization',
        data: metrics.optimization_trends.map(trend => trend.score_before * 100),
        borderColor: '#ff9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Score After Optimization',
        data: metrics.optimization_trends.map(trend => trend.score_after * 100),
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
      },
    ],
  } : null;

  const keywordChartData = metrics ? {
    labels: metrics.keyword_analysis.map(kw => kw.keyword),
    datasets: [
      {
        label: 'Frequency',
        data: metrics.keyword_analysis.map(kw => kw.frequency),
        backgroundColor: '#1976d2',
        borderColor: '#1976d2',
        borderWidth: 1,
        yAxisID: 'y',
      },
      {
        label: 'Importance Score',
        data: metrics.keyword_analysis.map(kw => kw.importance * 100),
        backgroundColor: '#4caf50',
        borderColor: '#4caf50',
        borderWidth: 1,
        yAxisID: 'y1',
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

  const keywordChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Keyword Frequency vs Importance',
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        beginAtZero: true,
        title: {
          display: true,
          text: 'Frequency',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Importance Score (%)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return '#4caf50';
      case 'down': return '#f44336';
      case 'stable': return '#ff9800';
      default: return '#757575';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading resume analytics...
        </Typography>
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Failed to load resume metrics
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Resume Analytics & Optimization
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <DescriptionIcon sx={{ mr: 2, color: '#1976d2' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.total_versions}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Resume Versions
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
                <AssessmentIcon sx={{ mr: 2, color: '#4caf50' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.avg_compatibility_score * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Compatibility
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
                <TrendingUpIcon sx={{ mr: 2, color: '#9c27b0' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    +{(metrics.optimization_improvement * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Optimization Gain
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
                <SpeedIcon sx={{ mr: 2, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.ats_compatibility * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ATS Compatibility
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
                Optimization Progress
              </Typography>
              {optimizationChartData && (
                <Box sx={{ height: 300 }}>
                  <Line 
                    data={optimizationChartData} 
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

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Keyword Analysis
              </Typography>
              {keywordChartData && (
                <Box sx={{ height: 300 }}>
                  <Bar 
                    data={keywordChartData} 
                    options={{
                      ...keywordChartOptions,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Resume Version Performance */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Resume Version Performance
              </Typography>
              <TableContainer component={Paper} elevation={0}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Version</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Compatibility</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Applications</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Response Rate</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Created</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {metrics.version_performance.map((version, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {version.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {version.version_id}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={version.compatibility_score * 100}
                              sx={{ 
                                width: 60, 
                                mr: 1,
                                height: 8,
                                borderRadius: 4,
                              }}
                            />
                            <Typography variant="body2">
                              {(version.compatibility_score * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">{version.applications_sent}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${(version.response_rate * 100).toFixed(1)}%`}
                            color={version.response_rate > 0.25 ? 'success' : version.response_rate > 0.15 ? 'warning' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          {new Date(version.created_date).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Top Keywords
              </Typography>
              {metrics.keyword_analysis.map((keyword, index) => (
                <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: index < metrics.keyword_analysis.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {keyword.keyword}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <TrendingUpIcon 
                        sx={{ 
                          fontSize: 16, 
                          mr: 0.5,
                          color: getTrendColor(keyword.trend)
                        }} 
                      />
                      <Typography variant="body2" color="text.secondary">
                        {keyword.frequency}x
                      </Typography>
                    </Box>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={keyword.importance * 100}
                    sx={{ 
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getTrendColor(keyword.trend),
                      }
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {(keyword.importance * 100).toFixed(0)}% importance
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

export default ResumeAnalytics;
