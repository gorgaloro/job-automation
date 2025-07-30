#!/usr/bin/env python3
"""
Cross-Device Sync Status Checker

This script helps you understand what files have been created/modified
and provides sync status for cross-device development.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def get_recent_files(directory, hours=24):
    """Get files modified in the last N hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '.venv', '__pycache__', 'node_modules', '.pytest_cache'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mod_time > cutoff_time:
                    relative_path = os.path.relpath(file_path, directory)
                    recent_files.append({
                        'path': relative_path,
                        'modified': mod_time,
                        'size': os.path.getsize(file_path)
                    })
            except (OSError, ValueError):
                continue
    
    return sorted(recent_files, key=lambda x: x['modified'], reverse=True)

def check_epic2_files():
    """Check if Epic 2 files exist"""
    epic2_files = [
        'src/core/personal_brand.py',
        'src/core/ai_career_coach.py', 
        'src/integrations/supabase/personal_brand_service.py',
        'src/integrations/supabase/supabase_client.py',
        'src/api/routes/personal_brand.py',
        'demo_personal_brand.py',
        'test_supabase_connection.py'
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in epic2_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            existing_files.append({
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
        else:
            missing_files.append(file_path)
    
    return existing_files, missing_files

def main():
    """Main sync status check"""
    print("=" * 70)
    print("CROSS-DEVICE SYNC STATUS CHECKER")
    print("=" * 70)
    print(f"Current machine: Windows PC")
    print(f"Project location: {os.getcwd()}")
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check recent files
    print("RECENT FILE CHANGES (Last 24 hours):")
    print("-" * 50)
    recent_files = get_recent_files(".", hours=24)
    
    if recent_files:
        for file_info in recent_files[:15]:  # Show top 15
            mod_time = file_info['modified'].strftime('%H:%M:%S')
            size_kb = file_info['size'] / 1024
            print(f"  {mod_time} | {size_kb:6.1f}KB | {file_info['path']}")
        
        if len(recent_files) > 15:
            print(f"  ... and {len(recent_files) - 15} more files")
    else:
        print("  No recent changes found")
    
    print()
    
    # Check Epic 2 specific files
    print("EPIC 2: PERSONAL BRAND SYSTEM FILES:")
    print("-" * 50)
    existing_files, missing_files = check_epic2_files()
    
    if existing_files:
        print("  EXISTS on this machine:")
        for file_info in existing_files:
            mod_time = file_info['modified'].strftime('%m/%d %H:%M')
            size_kb = file_info['size'] / 1024
            print(f"    {mod_time} | {size_kb:6.1f}KB | {file_info['path']}")
    
    if missing_files:
        print("  MISSING on this machine:")
        for file_path in missing_files:
            print(f"    X | {file_path}")
    
    print()
    
    # Sync recommendations
    print("CROSS-DEVICE SYNC RECOMMENDATIONS:")
    print("-" * 50)
    
    if not existing_files:
        print("  WARNING: Epic 2 files not found on this machine!")
        print("  This suggests sync issues or you're on the wrong machine.")
    else:
        print("  SUCCESS: Epic 2 files found on this machine")
        print("  These files should sync to your Mac via iCloud Drive")
    
    print()
    print("TO SYNC WITH YOUR MAC:")
    print("1. Wait for iCloud Drive to sync (check iCloud status)")
    print("2. On Mac: Open Windsurf in the same project directory")
    print("3. On Mac: Files should be available, but conversation won't sync")
    print("4. Install Git on Windows for proper version control")
    print()
    
    print("INSTALL GIT ON WINDOWS:")
    print("1. Download: https://git-scm.com/download/win")
    print("2. Or use: winget install Git.Git")
    print("3. Restart terminal after installation")
    print("4. Run: git status (to verify)")
    print()
    
    print("ALTERNATIVE: MANUAL FILE TRANSFER")
    print("If iCloud isn't syncing, you can manually copy these key files:")
    for file_info in existing_files:
        print(f"  - {file_info['path']}")
    
    print()
    print("=" * 70)
    print("SYNC STATUS CHECK COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSync check interrupted. Goodbye!")
    except Exception as e:
        print(f"\nSync check failed: {e}")
