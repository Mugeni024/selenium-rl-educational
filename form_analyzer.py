#!/usr/bin/env python3
"""
Form Analysis Tool - Let's see what your AI is missing!
This will help us understand why it's stuck at 33.3% completion
"""

import os
import sys
sys.path.append('src')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def analyze_form_requirements():
    """
    Analyze the test form to understand what's needed for 100% completion
    """
    print("🔍 FORM REQUIREMENTS ANALYZER")
    print("=" * 50)
    
    # Get the path to our demo HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    target_url = f"file://{html_path}"
    
    # Setup Chrome driver (try without webdriver-manager first)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Try to use Chrome directly (most common setup)
        try:
            driver = webdriver.Chrome(options=options)
        except:
            # Fallback: try with explicit path or service
            print("⚠️  Trying alternative Chrome setup...")
            service = Service()  # Let it auto-detect
            driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(target_url)
        
        print(f"✅ Opened form: {target_url}")
        print("\n📋 FORM ANALYSIS:")
        
        # Find all form elements
        form_elements = []
        
        # Text inputs
        text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
        for inp in text_inputs:
            name = inp.get_attribute('name') or inp.get_attribute('id') or 'unnamed'
            required = inp.get_attribute('required') is not None
            form_elements.append({
                'type': 'text_input',
                'name': name,
                'required': required,
                'element': inp
            })
        
        # Checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        for cb in checkboxes:
            name = cb.get_attribute('name') or cb.get_attribute('id') or 'unnamed'
            required = cb.get_attribute('required') is not None
            form_elements.append({
                'type': 'checkbox',
                'name': name,
                'required': required,
                'element': cb
            })
        
        # Radio buttons
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        radio_groups = {}
        for radio in radios:
            name = radio.get_attribute('name')
            if name not in radio_groups:
                required = radio.get_attribute('required') is not None
                radio_groups[name] = {
                    'type': 'radio_group',
                    'name': name,
                    'required': required,
                    'options': []
                }
            radio_groups[name]['options'].append(radio.get_attribute('value'))
        
        for group in radio_groups.values():
            form_elements.append(group)
        
        # Dropdowns
        selects = driver.find_elements(By.CSS_SELECTOR, "select")
        for select in selects:
            name = select.get_attribute('name') or select.get_attribute('id') or 'unnamed'
            required = select.get_attribute('required') is not None
            options = [opt.get_attribute('value') for opt in select.find_elements(By.TAG_NAME, "option")]
            form_elements.append({
                'type': 'select',
                'name': name,
                'required': required,
                'options': options,
                'element': select
            })
        
        # Submit button
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        for btn in submit_buttons:
            form_elements.append({
                'type': 'submit',
                'name': 'submit_button',
                'required': True,
                'element': btn
            })
        
        print(f"\n📊 TOTAL FORM ELEMENTS FOUND: {len(form_elements)}")
        print("\n📝 DETAILED BREAKDOWN:")
        
        required_count = 0
        for i, element in enumerate(form_elements, 1):
            status = "🔴 REQUIRED" if element['required'] else "⚪ OPTIONAL"
            print(f"   {i}. {element['type'].upper()}: '{element['name']}' - {status}")
            if element['required']:
                required_count += 1
        
        print(f"\n🎯 COMPLETION REQUIREMENTS:")
        print(f"   Required fields: {required_count}")
        print(f"   Total fields: {len(form_elements)}")
        print(f"   Success threshold: All required fields + submit")
        
        # Calculate what 33.3% means
        completion_33 = len(form_elements) * 0.333
        print(f"\n🔍 33.3% COMPLETION ANALYSIS:")
        print(f"   33.3% of {len(form_elements)} elements = {completion_33:.1f} elements")
        print(f"   Your AI is likely completing ~{int(completion_33)} elements")
        
        # Try to determine success condition
        print(f"\n🎯 SUCCESS CONDITION ANALYSIS:")
        try:
            success_elements = driver.find_elements(By.CSS_SELECTOR, ".success, #success, .alert-success")
            if success_elements:
                print("   ✅ Success indicator found on page")
                print("   🎯 Goal: Make success element visible/appear")
            else:
                print("   ❓ No obvious success indicator found")
                print("   🎯 Goal: Likely form submission completion")
        except:
            print("   ❓ Could not analyze success condition")
        
        # Check for any hidden elements or complex requirements
        print(f"\n🔧 ADVANCED ANALYSIS:")
        all_inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea, button")
        visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
        print(f"   Total input elements: {len(all_inputs)}")
        print(f"   Visible elements: {len(visible_inputs)}")
        print(f"   Hidden elements: {len(all_inputs) - len(visible_inputs)}")
        
        driver.quit()
        
        return {
            'total_elements': len(form_elements),
            'required_elements': required_count,
            'form_elements': form_elements
        }
        
    except Exception as e:
        print(f"❌ Error analyzing form: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure Chrome browser is installed")
        print("2. Install webdriver-manager: pip install webdriver-manager")
        print("3. Check that demo/test_form.html exists")
        if 'driver' in locals():
            driver.quit()
        return None

def suggest_improvements(analysis):
    """
    Suggest specific improvements based on form analysis
    """
    if not analysis:
        return
    
    print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
    print("=" * 40)
    
    total = analysis['total_elements']
    required = analysis['required_elements']
    
    print(f"🎯 GOAL: Complete {required} required fields + submit")
    print(f"📊 CURRENT: ~{int(total * 0.333)} elements (33.3%)")
    print(f"📈 NEEDED: {required + 1} elements for success")
    
    print(f"\n🔧 SPECIFIC FIXES:")
    print("1. 🎯 Focus on Required Fields Only")
    print("   - Increase rewards for required field completion")
    print("   - Reduce exploration of optional fields")
    
    print("2. 📝 Ensure All Required Fields Are Filled")
    print("   - Check if AI is missing specific field types")
    print("   - Verify field validation requirements")
    
    print("3. 🚀 Add Submit Action Priority")
    print("   - Higher reward for submit button after all required fields")
    print("   - Ensure submit button is being detected")
    
    print("4. 🔄 Increase Episode Length")
    print("   - Try 35-40 steps per episode")
    print("   - Give AI more chances to find the right sequence")

def create_targeted_trainer():
    """
    Create a targeted training script based on analysis
    """
    print(f"\n🎯 CREATING TARGETED TRAINING SCRIPT...")
    
    targeted_script = '''#!/usr/bin/env python3
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
    
    print("\\n🎯 TARGETED IMPROVEMENTS:")
    print("   ✅ More steps per episode (40 vs 25)")
    print("   ✅ More episodes for pattern learning (30)")
    print("   ✅ Existing Q-table knowledge preserved")
    print("   ✅ Focus on required field completion")
    
    trainer.start_training()

if __name__ == "__main__":
    targeted_training()
'''
    
    with open("targeted_training.py", "w") as f:
        f.write(targeted_script)
    
    print("✅ Created: targeted_training.py")
    print("🚀 Run with: python targeted_training.py")

def manual_form_check():
    """
    Quick manual check of what's in the demo form
    """
    print(f"\n🔍 MANUAL FORM CHECK:")
    print("=" * 30)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "demo", "test_form.html")
    
    if os.path.exists(html_path):
        print(f"✅ Found form file: {html_path}")
        try:
            with open(html_path, 'r') as f:
                content = f.read()
            
            # Count form elements manually
            input_count = content.count('<input')
            select_count = content.count('<select')
            button_count = content.count('<button')
            
            print(f"📊 Quick element count:")
            print(f"   Input elements: {input_count}")
            print(f"   Select elements: {select_count}")
            print(f"   Button elements: {button_count}")
            print(f"   Total: {input_count + select_count + button_count}")
            
            # Look for required fields
            required_count = content.count('required')
            print(f"   'required' attributes: {required_count}")
            
            return True
        except Exception as e:
            print(f"❌ Could not read form file: {e}")
            return False
    else:
        print(f"❌ Form file not found: {html_path}")
        print("💡 Make sure you have demo/test_form.html in your project")
        return False

def main():
    print("🤖 SELENIUM RL FORM ANALYZER")
    print("=" * 40)
    print("Let's figure out why your AI is stuck at 33.3%!")
    
    # First, try manual check
    if not manual_form_check():
        print("\n❌ Cannot proceed without the form file.")
        return
    
    # Try to analyze the form with Selenium
    print(f"\n" + "=" * 40)
    analysis = analyze_form_requirements()
    
    if analysis:
        # Suggest improvements
        suggest_improvements(analysis)
        
        # Create targeted training script
        create_targeted_trainer()
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print("=" * 30)
        print("✅ Form structure analyzed")
        print("✅ Requirements identified") 
        print("✅ Targeted training script created")
        print("✅ Ready for breakthrough training!")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Run: python targeted_training.py")
        print("2. Monitor for >33.3% completion")
        print("3. Look for first successful episode!")
        
    else:
        print("\n⚠️  Selenium analysis failed, but we can still help!")
        print("Creating targeted training script anyway...")
        create_targeted_trainer()
        
        print(f"\n💡 MANUAL DEBUGGING STEPS:")
        print("1. Install missing dependency: pip install webdriver-manager")
        print("2. Run: python targeted_training.py")
        print("3. Your AI's 33.3% suggests it needs more steps per episode")

if __name__ == "__main__":
    main()