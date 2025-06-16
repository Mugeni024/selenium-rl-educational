#!/usr/bin/env python3
"""
Form Analysis Tool - Let's see what your AI is missing!
This will help us understand why it's stuck at 33.3% completion
"""

import os
import sys
sys.path.append('src')

def manual_form_check():
    """
    Quick manual check of what's in the demo form
    """
    print("🔍 MANUAL FORM CHECK:")
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
            
            # Look for specific patterns
            if 'name' in content:
                print("   ✅ Name field detected")
            if 'email' in content:
                print("   ✅ Email field detected")
            if 'submit' in content.lower():
                print("   ✅ Submit button detected")
            
            # Calculate 33.3% completion meaning
            total_elements = input_count + select_count + button_count
            completion_33 = total_elements * 0.333
            print(f"\n🔍 33.3% COMPLETION ANALYSIS:")
            print(f"   33.3% of {total_elements} elements = {completion_33:.1f} elements")
            print(f"   Your AI is completing ~{int(completion_33)} out of {total_elements} elements")
            
            return total_elements, required_count
        except Exception as e:
            print(f"❌ Could not read form file: {e}")
            return 0, 0
    else:
        print(f"❌ Form file not found: {html_path}")
        print("💡 Make sure you have demo/test_form.html in your project")
        return 0, 0

def create_targeted_trainer():
    """
    Create a targeted training script based on analysis
    """
    print("\n🎯 CREATING TARGETED TRAINING SCRIPT...")
    
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
        max_episodes=35,              # More episodes
        max_steps_per_episode=50,     # Significantly more steps
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
    print("   ✅ More steps per episode (50 vs 25)")
    print("   ✅ More episodes for pattern learning (35)")
    print("   ✅ Existing Q-table knowledge preserved")
    print("   ✅ Focus on breaking the 33.3% barrier")
    
    trainer.start_training()

if __name__ == "__main__":
    targeted_training()
'''
    
    with open("targeted_training.py", "w") as f:
        f.write(targeted_script)
    
    print("✅ Created: targeted_training.py")
    print("🚀 Run with: python3 targeted_training.py")

def suggest_improvements(total_elements, required_count):
    """
    Suggest specific improvements based on form analysis
    """
    print("\n💡 IMPROVEMENT SUGGESTIONS:")
    print("=" * 40)
    
    completion_33 = int(total_elements * 0.333)
    
    print(f"🎯 ANALYSIS RESULTS:")
    print(f"   Total form elements: {total_elements}")
    print(f"   Required fields: {required_count}")
    print(f"   33.3% completion = {completion_33} elements")
    print(f"   Missing: {total_elements - completion_33} elements")
    
    print(f"\n🔧 SPECIFIC FIXES:")
    print("1. 🎯 Increase Steps Per Episode")
    print("   - Current: 25 steps")
    print("   - Recommended: 50+ steps")
    print("   - Reason: AI needs more actions to complete all fields")
    
    print("2. 📝 Focus on Sequential Completion")
    print("   - AI is completing exactly 1/3 of fields")
    print("   - Needs to learn the full sequence")
    print("   - More episodes will help find the pattern")
    
    print("3. 🚀 Breakthrough Strategy")
    print("   - 54.97 reward shows AI is learning")
    print("   - 96.6% action success is excellent")
    print("   - Just needs more time to find complete solution")
    
    print("4. 🔄 Patient Training")
    print("   - Your AI is SO CLOSE to success!")
    print("   - The consistent 33.3% shows it found a pattern")
    print("   - More episodes + steps should break through")

def main():
    print("🤖 SELENIUM RL FORM ANALYZER")
    print("=" * 40)
    print("Let's figure out why your AI is stuck at 33.3%!")
    
    # Manual form analysis
    total_elements, required_count = manual_form_check()
    
    if total_elements > 0:
        # Suggest improvements
        suggest_improvements(total_elements, required_count)
        
        # Create targeted training script
        create_targeted_trainer()
        
        print("\n🎉 ANALYSIS COMPLETE!")
        print("=" * 30)
        print("✅ Form structure analyzed")
        print("✅ Requirements identified") 
        print("✅ Targeted training script created")
        print("✅ Ready for breakthrough training!")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python3 targeted_training.py")
        print("2. Monitor for >33.3% completion")
        print("3. Look for first successful episode!")
        print("4. Your AI remembers all previous learning!")
        
        print("\n📊 PREDICTION:")
        print("With 50 steps per episode, your AI should")
        print("break through the 33.3% barrier and achieve")
        print("its first successful form completion! 🎯")
        
    else:
        print("\n❌ Could not analyze form file")
        print("But creating training script anyway...")
        create_targeted_trainer()

if __name__ == "__main__":
    main()
