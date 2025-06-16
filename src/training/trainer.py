"""
Main Training Loop - Orchestrates RL Training
=============================================

This module contains the main training loop that coordinates
the agent, environment, and training process.
"""

import time
import json
from typing import Dict, Any, List
from src.agents.q_learning_agent import QLearningAgent
from src.environment.web_environment import WebEnvironment

class Trainer:
    """
    Main training orchestrator for Selenium RL
    
    Coordinates the training process between agent and environment
    """
    
    def __init__(self, 
                 environment: WebEnvironment,
                 agent: QLearningAgent,
                 max_episodes: int = 100,
                 debug: bool = False):
        """
        Initialize the trainer
        
        Args:
            environment: Web environment to train in
            agent: RL agent to train
            max_episodes: Maximum number of training episodes
            debug: Enable debug output
        """
        self.environment = environment
        self.agent = agent
        self.max_episodes = max_episodes
        self.debug = debug
        
        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.success_episodes = []
        
    def train(self) -> Dict[str, Any]:
        """
        Run the main training loop
        
        Returns:
            Training statistics and results
        """
        print(f"🚀 Starting training for {self.max_episodes} episodes...")
        
        for episode in range(self.max_episodes):
            episode_reward, episode_length, success = self._run_episode(episode + 1)
            
            # Record statistics
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            self.success_episodes.append(success)
            
            # Print progress
            if self.debug or episode % 10 == 0:
                avg_reward = sum(self.episode_rewards[-10:]) / min(10, len(self.episode_rewards))
                success_rate = sum(self.success_episodes[-10:]) / min(10, len(self.success_episodes))
                print(f"Episode {episode + 1}: Reward={episode_reward:.2f}, "
                      f"Avg={avg_reward:.2f}, Success={success_rate:.1%}")
        
        # Training completed
        return self._get_training_stats()
    
    def _run_episode(self, episode_num: int) -> tuple[float, int, bool]:
        """
        Run a single training episode
        
        Returns:
            Tuple of (total_reward, episode_length, success)
        """
        # Reset environment
        observation = self.environment.reset()
        
        # Start episode
        self.agent.start_episode()
        
        total_reward = 0
        step_count = 0
        done = False
        
        while not done:
            # Get current state
            elements = observation['elements']
            form_state = observation['form_state']
            state = self.agent.get_state_signature(elements, form_state)
            
            # Choose action
            possible_actions = self.agent.get_possible_actions(elements)
            if not possible_actions:
                break
                
            action = self.agent.choose_action(state, possible_actions)
            
            # Execute action
            next_observation, reward, done, info = self.environment.step(action)
            
            # Get next state
            next_elements = next_observation['elements']
            next_form_state = next_observation['form_state']
            next_state = self.agent.get_state_signature(next_elements, next_form_state)
            
            # Learn from experience
            self.agent.learn(state, action, reward, next_state, done)
            self.agent.step(reward)
            
            # Update for next iteration
            observation = next_observation
            total_reward += reward
            step_count += 1
        
        # End episode
        success = observation['form_state']['success']
        self.agent.end_episode(success)
        
        return total_reward, step_count, success
    
    def _get_training_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive training statistics
        """
        total_episodes = len(self.episode_rewards)
        total_successes = sum(self.success_episodes)
        
        return {
            'total_episodes': total_episodes,
            'total_successes': total_successes,
            'success_rate': total_successes / total_episodes if total_episodes > 0 else 0,
            'average_reward': sum(self.episode_rewards) / total_episodes if total_episodes > 0 else 0,
            'best_reward': max(self.episode_rewards) if self.episode_rewards else 0,
            'average_episode_length': sum(self.episode_lengths) / total_episodes if total_episodes > 0 else 0,
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'success_episodes': self.success_episodes
        }
