# Job Worklist - Requirements & Design

## Overview
The Job Worklist feature enables users to flag jobs for later review and application across the platform. This integrates with the existing job applications system to provide a unified job tracking experience.

## Core Requirements

### 1. Worklist Status Integration
- **Extend ApplicationStatus enum** to include `WORKLIST = "worklist"`
- **Jobs in worklist** are JobApplication records with `status = WORKLIST`
- **No application submission** required - jobs can be added directly to worklist
- **Seamless progression** from worklist → applied → interview → offer/rejection

### 2. Add to Worklist Functionality
- **"Add to Worklist" button** on job listings throughout the platform
- **Bulk "Add to Worklist"** for multiple jobs simultaneously
- **Quick add from search results** in Prospecting Dashboard
- **Add from job board integrations** (Indeed, Greenhouse, etc.)
- **Add from company research** when discovering interesting roles

### 3. Worklist Management Interface
- **Dedicated worklist page** showing all flagged jobs
- **Sortable columns**: Company, Role, Date Added, Salary, Location, Match Score
- **Filterable views**: By company, role type, salary range, location, date range
- **Bulk actions**: Remove from worklist, move to applied, export
- **Individual actions**: View details, apply now, remove, add notes

### 4. Worklist Analytics
- **Worklist size tracking** - total jobs saved over time
- **Conversion metrics** - worklist → application rate
- **Time in worklist** - how long jobs stay before action
- **Top companies/roles** - most frequently saved positions
- **Deadline tracking** - application deadlines for worklist jobs

## Technical Implementation

### 1. Database Schema Updates
```sql
-- Extend ApplicationStatus enum
ALTER TYPE application_status ADD VALUE 'worklist';

-- Add worklist-specific fields to job_applications table
ALTER TABLE job_applications ADD COLUMN worklist_added_at TIMESTAMP;
ALTER TABLE job_applications ADD COLUMN worklist_notes TEXT;
ALTER TABLE job_applications ADD COLUMN application_deadline DATE;
ALTER TABLE job_applications ADD COLUMN priority_level INTEGER DEFAULT 3; -- 1=high, 2=medium, 3=low
```

### 2. API Endpoints
```
POST   /api/v1/worklist/add              # Add job to worklist
POST   /api/v1/worklist/bulk-add         # Bulk add jobs to worklist
GET    /api/v1/worklist                  # Get user's worklist
DELETE /api/v1/worklist/{job_id}         # Remove from worklist
PUT    /api/v1/worklist/{job_id}         # Update worklist job (notes, priority)
POST   /api/v1/worklist/{job_id}/apply   # Move from worklist to applied
GET    /api/v1/worklist/analytics        # Worklist analytics
```

### 3. Frontend Integration Points
- **Prospecting Dashboard**: "Save to Worklist" buttons on job results
- **Job Discovery Pages**: "Add to Worklist" on individual job listings
- **Company Research**: "Save Interesting Roles" during company analysis
- **Job Board Integrations**: "Worklist" option alongside "Apply Now"
- **Dedicated Worklist Page**: Full management interface

## User Experience Flow

### 1. Adding Jobs to Worklist
```
User sees interesting job → Clicks "Add to Worklist" → 
Job saved with WORKLIST status → Success notification → 
Job appears in worklist dashboard
```

### 2. Managing Worklist
```
User opens worklist → Reviews saved jobs → 
Filters/sorts by criteria → Takes action:
- Apply now (launches Application Compiler)
- Remove from worklist
- Add notes/priority
- Set application deadline reminder
```

### 3. Bulk Operations
```
User selects multiple jobs → Chooses bulk action:
- Bulk remove from worklist
- Bulk move to applied
- Bulk export to CSV
- Bulk update priority/deadline
```

## Data Structure

### JobApplication with Worklist Fields
```python
@dataclass
class JobApplication:
    # Existing fields...
    status: ApplicationStatus = ApplicationStatus.WORKLIST
    worklist_added_at: Optional[str] = None
    worklist_notes: Optional[str] = None
    application_deadline: Optional[str] = None
    priority_level: int = 3  # 1=high, 2=medium, 3=low
```

### Worklist-Specific Models
```python
@dataclass
class WorklistJob:
    """Simplified view for worklist display"""
    job_id: str
    job_title: str
    company_name: str
    location: str
    salary_range: Optional[str]
    match_score: Optional[float]
    added_date: str
    priority_level: int
    application_deadline: Optional[str]
    notes: Optional[str]
    job_url: Optional[str]

@dataclass
class WorklistAnalytics:
    """Worklist analytics data"""
    total_jobs: int
    jobs_added_this_week: int
    jobs_applied_this_week: int
    conversion_rate: float
    average_time_in_worklist_days: float
    top_companies: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
```

## Integration with Existing Systems

### 1. Prospecting Dashboard
- **"Save to Worklist" buttons** on company and job result rows
- **Bulk worklist actions** in multi-select operations
- **Worklist count indicator** in dashboard metrics

### 2. Application Compiler
- **"Apply from Worklist"** entry point
- **Pre-populated job data** from worklist record
- **Automatic status update** from WORKLIST → SUBMITTED

### 3. HubSpot Integration
- **Company enrichment** for worklist jobs
- **Deal creation** when moving from worklist to applied
- **Activity tracking** for worklist management actions

### 4. Notification System
- **Application deadline reminders** for worklist jobs
- **Weekly worklist summary** emails
- **Conversion milestone notifications** (e.g., "10 jobs applied from worklist this month")

## Reporting & Analytics

### 1. Worklist Dashboard Metrics
- **Current worklist size** with trend indicators
- **Weekly add/apply rates** with conversion percentages
- **Average time in worklist** before action
- **Top saved companies/roles** for pattern recognition

### 2. Worklist Reports
- **Worklist Summary Report**: All jobs with key details
- **Deadline Report**: Jobs with upcoming application deadlines
- **Conversion Report**: Worklist → application → interview → offer funnel
- **Company Analysis**: Which companies have most worklisted jobs

### 3. Export Capabilities
- **CSV export** of entire worklist with all fields
- **PDF report** with formatted job summaries
- **Integration export** to external tools (Notion, Airtable, etc.)

## Success Metrics

### User Engagement
- **Worklist adoption rate**: % of users who use worklist feature
- **Jobs per worklist**: Average number of jobs saved per user
- **Worklist activity**: Frequency of adds/removes/updates
- **Conversion rate**: % of worklist jobs that get applied to

### Business Impact
- **Application volume**: Increase in total applications via worklist
- **Application quality**: Success rate of worklist-originated applications
- **User retention**: Impact on platform engagement and return visits
- **Time to apply**: Reduction in time from job discovery to application

## Future Enhancements

### Phase 2 Features
- **Smart recommendations**: AI-suggested jobs based on worklist patterns
- **Deadline automation**: Auto-apply before deadlines with user approval
- **Collaborative worklists**: Share interesting jobs with mentors/peers
- **Integration with calendar**: Schedule application time blocks

### Phase 3 Features
- **Advanced analytics**: ML-powered insights on worklist patterns
- **Automated follow-up**: Smart reminders based on application status
- **Portfolio integration**: Match worklist jobs with relevant portfolio pieces
- **Network integration**: Connect worklist jobs with LinkedIn contacts

## Implementation Priority

### Phase 1 (Week 1-2): Core Functionality
1. Extend ApplicationStatus enum with WORKLIST
2. Update database schema with worklist fields
3. Implement basic add/remove worklist functionality
4. Create simple worklist view page

### Phase 2 (Week 3-4): Enhanced Features
1. Build comprehensive worklist management interface
2. Add bulk operations and filtering
3. Implement worklist analytics dashboard
4. Integrate with Prospecting Dashboard

### Phase 3 (Week 5-6): Advanced Features
1. Add deadline tracking and notifications
2. Implement export and reporting capabilities
3. Build worklist-specific API endpoints
4. Add integration with Application Compiler workflow

This approach leverages your existing robust job applications infrastructure while adding the worklist functionality you need. The beauty is that it's just another status in your existing system, making it simple to implement and maintain while providing powerful job management capabilities.
