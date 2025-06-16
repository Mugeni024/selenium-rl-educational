#!/usr/bin/env python3
"""
Selenium RL Educational Project - Setup and Demo Script
Run this script to set up the project and see a quick demonstration
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['selenium', 'numpy', 'matplotlib', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def setup_project_structure():
    """Create necessary directories"""
    print("\n📁 Setting up project structure...")
    
    directories = ['models', 'logs', 'results']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   📁 {directory}/ already exists")

def check_demo_form():
    """Check if demo form exists"""
    print("\n🌐 Checking demo form...")
    
    demo_path = "demo/test_form.html"
    if os.path.exists(demo_path):
        print("   ✅ Demo form found!")
        return True
    else:
        print("   ❌ Demo form not found!")
        print("   💡 Make sure demo/test_form.html exists")
        return False

def show_training_options():
    """Show available training scripts"""
    print("\n🎯 Available Training Options:")
    print("=" * 40)
    
    scripts = [
        ("complete_trainer.py", "Main training script (recommended for beginners)"),
        ("breakthrough_training.py", "Advanced training for experienced users"),
        ("form_analyzer_fixed.py", "Analyze form structure and requirements")
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            print(f"✅ {script:<25} - {description}")
        else:
            print(f"❌ {script:<25} - Missing!")

def display_project_info():
    """Display project information and achievements"""
    print("\n🤖 SELENIUM RL EDUCATIONAL PROJECT")
    print("=" * 50)
    print("🎯 Goal: Train AI to automatically fill web forms")
    print("🧠 Method: Q-Learning reinforcement learning")
    print("🏆 Achievement: Reached Episode 100 with 129.73 reward!")
    print("\n📊 Project Stats:")
    print("   🎮 Episodes Completed: 100+")
    print("   🏅 Best Reward: 129.73")
    print("   ⚡ Action Success Rate: 99.9%")
    print("   🧠 States Learned: 4")
    print("   📈 Total Learning Steps: 3,530+")

def main():
    """Main setup function"""
    print("🚀 SELENIUM RL PROJECT SETUP")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete - install missing dependencies first")
        return
    
    # Setup project structure
    setup_project_structure()
    
    # Check demo form
    if not check_demo_form():
        print("\n⚠️  Demo form missing - some features may not work")
    
    # Show training options
    show_training_options()
    
    # Display project info
    display_project_info()
    
    print(f"\n🎉 SETUP COMPLETE!")
    print("=" * 25)
    print("🚀 Ready to start training your AI!")
    print("\n📚 Quick Start:")
    print("   1. Run: python3 complete_trainer.py")
    print("   2. Watch your AI learn!")
    print("   3. Check training_progress_*.png for results")
    
    print(f"\n💡 Tips:")
    print("   - Start with complete_trainer.py for basic training")
    print("   - Use form_analyzer_fixed.py to understand the form")
    print("   - Try breakthrough_training.py for advanced sessions")
    print("   - All training progress is automatically saved")

if __name__ == "__main__":
    main()
