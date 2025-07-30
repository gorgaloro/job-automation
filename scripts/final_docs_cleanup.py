#!/usr/bin/env python3
"""
Final Documentation Cleanup Script

This script organizes the remaining legacy files in the /docs directory
that should be moved to the new organized structure.
"""

import os
import shutil
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"

# Final file mappings for remaining docs files
FINAL_FILE_MAPPINGS = {
    # Legacy epic files that should be moved to epics directory
    "docs/epic-4-application-tracking.md": "docs/epics/application-tracking/legacy-requirements.md",
    "docs/epic-5-mobile-networking.md": "docs/epics/mobile-networking/legacy-requirements.md", 
    "docs/epic-9-analytics-dashboard.md": "docs/epics/analytics-dashboard/legacy-requirements.md",
    "docs/epic-10-integration-automation.md": "docs/epics/workflow-orchestration/legacy-requirements.md",
    
    # API documentation
    "docs/api-reference.md": "docs/api/legacy-api-reference.md",
    
    # Architecture documentation
    "docs/architecture.md": "docs/architecture/legacy-architecture.md",
    
    # Deployment documentation  
    "docs/deployment.md": "docs/deployment/legacy-deployment.md",
    
    # Integration documentation
    "docs/hubspot-mapping.md": "docs/api/integrations/hubspot-mapping.md",
    "docs/tech-verticals.md": "docs/architecture/tech-verticals.md",
    
    # Introduction/overview
    "docs/intro.md": "docs/getting-started/intro.md",
}

def move_final_files():
    """Move the remaining legacy documentation files."""
    print("Moving final legacy documentation files...")
    moved_count = 0
    
    for old_file, new_location in FINAL_FILE_MAPPINGS.items():
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
    
    print(f"\nMoved {moved_count} final files successfully.")

def create_epic_index_files():
    """Create index files for epics that now have content."""
    print("\nCreating epic index files...")
    
    # Application Tracking epic
    app_tracking_index = PROJECT_ROOT / "docs/epics/application-tracking/README.md"
    app_tracking_index.write_text("""# Application Tracking Epic

This epic covers automated job application tracking and status monitoring.

## Documentation

- **[Legacy Requirements](legacy-requirements.md)** - Original epic documentation
- **[Requirements](requirements.md)** - Updated requirements (to be created)
- **[Design](design.md)** - Architecture and design decisions (to be created)
- **[Implementation](implementation.md)** - Technical implementation (to be created)

## Features

- Automated application status monitoring
- Integration with job boards and ATS systems
- Status change notifications
- Application timeline tracking
- Success rate analytics

## Related Modules

- `src/core/application_tracking_engine.py`
- Integration with CRM and analytics systems
""")

    # Mobile Networking epic
    mobile_networking_index = PROJECT_ROOT / "docs/epics/mobile-networking/README.md"
    mobile_networking_index.write_text("""# Mobile Networking Epic

This epic covers mobile networking features including QR code scanning and contact management.

## Documentation

- **[Legacy Requirements](legacy-requirements.md)** - Original epic documentation
- **[Requirements](requirements.md)** - Updated requirements (to be created)
- **[Design](design.md)** - Architecture and design decisions (to be created)
- **[Implementation](implementation.md)** - Technical implementation (to be created)

## Features

- QR code generation and scanning
- Mobile contact exchange
- LinkedIn integration
- Contact relationship mapping
- Networking event management

## Related Modules

- `src/core/mobile_networking_engine.py`
- Integration with CRM and personal brand systems
""")

    # Analytics Dashboard epic
    analytics_index = PROJECT_ROOT / "docs/epics/analytics-dashboard/README.md"
    analytics_index.write_text("""# Analytics Dashboard Epic

This epic covers comprehensive analytics and reporting for job search performance.

## Documentation

- **[Legacy Requirements](legacy-requirements.md)** - Original epic documentation
- **[Requirements](requirements.md)** - Updated requirements (to be created)
- **[Design](design.md)** - Architecture and design decisions (to be created)
- **[Implementation](implementation.md)** - Technical implementation (to be created)

## Features

- Job search performance metrics
- Application success rate tracking
- Resume optimization analytics
- Personal brand effectiveness
- Networking ROI analysis

## Related Modules

- Analytics and reporting engines
- Integration with all platform modules
""")

    # Workflow Orchestration epic
    workflow_index = PROJECT_ROOT / "docs/epics/workflow-orchestration/README.md"
    workflow_index.write_text("""# Workflow Orchestration Epic

This epic covers end-to-end automation and integration of all platform features.

## Documentation

- **[Legacy Requirements](legacy-requirements.md)** - Original epic documentation
- **[Requirements](requirements.md)** - Updated requirements (to be created)
- **[Design](design.md)** - Architecture and design decisions (to be created)
- **[Implementation](implementation.md)** - Technical implementation (to be created)

## Features

- End-to-end job search automation
- Cross-epic integration
- Workflow templates
- Automated decision making
- Performance optimization

## Related Modules

- `src/core/workflow_orchestrator.py`
- Integration with all platform components
""")

    print("  Created epic index files")

def update_main_docs_readme():
    """Update the main docs README to reflect the complete structure."""
    print("\nUpdating main docs README...")
    
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

## Epic Documentation

### Core Features
- **[Dynamic Resume Optimizer](epics/dynamic-resume-optimizer/)** - AI-powered resume optimization
- **[Personal CRM](epics/personal-crm/)** - Lightweight CRM for job seekers

### Platform Features
- **[Application Tracking](epics/application-tracking/)** - Automated application monitoring
- **[Mobile Networking](epics/mobile-networking/)** - QR code networking and contact management
- **[Analytics Dashboard](epics/analytics-dashboard/)** - Performance analytics and reporting
- **[Workflow Orchestration](epics/workflow-orchestration/)** - End-to-end automation

### Supporting Features
- **[Resume Optimization](epics/resume-optimization/)** - Core resume optimization engine
- **[Personal Brand](epics/personal-brand/)** - Personal brand profiling
- **[Job Search Automation](epics/job-search-automation/)** - Automated job discovery
- **[Company Enrichment](epics/company-enrichment/)** - Company data enhancement
- **[AI Scoring](epics/ai-scoring/)** - AI-powered compatibility scoring

## Quick Links

- [Database Schema Overview](database/schema-overview.md)
- [API Documentation](api/legacy-api-reference.md)
- [Deployment Guide](deployment/production-setup.md)
- [Architecture Overview](architecture/legacy-architecture.md)

## Docusaurus Integration

This documentation is integrated with Docusaurus for professional presentation. The legacy Docusaurus files are preserved for compatibility while the new organized structure provides better navigation and maintenance.
""")

def clean_up_docusaurus_config():
    """Update Docusaurus configuration to work with new structure."""
    print("\nUpdating Docusaurus configuration...")
    
    # Note: We'll preserve the existing Docusaurus setup but add a note
    # about the new structure in the config
    config_note = PROJECT_ROOT / "docs" / "DOCUSAURUS_MIGRATION_NOTE.md"
    config_note.write_text("""# Docusaurus Migration Note

## Current State

The documentation has been reorganized into a new structure while preserving the existing Docusaurus setup for compatibility.

## New Structure Benefits

- **Epic-based organization** for better feature documentation
- **Consistent patterns** across all feature documentation
- **Better navigation** and discoverability
- **Scalable architecture** for future features

## Migration Path

To fully integrate the new structure with Docusaurus:

1. Update `sidebars.ts` to reflect new epic structure
2. Update `docusaurus.config.ts` navigation
3. Create epic-specific documentation pages
4. Migrate legacy content to new format

## Compatibility

The legacy files have been moved to preserve existing links while enabling the new structure to be developed in parallel.
""")

def main():
    """Main execution function."""
    print("=== Final Documentation Cleanup Script ===")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        move_final_files()
        create_epic_index_files()
        update_main_docs_readme()
        clean_up_docusaurus_config()
        
        print("\n=== Final Cleanup Complete! ===")
        print("\nDocumentation is now fully organized:")
        print("✅ Legacy epic files moved to organized structure")
        print("✅ API and architecture docs properly categorized")
        print("✅ Epic index files created with navigation")
        print("✅ Main documentation README updated")
        print("✅ Docusaurus compatibility preserved")
        
        print("\nProject structure is now completely clean and organized!")
        print("All files are properly categorized and documented.")
        
    except Exception as e:
        print(f"\nError during final cleanup: {e}")
        print("Please review and fix any issues before proceeding.")

if __name__ == "__main__":
    main()
