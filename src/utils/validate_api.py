#!/usr/bin/env python3
"""
Validate API key and test direct Gemini API call
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

def main():
    load_dotenv()
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    print("API Key Information:")
    print(f"  GEMINI_API_KEY: {gemini_key[:20]}...{gemini_key[-5:] if gemini_key else None}")
    print(f"  GOOGLE_API_KEY: {google_key[:20]}...{google_key[-5:] if google_key else None}")
    print(f"  Keys are same: {gemini_key == google_key}")
    print()
    
    # Test API key format
    if gemini_key:
        print(f"Key length: {len(gemini_key)}")
        print(f"Starts with AIza: {gemini_key.startswith('AIza')}")
        print()
    
    # Try direct API call with explicit configuration
    for key_name, key_value in [("GEMINI_API_KEY", gemini_key), ("GOOGLE_API_KEY", google_key)]:
        if key_value:
            print(f"Testing with {key_name}...")
            try:
                # Configure with explicit key
                genai.configure(api_key=key_value)
                
                # Create model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Test generation
                response = model.generate_content("Say hello")
                print(f"✅ Success with {key_name}: {response.text[:50]}...")
                break
                
            except Exception as e:
                print(f"❌ Failed with {key_name}: {e}")
                print()
    
    # Test with environment variable detection
    print("Testing environment variable detection...")
    try:
        # Don't configure, let it auto-detect
        genai.configure()
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        print(f"✅ Auto-detection success: {response.text[:50]}...")
    except Exception as e:
        print(f"❌ Auto-detection failed: {e}")

if __name__ == "__main__":
    main()
