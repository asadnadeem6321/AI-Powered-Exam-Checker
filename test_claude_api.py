#!/usr/bin/env python3
"""Test Claude API and find working model"""
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('CLAUDE_API_KEY')

print(f"API Key: {api_key[:20]}...")
print(f"Testing Claude API...")

try:
    client = anthropic.Anthropic(api_key=api_key)
    
    # First try the configured model
    print("\n1. Trying configured model: claude-3-5-sonnet-20241022")
    try:
        message = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=100,
            messages=[
                {'role': 'user', 'content': 'Say hello'}
            ]
        )
        print("✅ SUCCESS!")
    except anthropic.NotFoundError:
        print("❌ Model not found")
    
    # Try alternative models
    print("\n2. Trying alternative models:")
    models_to_try = [
        'claude-3-5-sonnet-20241022',
        'claude-opus-4-1-20250805',
        'claude-3-sonnet-20240229',
        'claude-3-opus-20240229',
        'claude-3-haiku-20240307',
    ]
    
    for model in models_to_try:
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{'role': 'user', 'content': 'Hi'}]
            )
            print(f"   ✅ {model} - WORKS!")
            break
        except anthropic.NotFoundError:
            print(f"   ❌ {model} - not available")
        except Exception as e:
            print(f"   ❌ {model} - error: {type(e).__name__}")
            
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
