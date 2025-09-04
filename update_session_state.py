#!/usr/bin/env python3
"""
Update session state after major development milestones
Call this to update DEVELOPMENT_STATE.md with current progress
"""
import subprocess
from datetime import datetime

def update_development_state(feature_completed=None, next_priority=None, notes=None):
    """Update the development state file with current progress"""
    
    # Get current git info
    try:
        commit_hash = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                   capture_output=True, text=True).stdout.strip()
        branch = subprocess.run(['git', 'branch', '--show-current'],
                               capture_output=True, text=True).stdout.strip()
    except:
        commit_hash = "unknown"
        branch = "main"
    
    # Read current state
    try:
        with open('DEVELOPMENT_STATE.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ DEVELOPMENT_STATE.md not found")
        return
    
    # Update timestamp
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('**Last Updated**'):
            lines[i] = f'**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        elif line.startswith('**Session**'):
            lines[i] = f'**Session**: {commit_hash} ({branch})'
        elif line.startswith('**Next Priority**') and next_priority:
            lines[i] = f'**Next Priority**: {next_priority}'
    
    # Add handoff summary if significant progress
    if feature_completed:
        handoff_section = f"""
## 🎯 Latest Session Handoff
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Completed**: {feature_completed}
**Commit**: {commit_hash}
**Next Steps**: {next_priority or 'Continue from where left off'}
**Notes**: {notes or 'No additional notes'}
"""
        # Insert after the current status section
        insert_index = next((i for i, line in enumerate(lines) if line.startswith('## ✅ Completed Components')), 10)
        lines.insert(insert_index, handoff_section)
    
    # Write updated content
    with open('DEVELOPMENT_STATE.md', 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Updated DEVELOPMENT_STATE.md")
    if feature_completed:
        print(f"📝 Logged completion: {feature_completed}")
    if next_priority:
        print(f"🎯 Next priority: {next_priority}")

def quick_commit_with_state_update(message, feature=None, next_step=None):
    """Make a commit and update state tracking"""
    
    # Make the commit
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print(f"✅ Committed: {message}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Commit failed: {e}")
        return False
    
    # Update state tracking
    if feature or next_step:
        update_development_state(feature, next_step)
    
    # Push to GitHub
    try:
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to GitHub")
    except subprocess.CalledProcessError:
        print("⚠️  Push failed - continuing anyway")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        feature = sys.argv[1]
        next_priority = sys.argv[2] if len(sys.argv) > 2 else None
        notes = sys.argv[3] if len(sys.argv) > 3 else None
        
        update_development_state(feature, next_priority, notes)
    else:
        print("Usage: python update_session_state.py 'Feature completed' 'Next priority' 'Optional notes'")
        print("Example: python update_session_state.py 'Square OAuth flow' 'Data sync pipeline' 'Ready for real spa testing'")