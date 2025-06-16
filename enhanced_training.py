#!/usr/bin/env python3
"""
Enhanced Training Configuration for Better Performance
Run this to continue training with optimized parameters
"""

import os
import sys
sys.path.append('src')

from complete_trainer import SeleniumRLTrainer

def enhanced_training():
    """
    Continue training with improved parameters for better success rate
    """
    # Get the path to our demo HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    target_url = f"file://{html_path}"
    
    print("🚀 ENHANCED TRAINING SESSION")
    print("=" * 50)
    
    # Enhanced trainer with better parameters
    trainer = SeleniumRLTrainer(
        target_url=target_url,
        max_episodes=20,              # More episodes for better learning
        max_steps_per_episode=25,     # More steps to complete complex tasks
        save_model_path="trained_model.pkl",
        debug=True
    )
    
    # Load previous training (your AI's accumulated knowledge)
    print("📂 Loading your AI's previous knowledge...")
    if trainer.agent.load_model("trained_model.pkl"):
        print("✅ Previous training loaded successfully!")
        print(f"   🧠 Your AI remembers {len(trainer.agent.q_table)} learned states")
        print(f"   📚 Continuing from episode {trainer.agent.total_episodes + 1}")
        print("   🎯 This training will BUILD ON previous learning")
    else:
        print("⚠️  No previous training found, starting fresh")
    
    # Display current AI knowledge
    if hasattr(trainer.agent, 'q_table') and trainer.agent.q_table:
        print(f"\n🧠 AI KNOWLEDGE STATUS:")
        print(f"   States learned: {len(trainer.agent.q_table)}")
        print(f"   Total actions tried: {sum(len(actions) for actions in trainer.agent.q_table.values())}")
        print("   🔄 This knowledge will be used and expanded")
    
    print("\n🎓 ENHANCED PARAMETERS:")
    print(f"   Episodes: {trainer.max_episodes}")
    print(f"   Steps per episode: {trainer.max_steps_per_episode}")
    print("   Learning rate: 0.1 (balanced learning)")
    print("   Exploration: Dynamic (starts high, decreases)")
    print("   Reward system: Progress-based")
    
    print("\n🎯 TRAINING GOALS:")
    print("   1. Achieve first successful form completion")
    print("   2. Build robust action patterns") 
    print("   3. Improve form completion beyond 33.3%")
    print("   4. Develop consistent success strategy")
    
    # Start enhanced training
    print("\n🚀 Starting enhanced training session...")
    print("   Your AI will continue learning from where it left off!")
    trainer.start_training()

def analyze_progress():
    """
    Quick analysis of your AI's learning progress
    """
    print("\n📊 PROGRESS ANALYSIS:")
    print("=" * 30)
    
    # Check for saved models
    if os.path.exists("trained_model.pkl"):
        print("✅ Trained model exists - AI has memory!")
        file_size = os.path.getsize("trained_model.pkl")
        print(f"   Model size: {file_size} bytes")
        print("   🧠 Contains accumulated Q-learning knowledge")
    else:
        print("❌ No saved model found")
    
    # Check for training data
    import glob
    training_files = glob.glob("training_data_*.json")
    if training_files:
        print(f"✅ {len(training_files)} training session(s) recorded")
        for file in sorted(training_files):
            size = os.path.getsize(file)
            print(f"   📄 {file}: {size} bytes")
    
    # Check for visualizations
    plot_files = glob.glob("training_progress_*.png")
    if plot_files:
        print(f"✅ {len(plot_files)} training visualization(s) saved")
        print("   📊 Check these graphs to see learning progress")

if __name__ == "__main__":
    print("🤖 SELENIUM RL TRAINING ENHANCER")
    print("=" * 40)
    
    # Analyze current progress
    analyze_progress()
    
    print("\n" + "=" * 40)
    
    # Ask user what they want to do
    choice = input("\nWhat would you like to do?\n"
                  "1. Continue enhanced training (recommended)\n"
                  "2. Just analyze current progress\n"
                  "3. Test current AI performance\n"
                  "Choice (1-3): ").strip()
    
    if choice == "1":
        enhanced_training()
    elif choice == "2":
        print("\n✅ Analysis complete! Your AI's knowledge is preserved.")
        print("💡 Tip: Run option 1 to continue improving your AI")
    elif choice == "3":
        print("\n🧪 Testing feature coming soon!")
        print("💡 For now, use the training completion test prompt")
    else:
        print("\n📚 Your AI's knowledge is safely stored in trained_model.pkl")
        print("   Run this script again anytime to continue training!")
