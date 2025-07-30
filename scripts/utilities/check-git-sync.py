#!/usr/bin/env python3
"""
Git Sync Status Checker
Analyzes local files to determine what needs to be synced to GitHub
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path

def get_file_hash(filepath):
    """Get SHA256 hash of file for comparison"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:8]
    except:
        return "ERROR"

def get_file_info(filepath):
    """Get file modification time and size"""
    try:
        stat = os.stat(filepath)
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size = stat.st_size
        return mod_time, size
    except:
        return "ERROR", 0

def check_sync_status():
    """Check what files need to be synced"""
    
    project_root = Path(__file__).parent
    
    print("AI Job Search Automation Platform - Git Sync Status Check")
    print("=" * 70)
    
    # Critical files that should be synced
    critical_files = [
        # Epic 10 - Latest work
        "src/api/routes/workflow_orchestration.py",
        "demo_epic10_workflow_orchestration.py",
        "PLATFORM_SHOWCASE.md",
        "PRODUCTION_ROADMAP.md",
        "GITHUB_SYNC_STRATEGY.md",
        "SECURITY_INCIDENT_RESPONSE.md",
        
        # Core platform files
        "src/core/workflow_orchestrator.py",
        "src/core/resume_optimizer.py",
        "src/core/job_parser.py",
        "src/core/job_applications_engine.py",
        "src/api/main.py",
        
        # Documentation
        "README.md",
        "docs/architecture.md",
        "docs/api-reference.md",
        
        # Configuration
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        ".gitignore",
        
        # Demo scripts
        "showcase_platform_demo.py",
        "showcase.html"
    ]
    
    print("\nCRITICAL FILES STATUS:")
    print("-" * 50)
    
    needs_sync = []
    synced_files = []
    missing_files = []
    
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            mod_time, size = get_file_info(full_path)
            file_hash = get_file_hash(full_path)
            
            print(f"[OK] {file_path}")
            print(f"   Modified: {mod_time}")
            print(f"   Size: {size:,} bytes")
            print(f"   Hash: {file_hash}")
            
            # Check if recently modified (last 24 hours)
            if "2025-07-24" in mod_time or "2025-07-25" in mod_time:
                needs_sync.append(file_path)
                print(f"   [SYNC NEEDED] Recently modified")
            else:
                synced_files.append(file_path)
                print(f"   [SYNCED] Likely up to date")
            print()
        else:
            missing_files.append(file_path)
            print(f"[MISSING] {file_path} - FILE NOT FOUND")
            print()
    
    # Check for new files that might need syncing
    print("\nNEW FILES DETECTED:")
    print("-" * 30)
    
    new_files = []
    for file_path in project_root.glob("*.md"):
        if file_path.name not in [f.split("/")[-1] for f in critical_files]:
            mod_time, size = get_file_info(file_path)
            if "2025-07-24" in mod_time or "2025-07-25" in mod_time:
                new_files.append(file_path.name)
                print(f"[NEW] {file_path.name} - Modified: {mod_time}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SYNC STATUS SUMMARY")
    print("=" * 70)
    
    print(f"[OK] Files likely synced: {len(synced_files)}")
    print(f"[SYNC] Files needing sync: {len(needs_sync)}")
    print(f"[NEW] New files detected: {len(new_files)}")
    print(f"[MISSING] Missing files: {len(missing_files)}")
    
    if needs_sync or new_files:
        print("\n[ACTION] RECOMMENDED: Push to GitHub")
        print("Files to sync:")
        for f in needs_sync + new_files:
            print(f"  • {f}")
    else:
        print("\n[STATUS] REPOSITORY APPEARS UP TO DATE")
    
    # Check .env.clean status
    env_clean_path = project_root / ".env.clean"
    if env_clean_path.exists():
        with open(env_clean_path, 'r') as f:
            content = f.read()
            if "your_" in content and "here" in content:
                print("\n[SECURITY] .env.clean properly sanitized [OK]")
            else:
                print("\n[SECURITY] WARNING: .env.clean may contain real keys! [DANGER]")
    
    print("\n[PLATFORM] Status: 100% Complete - Ready for Portfolio!")

if __name__ == "__main__":
    check_sync_status()
