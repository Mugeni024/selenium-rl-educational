import os
import sys
sys.path.append('src')

from complete_trainer import SeleniumRLTrainer

def continue_training():
    # Get the path to our demo HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    target_url = f"file://{html_path}"
    
    # Create trainer
    trainer = SeleniumRLTrainer(
        target_url=target_url,
        max_episodes=10,  # Additional episodes
        max_steps_per_episode=15,  # More steps per episode
        save_model_path="trained_model.pkl",
        debug=True
    )
    
    # Load previous training
    print("📂 Loading previous training...")
    if trainer.agent.load_model("trained_model.pkl"):
        print("✅ Previous training loaded successfully!")
        print(f"   Continuing from episode {trainer.agent.total_episodes + 1}")
    else:
        print("⚠️  No previous training found, starting fresh")
    
    # Continue training
    trainer.start_training()

if __name__ == "__main__":
    continue_training()
