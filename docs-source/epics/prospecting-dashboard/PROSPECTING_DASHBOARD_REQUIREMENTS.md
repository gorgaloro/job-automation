# Prospecting Dashboard Requirements

## Overview
The Prospecting Dashboard is an AI-powered interface that enables users to discover and take action on matching companies and job opportunities through workflow-enabled search results with multi-select bulk operations.

## Core Functionality

### 1. AI-Powered Search
- **Universal Search Bar**: Single input field for natural language queries
- **Saved Prompts**: Quick-access buttons for common search patterns
- **Real-time Results**: Dynamic display of matching companies and jobs
- **Search Metadata**: Display search time, result counts, and query context

### 2. Two-Column Result Layout

#### Company Results (Left Column)
- **Result Count**: Display number of matching companies
- **Search Time**: Show query execution time
- **Company Rows**: Each result displays:
  - Multi-select checkbox
  - Company name and match percentage
  - Sector, funding stage, employee count
  - Relevant tags (Fast Growing, Remote-First, etc.)
  - Workflow action buttons

#### Job Results (Right Column)
- **Result Count**: Display number of matching jobs
- **Search Time**: Show query execution time
- **Job Rows**: Each result displays:
  - Multi-select checkbox
  - Job title and match percentage
  - Company, location, salary range
  - Posting date and relevant tags
  - Workflow action buttons

### 3. Workflow Actions

#### Company Workflows
- **Add to HubSpot** (Primary): Launch company enrichment workflow
- **Add to Worklist** (Secondary): Save company for later research
- **Multi-select Support**: Bulk operations for selected companies

#### Job Workflows
- **Apply** (Primary): Launch Application Compiler workflow
- **Save to Worklist** (Secondary): Save job for later application
- **Multi-select Support**: Bulk operations for selected jobs

### 4. Multi-Select & Bulk Operations

#### Selection Management
- **Individual Checkboxes**: Select/deselect individual results
- **Visual Feedback**: Highlight selected rows
- **Selection Counter**: Display number of selected items

#### Bulk Action Bars
- **Company Bulk Actions**:
  - Bulk add to HubSpot
  - Bulk add to worklist
  - Clear selection
- **Job Bulk Actions**:
  - Bulk save to worklist
  - Clear selection

### 5. User Feedback & Notifications
- **Real-time Notifications**: Immediate feedback for all workflow actions
- **Loading States**: Visual indicators during search and workflow execution
- **Success/Error Messages**: Clear status communication

## Data Requirements

### Company Data Structure
```json
{
  "id": "string",
  "name": "string",
  "sector": "string",
  "funding": "string",
  "employees": "string",
  "score": "number (0-100)",
  "tags": ["string"],
  "location": "string",
  "description": "string"
}
```

### Job Data Structure
```json
{
  "id": "string",
  "title": "string",
  "company": "string",
  "location": "string",
  "salary": "string",
  "posted": "string",
  "score": "number (0-100)",
  "tags": ["string"],
  "description": "string",
  "requirements": ["string"]
}
```

### Search Metadata
```json
{
  "query": "string",
  "searchTime": "string",
  "companyCount": "number",
  "jobCount": "number",
  "timestamp": "string"
}
```

## API Requirements

### Search Endpoint
- **POST /api/search/prospecting**
- **Input**: Natural language query
- **Output**: Companies and jobs with relevance scores

### Workflow Endpoints
- **POST /api/workflows/company/hubspot**: Add company to HubSpot
- **POST /api/workflows/company/worklist**: Add company to worklist
- **POST /api/workflows/job/apply**: Launch job application workflow
- **POST /api/workflows/job/worklist**: Save job to worklist

### Bulk Operation Endpoints
- **POST /api/workflows/bulk/companies/hubspot**: Bulk add companies to HubSpot
- **POST /api/workflows/bulk/companies/worklist**: Bulk add companies to worklist
- **POST /api/workflows/bulk/jobs/worklist**: Bulk save jobs to worklist

## UI/UX Requirements

### Visual Design
- **Two-column layout** with consistent styling
- **Purple gradient theme** matching overall dashboard design
- **Row-based results** with clear visual hierarchy
- **Responsive design** for various screen sizes

### Interaction Patterns
- **Hover effects** on rows and buttons
- **Visual selection feedback** with border/background changes
- **Contextual bulk action bars** that appear when items are selected
- **Smooth animations** for state transitions

### Accessibility
- **Keyboard navigation** support
- **Screen reader compatibility**
- **High contrast ratios** for text and backgrounds
- **Focus indicators** for interactive elements

## Integration Requirements

### External Systems
- **HubSpot API**: Company enrichment and CRM integration
- **Application Compiler**: Job application workflow integration
- **Worklist Management**: Personal task/research list management
- **AI Search Engine**: Natural language query processing

### Internal Systems
- **User Authentication**: Session management and permissions
- **Notification System**: Real-time user feedback
- **Analytics Tracking**: User interaction and workflow metrics
- **Data Storage**: Search history and user preferences

## Performance Requirements
- **Search Response Time**: < 2 seconds for typical queries
- **UI Responsiveness**: < 100ms for interaction feedback
- **Concurrent Users**: Support 100+ simultaneous searches
- **Data Freshness**: Job/company data updated daily

## Security Requirements
- **Input Validation**: Sanitize all search queries
- **Rate Limiting**: Prevent search abuse
- **Data Privacy**: Secure handling of user search history
- **API Authentication**: Secure workflow endpoint access

## Future Enhancements
- **Advanced Filters**: Industry, location, company size filters
- **Saved Searches**: Persistent search queries with alerts
- **Export Functionality**: CSV/PDF export of search results
- **Integration Expansion**: Additional CRM and job board APIs
