#!/usr/bin/env python3
"""
Enhanced Documentation Organization Script - Phase 2

This script organizes the remaining scattered files in the project root
including demo scripts, HTML pages, server files, and other development assets.
"""

import os
import shutil
from pathlib import Path
import re

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent

# Additional file mappings for remaining files
REMAINING_FILE_MAPPINGS = {
    # Demo Scripts - organize by epic/functionality
    "demo_ai_scoring.py": "demos/epics/ai-scoring/demo.py",
    "demo_candidate_profile.py": "demos/epics/candidate-profile/demo.py",
    "demo_company_enrichment.py": "demos/epics/company-enrichment/demo.py",
    "demo_epic10_workflow_orchestration.py": "demos/epics/workflow-orchestration/demo.py",
    "demo_epic4_application_tracking.py": "demos/epics/application-tracking/demo.py",
    "demo_epic5_mobile_networking.py": "demos/epics/mobile-networking/demo.py",
    "demo_epic9_analytics_dashboard.py": "demos/epics/analytics-dashboard/demo.py",
    "demo_job_applications.py": "demos/core/job-applications/basic-demo.py",
    "demo_job_applications_api.py": "demos/core/job-applications/api-demo.py",
    "demo_job_applications_service.py": "demos/core/job-applications/service-demo.py",
    "demo_job_parser.py": "demos/core/job-parser/demo.py",
    "demo_new_integrations.py": "demos/integrations/new-apis/demo.py",
    "demo_personal_brand.py": "demos/epics/personal-brand/demo.py",
    "demo_resume_optimizer.py": "demos/epics/resume-optimizer/demo.py",
    "demo_resume_simple.py": "demos/epics/resume-optimizer/simple-demo.py",
    "demo_simple.py": "demos/core/simple-platform-demo.py",
    "micross_demo_simple.py": "demos/scenarios/micross-components/demo.py",
    "showcase_platform_demo.py": "demos/showcase/platform-demo.py",
    "simple_candidate_profile_demo.py": "demos/epics/candidate-profile/simple-demo.py",
    "simple_test.py": "demos/testing/simple-integration-test.py",
    
    # HTML Pages - organize by purpose
    "dynamic_resume_optimizer.html": "frontend/pages/dynamic-resume-optimizer.html",
    "dynamic_resume_optimizer_clean.html": "frontend/pages/dynamic-resume-optimizer-clean.html",
    "candidate_profile_dashboard.html": "frontend/pages/candidate-profile-dashboard.html",
    "updated_candidate_profile_dashboard.html": "frontend/pages/candidate-profile-dashboard-v2.html",
    "showcase.html": "frontend/pages/platform-showcase.html",
    
    # Server Files - organize by purpose and status
    "dynamic_resume_server.py": "servers/dynamic-resume/main-server.py",
    "working_server.py": "servers/dynamic-resume/working-server.py",
    "quick_fix_server.py": "servers/dynamic-resume/quick-fix-server.py",
    "quick_server.py": "servers/utilities/quick-server.py",
    "simple_server.py": "servers/utilities/simple-server.py",
    "simple_resume_server.py": "servers/dynamic-resume/simple-resume-server.py",
    "simple_resume_server_with_baseline.py": "servers/dynamic-resume/baseline-server.py",
    "resume_optimizer_server.py": "servers/resume-optimizer/main-server.py",
    "resume_optimizer_server_corrected.py": "servers/resume-optimizer/corrected-server.py",
    "resume_optimizer_server_fixed.py": "servers/resume-optimizer/fixed-server.py",
    "resume_optimizer_server_fixed_final.py": "servers/resume-optimizer/final-server.py",
    "resume_optimizer_server_fixed_structure.py": "servers/resume-optimizer/structured-server.py",
    "simple_api.py": "servers/utilities/simple-api.py",
    
    # Data Processing and Utilities
    "resume_data_processor.py": "src/utilities/resume-data-processor.py",
    "resume_data_processor_real.py": "src/utilities/resume-data-processor-real.py",
    "supabase_writer.py": "src/utilities/supabase-writer.py",
    "hubspot_client.py": "src/integrations/hubspot/client.py",
    "hubspot_transform.py": "src/integrations/hubspot/transform.py",
    
    # Testing Files
    "test_complete_live_integration.py": "tests/integration/complete-live-test.py",
    "test_live_integration.py": "tests/integration/live-test.py",
    "test_micross_scenario.py": "tests/scenarios/micross-test.py",
    "test_tech_mapping.py": "tests/unit/tech-mapping-test.py",
    "integrated_resume_test.py": "tests/integration/resume-test.py",
    
    # Mapping and Industry Scripts
    "ai_map_industry.py": "src/utilities/ai-map-industry.py",
    "ai_score_verticals.py": "src/utilities/ai-score-verticals.py",
    "map_industry.py": "src/utilities/map-industry.py",
    "sync_tech_verticals.py": "src/utilities/sync-tech-verticals.py",
    
    # Deployment and Infrastructure
    "railway_main.py": "deployment/railway/main.py",
    "insert_job.py": "scripts/database/insert-job.py",
    
    # Documentation (move to appropriate docs location)
    "DOCUMENTATION_STRUCTURE_PLAN.md": "docs/architecture/documentation-structure.md",
}

# Additional directories to create
ADDITIONAL_DIRECTORIES = [
    # Demo structure
    "demos/core/job-applications",
    "demos/core/job-parser",
    "demos/epics/ai-scoring",
    "demos/epics/candidate-profile",
    "demos/epics/company-enrichment",
    "demos/epics/workflow-orchestration",
    "demos/epics/application-tracking",
    "demos/epics/mobile-networking",
    "demos/epics/analytics-dashboard",
    "demos/epics/personal-brand",
    "demos/epics/resume-optimizer",
    "demos/integrations/new-apis",
    "demos/scenarios/micross-components",
    "demos/showcase",
    "demos/testing",
    
    # Frontend structure
    "frontend/pages",
    
    # Server structure
    "servers/dynamic-resume",
    "servers/resume-optimizer",
    "servers/utilities",
    
    # Testing structure
    "tests/integration",
    "tests/scenarios",
    "tests/unit",
    
    # Deployment structure
    "deployment/railway",
    "deployment/docker",
    "deployment/production",
    
    # Source utilities (if not exists)
    "src/utilities",
]

def create_additional_directories():
    """Create the additional directory structure."""
    print("Creating additional directories...")
    for directory in ADDITIONAL_DIRECTORIES:
        dir_path = PROJECT_ROOT / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")

def move_remaining_files():
    """Move remaining files according to the mapping."""
    print("\nMoving remaining files to organized locations...")
    moved_count = 0
    
    for old_file, new_location in REMAINING_FILE_MAPPINGS.items():
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
    
    print(f"\nMoved {moved_count} additional files successfully.")

def create_demo_readme_files():
    """Create README files for demo directories."""
    print("\nCreating demo documentation...")
    
    # Main demos README
    demos_readme = PROJECT_ROOT / "demos" / "README.md"
    demos_readme.write_text("""# Demos

This directory contains demonstration scripts and examples for all platform features.

## Structure

- **[Core](core/)** - Core platform functionality demos
- **[Epics](epics/)** - Feature-specific demonstrations
- **[Integrations](integrations/)** - API integration examples
- **[Scenarios](scenarios/)** - Real-world scenario tests
- **[Showcase](showcase/)** - Platform showcase demonstrations
- **[Testing](testing/)** - Integration test examples

## Usage

Most demo scripts can be run directly from the project root:

```bash
# Run a specific epic demo
python demos/epics/resume-optimizer/demo.py

# Run integration tests
python demos/testing/simple-integration-test.py
```

## Demo Categories

### Epic Demonstrations
- **Resume Optimizer**: AI-powered resume optimization
- **Personal Brand**: Personal brand profiling and analysis
- **Company Enrichment**: Company data enhancement
- **Application Tracking**: Job application monitoring
- **Mobile Networking**: QR code networking features
- **Analytics Dashboard**: Performance analytics
- **Workflow Orchestration**: End-to-end automation

### Integration Examples
- **Job Board APIs**: Indeed, GitHub, and other integrations
- **CRM Integration**: HubSpot and Salesforce examples
- **AI Services**: OpenAI GPT-4 integration patterns

### Scenario Testing
- **Real Company Examples**: Micross Components and other real-world tests
- **End-to-End Workflows**: Complete job search automation scenarios
""")
    
    # Frontend README
    frontend_readme = PROJECT_ROOT / "frontend" / "README.md"
    if not frontend_readme.exists():
        frontend_readme.write_text("""# Frontend

This directory contains frontend applications and pages.

## Structure

- **[Pages](pages/)** - HTML pages and applications
- **[Components](components/)** - Reusable UI components (if applicable)
- **[Assets](assets/)** - Frontend-specific assets

## Applications

### Dynamic Resume Optimizer
- **Main Application**: `pages/dynamic-resume-optimizer.html`
- **Clean Version**: `pages/dynamic-resume-optimizer-clean.html`

### Candidate Profile Dashboard
- **Current Version**: `pages/candidate-profile-dashboard.html`
- **Updated Version**: `pages/candidate-profile-dashboard-v2.html`

### Platform Showcase
- **Showcase Page**: `pages/platform-showcase.html`

## Development

Frontend applications are designed to work with the backend servers in the `servers/` directory.
""")
    
    # Servers README
    servers_readme = PROJECT_ROOT / "servers" / "README.md"
    servers_readme.write_text("""# Servers

This directory contains various server implementations for different features.

## Structure

- **[Dynamic Resume](dynamic-resume/)** - Resume optimizer servers
- **[Resume Optimizer](resume-optimizer/)** - Resume optimization API servers
- **[Utilities](utilities/)** - Simple utility servers

## Server Categories

### Dynamic Resume Servers
- **Main Server**: `dynamic-resume/main-server.py` - Primary implementation
- **Working Server**: `dynamic-resume/working-server.py` - Current working version
- **Baseline Server**: `dynamic-resume/baseline-server.py` - Template management

### Resume Optimizer Servers
- **Final Server**: `resume-optimizer/final-server.py` - Latest stable version
- **Structured Server**: `resume-optimizer/structured-server.py` - Enhanced structure

### Utility Servers
- **Simple API**: `utilities/simple-api.py` - Basic API server
- **Quick Server**: `utilities/quick-server.py` - Development server

## Usage

Run servers from the project root:

```bash
# Run the main dynamic resume server
python servers/dynamic-resume/working-server.py

# Run a utility server
python servers/utilities/simple-api.py
```
""")
    
    # Tests README
    tests_readme = PROJECT_ROOT / "tests" / "README.md"
    tests_readme.write_text("""# Tests

This directory contains various test implementations.

## Structure

- **[Integration](integration/)** - Integration tests
- **[Scenarios](scenarios/)** - Real-world scenario tests
- **[Unit](unit/)** - Unit tests

## Test Categories

### Integration Tests
- **Complete Live Test**: End-to-end platform testing
- **Resume Test**: Resume optimization integration testing

### Scenario Tests
- **Micross Test**: Real company scenario testing

### Unit Tests
- **Tech Mapping**: Technology mapping functionality tests

## Running Tests

```bash
# Run integration tests
python tests/integration/complete-live-test.py

# Run scenario tests
python tests/scenarios/micross-test.py
```
""")

def update_gitignore():
    """Update .gitignore to account for new structure."""
    print("\nUpdating .gitignore...")
    
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        
        # Add new directories to gitignore if needed
        additions = [
            "\n# Demo outputs",
            "demos/*/output/",
            "demos/*/logs/",
            "\n# Server logs",
            "servers/*/logs/",
            "servers/*/temp/",
            "\n# Test outputs",
            "tests/*/output/",
            "tests/*/reports/",
        ]
        
        for addition in additions:
            if addition.strip() not in content:
                content += addition + "\n"
        
        gitignore_path.write_text(content)
        print("  Updated .gitignore with new structure")

def create_deployment_structure():
    """Create deployment-specific files."""
    print("\nCreating deployment structure...")
    
    # Railway deployment
    railway_readme = PROJECT_ROOT / "deployment" / "railway" / "README.md"
    railway_readme.write_text("""# Railway Deployment

This directory contains Railway-specific deployment files.

## Files

- **main.py** - Railway entry point
- **railway.json** - Railway configuration (in project root)
- **Procfile** - Process configuration (in project root)

## Deployment

Railway deployment is configured to use the main.py file in this directory.
See the main deployment documentation for complete setup instructions.
""")
    
    # Docker deployment
    docker_readme = PROJECT_ROOT / "deployment" / "docker" / "README.md"
    docker_readme.write_text("""# Docker Deployment

This directory contains Docker-specific deployment files.

## Files

- **Dockerfile** - Docker image configuration (in project root)
- **docker-compose.yml** - Multi-service configuration (in project root)

## Usage

```bash
# Build and run with Docker Compose
docker-compose up --build

# Build Docker image
docker build -t job-search-automation .
```
""")

def main():
    """Main execution function."""
    print("=== Enhanced Documentation Organization Script ===")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        create_additional_directories()
        move_remaining_files()
        create_demo_readme_files()
        update_gitignore()
        create_deployment_structure()
        
        print("\n=== Enhanced Organization Complete! ===")
        print("\nProject structure is now fully organized:")
        print("✅ All demo scripts organized by epic/functionality")
        print("✅ HTML pages moved to frontend/pages/")
        print("✅ Server files organized by purpose")
        print("✅ Test files properly categorized")
        print("✅ Utilities and data processors organized")
        print("✅ Deployment files structured")
        print("✅ Comprehensive README files created")
        
        print("\nNext steps:")
        print("1. Update any hardcoded paths in moved files")
        print("2. Test that demo scripts still work from new locations")
        print("3. Update CI/CD configurations if needed")
        print("4. Commit the organized structure")
        
    except Exception as e:
        print(f"\nError during enhanced organization: {e}")
        print("Please review and fix any issues before proceeding.")

if __name__ == "__main__":
    main()
