"""
Complete AI Trainer - The Full Selenium Reinforcement Learning System
====================================================================

This brings together all components:
1. Element Detector (AI's eyes) - Scans webpage
2. Q-Learning Agent (AI's brain) - Makes decisions  
3. Web Action Executor (AI's hands) - Performs actions

Watch the AI learn to fill forms through trial and error!
"""

import os
import sys
import time
import json
from typing import Dict, List, Any
import matplotlib.pyplot as plt

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from environment.element_detector import ElementDetector
from agents.q_learning_agent import QLearningAgent
from environment.web_action_executor import WebActionExecutor, ActionResult

class SeleniumRLTrainer:
    """
    Complete AI Training System
    
    This orchestrates the entire learning process:
    1. Start browser and load webpage
    2. Let AI observe the page (Element Detector)
    3. AI chooses actions (Q-Learning Agent)
    4. Execute actions on webpage (Web Action Executor)
    5. Calculate rewards and learn from results
    6. Repeat until AI masters the task!
    """
    
    def __init__(self, 
                 target_url: str,
                 max_episodes: int = 20,
                 max_steps_per_episode: int = 15,
                 save_model_path: str = "trained_model.pkl",
                 debug: bool = True):
        """
        Initialize the complete training system
        
        Args:
            target_url: URL of webpage to train on
            max_episodes: How many training attempts
            max_steps_per_episode: Max actions per attempt
            save_model_path: Where to save the trained AI
            debug: Print detailed information
        """
        self.target_url = target_url
        self.max_episodes = max_episodes
        self.max_steps_per_episode = max_steps_per_episode
        self.save_model_path = save_model_path
        self.debug = debug
        
        # Initialize all components
        self.detector = ElementDetector(debug=debug)
        self.agent = QLearningAgent(
            learning_rate=0.15,
            epsilon=0.4,  # More exploration initially
            epsilon_decay=0.95,
            debug=debug
        )
        self.executor = None  # Will be initialized after browser starts
        
        # Training statistics
        self.training_stats = {
            'episode_rewards': [],
            'episode_steps': [],
            'success_episodes': [],
            'form_completion_progress': [],
            'action_success_rates': []
        }
        
        self.best_episode_reward = -float('inf')
        self.consecutive_successes = 0
        
        if self.debug:
            print("🚀 Selenium RL Trainer initialized!")
            print(f"   Target URL: {target_url}")
            print(f"   Max episodes: {max_episodes}")
            print(f"   Max steps per episode: {max_steps_per_episode}")
    
    def start_training(self):
        """
        Start the complete AI training process!
        This is where the magic happens.
        """
        print("\n" + "="*80)
        print("🎓 STARTING AI TRAINING SESSION")
        print("="*80)
        print("The AI will now learn to complete the form through trial and error!")
        print("Watch as it gets smarter with each episode...\n")
        
        # Start browser and load page
        if not self._initialize_environment():
            print("❌ Failed to initialize environment")
            return False
        
        try:
            # Main training loop
            for episode in range(1, self.max_episodes + 1):
                success = self._run_episode(episode)
                
                # Check if AI has mastered the task
                if self._check_mastery():
                    print(f"\n🏆 AI HAS MASTERED THE TASK! Training completed after {episode} episodes.")
                    break
                
                # Brief pause between episodes
                time.sleep(1)
            
            # Training completed
            self._finalize_training()
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Training interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            return False
        finally:
            self._cleanup()
    
    def _initialize_environment(self) -> bool:
        """Set up browser and load the target webpage"""
        print("🌐 Initializing environment...")
        
        # Start browser
        if not self.detector.start_browser():
            return False
        
        # Load target page
        if not self.detector.load_page(self.target_url):
            return False
        
        # Initialize executor with the browser driver
        self.executor = WebActionExecutor(self.detector.driver, debug=self.debug)
        
        print("✅ Environment ready!")
        return True
    
    def _run_episode(self, episode_num: int) -> bool:
        """
        Run a single training episode
        
        Returns:
            bool: True if episode was successful (goal achieved)
        """
        if self.debug:
            print(f"\n{'='*60}")
            print(f"🎮 EPISODE {episode_num}")
            print(f"{'='*60}")
        
        # Start new episode
        self.agent.start_episode()
        
        # Reset page to initial state
        self.detector.driver.refresh()
        time.sleep(2)
        
        episode_reward = 0
        previous_progress = 0
        steps_taken = 0
        success_achieved = False
        
        # Episode loop: observe → decide → act → learn
        for step in range(self.max_steps_per_episode):
            steps_taken += 1
            
            if self.debug:
                print(f"\n--- Step {step + 1} ---")
            
            # 1. OBSERVE: AI scans the webpage
            elements = self.detector.detect_elements()
            form_state = self.detector.get_form_completion_state()
            current_progress = form_state.get('progress', 0)
            
            # Check if goal is achieved
            if form_state.get('success', False):
                if self.debug:
                    print("🎉 GOAL ACHIEVED! Success panel is visible!")
                success_achieved = True
                break
            
            # 2. DECIDE: AI chooses what to do next
            current_state = self.agent.get_state_signature(elements, form_state)
            possible_actions = self.agent.get_possible_actions(elements)
            
            if not possible_actions:
                if self.debug:
                    print("⚠️  No possible actions available")
                break
            
            chosen_action = self.agent.choose_action(current_state, possible_actions)
            
            # 3. ACT: AI performs the chosen action
            execution_result = self.executor.execute_action(chosen_action, elements)
            
            # 4. CALCULATE REWARD: How well did the AI do?
            action_reward = execution_result.reward
            
            # Add progress-based reward
            progress_reward = self.executor.calculate_progress_reward(
                previous_progress, current_progress, success_achieved
            )
            
            total_reward = action_reward + progress_reward
            episode_reward += total_reward
            
            # 5. LEARN: Update AI's knowledge
            # Get new state after action
            time.sleep(0.5)  # Wait for any page changes
            new_elements = self.detector.detect_elements()
            new_form_state = self.detector.get_form_completion_state()
            next_state = self.agent.get_state_signature(new_elements, new_form_state)
            
            # Check if episode should end
            done = (success_achieved or 
                   step == self.max_steps_per_episode - 1 or
                   execution_result.result == ActionResult.FAILED)
            
            # Teach the AI what happened
            self.agent.learn(current_state, chosen_action, total_reward, next_state, done)
            self.agent.step(total_reward)
            
            # Update progress tracking
            previous_progress = current_progress
            
            if self.debug:
                print(f"   Progress: {current_progress:.1f}% → Reward: {total_reward:+.2f}")
            
            if done:
                break
        
        # End episode
        self.agent.end_episode(success_achieved)
        
        # Record statistics
        self._record_episode_stats(episode_reward, steps_taken, success_achieved, current_progress)
        
        # Show episode summary
        if self.debug:
            self._print_episode_summary(episode_num, episode_reward, steps_taken, 
                                      success_achieved, current_progress)
        
        return success_achieved
    
    def _record_episode_stats(self, reward: float, steps: int, success: bool, progress: float):
        """Record statistics for this episode"""
        self.training_stats['episode_rewards'].append(reward)
        self.training_stats['episode_steps'].append(steps)
        self.training_stats['success_episodes'].append(success)
        self.training_stats['form_completion_progress'].append(progress)
        
        # Track action success rate
        action_stats = self.executor.get_action_statistics()
        if action_stats.get('total_actions', 0) > 0:
            self.training_stats['action_success_rates'].append(action_stats['success_rate'])
        
        # Update best episode tracking
        if reward > self.best_episode_reward:
            self.best_episode_reward = reward
        
        # Track consecutive successes
        if success:
            self.consecutive_successes += 1
        else:
            self.consecutive_successes = 0
    
    def _print_episode_summary(self, episode: int, reward: float, steps: int, 
                              success: bool, progress: float):
        """Print a summary of the episode"""
        status = "🎉 SUCCESS" if success else "❌ Failed"
        print(f"\n📊 Episode {episode} Summary:")
        print(f"   Status: {status}")
        print(f"   Reward: {reward:.2f} (best: {self.best_episode_reward:.2f})")
        print(f"   Steps: {steps}")
        print(f"   Form completion: {progress:.1f}%")
        
        # Show recent performance
        if len(self.training_stats['success_episodes']) >= 5:
            recent_successes = sum(self.training_stats['success_episodes'][-5:])
            print(f"   Recent success rate: {recent_successes}/5 ({recent_successes*20:.0f}%)")
        
        # Show learning progress
        agent_stats = self.agent.get_learning_stats()
        print(f"   Exploration rate: {agent_stats['exploration_rate']:.3f}")
        print(f"   Knowledge base: {agent_stats['q_table_size']} states learned")
    
    def _check_mastery(self) -> bool:
        """Check if AI has mastered the task"""
        # Need at least 5 episodes to evaluate
        if len(self.training_stats['success_episodes']) < 5:
            return False
        
        # Check if last 3 episodes were all successful
        recent_successes = self.training_stats['success_episodes'][-3:]
        if all(recent_successes):
            return True
        
        # Check if success rate is very high over last 10 episodes
        if len(self.training_stats['success_episodes']) >= 10:
            last_10_success_rate = sum(self.training_stats['success_episodes'][-10:]) / 10
            if last_10_success_rate >= 0.8:  # 80% success rate
                return True
        
        return False
    
    def _finalize_training(self):
        """Complete the training process"""
        print("\n" + "="*80)
        print("🎓 TRAINING COMPLETED!")
        print("="*80)
        
        # Save the trained model
        self.agent.save_model(self.save_model_path)
        
        # Print final statistics
        self._print_final_statistics()
        
        # Create visualizations
        self._create_training_visualizations()
        
        # Save training data
        self._save_training_data()
    
    def _print_final_statistics(self):
        """Print comprehensive training statistics"""
        total_episodes = len(self.training_stats['episode_rewards'])
        total_successes = sum(self.training_stats['success_episodes'])
        
        print("📈 FINAL TRAINING STATISTICS:")
        print(f"   Episodes completed: {total_episodes}")
        print(f"   Successful episodes: {total_successes}")
        print(f"   Overall success rate: {(total_successes/total_episodes)*100:.1f}%")
        print(f"   Best episode reward: {self.best_episode_reward:.2f}")
        print(f"   Average episode length: {sum(self.training_stats['episode_steps'])/total_episodes:.1f} steps")
        
        if self.training_stats['episode_rewards']:
            print(f"   Average reward: {sum(self.training_stats['episode_rewards'])/total_episodes:.2f}")
        
        # AI knowledge statistics
        agent_stats = self.agent.get_learning_stats()
        print(f"\n🧠 AI KNOWLEDGE BASE:")
        print(f"   States learned: {agent_stats['q_table_size']}")
        print(f"   Actions tried: {agent_stats['unique_actions']}")
        print(f"   Total learning steps: {agent_stats['total_steps']}")
        
        # Action execution statistics
        action_stats = self.executor.get_action_statistics()
        if action_stats.get('total_actions', 0) > 0:
            print(f"\n🤲 ACTION EXECUTION:")
            print(f"   Total actions: {action_stats['total_actions']}")
            print(f"   Action success rate: {action_stats['success_rate']:.1f}%")
    
    def _create_training_visualizations(self):
        """Create plots showing training progress"""
        if len(self.training_stats['episode_rewards']) < 2:
            print("⚠️  Not enough data for visualizations")
            return
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('🤖 AI Training Progress', fontsize=16, fontweight='bold')
            
            episodes = range(1, len(self.training_stats['episode_rewards']) + 1)
            
            # Episode rewards
            ax1.plot(episodes, self.training_stats['episode_rewards'], 'b-o', markersize=4)
            ax1.set_title('📊 Episode Rewards')
            ax1.set_xlabel('Episode')
            ax1.set_ylabel('Total Reward')
            ax1.grid(True, alpha=0.3)
            
            # Success rate (rolling window)
            if len(episodes) >= 3:
                window_size = min(5, len(episodes))
                success_rate = []
                for i in range(len(episodes)):
                    start_idx = max(0, i - window_size + 1)
                    window_successes = self.training_stats['success_episodes'][start_idx:i+1]
                    success_rate.append(sum(window_successes) / len(window_successes) * 100)
                
                ax2.plot(episodes, success_rate, 'g-o', markersize=4)
                ax2.set_title(f'📈 Success Rate (Rolling {window_size}-Episode Window)')
                ax2.set_xlabel('Episode')
                ax2.set_ylabel('Success Rate (%)')
                ax2.set_ylim(0, 105)
                ax2.grid(True, alpha=0.3)
            
            # Form completion progress
            ax3.plot(episodes, self.training_stats['form_completion_progress'], 'orange', marker='o', markersize=4)
            ax3.set_title('📝 Form Completion Progress')
            ax3.set_xlabel('Episode')
            ax3.set_ylabel('Completion (%)')
            ax3.set_ylim(0, 105)
            ax3.grid(True, alpha=0.3)
            
            # Episode lengths
            ax4.plot(episodes, self.training_stats['episode_steps'], 'purple', marker='o', markersize=4)
            ax4.set_title('⏱️  Episode Lengths')
            ax4.set_xlabel('Episode')
            ax4.set_ylabel('Steps per Episode')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save the plot
            plot_filename = f"training_progress_{int(time.time())}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"📊 Training visualizations saved to {plot_filename}")
            
            # Show plot for 3 seconds then close
            plt.show(block=False)
            time.sleep(3)
            plt.close()
            
        except Exception as e:
            print(f"⚠️  Could not create visualizations: {e}")
    
    def _save_training_data(self):
        """Save training data to JSON file"""
        try:
            training_data = {
                'training_stats': self.training_stats,
                'agent_stats': self.agent.get_learning_stats(),
                'executor_stats': self.executor.get_action_statistics(),
                'training_config': {
                    'max_episodes': self.max_episodes,
                    'max_steps_per_episode': self.max_steps_per_episode,
                    'target_url': self.target_url
                },
                'timestamp': time.time()
            }
            
            data_filename = f"training_data_{int(time.time())}.json"
            with open(data_filename, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            print(f"💾 Training data saved to {data_filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save training data: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        if self.detector:
            self.detector.close()
        print("🔒 Browser closed and resources cleaned up")
    
    def test_trained_model(self, model_path: str = None):
        """Test a previously trained model"""
        if model_path is None:
            model_path = self.save_model_path
        
        print(f"\n🧪 Testing trained model from {model_path}")
        
        # Load the trained model
        if not self.agent.load_model(model_path):
            print("❌ Failed to load model")
            return False
        
        # Set to pure exploitation (no exploration)
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0.0
        
        # Initialize environment
        if not self._initialize_environment():
            return False
        
        try:
            # Run a test episode
            print("🎮 Running test episode...")
            success = self._run_episode("TEST")
            
            print(f"\n🎯 Test Result: {'SUCCESS' if success else 'FAILED'}")
            
            return success
            
        finally:
            self.agent.epsilon = original_epsilon
            self._cleanup()

def main():
    """
    Main function to run the complete training system
    """
    print("🚀 Welcome to Selenium Reinforcement Learning!")
    print("="*60)
    
    # Get the path to our demo HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    
    if not os.path.exists(html_path):
        print(f"❌ Demo HTML file not found at: {html_path}")
        print("Please make sure demo/test_form.html exists!")
        return
    
    target_url = f"file://{html_path}"
    
    # Create trainer
    trainer = SeleniumRLTrainer(
        target_url=target_url,
        max_episodes=15,  # Start with fewer episodes for demo
        max_steps_per_episode=12,
        debug=True
    )
    
    # Start training
    print(f"🎯 Target: AI will learn to complete the form at {target_url}")
    print("\nPress Ctrl+C at any time to stop training\n")
    
    success = trainer.start_training()
    
    if success:
        print("\n🎉 Training completed successfully!")
        
        # Ask if user wants to test the trained model
        try:
            response = input("\n🧪 Would you like to test the trained AI? (y/n): ").lower()
            if response == 'y':
                print("\n🎮 Testing the trained AI...")
                trainer.test_trained_model()
        except:
            pass
    else:
        print("\n❌ Training was not completed")

if __name__ == "__main__":
    main()