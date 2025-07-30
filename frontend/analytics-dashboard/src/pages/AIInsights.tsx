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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Lightbulb as LightbulbIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { Bar, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface AIMetrics {
  overall_accuracy: number;
  job_scoring_accuracy: number;
  resume_optimization_effectiveness: number;
  recommendation_precision: number;
  model_performance: {
    response_time_ms: number;
    confidence_score: number;
    error_rate: number;
  };
  scoring_distribution: Array<{
    score_range: string;
    count: number;
    success_rate: number;
  }>;
  recent_insights: Array<{
    type: string;
    insight: string;
    confidence: number;
    timestamp: string;
  }>;
  recommendations: Array<{
    category: string;
    suggestion: string;
    priority: string;
    impact: string;
  }>;
}

const AIInsights: React.FC = () => {
  const [metrics, setMetrics] = useState<AIMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAIMetrics();
  }, []);

  const fetchAIMetrics = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/ai-insights
      const mockMetrics: AIMetrics = {
        overall_accuracy: 0.873,
        job_scoring_accuracy: 0.891,
        resume_optimization_effectiveness: 0.845,
        recommendation_precision: 0.892,
        model_performance: {
          response_time_ms: 1250,
          confidence_score: 0.87,
          error_rate: 0.023,
        },
        scoring_distribution: [
          { score_range: "90-100", count: 12, success_rate: 0.92 },
          { score_range: "80-89", count: 18, success_rate: 0.83 },
          { score_range: "70-79", count: 15, success_rate: 0.67 },
          { score_range: "60-69", count: 8, success_rate: 0.38 },
          { score_range: "50-59", count: 4, success_rate: 0.25 },
        ],
        recent_insights: [
          {
            type: "job_match",
            insight: "Senior Engineer role at TechCorp shows 94% compatibility with your profile",
            confidence: 0.94,
            timestamp: "2025-07-24T20:30:00Z"
          },
          {
            type: "resume_optimization",
            insight: "Adding 'microservices architecture' keyword could improve ATS compatibility by 15%",
            confidence: 0.87,
            timestamp: "2025-07-24T18:15:00Z"
          },
          {
            type: "networking",
            insight: "Connecting with Sarah Chen could open 3 potential opportunities at TechCorp",
            confidence: 0.82,
            timestamp: "2025-07-24T16:45:00Z"
          },
        ],
        recommendations: [
          {
            category: "Resume Optimization",
            suggestion: "Focus on cloud technologies and DevOps skills in your resume",
            priority: "high",
            impact: "Could increase interview rate by 25%"
          },
          {
            category: "Job Targeting",
            suggestion: "Target mid-size tech companies (100-500 employees) for better response rates",
            priority: "medium",
            impact: "Historical data shows 40% higher response rate"
          },
          {
            category: "Networking",
            suggestion: "Engage more with AI/ML professionals in your network",
            priority: "medium",
            impact: "Could unlock 5-8 new opportunities"
          },
        ],
      };

      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch AI metrics:', error);
      setLoading(false);
    }
  };

  const scoringChartData = metrics ? {
    labels: metrics.scoring_distribution.map(item => item.score_range),
    datasets: [
      {
        label: 'Job Count',
        data: metrics.scoring_distribution.map(item => item.count),
        backgroundColor: '#1976d2',
        borderColor: '#1976d2',
        borderWidth: 1,
        yAxisID: 'y',
      },
      {
        label: 'Success Rate (%)',
        data: metrics.scoring_distribution.map(item => item.success_rate * 100),
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
      title: {
        display: true,
        text: 'AI Scoring Distribution vs Success Rate',
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
          text: 'Job Count',
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
          text: 'Success Rate (%)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'job_match': return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'resume_optimization': return <LightbulbIcon sx={{ color: '#ff9800' }} />;
      case 'networking': return <TrendingUpIcon sx={{ color: '#1976d2' }} />;
      default: return <PsychologyIcon sx={{ color: '#9c27b0' }} />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading AI insights...
        </Typography>
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Failed to load AI metrics
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        AI Insights & Performance
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PsychologyIcon sx={{ mr: 2, color: '#1976d2' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.overall_accuracy * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overall Accuracy
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
                    {(metrics.job_scoring_accuracy * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Job Scoring Accuracy
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
                <SpeedIcon sx={{ mr: 2, color: '#9c27b0' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.model_performance.response_time_ms}ms
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Response Time
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
                <LightbulbIcon sx={{ mr: 2, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.recommendation_precision * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Recommendation Precision
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Model Performance Alert */}
      <Alert severity="success" sx={{ mb: 4 }}>
        <Typography variant="body1" sx={{ fontWeight: 600 }}>
          AI Model Performance: Excellent
        </Typography>
        <Typography variant="body2">
          Your AI models are performing at {(metrics.overall_accuracy * 100).toFixed(1)}% accuracy with 
          {' '}{(metrics.model_performance.error_rate * 100).toFixed(1)}% error rate. 
          Confidence score: {(metrics.model_performance.confidence_score * 100).toFixed(0)}%
        </Typography>
      </Alert>

      {/* Charts and Insights */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                AI Scoring Performance Analysis
              </Typography>
              {scoringChartData && (
                <Box sx={{ height: 400 }}>
                  <Bar 
                    data={scoringChartData} 
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
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Recent AI Insights
              </Typography>
              <List>
                {metrics.recent_insights.map((insight, index) => (
                  <ListItem key={index} sx={{ px: 0, py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {getInsightIcon(insight.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {insight.insight}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Chip
                            label={`${(insight.confidence * 100).toFixed(0)}% confidence`}
                            size="small"
                            color="primary"
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(insight.timestamp).toLocaleDateString()}
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

      {/* AI Recommendations */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            AI-Powered Recommendations
          </Typography>
          <Grid container spacing={3}>
            {metrics.recommendations.map((rec, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {rec.category}
                      </Typography>
                      <Chip
                        label={rec.priority.toUpperCase()}
                        color={getPriorityColor(rec.priority) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {rec.suggestion}
                    </Typography>
                    <Box sx={{ 
                      backgroundColor: '#f5f5f5', 
                      borderRadius: 1, 
                      p: 1.5,
                      display: 'flex',
                      alignItems: 'center'
                    }}>
                      <TrendingUpIcon sx={{ mr: 1, color: '#4caf50', fontSize: 20 }} />
                      <Typography variant="caption" sx={{ fontWeight: 500 }}>
                        {rec.impact}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AIInsights;
