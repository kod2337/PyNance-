#!/usr/bin/env python3
"""
Test script to check available Gemini models and test basic functionality
"""

import os
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, skipping .env loading")

# Initialize colorama
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent.parent  # Go up one level since we're in tests/
sys.path.insert(0, str(project_root))

from services.ai_service import get_ai_service


def test_api_key():
    """Test if API key is loaded"""
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        if api_key == "your_gemini_api_key_here" or api_key == "your_actual_gemini_api_key_here":
            print(f"{Fore.RED}❌ Please set your actual GEMINI_API_KEY")
            return False
        else:
            print(f"{Fore.GREEN}✅ GEMINI_API_KEY is set (length: {len(api_key)})")
            return True
    else:
        print(f"{Fore.RED}❌ GEMINI_API_KEY not found")
        return False


def test_model_availability():
    """Test available models"""
    print(f"\n{Fore.CYAN}🔍 Testing Gemini Model Availability{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    # List available models
    models = ai_service.list_available_models()
    
    if models:
        print(f"\n{Fore.GREEN}✅ Found {len(models)} available models")
    else:
        print(f"\n{Fore.RED}❌ No models found or API error")
    
    return len(models) > 0


def test_ai_initialization():
    """Test AI service initialization"""
    print(f"\n{Fore.CYAN}🤖 Testing AI Service Initialization{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    if ai_service.is_available():
        print(f"{Fore.GREEN}✅ AI service initialized successfully!")
        return True
    else:
        print(f"{Fore.RED}❌ AI service failed to initialize")
        return False


def test_basic_ai_functionality():
    """Test basic AI functionality"""
    print(f"\n{Fore.CYAN}🧪 Testing Basic AI Functionality{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 35}{Style.RESET_ALL}")
    
    ai_service = get_ai_service()
    
    if not ai_service.is_available():
        print(f"{Fore.RED}❌ AI service not available for testing")
        return False
    
    try:
        # Test categorization
        print("Testing transaction categorization...")
        category = ai_service.categorize_transaction("Coffee at Starbucks", 4.50)
        print(f"   Result: {category}")
        
        # Test natural language parsing
        print("Testing natural language parsing...")
        parsed = ai_service.parse_natural_language_transaction("I spent $5 on coffee")
        print(f"   Result: {parsed.get('description', 'N/A')} - ${abs(float(parsed.get('amount', 0))):.2f}")
        
        print(f"{Fore.GREEN}✅ Basic AI functionality working!")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ AI functionality test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print(f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     {Fore.YELLOW}🧪 GEMINI AI MODEL TESTER 🤖{Fore.CYAN}                    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")
    
    # Test API key
    api_key_ok = test_api_key()
    
    if not api_key_ok:
        print(f"\n{Fore.YELLOW}💡 To set up your API key:{Style.RESET_ALL}")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Create .env file: echo 'GEMINI_API_KEY=your_key_here' > .env")
        print("3. Or set environment variable: $env:GEMINI_API_KEY='your_key_here'")
        return
    
    # Test model availability
    models_ok = test_model_availability()
    
    # Test AI initialization
    init_ok = test_ai_initialization()
    
    # Test basic functionality
    if init_ok:
        test_basic_ai_functionality()
    
    print(f"\n{Fore.CYAN}{'═' * 55}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"API Key: {'✅' if api_key_ok else '❌'}")
    print(f"Models Available: {'✅' if models_ok else '❌'}")
    print(f"AI Initialization: {'✅' if init_ok else '❌'}")
    
    if api_key_ok and models_ok and init_ok:
        print(f"\n{Fore.GREEN}🎉 All tests passed! AI features are ready to use.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Run: python main.py{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check the setup above.{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 