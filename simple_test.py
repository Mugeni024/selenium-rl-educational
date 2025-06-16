import sys
import os

# Check if our files exist
print("Checking files...")
files_to_check = [
    'src/environment/element_detector.py',
    'src/agents/q_learning_agent.py',
    'src/environment/web_action_executor.py'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"✅ {file} exists")
    else:
        print(f"❌ {file} missing")

# Test imports
sys.path.append('src')
try:
    from environment.element_detector import ElementDetector
    print("✅ ElementDetector import works")
except ImportError as e:
    print(f"❌ ElementDetector import failed: {e}")

try:
    from agents.q_learning_agent import QLearningAgent
    print("✅ QLearningAgent import works")
except ImportError as e:
    print(f"❌ QLearningAgent import failed: {e}")
