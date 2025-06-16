"""
Q-Learning Agent - The AI's Decision-Making Brain
==============================================

This is the core intelligence that learns from experience:
1. Remembers what actions worked in what situations
2. Explores new possibilities vs exploiting known good actions
3. Updates its knowledge based on rewards
4. Gets smarter over time!

Think of it as the AI's memory and decision-making center.
"""

import numpy as np
import pandas as pd
import pickle
import random
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import matplotlib.pyplot as plt

@dataclass
class Experience:
    """A single learning experience: what happened when the AI took an action"""
    state: str
    action: str
    reward: float
    next_state: str
    done: bool
    timestamp: float

class QLearningAgent:
    """
    The AI's Brain - Learns from trial and error using Q-Learning
    
    Q-Learning works by maintaining a table of "Q-values" that represent
    how good each action is in each state. The AI updates these values
    based on the rewards it receives.
    """
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.3,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 debug: bool = True):
        """
        Initialize the AI's brain
        
        Args:
            learning_rate: How fast the AI learns (0.1 = slow but stable)
            discount_factor: How much future rewards matter (0.95 = values future)
            epsilon: Exploration rate (0.3 = explores 30% of the time)
            epsilon_decay: How quickly exploration decreases
            epsilon_min: Minimum exploration rate
            debug: Print learning information
        """
        # Core Q-Learning parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.debug = debug
        
        # Q-table: stores the "value" of each action in each state
        # Format: Q[state][action] = expected_reward
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Learning statistics
        self.total_episodes = 0
        self.total_steps = 0
        self.episode_rewards = []
        self.episode_lengths = []
        self.success_episodes = []
        
        # Experience memory for advanced learning
        self.memory = deque(maxlen=10000)
        self.experience_count = 0
        
        # Action tracking
        self.action_counts = defaultdict(int)
        self.state_visits = defaultdict(int)
        
        if self.debug:
            print("🧠 Q-Learning Agent initialized!")
            print(f"   Learning rate: {learning_rate}")
            print(f"   Exploration rate: {epsilon}")
            print(f"   Discount factor: {discount_factor}")
    
    def get_state_signature(self, elements: List, form_state: Dict) -> str:
        """
        Convert webpage state into a string signature
        This is how the AI "remembers" different webpage situations
        """
        # Count different types of elements
        element_counts = {}
        filled_fields = 0
        required_fields = 0
        
        for elem in elements:
            elem_type = elem.element_type.value
            element_counts[elem_type] = element_counts.get(elem_type, 0) + 1
            
            if elem.is_required:
                required_fields += 1
                if elem.value and elem.value.strip():
                    filled_fields += 1
        
        # Include form completion progress
        progress = form_state.get('progress', 0)
        is_complete = form_state.get('completed', False)
        
        # Create a state signature
        state_parts = [
            f"progress_{int(progress//10)*10}",  # Progress in 10% buckets
            f"filled_{filled_fields}",
            f"required_{required_fields}",
            f"complete_{is_complete}"
        ]
        
        # Add element type counts
        for elem_type, count in sorted(element_counts.items()):
            state_parts.append(f"{elem_type}_{count}")
        
        state_signature = "|".join(state_parts)
        self.state_visits[state_signature] += 1
        
        return state_signature
    
    def get_possible_actions(self, elements: List) -> List[str]:
        """
        Generate all possible actions the AI can take
        Each action is a string like "click_submitBtn" or "type_name_John"
        """
        actions = []
        
        for elem in elements:
            if not elem.is_enabled:
                continue
                
            elem_id = elem.id
            
            # Generate actions based on element type and capabilities
            for action_type in elem.possible_actions:
                if action_type.value == "click":
                    actions.append(f"click_{elem_id}")
                    
                elif action_type.value == "type_text":
                    # Generate different text options
                    sample_texts = self._get_sample_texts(elem)
                    for text in sample_texts:
                        actions.append(f"type_{elem_id}_{text}")
                        
                elif action_type.value == "select_option":
                    # For dropdowns, we'll add generic select action
                    actions.append(f"select_{elem_id}")
                    
                elif action_type.value == "check":
                    actions.append(f"check_{elem_id}")
                    
                elif action_type.value == "uncheck":
                    actions.append(f"uncheck_{elem_id}")
                    
                elif action_type.value == "clear":
                    actions.append(f"clear_{elem_id}")
        
        return actions
    
    def _get_sample_texts(self, elem) -> List[str]:
        """Generate appropriate sample texts for different input types"""
        elem_type = elem.element_type.value
        elem_id = elem.id.lower()
        
        if elem_type == "email_input":
            return ["test@example.com", "user@demo.com"]
        elif "name" in elem_id:
            return ["John_Doe", "Jane_Smith"]
        elif elem_type == "textarea":
            return ["AI_learning_demo", "Test_description"]
        else:
            return ["sample_text", "test_input"]
    
    def choose_action(self, state: str, possible_actions: List[str]) -> str:
        """
        The AI's decision-making: choose the best action for current state
        
        Uses epsilon-greedy strategy:
        - Most of the time: pick the action with highest Q-value (exploit)
        - Sometimes: pick a random action (explore)
        """
        if not possible_actions:
            return None
        
        # Exploration vs Exploitation decision
        if random.random() < self.epsilon:
            # EXPLORE: Try something random
            action = random.choice(possible_actions)
            if self.debug:
                print(f"🎲 EXPLORING: Random action '{action[:30]}...'")
        else:
            # EXPLOIT: Use what we've learned
            action = self._get_best_action(state, possible_actions)
            if self.debug:
                print(f"🎯 EXPLOITING: Best known action '{action[:30]}...'")
        
        # Track action usage
        self.action_counts[action] += 1
        return action
    
    def _get_best_action(self, state: str, possible_actions: List[str]) -> str:
        """Find the action with highest Q-value for this state"""
        q_values = {}
        
        for action in possible_actions:
            q_values[action] = self.q_table[state][action]
        
        # Find action with highest Q-value
        best_action = max(q_values.keys(), key=lambda a: q_values[a])
        
        if self.debug and q_values[best_action] > 0:
            print(f"   Q-value: {q_values[best_action]:.3f}")
        
        return best_action
    
    def learn(self, state: str, action: str, reward: float, next_state: str, done: bool):
        """
        Update the AI's knowledge based on what just happened
        This is the core of Q-Learning!
        
        Q(s,a) = Q(s,a) + α * [reward + γ * max(Q(s',a')) - Q(s,a)]
        """
        # Get current Q-value
        current_q = self.q_table[state][action]
        
        # Find the best possible future reward
        if done:
            # Episode ended, no future rewards
            max_future_q = 0
        else:
            # Look at all possible actions in next state
            next_state_actions = list(self.q_table[next_state].keys())
            if next_state_actions:
                max_future_q = max(self.q_table[next_state][a] for a in next_state_actions)
            else:
                max_future_q = 0
        
        # Calculate new Q-value using Q-Learning formula
        target_q = reward + self.discount_factor * max_future_q
        new_q = current_q + self.learning_rate * (target_q - current_q)
        
        # Update Q-table
        self.q_table[state][action] = new_q
        
        # Store experience for analysis
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            timestamp=self.experience_count
        )
        self.memory.append(experience)
        self.experience_count += 1
        
        # Debug information
        if self.debug and abs(new_q - current_q) > 0.001:
            print(f"📚 LEARNING: Q({state[:20]}..., {action[:20]}...) = {new_q:.3f} (was {current_q:.3f})")
            print(f"   Reward: {reward:.2f}, Future value: {max_future_q:.3f}")
    
    def start_episode(self):
        """Start a new learning episode"""
        self.total_episodes += 1
        self.current_episode_steps = 0
        self.current_episode_reward = 0
        
        if self.debug:
            print(f"\n🚀 Starting Episode {self.total_episodes}")
            print(f"   Exploration rate: {self.epsilon:.3f}")
    
    def end_episode(self, success: bool = False):
        """End the current episode and update statistics"""
        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Record statistics
        self.episode_rewards.append(self.current_episode_reward)
        self.episode_lengths.append(self.current_episode_steps)
        self.success_episodes.append(success)
        
        if self.debug:
            print(f"✅ Episode {self.total_episodes} completed!")
            print(f"   Steps: {self.current_episode_steps}")
            print(f"   Total reward: {self.current_episode_reward:.2f}")
            print(f"   Success: {'YES' if success else 'NO'}")
            
            # Show recent performance
            if len(self.success_episodes) >= 10:
                recent_success_rate = sum(self.success_episodes[-10:]) / 10 * 100
                print(f"   Recent success rate: {recent_success_rate:.1f}%")
    
    def step(self, reward: float):
        """Record a step in the current episode"""
        self.current_episode_steps += 1
        self.current_episode_reward += reward
        self.total_steps += 1
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        if not self.episode_rewards:
            return {"message": "No episodes completed yet"}
        
        recent_episodes = min(10, len(self.episode_rewards))
        recent_rewards = self.episode_rewards[-recent_episodes:]
        recent_successes = self.success_episodes[-recent_episodes:]
        
        stats = {
            "total_episodes": self.total_episodes,
            "total_steps": self.total_steps,
            "q_table_size": len(self.q_table),
            "unique_states": len(self.state_visits),
            "unique_actions": len(self.action_counts),
            "exploration_rate": self.epsilon,
            
            "recent_performance": {
                "avg_reward": np.mean(recent_rewards),
                "avg_episode_length": np.mean(self.episode_lengths[-recent_episodes:]),
                "success_rate": np.mean(recent_successes) * 100,
                "episodes_analyzed": recent_episodes
            },
            
            "overall_performance": {
                "avg_reward": np.mean(self.episode_rewards),
                "total_successes": sum(self.success_episodes),
                "overall_success_rate": np.mean(self.success_episodes) * 100 if self.success_episodes else 0
            }
        }
        
        return stats
    
    def save_model(self, filepath: str):
        """Save the AI's learned knowledge to a file"""
        model_data = {
            "q_table": dict(self.q_table),
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "epsilon": self.epsilon,
            "total_episodes": self.total_episodes,
            "total_steps": self.total_steps,
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "success_episodes": self.success_episodes,
            "action_counts": dict(self.action_counts),
            "state_visits": dict(self.state_visits)
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        if self.debug:
            print(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load previously learned knowledge"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restore Q-table with proper defaultdict structure
            self.q_table = defaultdict(lambda: defaultdict(float))
            for state, actions in model_data["q_table"].items():
                for action, q_value in actions.items():
                    self.q_table[state][action] = q_value
            
            # Restore other attributes
            for attr in ["learning_rate", "discount_factor", "epsilon", "total_episodes", 
                        "total_steps", "episode_rewards", "episode_lengths", "success_episodes"]:
                if attr in model_data:
                    setattr(self, attr, model_data[attr])
            
            self.action_counts = defaultdict(int, model_data.get("action_counts", {}))
            self.state_visits = defaultdict(int, model_data.get("state_visits", {}))
            
            if self.debug:
                print(f"📂 Model loaded from {filepath}")
                print(f"   Episodes: {self.total_episodes}")
                print(f"   Q-table entries: {len(self.q_table)}")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"❌ Failed to load model: {e}")
            return False
    
    def plot_learning_progress(self, save_path: str = None):
        """Create visualizations of the learning progress"""
        if len(self.episode_rewards) < 2:
            print("❌ Not enough data to plot (need at least 2 episodes)")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Episode rewards over time
        ax1.plot(self.episode_rewards, 'b-', alpha=0.7)
        ax1.set_title('Episode Rewards Over Time')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True)
        
        # Moving average of rewards
        if len(self.episode_rewards) >= 10:
            window = min(10, len(self.episode_rewards))
            moving_avg = pd.Series(self.episode_rewards).rolling(window=window).mean()
            ax1.plot(moving_avg, 'r-', linewidth=2, label=f'{window}-episode average')
            ax1.legend()
        
        # Success rate over time
        success_rate = []
        window_size = 10
        for i in range(len(self.success_episodes)):
            start_idx = max(0, i - window_size + 1)
            window_successes = self.success_episodes[start_idx:i+1]
            success_rate.append(sum(window_successes) / len(window_successes) * 100)
        
        ax2.plot(success_rate, 'g-', linewidth=2)
        ax2.set_title(f'Success Rate (Rolling {window_size}-episode window)')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_ylim(0, 105)
        ax2.grid(True)
        
        # Episode lengths
        ax3.plot(self.episode_lengths, 'orange', alpha=0.7)
        ax3.set_title('Episode Lengths')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Steps per Episode')
        ax3.grid(True)
        
        # Exploration rate over time
        exploration_rates = []
        epsilon = 0.3  # Starting epsilon
        for _ in range(self.total_episodes):
            exploration_rates.append(epsilon)
            epsilon = max(self.epsilon_min, epsilon * self.epsilon_decay)
        
        ax4.plot(exploration_rates, 'purple', linewidth=2)
        ax4.set_title('Exploration Rate Over Time')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Epsilon (Exploration Rate)')
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Learning progress saved to {save_path}")
        
        plt.show()

# Demo function to test the Q-Learning Agent
def demo_q_learning():
    """
    Demo: See how the AI's brain works!
    """
    print("🧠 Q-Learning Agent Demo")
    print("="*50)
    
    agent = QLearningAgent(debug=True)
    
    # Simulate a simple learning scenario
    print("\n🎮 Simulating AI learning...")
    
    # Define a simple state and actions
    states = ["empty_form", "partial_form", "complete_form"]
    actions = ["click_name", "type_name_John", "click_email", "type_email_test", "click_submit"]
    
    # Simulate 5 episodes of learning
    for episode in range(5):
        agent.start_episode()
        
        current_state = "empty_form"
        
        for step in range(10):  # Max 10 steps per episode
            # Choose action
            action = agent.choose_action(current_state, actions)
            
            # Simulate reward and next state
            if "submit" in action and current_state == "complete_form":
                reward = 10.0  # Big reward for successful completion
                next_state = "success"
                done = True
            elif "type" in action:
                reward = 1.0   # Small reward for filling fields
                next_state = "partial_form" if current_state == "empty_form" else "complete_form"
                done = False
            elif "click" in action:
                reward = 0.1   # Tiny reward for clicking
                next_state = current_state
                done = False
            else:
                reward = -0.1  # Small penalty for other actions
                next_state = current_state
                done = False
            
            # Learn from this experience
            agent.learn(current_state, action, reward, next_state, done)
            agent.step(reward)
            
            current_state = next_state
            
            if done:
                break
        
        # End episode
        success = current_state == "success"
        agent.end_episode(success)
    
    # Show final statistics
    print("\n📊 Final Learning Statistics:")
    stats = agent.get_learning_stats()
    print(f"   Total episodes: {stats['total_episodes']}")
    print(f"   Success rate: {stats['overall_performance']['overall_success_rate']:.1f}%")
    print(f"   Q-table size: {stats['q_table_size']} states")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    demo_q_learning()