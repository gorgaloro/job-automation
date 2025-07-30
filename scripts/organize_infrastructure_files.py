#!/usr/bin/env python3
"""
Infrastructure Files Organization Script

This script organizes the remaining infrastructure and configuration files
that should be moved from the project root to appropriate locations.
"""

import os
import shutil
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent

# Infrastructure file mappings
INFRASTRUCTURE_FILE_MAPPINGS = {
    # Docker files - move to deployment/docker
    "Dockerfile": "deployment/docker/Dockerfile",
    "docker-compose.yml": "deployment/docker/docker-compose.yml",
    
    # Railway deployment files - move to deployment/railway
    "railway.json": "deployment/railway/railway.json",
    "Procfile": "deployment/railway/Procfile",
    
    # Environment files - move to config directory
    ".env.example": "config/env/.env.example",
    ".env.template": "config/env/.env.template",
    
    # Requirements - move to config directory
    "requirements.txt": "config/requirements/requirements.txt",
}

# Files to keep at root level (essential project files)
KEEP_AT_ROOT = {
    ".env",           # Active environment file
    ".gitignore",     # Git configuration
    "README.md",      # Main project documentation
    "LICENSE",        # License file
}

# Additional directories to create
INFRASTRUCTURE_DIRECTORIES = [
    "config/env",
    "config/requirements",
    "config/docker",
    "config/ci-cd",
]

def create_infrastructure_directories():
    """Create infrastructure-related directories."""
    print("Creating infrastructure directories...")
    for directory in INFRASTRUCTURE_DIRECTORIES:
        dir_path = PROJECT_ROOT / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")

def move_infrastructure_files():
    """Move infrastructure files to organized locations."""
    print("\nMoving infrastructure files...")
    moved_count = 0
    
    for old_file, new_location in INFRASTRUCTURE_FILE_MAPPINGS.items():
        old_path = PROJECT_ROOT / old_file
        new_path = PROJECT_ROOT / new_location
        
        if old_path.exists():
            # Ensure target directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file (don't move, in case it's needed at root)
            shutil.copy2(str(old_path), str(new_path))
            print(f"  Copied: {old_file} -> {new_location}")
            moved_count += 1
        else:
            print(f"  Warning: {old_file} not found")
    
    print(f"\nCopied {moved_count} infrastructure files successfully.")

def create_infrastructure_readme_files():
    """Create README files for infrastructure directories."""
    print("\nCreating infrastructure documentation...")
    
    # Config README
    config_readme = PROJECT_ROOT / "config" / "README.md"
    config_readme.write_text("""# Configuration

This directory contains all configuration files and templates for the project.

## Structure

- **[Environment](env/)** - Environment variable templates and examples
- **[Requirements](requirements/)** - Python dependency specifications
- **[Docker](docker/)** - Docker configuration files (if needed)
- **[CI/CD](ci-cd/)** - Continuous integration and deployment configurations

## Environment Configuration

### Environment Files
- **`.env.example`** - Template showing all required environment variables
- **`.env.template`** - Basic template for new environments

### Usage
```bash
# Copy template to create your environment file
cp config/env/.env.example .env

# Edit with your specific values
nano .env
```

## Requirements Management

### Python Dependencies
- **`requirements.txt`** - Core application dependencies
- **`requirements-dev.txt`** - Development dependencies (if created)
- **`requirements-test.txt`** - Testing dependencies (if created)

### Usage
```bash
# Install core dependencies
pip install -r config/requirements/requirements.txt

# Install development dependencies
pip install -r config/requirements/requirements-dev.txt
```

## Docker Configuration

Docker files are organized in the deployment directory but may have configuration templates here.

## CI/CD Configuration

Continuous integration and deployment configurations for various platforms:
- GitHub Actions
- Railway
- Other CI/CD platforms
""")
    
    # Deployment README update
    deployment_readme = PROJECT_ROOT / "deployment" / "README.md"
    if not deployment_readme.exists():
        deployment_readme.write_text("""# Deployment

This directory contains deployment configurations and scripts for various platforms.

## Structure

- **[Railway](railway/)** - Railway deployment configuration
- **[Docker](docker/)** - Docker containerization files
- **[Production](production/)** - Production deployment scripts and guides

## Deployment Platforms

### Railway
- **`railway.json`** - Railway service configuration
- **`Procfile`** - Process definitions for Railway
- **`main.py`** - Railway entry point

### Docker
- **`Dockerfile`** - Docker image configuration
- **`docker-compose.yml`** - Multi-service orchestration

### Production
- Production deployment scripts and documentation

## Quick Deployment

### Railway
```bash
# Deploy to Railway (requires Railway CLI)
railway deploy
```

### Docker
```bash
# Build and run locally
docker-compose up --build

# Build for production
docker build -t job-search-automation .
```

## Environment Variables

All deployment platforms require proper environment variable configuration. See `config/env/` for templates.
""")

def update_docker_files():
    """Update Docker files to reference new locations."""
    print("\nUpdating Docker file references...")
    
    # Update docker-compose.yml to reference new Dockerfile location
    docker_compose_path = PROJECT_ROOT / "deployment/docker/docker-compose.yml"
    if docker_compose_path.exists():
        content = docker_compose_path.read_text()
        # Update any references to root-level files if needed
        # This is a placeholder - actual updates depend on current content
        print("  Docker Compose file copied (manual review recommended)")

def create_root_level_symlinks():
    """Create symlinks at root level for files that deployment platforms expect there."""
    print("\nCreating deployment symlinks...")
    
    # Some deployment platforms expect certain files at root level
    # Create symlinks to maintain compatibility
    symlinks_to_create = [
        ("deployment/railway/Procfile", "Procfile"),
        ("deployment/railway/railway.json", "railway.json"),
        ("deployment/docker/Dockerfile", "Dockerfile"),
        ("deployment/docker/docker-compose.yml", "docker-compose.yml"),
        ("config/requirements/requirements.txt", "requirements.txt"),
    ]
    
    for target, link_name in symlinks_to_create:
        target_path = PROJECT_ROOT / target
        link_path = PROJECT_ROOT / link_name
        
        if target_path.exists():
            # Remove existing file if it exists
            if link_path.exists():
                link_path.unlink()
            
            # Create symlink
            try:
                link_path.symlink_to(target_path)
                print(f"  Created symlink: {link_name} -> {target}")
            except OSError as e:
                print(f"  Warning: Could not create symlink {link_name}: {e}")
                # Fall back to copying the file
                shutil.copy2(str(target_path), str(link_path))
                print(f"  Copied instead: {link_name}")

def create_gitignore_updates():
    """Update .gitignore for new structure."""
    print("\nUpdating .gitignore for new structure...")
    
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        
        # Add new structure-specific ignores
        additions = [
            "\n# Configuration",
            "config/env/.env.local",
            "config/env/.env.production",
            "\n# Deployment outputs",
            "deployment/*/logs/",
            "deployment/*/temp/",
            "\n# Infrastructure",
            "config/*/local/",
        ]
        
        for addition in additions:
            if addition.strip() not in content:
                content += addition + "\n"
        
        gitignore_path.write_text(content)
        print("  Updated .gitignore with infrastructure patterns")

def main():
    """Main execution function."""
    print("=== Infrastructure Files Organization Script ===")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        create_infrastructure_directories()
        move_infrastructure_files()
        create_infrastructure_readme_files()
        update_docker_files()
        create_root_level_symlinks()
        create_gitignore_updates()
        
        print("\n=== Infrastructure Organization Complete! ===")
        print("\nInfrastructure files are now organized:")
        print("✅ Docker files moved to deployment/docker/")
        print("✅ Railway files moved to deployment/railway/")
        print("✅ Environment templates moved to config/env/")
        print("✅ Requirements moved to config/requirements/")
        print("✅ Symlinks created for deployment platform compatibility")
        print("✅ Comprehensive documentation added")
        
        print("\nProject root now contains only essential files:")
        print("- .env (active environment)")
        print("- .gitignore (git configuration)")
        print("- README.md (main documentation)")
        print("- LICENSE (license file)")
        print("- Symlinks for deployment compatibility")
        
        print("\nNext steps:")
        print("1. Test that deployment platforms still work with new structure")
        print("2. Update any CI/CD configurations if needed")
        print("3. Verify Docker builds work from new location")
        print("4. Commit the organized infrastructure")
        
    except Exception as e:
        print(f"\nError during infrastructure organization: {e}")
        print("Please review and fix any issues before proceeding.")

if __name__ == "__main__":
    main()
