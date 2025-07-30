#!/usr/bin/env python3
"""
Cleanup script to remove original infrastructure files from project root
after they've been organized and symlinked by organize_infrastructure_files.py

This script removes the original files that are now duplicated by symlinks,
leaving only essential project files at the root level.
"""

import os
import shutil
from pathlib import Path

def cleanup_root_infrastructure():
    """Remove original infrastructure files from root after organization"""
    
    project_root = Path.cwd()
    print(f"=== Root Infrastructure Cleanup Script ===")
    print(f"Project root: {project_root}")
    
    # Files to remove (now that they're organized and symlinked)
    files_to_remove = [
        ".env.example",
        ".env.template", 
        "Dockerfile",
        "docker-compose.yml",
        "Procfile",
        "railway.json",
        "requirements.txt"
    ]
    
    print("\nRemoving original infrastructure files...")
    
    removed_count = 0
    for file_name in files_to_remove:
        file_path = project_root / file_name
        
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"  Removed: {file_name}")
                    removed_count += 1
                else:
                    print(f"  Skipped: {file_name} (not a file)")
            except Exception as e:
                print(f"  Error removing {file_name}: {e}")
        else:
            print(f"  Not found: {file_name}")
    
    print(f"\nRemoved {removed_count} original infrastructure files.")
    
    # Verify symlinks are still working
    print("\nVerifying symlinks are intact...")
    
    symlinks_to_check = [
        ("Dockerfile", "deployment/docker/Dockerfile"),
        ("docker-compose.yml", "deployment/docker/docker-compose.yml"),
        ("Procfile", "deployment/railway/Procfile"),
        ("railway.json", "deployment/railway/railway.json"),
        ("requirements.txt", "config/requirements/requirements.txt")
    ]
    
    working_symlinks = 0
    for symlink_name, target_path in symlinks_to_check:
        symlink_path = project_root / symlink_name
        target_full_path = project_root / target_path
        
        if symlink_path.is_symlink() and target_full_path.exists():
            print(f"  ✅ {symlink_name} -> {target_path}")
            working_symlinks += 1
        else:
            print(f"  ❌ {symlink_name} -> {target_path} (broken or missing)")
    
    print(f"\n{working_symlinks}/{len(symlinks_to_check)} symlinks working correctly.")
    
    # Show final root directory state
    print("\nFinal root directory contents:")
    essential_files = []
    other_files = []
    directories = []
    
    for item in sorted(project_root.iterdir()):
        if item.name.startswith('.'):
            continue  # Skip hidden files/dirs for cleaner output
            
        if item.is_dir():
            directories.append(item.name)
        elif item.name in ['README.md', 'LICENSE']:
            essential_files.append(item.name)
        else:
            other_files.append(item.name)
    
    print("  Essential files:")
    for file in essential_files:
        print(f"    📄 {file}")
    
    if other_files:
        print("  Other files:")
        for file in other_files:
            print(f"    🔗 {file}")
    
    print("  Directories:")
    for dir_name in directories:
        print(f"    📁 {dir_name}/")
    
    print("\n=== Root Cleanup Complete! ===")
    print("\nProject root now contains only:")
    print("✅ Essential files (README.md, LICENSE)")
    print("✅ Active configuration (.env, .gitignore)")
    print("✅ Deployment symlinks (for platform compatibility)")
    print("✅ Organized directories (src/, docs/, config/, etc.)")

if __name__ == "__main__":
    cleanup_root_infrastructure()
