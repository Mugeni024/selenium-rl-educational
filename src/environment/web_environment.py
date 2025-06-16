"""
Web Environment - Selenium RL Environment Interface
==================================================

This module provides the main environment interface for training
reinforcement learning agents with Selenium WebDriver.
"""

import time
from typing import Dict, List, Tuple, Any
from src.environment.element_detector import ElementDetector
from src.environment.web_action_executor import WebActionExecutor

class WebEnvironment:
    """
    Main environment interface for Selenium RL training
    
    This class orchestrates the interaction between:
    - Element detection (observation)
    - Action execution (interaction) 
    - Reward calculation (feedback)
    """
    
    def __init__(self, target_url: str, debug: bool = False):
        """
        Initialize the web environment
        
        Args:
            target_url: URL of the webpage to interact with
            debug: Enable debug output
        """
        self.target_url = target_url
        self.debug = debug
        
        # Initialize components
        self.detector = ElementDetector(debug=debug)
        self.executor = None
        
        # Environment state
        self.current_state = None
        self.episode_steps = 0
        self.max_steps = 50
        
    def reset(self) -> Dict[str, Any]:
        """
        Reset environment to initial state
        
        Returns:
            Initial observation of the environment
        """
        # Start browser if not running
        if not self.detector.driver:
            if not self.detector.start_browser():
                raise RuntimeError("Failed to start browser")
        
        # Load the target page
        if not self.detector.load_page(self.target_url):
            raise RuntimeError("Failed to load target page")
        
        # Initialize executor
        self.executor = WebActionExecutor(self.detector.driver, debug=self.debug)
        
        # Reset episode state
        self.episode_steps = 0
        
        # Get initial observation
        return self._get_observation()
    
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Execute an action and return the result
        
        Args:
            action: Action to execute
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        self.episode_steps += 1
        
        # Get current elements
        elements = self.detector.detect_elements()
        
        # Execute the action
        result = self.executor.execute_action(action, elements)
        
        # Get new observation
        observation = self._get_observation()
        
        # Calculate reward
        reward = result.reward
        
        # Check if episode is done
        done = (
            observation['form_state']['success'] or  # Success achieved
            self.episode_steps >= self.max_steps or  # Max steps reached
            result.result.value == 'error'  # Error occurred
        )
        
        # Additional info
        info = {
            'action_result': result.result.value,
            'steps': self.episode_steps,
            'form_progress': observation['form_state']['progress']
        }
        
        return observation, reward, done, info
    
    def _get_observation(self) -> Dict[str, Any]:
        """
        Get current observation of the environment
        
        Returns:
            Dictionary containing current state information
        """
        elements = self.detector.detect_elements()
        form_state = self.detector.get_form_completion_state()
        
        return {
            'elements': elements,
            'form_state': form_state,
            'step_count': self.episode_steps
        }
    
    def close(self):
        """
        Clean up environment resources
        """
        if self.detector:
            self.detector.close()
