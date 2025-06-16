"""
Element Detector - The AI's Web Scanner
=====================================

This class teaches the AI to "see" webpages by:
1. Finding all interactive elements
2. Understanding what each element does
3. Creating possible actions
4. Building a "map" of the webpage

Think of it as giving the AI digital eyes!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class ElementType(Enum):
    """Types of elements the AI can interact with"""
    TEXT_INPUT = "text_input"
    EMAIL_INPUT = "email_input"
    PASSWORD_INPUT = "password_input"
    TEXTAREA = "textarea"
    SELECT_DROPDOWN = "select"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio"
    BUTTON = "button"
    SUBMIT_BUTTON = "submit"
    LINK = "link"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Actions the AI can perform"""
    CLICK = "click"
    TYPE_TEXT = "type_text"
    SELECT_OPTION = "select_option"
    CHECK = "check"
    UNCHECK = "uncheck"
    CLEAR = "clear"
    SUBMIT = "submit"

@dataclass
class WebElement:
    """Represents a web element the AI can interact with"""
    id: str
    element_type: ElementType
    tag_name: str
    text: str
    placeholder: str
    value: str
    is_required: bool
    is_visible: bool
    is_enabled: bool
    xpath: str
    css_selector: str
    possible_actions: List[ActionType]
    coordinates: tuple  # (x, y) position
    size: tuple  # (width, height)
    
    def __str__(self):
        return f"{self.element_type.value}[{self.id or 'no-id'}]: '{self.text or self.placeholder}'"

class ElementDetector:
    """
    The AI's Web Scanner - Finds and analyzes all interactive elements
    """
    
    def __init__(self, headless: bool = False, debug: bool = True):
        """Initialize the web scanner"""
        self.debug = debug
        self.driver = None
        self.headless = headless
        self.detected_elements = []
        
        # Sample text data for form filling
        self.sample_data = {
            'names': ['John Doe', 'Jane Smith', 'Alex Johnson', 'Chris Lee'],
            'emails': ['test@example.com', 'user@demo.com', 'sample@test.org'],
            'descriptions': [
                'I am interested in learning about AI and machine learning.',
                'Looking forward to exploring new technologies.',
                'Excited to be part of this training program.',
                'AI enthusiast with a passion for automation.'
            ]
        }
    
    def start_browser(self) -> bool:
        """Start the web browser"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            if self.debug:
                print("✅ Browser started successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            return False
    
    def load_page(self, url: str) -> bool:
        """Load a webpage"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            if self.debug:
                print(f"✅ Page loaded: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            return False
    
    def detect_elements(self) -> List[WebElement]:
        """
        Scan the page and find all interactive elements
        This is where the AI 'sees' the webpage!
        """
        if not self.driver:
            print("❌ No browser session active!")
            return []
        
        print("\n🔍 AI is scanning the webpage...")
        self.detected_elements = []
        
        # Find all potentially interactive elements
        selectors = [
            "input",
            "button", 
            "select",
            "textarea",
            "a[href]",
            "[onclick]",
            "[role='button']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    web_element = self._analyze_element(elem)
                    if web_element and web_element.is_visible:
                        self.detected_elements.append(web_element)
            except Exception as e:
                if self.debug:
                    print(f"⚠️  Error scanning {selector}: {e}")
        
        # Sort by position (top to bottom, left to right)
        self.detected_elements.sort(key=lambda x: (x.coordinates[1], x.coordinates[0]))
        
        if self.debug:
            print(f"🎯 Found {len(self.detected_elements)} interactive elements!")
            self._print_element_summary()
        
        return self.detected_elements
    
    def _analyze_element(self, elem) -> Optional[WebElement]:
        """Analyze a single element and extract its properties"""
        try:
            # Get basic properties
            tag_name = elem.tag_name.lower()
            element_id = elem.get_attribute('id') or f"elem_{hash(elem)}"
            text = elem.text.strip()
            placeholder = elem.get_attribute('placeholder') or ""
            value = elem.get_attribute('value') or ""
            is_required = elem.get_attribute('required') is not None
            
            # Check visibility and interaction ability
            is_visible = elem.is_displayed() and elem.size['width'] > 0
            is_enabled = elem.is_enabled()
            
            if not is_visible:
                return None
            
            # Get position and size
            location = elem.location
            size = elem.size
            coordinates = (location['x'], location['y'])
            element_size = (size['width'], size['height'])
            
            # Generate selectors
            xpath = self._generate_xpath(elem)
            css_selector = self._generate_css_selector(elem)
            
            # Determine element type and possible actions
            element_type = self._classify_element(elem, tag_name)
            possible_actions = self._determine_actions(element_type, elem)
            
            return WebElement(
                id=element_id,
                element_type=element_type,
                tag_name=tag_name,
                text=text,
                placeholder=placeholder,
                value=value,
                is_required=is_required,
                is_visible=is_visible,
                is_enabled=is_enabled,
                xpath=xpath,
                css_selector=css_selector,
                possible_actions=possible_actions,
                coordinates=coordinates,
                size=element_size
            )
            
        except Exception as e:
            if self.debug:
                print(f"⚠️  Error analyzing element: {e}")
            return None
    
    def _classify_element(self, elem, tag_name: str) -> ElementType:
        """Determine what type of element this is"""
        if tag_name == "input":
            input_type = elem.get_attribute('type') or 'text'
            
            if input_type == 'email':
                return ElementType.EMAIL_INPUT
            elif input_type == 'password':
                return ElementType.PASSWORD_INPUT
            elif input_type == 'checkbox':
                return ElementType.CHECKBOX
            elif input_type == 'radio':
                return ElementType.RADIO_BUTTON
            elif input_type == 'submit':
                return ElementType.SUBMIT_BUTTON
            else:
                return ElementType.TEXT_INPUT
                
        elif tag_name == "textarea":
            return ElementType.TEXTAREA
        elif tag_name == "select":
            return ElementType.SELECT_DROPDOWN
        elif tag_name == "button":
            button_type = elem.get_attribute('type')
            if button_type == 'submit':
                return ElementType.SUBMIT_BUTTON
            return ElementType.BUTTON
        elif tag_name == "a":
            return ElementType.LINK
        else:
            return ElementType.UNKNOWN
    
    def _determine_actions(self, element_type: ElementType, elem) -> List[ActionType]:
        """Determine what actions the AI can perform on this element"""
        actions = []
        
        if element_type in [ElementType.TEXT_INPUT, ElementType.EMAIL_INPUT, 
                           ElementType.PASSWORD_INPUT, ElementType.TEXTAREA]:
            actions.extend([ActionType.CLICK, ActionType.TYPE_TEXT, ActionType.CLEAR])
            
        elif element_type == ElementType.SELECT_DROPDOWN:
            actions.extend([ActionType.CLICK, ActionType.SELECT_OPTION])
            
        elif element_type == ElementType.CHECKBOX:
            actions.extend([ActionType.CHECK, ActionType.UNCHECK])
            
        elif element_type in [ElementType.BUTTON, ElementType.SUBMIT_BUTTON, ElementType.LINK]:
            actions.append(ActionType.CLICK)
            if element_type == ElementType.SUBMIT_BUTTON:
                actions.append(ActionType.SUBMIT)
        
        return actions
    
    def _generate_xpath(self, elem) -> str:
        """Generate XPath for the element"""
        try:
            return self.driver.execute_script(
                "function getXPath(element) {"
                "  if (element.id !== '') {"
                "    return '//*[@id=\"' + element.id + '\"]';"
                "  }"
                "  if (element === document.body) {"
                "    return '/html/body';"
                "  }"
                "  var ix = 0;"
                "  var siblings = element.parentNode.childNodes;"
                "  for (var i = 0; i < siblings.length; i++) {"
                "    var sibling = siblings[i];"
                "    if (sibling === element) {"
                "      return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';"
                "    }"
                "    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {"
                "      ix++;"
                "    }"
                "  }"
                "}"
                "return getXPath(arguments[0]);", elem)
        except:
            return f"//{elem.tag_name}[{hash(elem)}]"
    
    def _generate_css_selector(self, elem) -> str:
        """Generate CSS selector for the element"""
        try:
            element_id = elem.get_attribute('id')
            if element_id:
                return f"#{element_id}"
            
            class_name = elem.get_attribute('class')
            if class_name:
                classes = '.'.join(class_name.split())
                return f"{elem.tag_name}.{classes}"
            
            return elem.tag_name
        except:
            return elem.tag_name
    
    def _print_element_summary(self):
        """Print a summary of detected elements"""
        print("\n" + "="*60)
        print("🤖 AI VISION: What the AI sees on this webpage")
        print("="*60)
        
        for i, elem in enumerate(self.detected_elements, 1):
            status = "✅" if elem.is_enabled else "❌"
            required = "⚠️  REQUIRED" if elem.is_required else ""
            
            print(f"{i:2d}. {status} {elem.element_type.value.upper():15} | {elem.id[:20]:20} | {required}")
            print(f"     Text: '{elem.text[:40]}'" if elem.text else f"     Placeholder: '{elem.placeholder[:40]}'")
            print(f"     Actions: {[a.value for a in elem.possible_actions]}")
            print(f"     Position: {elem.coordinates}, Size: {elem.size}")
            print()
    
    def get_sample_data_for_element(self, element: WebElement) -> str:
        """Get appropriate sample data for an element"""
        elem_type = element.element_type
        
        if elem_type == ElementType.EMAIL_INPUT:
            return self.sample_data['emails'][0]
        elif elem_type in [ElementType.TEXT_INPUT] and 'name' in element.id.lower():
            return self.sample_data['names'][0]
        elif elem_type == ElementType.TEXTAREA:
            return self.sample_data['descriptions'][0]
        else:
            return "Sample text"
    
    def get_form_completion_state(self) -> Dict[str, Any]:
        """Check how much of the form is completed - this will be our reward signal!"""
        try:
            # Check if success panel is visible (our ultimate goal!)
            success_panel = self.driver.find_element(By.ID, "successPanel")
            if success_panel.is_displayed():
                return {
                    'completed': True,
                    'progress': 100,
                    'success': True,
                    'message': '🎉 GOAL ACHIEVED! Success panel is visible!'
                }
            
            # Get progress from the webpage
            progress_js = """
                return window.checkFormState ? window.checkFormState() : null;
            """
            form_state = self.driver.execute_script(progress_js)
            
            if form_state:
                return {
                    'completed': form_state.get('isComplete', False),
                    'progress': form_state.get('progress', 0),
                    'success': False,
                    'values': form_state.get('values', {}),
                    'message': f"Form {form_state.get('progress', 0):.0f}% complete"
                }
            
            return {'completed': False, 'progress': 0, 'success': False, 'message': 'No progress detected'}
            
        except Exception as e:
            return {'completed': False, 'progress': 0, 'success': False, 'message': f'Error: {e}'}
    
    def close(self):
        """Clean up and close the browser"""
        if self.driver:
            self.driver.quit()
            if self.debug:
                print("🔒 Browser closed.")

# Demo function to test the Element Detector
def demo_element_detection():
    """
    Demo: See how the AI scans your webpage!
    """
    print("🚀 Starting Element Detector Demo...")
    
    detector = ElementDetector(debug=True)
    
    # Start browser and load our demo form
    if not detector.start_browser():
        return
    
    # Load the HTML file (adjust path as needed)
    import os
    html_path = os.path.abspath("demo/test_form.html")
    file_url = f"file://{html_path}"
    
    if not detector.load_page(file_url):
        detector.close()
        return
    
    # Let the AI scan the page
    elements = detector.detect_elements()
    
    # Show current form state
    print("\n📊 Current Form State:")
    state = detector.get_form_completion_state()
    print(f"   {state['message']}")
    
    # Keep browser open for 10 seconds so you can see it
    print("\n⏰ Browser will stay open for 10 seconds so you can see the page...")
    time.sleep(10)
    
    detector.close()
    print("✅ Demo completed!")

if __name__ == "__main__":
    demo_element_detection()