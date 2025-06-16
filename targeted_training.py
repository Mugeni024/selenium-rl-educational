#!/usr/bin/env python3
"""
TARGETED TRAINING - Focused on Breaking Through 33.3% Barrier
"""

import os
import sys
sys.path.append('src')

from complete_trainer import SeleniumRLTrainer

def targeted_training():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    target_url = f"file://{html_path}"
    
    print("🎯 TARGETED TRAINING - BREAKING THE 33.3% BARRIER")
    print("=" * 60)
    
    # Even more focused training
    trainer = SeleniumRLTrainer(
        target_url=target_url,
        max_episodes=30,              # More episodes
        max_steps_per_episode=40,     # More steps to complete task
        save_model_path="trained_model.pkl",
        debug=True
    )
    
    # Load existing knowledge
    if trainer.agent.load_model("trained_model.pkl"):
        print("✅ Loading your AI's accumulated knowledge...")
        print(f"   📚 Episodes completed so far: {trainer.agent.total_episodes}")
        print(f"   🧠 States learned: {len(trainer.agent.q_table)}")
        print("   🚀 Continuing with improved parameters!")
    
    print("\n🎯 TARGETED IMPROVEMENTS:")
    print("   ✅ More steps per episode (40 vs 25)")
    print("   ✅ More episodes for pattern learning (30)")
    print("   ✅ Existing Q-table knowledge preserved")
    print("   ✅ Focus on required field completion")
    
    trainer.start_training()

if __name__ == "__main__":
    targeted_training()
