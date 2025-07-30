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
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import { Doughnut, Bar } from 'react-chartjs-2';

interface CompanyMetrics {
  total_companies_analyzed: number;
  avg_culture_fit_score: number;
  top_industry_match: string;
  companies_with_openings: number;
  top_companies: Array<{
    name: string;
    industry: string;
    culture_fit_score: number;
    tech_stack_match: number;
    open_positions: number;
    application_status: string;
  }>;
  industry_distribution: Record<string, number>;
  tech_stack_analysis: Array<{
    technology: string;
    companies_using: number;
    match_score: number;
    trend: string;
  }>;
  culture_metrics: {
    work_life_balance: number;
    innovation_focus: number;
    team_collaboration: number;
    growth_opportunities: number;
    compensation_competitiveness: number;
  };
}

const CompanyAnalytics: React.FC = () => {
  const [metrics, setMetrics] = useState<CompanyMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanyMetrics();
  }, []);

  const fetchCompanyMetrics = async () => {
    try {
      // Simulate API call - in real implementation, this would call /analytics/companies
      const mockMetrics: CompanyMetrics = {
        total_companies_analyzed: 156,
        avg_culture_fit_score: 0.782,
        top_industry_match: "Technology",
        companies_with_openings: 89,
        top_companies: [
          {
            name: "TechCorp",
            industry: "Technology",
            culture_fit_score: 0.94,
            tech_stack_match: 0.89,
            open_positions: 12,
            application_status: "applied"
          },
          {
            name: "InnovateLabs",
            industry: "AI/ML",
            culture_fit_score: 0.91,
            tech_stack_match: 0.92,
            open_positions: 8,
            application_status: "interested"
          },
          {
            name: "CloudWorks",
            industry: "Cloud Computing",
            culture_fit_score: 0.87,
            tech_stack_match: 0.85,
            open_positions: 15,
            application_status: "researching"
          },
          {
            name: "DataSystems",
            industry: "Data Analytics",
            culture_fit_score: 0.84,
            tech_stack_match: 0.88,
            open_positions: 6,
            application_status: "applied"
          },
        ],
        industry_distribution: {
          "Technology": 45,
          "AI/ML": 23,
          "Cloud Computing": 18,
          "Data Analytics": 15,
          "Fintech": 12,
          "Healthcare Tech": 8,
          "E-commerce": 10,
          "Cybersecurity": 7,
          "DevOps": 9,
          "Startups": 9,
        },
        tech_stack_analysis: [
          { technology: "React", companies_using: 78, match_score: 0.95, trend: "up" },
          { technology: "AWS", companies_using: 92, match_score: 0.88, trend: "stable" },
          { technology: "Python", companies_using: 67, match_score: 0.82, trend: "up" },
          { technology: "Docker", companies_using: 84, match_score: 0.79, trend: "up" },
          { technology: "Kubernetes", companies_using: 56, match_score: 0.76, trend: "up" },
          { technology: "TypeScript", companies_using: 71, match_score: 0.91, trend: "up" },
        ],
        culture_metrics: {
          work_life_balance: 0.78,
          innovation_focus: 0.85,
          team_collaboration: 0.82,
          growth_opportunities: 0.79,
          compensation_competitiveness: 0.81,
        },
      };

      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch company metrics:', error);
      setLoading(false);
    }
  };

  const industryColors = [
    '#1976d2', '#4caf50', '#ff9800', '#9c27b0', '#f44336',
    '#00bcd4', '#795548', '#607d8b', '#3f51b5', '#e91e63'
  ];

  const industryChartData = metrics ? {
    labels: Object.keys(metrics.industry_distribution),
    datasets: [
      {
        data: Object.values(metrics.industry_distribution),
        backgroundColor: industryColors,
        borderWidth: 0,
      },
    ],
  } : null;

  const techStackChartData = metrics ? {
    labels: metrics.tech_stack_analysis.map(tech => tech.technology),
    datasets: [
      {
        label: 'Companies Using',
        data: metrics.tech_stack_analysis.map(tech => tech.companies_using),
        backgroundColor: '#1976d2',
        borderColor: '#1976d2',
        borderWidth: 1,
        yAxisID: 'y',
      },
      {
        label: 'Match Score (%)',
        data: metrics.tech_stack_analysis.map(tech => tech.match_score * 100),
        backgroundColor: '#4caf50',
        borderColor: '#4caf50',
        borderWidth: 1,
        yAxisID: 'y1',
      },
    ],
  } : null;

  const techStackChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Technology Adoption vs Match Score',
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
          text: 'Companies Using',
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
          text: 'Match Score (%)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied': return '#4caf50';
      case 'interested': return '#ff9800';
      case 'researching': return '#2196f3';
      default: return '#757575';
    }
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
          Loading company analytics...
        </Typography>
      </Box>
    );
  }

  if (!metrics) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Failed to load company metrics
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Company Intelligence & Market Analysis
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BusinessIcon sx={{ mr: 2, color: '#1976d2' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.total_companies_analyzed}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Companies Analyzed
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
                <StarIcon sx={{ mr: 2, color: '#4caf50' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {(metrics.avg_culture_fit_score * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Culture Fit
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
                    {metrics.companies_with_openings}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    With Open Positions
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
                <AssessmentIcon sx={{ mr: 2, color: '#ff9800' }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {metrics.top_industry_match}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Top Industry Match
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
                Industry Distribution
              </Typography>
              {industryChartData && (
                <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                  <Doughnut 
                    data={industryChartData} 
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
                Technology Stack Analysis
              </Typography>
              {techStackChartData && (
                <Box sx={{ height: 300 }}>
                  <Bar 
                    data={techStackChartData} 
                    options={{
                      ...techStackChartOptions,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Culture Metrics and Top Companies */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Culture Fit Analysis
              </Typography>
              {Object.entries(metrics.culture_metrics).map(([metric, score], index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                      {metric.replace(/_/g, ' ')}
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {(score * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={score * 100}
                    sx={{ 
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: score > 0.8 ? '#4caf50' : score > 0.6 ? '#ff9800' : '#f44336',
                      }
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Top Target Companies
              </Typography>
              <List>
                {metrics.top_companies.map((company, index) => (
                  <ListItem key={index} sx={{ px: 0, py: 1 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: '#1976d2' }}>
                        {company.name.substring(0, 2).toUpperCase()}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {company.name}
                          </Typography>
                          <Chip
                            label={company.application_status}
                            size="small"
                            sx={{
                              backgroundColor: getStatusColor(company.application_status) + '20',
                              color: getStatusColor(company.application_status),
                            }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {company.industry} • {company.open_positions} open positions
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip
                              label={`${(company.culture_fit_score * 100).toFixed(0)}% culture fit`}
                              size="small"
                              variant="outlined"
                            />
                            <Chip
                              label={`${(company.tech_stack_match * 100).toFixed(0)}% tech match`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
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

export default CompanyAnalytics;
