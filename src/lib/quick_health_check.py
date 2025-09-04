#!/usr/bin/env python3
"""
Quick health check for Keeper development environment
Run this to verify everything is still working between Claude sessions
"""
import os
import sys
from dotenv import load_dotenv

def quick_health_check():
    """Fast validation that all systems are operational"""
    
    print("🔍 Keeper Quick Health Check")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    issues = []
    
    # Check 1: Environment file exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file missing")
    else:
        print("✅ .env file exists")
    
    # Check 2: Required API keys present
    required_keys = [
        'SQUARE_APPLICATION_ID',
        'SQUARE_ACCESS_TOKEN', 
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        issues.append(f"❌ Missing API keys: {', '.join(missing_keys)}")
    else:
        print("✅ All required API keys present")
    
    # Check 3: Python dependencies
    try:
        import requests
        import supabase
        print("✅ Python dependencies available")
    except ImportError as e:
        issues.append(f"❌ Missing Python dependency: {e}")
    
    # Check 4: Git repository status
    import subprocess
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository accessible")
            if result.stdout.strip():
                print(f"ℹ️  Uncommitted changes: {len(result.stdout.strip().split())} files")
        else:
            issues.append("❌ Git repository issues")
    except Exception:
        issues.append("❌ Git not available")
    
    # Summary
    print("-" * 40)
    if not issues:
        print("🎉 HEALTH CHECK PASSED")
        print("✅ Environment ready for development")
        print("\n🚀 Next step: Run 'python test_complete_setup.py' for full validation")
        return True
    else:
        print("⚠️  HEALTH CHECK ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 Fix these issues before continuing development")
        return False

def show_current_state():
    """Show current development state"""
    print("\n📊 CURRENT STATE:")
    print("-" * 20)
    
    try:
        with open('DEVELOPMENT_STATE.md', 'r') as f:
            lines = f.readlines()
            for line in lines[0:15]:  # Show first few lines
                if line.startswith('**Next Priority**'):
                    print(f"🎯 {line.strip()}")
                elif line.startswith('**Last Updated**'):
                    print(f"📅 {line.strip()}")
                elif line.startswith('- [x]') or line.startswith('- [ ]'):
                    print(f"   {line.strip()}")
    except FileNotFoundError:
        print("   No development state file found")

if __name__ == "__main__":
    if quick_health_check():
        show_current_state()
        print("\n🎪 Ready to continue Keeper development!")
    else:
        sys.exit(1)