"""
Debug Anthropic import
"""
import sys

print("Python version:", sys.version)
print("\nTrying to import anthropic...")

try:
    import anthropic
    print(f"✅ Anthropic version: {anthropic.__version__}")
    
    print("\nTrying to create client...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"API key found: {bool(api_key)}")
    
    # Try different initialization methods
    print("\nMethod 1: Simple initialization")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Method 1 works")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    print("\nMethod 2: With explicit parameters")
    try:
        client = anthropic.Client(api_key=api_key)
        print("✅ Method 2 works")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()