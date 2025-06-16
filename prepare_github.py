#!/usr/bin/env python3
"""
GitHub Preparation Script
Cleans up the project and prepares it for GitHub repository
"""

import os
import shutil
import glob

def clean_training_artifacts():
    """Clean up training artifacts that shouldn't be in the repo"""
    print("🧹 Cleaning training artifacts...")
    
    # Files to remove
    artifacts_to_remove = [
        "trained_model.pkl",
        "training_data_*.json",
        "training_progress_*.png"
    ]
    
    removed_count = 0
    for pattern in artifacts_to_remove:
        files = glob.glob(pattern)
        for file in files:
            if os.path.exists(file):
                os.remove(file)
                print(f"   🗑️  Removed {file}")
                removed_count += 1
    
    if removed_count == 0:
        print("   ✅ No training artifacts to clean")
    else:
        print(f"   ✅ Cleaned {removed_count} training artifact(s)")

def create_sample_results():
    """Create sample results directory with placeholder"""
    print("\n📊 Creating sample results structure...")
    
    if not os.path.exists("results"):
        os.makedirs("results")
        print("   📁 Created results/ directory")
    
    # Create a README for results
    results_readme = """# Training Results

This directory will contain your training results after running the AI:

## Generated Files
- `training_progress_*.png` - Learning curve visualizations
- `training_data_*.json` - Detailed training session logs
- `trained_model.pkl` - Saved AI model (in models/ directory)

## Example Results
After training, you'll see files like:
- Episode progression charts
- Reward accumulation graphs
- Form completion statistics
- Q-table learning visualizations

Start training with:
```bash
python3 complete_trainer.py
```

Your AI will learn and save results here automatically!
"""
    
    with open("results/README.md", "w") as f:
        f.write(results_readme)
    print("   📄 Created results/README.md")

def create_models_directory():
    """Create models directory with explanation"""
    print("\n🧠 Creating models directory...")
    
    if not os.path.exists("models"):
        os.makedirs("models")
        print("   📁 Created models/ directory")
    
    models_readme = """# AI Models

This directory stores your trained AI models.

## Generated Files
- `trained_model.pkl` - Your AI's learned Q-table and knowledge

## Model Information
The trained model contains:
- Q-table with state-action values
- Episode count and training history
- Learning parameters and configuration

## Usage
Models are automatically saved after each training session and loaded when you continue training.

Your AI's memory persists between sessions!
"""
    
    with open("models/README.md", "w") as f:
        f.write(models_readme)
    print("   📄 Created models/README.md")

def verify_project_structure():
    """Verify all necessary files are present"""
    print("\n✅ Verifying project structure...")
    
    required_files = [
        "README.md",
        "CHANGELOG.md", 
        "LICENSE",
        "requirements.txt",
        ".gitignore",
        "setup.py",
        "complete_trainer.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    else:
        print("\n🎉 All required files present!")
        return True

def show_github_instructions():
    """Show instructions for creating GitHub repo"""
    print("\n🚀 GITHUB SETUP INSTRUCTIONS")
    print("=" * 40)
    
    print("\n1. 📁 Create new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Repository name: selenium-rl-educational")
    print("   - Description: Educational Selenium RL project with Q-Learning")
    print("   - Make it Public (for educational sharing)")
    print("   - Don't initialize with README (we have our own)")
    
    print("\n2. 🔗 Initialize and push your project:")
    print("   cd /Users/abaasi/Desktop/selenium-rl-python")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit: Selenium RL Educational Project v1.0.0'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/YOUR_USERNAME/selenium-rl-educational.git")
    print("   git push -u origin main")
    
    print("\n3. 🎯 Add topics to your repo (on GitHub):")
    print("   - reinforcement-learning")
    print("   - selenium")
    print("   - q-learning")
    print("   - education")
    print("   - python")
    print("   - ai")
    print("   - machine-learning")
    print("   - web-automation")
    
    print("\n4. 📝 Update README.md after creating repo:")
    print("   - Replace YOUR_USERNAME with your GitHub username")
    print("   - Update clone URL in installation section")

def main():
    """Main cleanup and preparation function"""
    print("🤖 SELENIUM RL - GITHUB PREPARATION")
    print("🏆 Preparing your Episode 100, 129.73 reward AI project!")
    print("=" * 60)
    
    # Clean up training artifacts
    clean_training_artifacts()
    
    # Create necessary directories
    create_sample_results()
    create_models_directory()
    
    # Verify project structure
    if verify_project_structure():
        print("\n🎉 PROJECT READY FOR GITHUB!")
        print("=" * 35)
        
        # Show GitHub instructions
        show_github_instructions()
        
        print(f"\n💡 YOUR PROJECT HIGHLIGHTS:")
        print("   🏆 Episode 100 completed")
        print("   🎯 129.73 best reward achieved")
        print("   🧠 4 states learned")
        print("   ⚡ 99.9% action success rate")
        print("   📚 Complete educational resource")
        print("   🔧 Ready-to-run training scripts")
        
        print(f"\n🚀 Ready to share your AI achievement with the world!")
        
    else:
        print("\n❌ Project not ready - please fix missing files first")

if __name__ == "__main__":
    main()
