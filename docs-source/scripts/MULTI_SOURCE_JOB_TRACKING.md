# Multi-Source Job Tracking & Analysis Scripts

## Overview

This document outlines the scripts and processes needed to identify duplicate jobs across multiple sources (LinkedIn, Indeed, company career pages, etc.) and analyze content deltas between primary and secondary sources.

## Key Concepts

### Source Classification
- **Primary Sources**: Company career pages, official ATS systems (Greenhouse, Lever, etc.)
- **Secondary Sources**: Job boards (LinkedIn, Indeed, Glassdoor, etc.)

### Data Flow
1. **Job Discovery**: Jobs identified through various sources
2. **Source Classification**: Determine primary vs secondary source
3. **Duplicate Detection**: Identify same job posted across multiple platforms
4. **Delta Analysis**: Compare content differences between sources
5. **Quality Assessment**: Evaluate company HR quality based on source consistency

## Required Scripts

### 1. Duplicate Detection Script

**Purpose**: Identify jobs posted across multiple platforms

**Script**: `run_duplicate_detection_script()`

**Process**:
```python
from src.core.multi_source_job_detector import run_duplicate_detection_script

# Example usage
job_sources = [...]  # List of JobSource objects
results = run_duplicate_detection_script(job_sources)

print(f"Found {results['duplicates_found']} duplicate job pairs")
```

**Output**:
- Total sources analyzed
- Number of duplicate pairs found
- Similarity scores for each duplicate pair
- Platform mapping for duplicates

### 2. Delta Analysis Script

**Purpose**: Analyze content differences between primary and secondary sources

**Script**: `run_delta_analysis_script()`

**Process**:
```python
from src.core.multi_source_job_detector import run_delta_analysis_script

# Example usage
job_sources = [...]  # List of JobSource objects with primary/secondary mix
results = run_delta_analysis_script(job_sources)

print(f"Average similarity: {results['avg_similarity_score']:.2%}")
print(f"Outdated secondaries: {results['outdated_secondaries']}")
```

**Output**:
- Average similarity scores across all source pairs
- Count of outdated secondary sources
- Breakdown by delta status (identical, minor differences, content drift, etc.)
- Poor sync indicators

### 3. Company Source Quality Analysis Script

**Purpose**: Evaluate company-level HR quality based on source management

**Script**: `MultiSourceJobDetector.analyze_company_sources()`

**Process**:
```python
from src.core.multi_source_job_detector import MultiSourceJobDetector

detector = MultiSourceJobDetector()
company_analytics = detector.analyze_company_sources(
    company_id="company_123",
    company_name="TechCorp Inc",
    job_sources=company_job_sources
)

print(f"HR Quality Score: {company_analytics.hr_quality_score:.2f}")
print(f"Content Consistency: {company_analytics.content_consistency_score:.2%}")
```

**Output**:
- HR quality score (0.0-1.0)
- Content consistency metrics
- Platform usage analysis
- Red flags and quality indicators

### 4. Cross-Platform Job Linking Script

**Purpose**: Link related job postings across platforms for the same position

**Database Function**: `detect_cross_source_duplicates()`

**Process**:
```sql
-- Detect potential duplicates for a specific company
SELECT * FROM detect_cross_source_duplicates('company_uuid', 0.85);

-- Detect duplicates across all companies
SELECT * FROM detect_cross_source_duplicates(NULL, 0.85);
```

**Output**:
- Job pairs that are likely duplicates
- Source IDs for each duplicate
- Similarity scores
- Duplicate confidence levels

## Implementation Workflow

### Phase 1: Data Collection
1. **Source Discovery**: Identify all platforms where jobs are posted
2. **Content Extraction**: Extract job details from each source
3. **Source Classification**: Label as primary or secondary
4. **Fingerprint Generation**: Create content hashes for duplicate detection

### Phase 2: Analysis
1. **Duplicate Detection**: Run similarity analysis across sources
2. **Delta Analysis**: Compare primary vs secondary content
3. **Quality Scoring**: Calculate company-level HR quality metrics
4. **Flag Generation**: Identify problematic patterns

### Phase 3: Reporting
1. **Company Scorecards**: HR quality assessments per company
2. **Platform Analysis**: Usage patterns and reliability scores
3. **Delta Reports**: Content consistency analysis
4. **Quality Alerts**: Automated flags for poor source management

## Database Schema Integration

### Core Tables
- `job_sources`: All job posting sources
- `job_source_deltas`: Content differences between sources
- `company_source_analytics`: Company-level quality metrics
- `source_discovery_log`: Audit trail of source discovery

### Key Functions
- `calculate_content_fingerprint()`: Generate content hashes
- `identify_primary_source()`: Determine authoritative source
- `calculate_company_hr_quality_score()`: Quality assessment
- `detect_cross_source_duplicates()`: Find duplicate jobs

## Quality Indicators

### HR Quality Red Flags
- **Missing Primary Sources**: Jobs only found on secondary platforms
- **Poor Content Consistency**: Significant differences between sources
- **Frequent Outdated Secondaries**: Secondary sources not updated
- **Poor Sync Quality**: Regular content drift between sources

### Delta Status Classifications
- **Identical**: Content matches exactly (similarity ≥ 0.98)
- **Minor Differences**: Small formatting variations (0.90-0.98)
- **Content Drift**: Meaningful differences (0.75-0.90)
- **Major Discrepancy**: Significant content differences (0.50-0.75)
- **Outdated Secondary**: Secondary appears stale (< 0.50)

## Automation Schedule

### Daily Tasks
- Run duplicate detection on new job postings
- Analyze deltas for jobs with multiple sources
- Update company quality scores
- Generate alerts for significant quality issues

### Weekly Tasks
- Comprehensive company source analysis
- Platform reliability assessment
- Quality trend reporting
- Source discovery optimization

### Monthly Tasks
- Full database delta analysis
- Company quality scorecard generation
- Platform usage analytics
- Source management best practices reporting

## Example Use Cases

### Use Case 1: Job Application Prioritization
```python
# Get company quality score before applying
company_analytics = detector.analyze_company_sources(company_id, company_name, sources)

if company_analytics.hr_quality_score < 0.5:
    print("⚠️ WARNING: Company has poor source management - may indicate HR dysfunction")
elif 'frequent_outdated_secondaries' in company_analytics.source_management_flags:
    print("📋 NOTE: Company may have outdated job postings on secondary platforms")
```

### Use Case 2: Source Reliability Assessment
```python
# Analyze which platforms provide most accurate job information
report = detector.generate_source_analysis_report(all_companies_analytics)

for platform, usage in report['platform_usage'].items():
    reliability = detector.platform_reliability.get(platform, 0.5)
    print(f"{platform}: {usage} companies, {reliability:.1%} reliability")
```

### Use Case 3: Content Freshness Monitoring
```python
# Identify jobs with stale secondary sources
deltas = run_delta_analysis_script(job_sources)

outdated_jobs = [d for d in deltas['delta_breakdown'] if d == 'outdated_secondary']
print(f"Found {len(outdated_jobs)} jobs with outdated secondary sources")
```

## Integration Points

### Job Discovery Pipeline
- Integrate source classification into job ingestion
- Automatically detect primary sources during scraping
- Flag potential duplicates during initial processing

### Application Compiler
- Use primary source content for application generation
- Flag inconsistencies between sources
- Prioritize most reliable source for job details

### Company Enrichment
- Include source quality metrics in company profiles
- Use HR quality scores for company assessment
- Flag companies with poor source management

### Monitoring Dashboard
- Display source quality metrics
- Show platform usage analytics
- Alert on quality degradation trends

This multi-source tracking system provides comprehensive insights into job posting quality and company HR practices, enabling more informed application decisions and better job market intelligence.
