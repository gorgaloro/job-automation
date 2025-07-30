#!/usr/bin/env python3
"""
Git Status Diagnostic Tool
Helps diagnose why GitHub Desktop isn't detecting changes
"""

import os
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_git_status():
    """Comprehensive Git status check"""
    
    project_root = Path(__file__).parent
    print("Git Status Diagnostic Tool")
    print("=" * 50)
    
    # Check if we're in a git repository
    print("\n1. Repository Check:")
    print("-" * 20)
    
    git_dir = project_root / ".git"
    if git_dir.exists():
        print("[OK] .git directory found")
        print(f"[PATH] {git_dir}")
    else:
        print("[ERROR] No .git directory found!")
        return
    
    # Check current branch
    print("\n2. Branch Information:")
    print("-" * 20)
    
    try:
        with open(git_dir / "HEAD", 'r') as f:
            head_content = f.read().strip()
            print(f"[HEAD] {head_content}")
            
        if head_content.startswith("ref: "):
            branch_ref = head_content[5:]  # Remove "ref: "
            print(f"[BRANCH] {branch_ref.split('/')[-1]}")
    except Exception as e:
        print(f"[ERROR] Could not read HEAD: {e}")
    
    # Check remote configuration
    print("\n3. Remote Configuration:")
    print("-" * 25)
    
    try:
        with open(git_dir / "config", 'r') as f:
            config_content = f.read()
            
        if 'remote "origin"' in config_content:
            print("[OK] Remote 'origin' configured")
            
            # Extract URL
            lines = config_content.split('\n')
            for i, line in enumerate(lines):
                if 'url =' in line:
                    url = line.split('url = ')[1]
                    # Mask sensitive parts of URL
                    if '@' in url:
                        parts = url.split('@')
                        masked_url = f"https://***@{parts[1]}"
                        print(f"[URL] {masked_url}")
                    else:
                        print(f"[URL] {url}")
        else:
            print("[WARNING] No remote 'origin' found")
            
    except Exception as e:
        print(f"[ERROR] Could not read config: {e}")
    
    # Check index file (staging area)
    print("\n4. Staging Area Check:")
    print("-" * 20)
    
    index_file = git_dir / "index"
    if index_file.exists():
        size = index_file.stat().st_size
        print(f"[OK] Index file exists ({size} bytes)")
        if size > 1000:
            print("[INFO] Index contains staged changes")
        else:
            print("[INFO] Index appears empty")
    else:
        print("[WARNING] No index file found")
    
    # Check for recent commits
    print("\n5. Recent Activity:")
    print("-" * 15)
    
    try:
        # Check COMMIT_EDITMSG for last commit
        commit_msg_file = git_dir / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            with open(commit_msg_file, 'r') as f:
                last_commit = f.read().strip()
                print(f"[LAST COMMIT] {last_commit[:50]}...")
        
        # Check FETCH_HEAD for last fetch
        fetch_head_file = git_dir / "FETCH_HEAD"
        if fetch_head_file.exists():
            print("[OK] Recent fetch activity detected")
        
    except Exception as e:
        print(f"[ERROR] Could not check recent activity: {e}")
    
    # Check working directory for changes
    print("\n6. Working Directory Analysis:")
    print("-" * 30)
    
    # Check recent files
    recent_files = []
    for file_path in project_root.rglob("*"):
        if file_path.is_file() and not str(file_path).startswith(str(git_dir)):
            try:
                stat = file_path.stat()
                mod_time = stat.st_mtime
                # Check if modified in last 24 hours
                import time
                if time.time() - mod_time < 86400:  # 24 hours
                    recent_files.append((file_path.relative_to(project_root), mod_time))
            except:
                pass
    
    print(f"[RECENT] {len(recent_files)} files modified in last 24 hours")
    
    # Show top 10 most recent
    recent_files.sort(key=lambda x: x[1], reverse=True)
    for file_path, mod_time in recent_files[:10]:
        import datetime
        dt = datetime.datetime.fromtimestamp(mod_time)
        print(f"  {file_path} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check .gitignore
    print("\n7. .gitignore Analysis:")
    print("-" * 20)
    
    gitignore_file = project_root / ".gitignore"
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
            
        lines = [line.strip() for line in gitignore_content.split('\n') if line.strip() and not line.startswith('#')]
        print(f"[OK] .gitignore has {len(lines)} active rules")
        
        # Check if any recent files are being ignored
        ignored_recent = []
        for file_path, _ in recent_files:
            file_str = str(file_path)
            for pattern in lines:
                if pattern in file_str or file_str.endswith(pattern.replace('*', '')):
                    ignored_recent.append(file_path)
                    break
        
        if ignored_recent:
            print(f"[WARNING] {len(ignored_recent)} recent files may be ignored:")
            for file_path in ignored_recent[:5]:
                print(f"  {file_path}")
    
    # Recommendations
    print("\n8. Recommendations:")
    print("-" * 15)
    
    if len(recent_files) > 0:
        print("[ACTION] Try refreshing GitHub Desktop (View → Refresh)")
        print("[ACTION] Check if GitHub Desktop is looking at the correct folder")
        print("[ACTION] Try closing and reopening the repository in GitHub Desktop")
        
        if len(recent_files) > 10:
            print("[INFO] Many recent changes detected - files should appear in GitHub Desktop")
    else:
        print("[INFO] No recent changes detected - repository may be up to date")
    
    print(f"\n[SUMMARY] Repository appears functional with {len(recent_files)} recent changes")

if __name__ == "__main__":
    check_git_status()
