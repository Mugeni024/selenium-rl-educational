"""
Web Action Executor - The AI's Hands
===================================

This class lets the AI actually DO things on webpages:
1. Execute actions chosen by the Q-Learning brain
2. Handle errors gracefully
3. Provide feedback on action success
4. Calculate rewards based on progress

Think of it as giving the AI hands to interact with the web!
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, 
    ElementClickInterceptedException, StaleElementReferenceException
)
import time
import random
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ActionResult(Enum):
    """Possible outcomes when the AI tries to perform an action"""
    SUCCESS = "success"
    FAILED = "failed"
    ELEMENT_NOT_FOUND = "element_not_found"
    ELEMENT_NOT_INTERACTABLE = "element_not_interactable"
    TIMEOUT = "timeout"
    ALREADY_COMPLETED = "already_completed"

@dataclass
class ExecutionResult:
    """Result of executing an action"""
    result: ActionResult
    message: str
    reward: float
    state_changed: bool
    element_id: str
    action_type: str
    execution_time: float

class WebActionExecutor:
    """
    The AI's Hands - Executes actions on webpages
    """
    
    def __init__(self, driver, debug: bool = True):
        """
        Initialize the action executor
        
        Args:
            driver: Selenium WebDriver instance
            debug: Print action details
        """
        self.driver = driver
        self.debug = debug
        self.wait = WebDriverWait(driver, 5)  # 5 second timeout
        
        # Track action history
        self.action_history = []
        self.successful_actions = 0
        self.failed_actions = 0
        
        # Sample data for form filling
        self.sample_data = {
            'names': ['John Doe', 'Jane Smith', 'Alex Johnson', 'Sarah Wilson'],
            'emails': ['john.doe@example.com', 'jane.smith@demo.com', 'alex.j@test.org'],
            'ages': ['18-25', '26-35', '36-45', '46+'],
            'descriptions': [
                'I am passionate about artificial intelligence and machine learning.',
                'Looking forward to exploring new technologies and innovations.',
                'Excited to participate in this AI training demonstration.',
                'Interested in automation and intelligent systems.'
            ]
        }
        
        if self.debug:
            print("🤲 Web Action Executor initialized!")
    
    def execute_action(self, action_string: str, elements: list) -> ExecutionResult:
        """
        Execute an action chosen by the AI
        
        Args:
            action_string: Action in format "action_type_element_id_value"
            elements: List of detected web elements
            
        Returns:
            ExecutionResult with outcome details
        """
        start_time = time.time()
        
        # Parse the action string
        action_parts = action_string.split('_', 2)
        if len(action_parts) < 2:
            return self._create_result(
                ActionResult.FAILED,
                f"Invalid action format: {action_string}",
                -0.5, False, "", "invalid", start_time
            )
        
        action_type = action_parts[0]
        element_id = action_parts[1]
        value = action_parts[2] if len(action_parts) > 2 else ""
        
        if self.debug:
            print(f"\n🎯 Executing: {action_type.upper()} on '{element_id}' with value '{value}'")
        
        # Find the target element
        target_element = self._find_element_by_id(element_id, elements)
        if not target_element:
            return self._create_result(
                ActionResult.ELEMENT_NOT_FOUND,
                f"Element '{element_id}' not found",
                -0.2, False, element_id, action_type, start_time
            )
        
        # Execute the specific action
        try:
            if action_type == "click":
                result = self._execute_click(target_element, element_id)
            elif action_type == "type":
                result = self._execute_type(target_element, element_id, value)
            elif action_type == "select":
                result = self._execute_select(target_element, element_id, value)
            elif action_type == "check":
                result = self._execute_check(target_element, element_id, True)
            elif action_type == "uncheck":
                result = self._execute_check(target_element, element_id, False)
            elif action_type == "clear":
                result = self._execute_clear(target_element, element_id)
            else:
                result = self._create_result(
                    ActionResult.FAILED,
                    f"Unknown action type: {action_type}",
                    -0.3, False, element_id, action_type, start_time
                )
            
            # Track success/failure
            if result.result == ActionResult.SUCCESS:
                self.successful_actions += 1
            else:
                self.failed_actions += 1
            
            # Add to history
            self.action_history.append({
                'action': action_string,
                'result': result.result.value,
                'reward': result.reward,
                'timestamp': time.time()
            })
            
            return result
            
        except Exception as e:
            if self.debug:
                print(f"❌ Unexpected error: {e}")
            
            return self._create_result(
                ActionResult.FAILED,
                f"Unexpected error: {str(e)}",
                -0.5, False, element_id, action_type, start_time
            )
    
    def _find_element_by_id(self, element_id: str, elements: list):
        """Find an element in the detected elements list"""
        for elem in elements:
            if elem.id == element_id:
                return elem
        return None
    
    def _find_selenium_element(self, web_element):
        """Find the actual Selenium element on the page"""
        try:
            # Try by ID first
            if web_element.id and web_element.id != "elem_":
                return self.driver.find_element(By.ID, web_element.id)
            
            # Try by CSS selector
            if web_element.css_selector:
                return self.driver.find_element(By.CSS_SELECTOR, web_element.css_selector)
            
            # Try by XPath
            if web_element.xpath:
                return self.driver.find_element(By.XPATH, web_element.xpath)
            
            return None
            
        except NoSuchElementException:
            return None
    
    def _execute_click(self, web_element, element_id: str) -> ExecutionResult:
        """Execute a click action"""
        try:
            selenium_element = self._find_selenium_element(web_element)
            if not selenium_element:
                return self._create_result(
                    ActionResult.ELEMENT_NOT_FOUND,
                    f"Could not locate element '{element_id}' on page",
                    -0.2, False, element_id, "click", time.time()
                )
            
            # Check if element is clickable
            if not selenium_element.is_enabled():
                return self._create_result(
                    ActionResult.ELEMENT_NOT_INTERACTABLE,
                    f"Element '{element_id}' is not clickable",
                    -0.1, False, element_id, "click", time.time()
                )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", selenium_element)
            time.sleep(0.2)
            
            # Perform the click
            selenium_element.click()
            time.sleep(0.5)  # Wait for any page changes
            
            if self.debug:
                print(f"✅ Successfully clicked '{element_id}'")
            
            # Calculate reward based on element type
            reward = self._calculate_click_reward(web_element)
            
            return self._create_result(
                ActionResult.SUCCESS,
                f"Clicked '{element_id}' successfully",
                reward, True, element_id, "click", time.time()
            )
            
        except ElementClickInterceptedException:
            return self._create_result(
                ActionResult.ELEMENT_NOT_INTERACTABLE,
                f"Click on '{element_id}' was intercepted",
                -0.1, False, element_id, "click", time.time()
            )
        except Exception as e:
            return self._create_result(
                ActionResult.FAILED,
                f"Click failed: {str(e)}",
                -0.2, False, element_id, "click", time.time()
            )
    
    def _execute_type(self, web_element, element_id: str, value: str) -> ExecutionResult:
        """Execute a text input action"""
        try:
            selenium_element = self._find_selenium_element(web_element)
            if not selenium_element:
                return self._create_result(
                    ActionResult.ELEMENT_NOT_FOUND,
                    f"Could not locate input '{element_id}'",
                    -0.2, False, element_id, "type", time.time()
                )
            
            # Check if already filled
            current_value = selenium_element.get_attribute('value') or ""
            if current_value.strip() and current_value.strip() == value.replace('_', ' '):
                return self._create_result(
                    ActionResult.ALREADY_COMPLETED,
                    f"Field '{element_id}' already contains this value",
                    0.0, False, element_id, "type", time.time()
                )
            
            # Clear and type new value
            selenium_element.clear()
            
            # Convert underscore-separated value to readable text
            readable_value = self._get_appropriate_value(web_element, value)
            
            selenium_element.send_keys(readable_value)
            time.sleep(0.3)
            
            if self.debug:
                print(f"✅ Successfully typed '{readable_value}' into '{element_id}'")
            
            # High reward for filling required fields
            reward = 2.0 if web_element.is_required else 1.0
            
            return self._create_result(
                ActionResult.SUCCESS,
                f"Typed '{readable_value}' into '{element_id}'",
                reward, True, element_id, "type", time.time()
            )
            
        except Exception as e:
            return self._create_result(
                ActionResult.FAILED,
                f"Type action failed: {str(e)}",
                -0.2, False, element_id, "type", time.time()
            )
    
    def _execute_select(self, web_element, element_id: str, value: str) -> ExecutionResult:
        """Execute a dropdown selection action"""
        try:
            selenium_element = self._find_selenium_element(web_element)
            if not selenium_element:
                return self._create_result(
                    ActionResult.ELEMENT_NOT_FOUND,
                    f"Could not locate dropdown '{element_id}'",
                    -0.2, False, element_id, "select", time.time()
                )
            
            # Create Select object
            select = Select(selenium_element)
            
            # Get available options
            options = [option.get_attribute('value') for option in select.options if option.get_attribute('value')]
            
            if not options:
                return self._create_result(
                    ActionResult.FAILED,
                    f"No selectable options found in '{element_id}'",
                    -0.1, False, element_id, "select", time.time()
                )
            
            # Choose a random option if no specific value provided
            if not value or value not in options:
                selected_value = random.choice(options)
            else:
                selected_value = value
            
            # Perform selection
            select.select_by_value(selected_value)
            time.sleep(0.3)
            
            if self.debug:
                print(f"✅ Successfully selected '{selected_value}' in '{element_id}'")
            
            return self._create_result(
                ActionResult.SUCCESS,
                f"Selected '{selected_value}' in dropdown '{element_id}'",
                1.5, True, element_id, "select", time.time()
            )
            
        except Exception as e:
            return self._create_result(
                ActionResult.FAILED,
                f"Select action failed: {str(e)}",
                -0.2, False, element_id, "select", time.time()
            )
    
    def _execute_check(self, web_element, element_id: str, should_check: bool) -> ExecutionResult:
        """Execute a checkbox check/uncheck action"""
        try:
            selenium_element = self._find_selenium_element(web_element)
            if not selenium_element:
                return self._create_result(
                    ActionResult.ELEMENT_NOT_FOUND,
                    f"Could not locate checkbox '{element_id}'",
                    -0.2, False, element_id, "check", time.time()
                )
            
            current_state = selenium_element.is_selected()
            
            # Check if action is needed
            if current_state == should_check:
                action_word = "checked" if should_check else "unchecked"
                return self._create_result(
                    ActionResult.ALREADY_COMPLETED,
                    f"Checkbox '{element_id}' is already {action_word}",
                    0.0, False, element_id, "check", time.time()
                )
            
            # Perform the action
            selenium_element.click()
            time.sleep(0.3)
            
            action_word = "checked" if should_check else "unchecked"
            if self.debug:
                print(f"✅ Successfully {action_word} '{element_id}'")
            
            # High reward for checking required checkboxes
            reward = 2.0 if web_element.is_required and should_check else 1.0
            
            return self._create_result(
                ActionResult.SUCCESS,
                f"Successfully {action_word} '{element_id}'",
                reward, True, element_id, "check", time.time()
            )
            
        except Exception as e:
            return self._create_result(
                ActionResult.FAILED,
                f"Checkbox action failed: {str(e)}",
                -0.2, False, element_id, "check", time.time()
            )
    
    def _execute_clear(self, web_element, element_id: str) -> ExecutionResult:
        """Execute a clear action"""
        try:
            selenium_element = self._find_selenium_element(web_element)
            if not selenium_element:
                return self._create_result(
                    ActionResult.ELEMENT_NOT_FOUND,
                    f"Could not locate element '{element_id}'",
                    -0.2, False, element_id, "clear", time.time()
                )
            
            # Check if already empty
            current_value = selenium_element.get_attribute('value') or ""
            if not current_value.strip():
                return self._create_result(
                    ActionResult.ALREADY_COMPLETED,
                    f"Field '{element_id}' is already empty",
                    0.0, False, element_id, "clear", time.time()
                )
            
            # Clear the field
            selenium_element.clear()
            time.sleep(0.2)
            
            if self.debug:
                print(f"✅ Successfully cleared '{element_id}'")
            
            return self._create_result(
                ActionResult.SUCCESS,
                f"Cleared field '{element_id}'",
                0.5, True, element_id, "clear", time.time()
            )
            
        except Exception as e:
            return self._create_result(
                ActionResult.FAILED,
                f"Clear action failed: {str(e)}",
                -0.2, False, element_id, "clear", time.time()
            )
    
    def _get_appropriate_value(self, web_element, suggested_value: str) -> str:
        """Get appropriate value for an element based on its type"""
        element_type = web_element.element_type.value
        element_id = web_element.id.lower()
        
        # Use suggested value if it looks reasonable
        if suggested_value and '_' in suggested_value:
            clean_value = suggested_value.replace('_', ' ')
            if len(clean_value) > 2:
                return clean_value
        
        # Generate appropriate value based on element type
        if element_type == "email_input":
            return random.choice(self.sample_data['emails'])
        elif "name" in element_id:
            return random.choice(self.sample_data['names'])
        elif element_type == "textarea":
            return random.choice(self.sample_data['descriptions'])
        else:
            return suggested_value.replace('_', ' ') if suggested_value else "Sample Text"
    
    def _calculate_click_reward(self, web_element) -> float:
        """Calculate reward for clicking an element"""
        element_type = web_element.element_type.value
        
        if element_type == "submit_button":
            return 0.5  # Medium reward for attempting submission
        elif element_type == "button":
            return 0.3  # Small reward for clicking buttons
        else:
            return 0.1  # Tiny reward for other clicks
    
    def _create_result(self, result: ActionResult, message: str, reward: float, 
                      state_changed: bool, element_id: str, action_type: str, 
                      start_time: float) -> ExecutionResult:
        """Create an ExecutionResult object"""
        execution_time = time.time() - start_time
        
        if self.debug:
            status_emoji = "✅" if result == ActionResult.SUCCESS else "❌"
            print(f"   {status_emoji} {message} (reward: {reward:+.1f})")
        
        return ExecutionResult(
            result=result,
            message=message,
            reward=reward,
            state_changed=state_changed,
            element_id=element_id,
            action_type=action_type,
            execution_time=execution_time
        )
    
    def calculate_progress_reward(self, previous_progress: float, current_progress: float, 
                                success_achieved: bool) -> float:
        """
        Calculate reward based on form completion progress
        This is the key reward signal that guides learning!
        """
        if success_achieved:
            return 10.0  # HUGE reward for completing the goal!
        
        progress_improvement = current_progress - previous_progress
        
        if progress_improvement > 0:
            # Reward proportional to progress made
            return progress_improvement / 10.0  # 10% progress = 1.0 reward
        elif progress_improvement < 0:
            # Small penalty for moving backwards
            return -0.2
        else:
            # No progress change
            return 0.0
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about executed actions"""
        total_actions = self.successful_actions + self.failed_actions
        
        if total_actions == 0:
            return {"message": "No actions executed yet"}
        
        return {
            "total_actions": total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "success_rate": (self.successful_actions / total_actions) * 100,
            "recent_actions": self.action_history[-5:] if self.action_history else []
        }

# Demo function to test the Web Action Executor
def demo_web_executor():
    """
    Demo: Watch the AI's hands in action!
    """
    print("🤲 Web Action Executor Demo")
    print("="*50)
    
    # This demo would need a WebDriver instance and detected elements
    # For now, we'll just show the concept
    print("✅ Web Action Executor is ready!")
    print("   Can execute: click, type, select, check, uncheck, clear")
    print("   Provides: detailed feedback, rewards, error handling")
    print("   Ready to connect with Q-Learning Agent!")

if __name__ == "__main__":
    demo_web_executor()