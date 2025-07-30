#!/usr/bin/env python3
"""
Documentation Organization Script

This script reorganizes the scattered documentation files in the project root
into a well-structured hierarchy based on the Documentation Structure Plan.
"""

import os
import shutil
from pathlib import Path
import re

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"
PROJECT_DOCS_ROOT = PROJECT_ROOT / "project-docs"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
ASSETS_ROOT = PROJECT_ROOT / "assets"

# File mapping: current_filename -> new_location
FILE_MAPPINGS = {
    # Epic Documentation
    "DYNAMIC_RESUME_OPTIMIZER_REQUIREMENTS.md": "docs/epics/dynamic-resume-optimizer/requirements.md",
    "DYNAMIC_RESUME_OPTIMIZER_REQUIREMENTS_USER_MARKUP.md": "docs/epics/dynamic-resume-optimizer/user-markup.md",
    "EPIC_PERSONAL_CRM.md": "docs/epics/personal-crm/requirements.md",
    
    # Database Documentation
    "DATABASE_SCHEMA.md": "docs/database/schema-overview.md",
    "SUPABASE_CANDIDATE_PROFILE_SCHEMA.sql": "docs/database/tables/candidate-profile.sql",
    "supabase_resume_tables.sql": "docs/database/tables/core-resume-sections.sql",
    "EXECUTIVE_SUMMARY_SCHEMA.sql": "docs/database/tables/executive-summary.sql",
    "EDUCATION_SCHEMA.sql": "docs/database/tables/education.sql",
    "CERTIFICATIONS_SCHEMA.sql": "docs/database/tables/certifications.sql",
    "COMMUNITY_LEADERSHIP_SCHEMA.sql": "docs/database/tables/community-leadership.sql",
    "EARLY_CAREER_ROLES_SCHEMA.sql": "docs/database/tables/early-career-roles.sql",
    "ADDITIONAL_EXPERIENCE_SCHEMA.sql": "docs/database/tables/additional-experience.sql",
    "ENHANCED_CAREER_HIGHLIGHTS_SCHEMA.sql": "docs/database/tables/strategic-impact.sql",
    "ENHANCED_EMPLOYMENT_SCHEMA.sql": "docs/database/tables/employment-history.sql",
    
    # Deployment Documentation
    "DEPLOYMENT_CHECKLIST.md": "docs/deployment/checklist.md",
    "PRODUCTION_DEPLOYMENT_PLAN.md": "docs/deployment/production-setup.md",
    "RAILWAY_DEPLOYMENT_GUIDE.md": "docs/deployment/railway-guide.md",
    "RAILWAY_DEPLOYMENT_SUCCESS.md": "docs/deployment/railway-success.md",
    "PRODUCTION_ROADMAP.md": "project-docs/planning/roadmap.md",
    
    # Testing Documentation
    "REGRESSION_TEST_CASES.md": "docs/testing/regression-tests.md",
    "Regression_Test_Cases_Job_Search_Automation.md": "docs/testing/job-search-regression.md",
    "INTEGRATED_REGRESSION_TEST_SUITE.md": "docs/testing/integrated-suite.md",
    
    # Project Management
    "PLATFORM_SHOWCASE.md": "project-docs/business/platform-showcase.md",
    "CANDIDATE_PROFILE_DATA_STRUCTURE.md": "docs/architecture/candidate-profile-structure.md",
    "GITHUB_SYNC_STRATEGY.md": "project-docs/operations/github-sync.md",
    "SYNC_STATUS.md": "project-docs/operations/sync-status.md",
    "SECURITY_INCIDENT_RESPONSE.md": "project-docs/compliance/incident-response.md",
    
    # Job Board Integration
    "job_board_api_inventory.md": "docs/api/integrations/job-boards.md",
    
    # Contributing
    "CONTRIBUTING.md": "docs/contributing/development-setup.md",
    
    # Scripts (move to scripts directory)
    "check_git_sync.py": "scripts/utilities/check-git-sync.py",
    "diagnose_git_status.py": "scripts/utilities/diagnose-git-status.py",
    "sync_status.py": "scripts/utilities/sync-status.py",
    "test_supabase_connection.py": "scripts/testing/test-supabase-connection.py",
    "e2e_regression_test_suite.py": "scripts/testing/e2e-regression-suite.py",
    "e2e_test_config.py": "scripts/testing/e2e-test-config.py",
    "e2e_test_runner.py": "scripts/testing/e2e-test-runner.py",
    
    # Sample Data and Assets
    "Resume - Allen Walker.md": "assets/data/sample-data/allen-walker-resume.md",
    "allen_walker_job_report_20250725_145906.html": "assets/data/sample-data/job-report-sample.html",
    "candidate_profile_allen_walker_001_20250725_153124.json": "assets/data/sample-data/candidate-profile-sample.json",
    "updated_candidate_profile_data.json": "assets/data/sample-data/candidate-profile-updated.json",
}

# Directories to create
DIRECTORIES_TO_CREATE = [
    # Docs structure
    "docs/getting-started",
    "docs/architecture",
    "docs/epics/dynamic-resume-optimizer",
    "docs/epics/personal-crm",
    "docs/epics/resume-optimization",
    "docs/epics/personal-brand",
    "docs/epics/job-search-automation",
    "docs/epics/application-tracking",
    "docs/epics/mobile-networking",
    "docs/epics/company-enrichment",
    "docs/epics/ai-scoring",
    "docs/epics/analytics-dashboard",
    "docs/epics/workflow-orchestration",
    "docs/database/tables",
    "docs/database/migrations",
    "docs/database/functions",
    "docs/api/endpoints",
    "docs/api/integrations",
    "docs/deployment",
    "docs/testing",
    "docs/contributing",
    
    # Project docs structure
    "project-docs/business",
    "project-docs/planning/sprint-planning",
    "project-docs/planning/retrospectives",
    "project-docs/planning/decision-records",
    "project-docs/compliance",
    "project-docs/operations",
    
    # Scripts structure
    "scripts/build",
    "scripts/deployment",
    "scripts/database",
    "scripts/testing",
    "scripts/utilities",
    
    # Assets structure
    "assets/images/architecture-diagrams",
    "assets/images/ui-mockups",
    "assets/images/screenshots",
    "assets/templates/email-templates",
    "assets/templates/resume-templates",
    "assets/templates/document-templates",
    "assets/data/sample-data",
    "assets/data/test-fixtures",
    "assets/data/reference-data",
]

def create_directories():
    """Create the new directory structure."""
    print("Creating directory structure...")
    for directory in DIRECTORIES_TO_CREATE:
        dir_path = PROJECT_ROOT / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")

def move_files():
    """Move files according to the mapping."""
    print("\nMoving files to new locations...")
    moved_count = 0
    
    for old_file, new_location in FILE_MAPPINGS.items():
        old_path = PROJECT_ROOT / old_file
        new_path = PROJECT_ROOT / new_location
        
        if old_path.exists():
            # Ensure target directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(old_path), str(new_path))
            print(f"  Moved: {old_file} -> {new_location}")
            moved_count += 1
        else:
            print(f"  Warning: {old_file} not found")
    
    print(f"\nMoved {moved_count} files successfully.")

def create_index_files():
    """Create README.md index files for major sections."""
    print("\nCreating index files...")
    
    # Main docs README
    docs_readme = DOCS_ROOT / "README.md"
    docs_readme.write_text("""# Documentation

This directory contains all technical documentation for the AI-Powered Job Search Automation Platform.

## Structure

- **[Getting Started](getting-started/)** - Installation and quick start guides
- **[Architecture](architecture/)** - System architecture and design
- **[Epics](epics/)** - Feature-specific documentation
- **[Database](database/)** - Database schema and migrations
- **[API](api/)** - API documentation and integration guides
- **[Deployment](deployment/)** - Deployment procedures and configuration
- **[Testing](testing/)** - Test strategies and procedures
- **[Contributing](contributing/)** - Development guidelines

## Quick Links

- [Dynamic Resume Optimizer](epics/dynamic-resume-optimizer/requirements.md)
- [Personal CRM](epics/personal-crm/requirements.md)
- [Database Schema](database/schema-overview.md)
- [API Overview](api/overview.md)
- [Deployment Guide](deployment/production-setup.md)
""")
    
    # Project docs README
    project_docs_readme = PROJECT_DOCS_ROOT / "README.md"
    project_docs_readme.write_text("""# Project Documentation

This directory contains project management, business, and operational documentation.

## Structure

- **[Business](business/)** - Product strategy and market analysis
- **[Planning](planning/)** - Project planning and roadmaps
- **[Compliance](compliance/)** - Security and regulatory documentation
- **[Operations](operations/)** - Operational procedures and maintenance

## Quick Links

- [Product Strategy](business/product-strategy.md)
- [Roadmap](planning/roadmap.md)
- [Security Requirements](compliance/security-requirements.md)
- [Incident Response](compliance/incident-response.md)
""")
    
    # Scripts README
    scripts_readme = SCRIPTS_ROOT / "README.md"
    scripts_readme.write_text("""# Scripts

This directory contains build, deployment, and utility scripts.

## Structure

- **[Build](build/)** - Build and compilation scripts
- **[Deployment](deployment/)** - Deployment automation scripts
- **[Database](database/)** - Database management scripts
- **[Testing](testing/)** - Test execution scripts
- **[Utilities](utilities/)** - General utility scripts

## Usage

Most scripts can be run from the project root directory. See individual script documentation for specific usage instructions.
""")
    
    # Assets README
    assets_readme = ASSETS_ROOT / "README.md"
    assets_readme.write_text("""# Assets

This directory contains static assets and resources.

## Structure

- **[Images](images/)** - Diagrams, mockups, and screenshots
- **[Templates](templates/)** - Document and email templates
- **[Data](data/)** - Sample data and test fixtures

## Guidelines

- Keep file sizes reasonable for version control
- Use descriptive filenames
- Organize by purpose and type
""")
    
    print("  Created index README files")

def update_main_readme():
    """Update the main project README to reference the new structure."""
    print("\nUpdating main README...")
    
    main_readme = PROJECT_ROOT / "README.md"
    if main_readme.exists():
        content = main_readme.read_text()
        
        # Add documentation section if not present
        if "## Documentation" not in content:
            documentation_section = """

## Documentation

This project uses a structured documentation approach:

- **[Technical Documentation](docs/)** - Architecture, APIs, deployment guides
- **[Project Documentation](project-docs/)** - Business strategy, planning, compliance
- **[Scripts](scripts/)** - Build, deployment, and utility scripts
- **[Assets](assets/)** - Static resources and sample data

### Quick Start
- [Installation Guide](docs/getting-started/installation.md)
- [API Documentation](docs/api/overview.md)
- [Database Schema](docs/database/schema-overview.md)

### Key Features
- [Dynamic Resume Optimizer](docs/epics/dynamic-resume-optimizer/requirements.md)
- [Personal CRM](docs/epics/personal-crm/requirements.md)
- [AI Scoring Engine](docs/epics/ai-scoring/requirements.md)
"""
            
            # Insert before the last section (usually license or contributing)
            lines = content.split('\n')
            insert_index = len(lines) - 10  # Insert near the end
            lines.insert(insert_index, documentation_section)
            
            main_readme.write_text('\n'.join(lines))
            print("  Updated main README with documentation links")

def create_gitkeep_files():
    """Create .gitkeep files in empty directories."""
    print("\nCreating .gitkeep files for empty directories...")
    
    for directory in DIRECTORIES_TO_CREATE:
        dir_path = PROJECT_ROOT / directory
        if dir_path.exists() and not any(dir_path.iterdir()):
            gitkeep = dir_path / ".gitkeep"
            gitkeep.write_text("")
            print(f"  Created .gitkeep in {directory}")

def main():
    """Main execution function."""
    print("=== Documentation Organization Script ===")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        create_directories()
        move_files()
        create_index_files()
        update_main_readme()
        create_gitkeep_files()
        
        print("\n=== Organization Complete! ===")
        print("\nNext steps:")
        print("1. Review moved files and update any broken internal links")
        print("2. Update Docusaurus configuration to reflect new structure")
        print("3. Create missing documentation files as needed")
        print("4. Commit changes to version control")
        
    except Exception as e:
        print(f"\nError during organization: {e}")
        print("Please review and fix any issues before proceeding.")

if __name__ == "__main__":
    main()
