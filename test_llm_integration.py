#!/usr/bin/env python3
"""
Test script for LLM integration with Recipe Genie bot
Supports both local LLM and OpenRouter
"""

import requests
import json
import os
from config import (
    LLM_PROVIDER, LLM_ENDPOINT, LLM_TIMEOUT, LLM_API_KEY, LLM_MODEL, 
    LLM_MAX_TOKENS, LLM_TEMPERATURE, OPENROUTER_API_KEY, OPENROUTER_ENDPOINT,
    OPENROUTER_MODEL, OPENROUTER_TIMEOUT, OPENROUTER_MAX_TOKENS, OPENROUTER_TEMPERATURE
)

def test_llm_connection():
    """Test the connection to your configured LLM provider."""
    print("🧪 Testing LLM Integration...")
    print(f"Provider: {LLM_PROVIDER}")
    print("-" * 50)
    
    if LLM_PROVIDER.lower() == "openrouter":
        print(f"OpenRouter Endpoint: {OPENROUTER_ENDPOINT}")
        print(f"OpenRouter Model: {OPENROUTER_MODEL}")
        print(f"OpenRouter API Key: {'Set' if OPENROUTER_API_KEY else 'Not set'}")
        print(f"OpenRouter Timeout: {OPENROUTER_TIMEOUT} seconds")
        print(f"OpenRouter Max Tokens: {OPENROUTER_MAX_TOKENS}")
        print(f"OpenRouter Temperature: {OPENROUTER_TEMPERATURE}")
    else:
        print(f"Local LLM Endpoint: {LLM_ENDPOINT}")
        print(f"Local LLM Model: {LLM_MODEL}")
        print(f"Local LLM API Key: {'Set' if LLM_API_KEY else 'Not set'}")
        print(f"Local LLM Timeout: {LLM_TIMEOUT} seconds")
        print(f"Local LLM Max Tokens: {LLM_MAX_TOKENS}")
        print(f"Local LLM Temperature: {LLM_TEMPERATURE}")
    print("-" * 50)
    
    # Test prompts
    test_prompts = [
        {
            "name": "Ingredient-based query",
            "prompt": "You are a friendly cooking assistant. Suggest a simple recipe or meal idea using these ingredients: tomato, chicken, rice. Include substitutions or quick tips if possible. Keep the response casual and easy to follow."
        },
        {
            "name": "Specific recipe query", 
            "prompt": "You are a helpful cooking assistant. Provide a clear, easy-to-follow recipe for: pancake recipe. Include ingredients, measurements, and simple instructions. Keep it casual and concise."
        }
    ]
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"Prompt: {test['prompt'][:100]}...")
        
        if LLM_PROVIDER.lower() == "openrouter":
            # Test OpenRouter
            try:
                if not OPENROUTER_API_KEY:
                    print("❌ OpenRouter API key not configured")
                    continue
                
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'HTTP-Referer': 'https://recipe-genie-bot.com',
                    'X-Title': 'Recipe Genie Bot'
                }
                
                data = {
                    'model': OPENROUTER_MODEL,
                    'messages': [{'role': 'user', 'content': test['prompt']}],
                    'max_tokens': OPENROUTER_MAX_TOKENS,
                    'temperature': OPENROUTER_TEMPERATURE,
                    'stream': False
                }
                
                response = requests.post(
                    OPENROUTER_ENDPOINT,
                    headers=headers,
                    json=data,
                    timeout=OPENROUTER_TIMEOUT
                )
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    print("✅ OpenRouter Success!")
                    content = result['choices'][0]['message']['content']
                    print(f"Response: {content[:200]}...")
                    
                    # Log usage if available
                    if 'usage' in result:
                        usage = result['usage']
                        print(f"Usage - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                              f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                              f"Total: {usage.get('total_tokens', 'N/A')}")
                else:
                    print("❌ OpenRouter failed - Invalid response format")
                    
            except requests.exceptions.ConnectionError:
                print("❌ OpenRouter connection failed - Check your internet connection")
            except requests.exceptions.Timeout:
                print("❌ OpenRouter request timed out")
            except Exception as e:
                print(f"❌ OpenRouter error: {str(e)}")
        
        else:
            # Test local LLM
            try:
                # Try different API formats
                
                # Format 1: Simple JSON with 'prompt' field
                try:
                    response = requests.post(
                        LLM_ENDPOINT,
                        json={'prompt': test['prompt']},
                        timeout=LLM_TIMEOUT
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if 'response' in result:
                        print("✅ Success! (Format 1)")
                        print(f"Response: {result['response'][:200]}...")
                        continue
                    elif 'text' in result:
                        print("✅ Success! (Format 1 with 'text' field)")
                        print(f"Response: {result['text'][:200]}...")
                        continue
                        
                except Exception as e:
                    print(f"❌ Format 1 failed: {str(e)}")
                
                # Format 2: LMStudio OpenAI-compatible format
                try:
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    
                    # Add API key if provided
                    if LLM_API_KEY:
                        headers['Authorization'] = f'Bearer {LLM_API_KEY}'
                    
                    data = {
                        'model': LLM_MODEL,
                        'messages': [{'role': 'user', 'content': test['prompt']}],
                        'max_tokens': LLM_MAX_TOKENS,
                        'temperature': LLM_TEMPERATURE,
                        'stream': False
                    }
                    response = requests.post(
                        LLM_ENDPOINT,
                        headers=headers,
                        json=data,
                        timeout=LLM_TIMEOUT
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        print("✅ Success! (LMStudio OpenAI-compatible format)")
                        content = result['choices'][0]['message']['content']
                        print(f"Response: {content[:200]}...")
                        continue
                        
                except Exception as e:
                    print(f"❌ LMStudio OpenAI-compatible format failed: {str(e)}")
                
                # Format 3: Simple text response
                try:
                    response = requests.post(
                        LLM_ENDPOINT,
                        data=test['prompt'],
                        headers={'Content-Type': 'text/plain'},
                        timeout=LLM_TIMEOUT
                    )
                    response.raise_for_status()
                    print("✅ Success! (Text format)")
                    print(f"Response: {response.text[:200]}...")
                    continue
                    
                except Exception as e:
                    print(f"❌ Text format failed: {str(e)}")
                
                print("❌ All local LLM formats failed for this test")
                
            except requests.exceptions.ConnectionError:
                print("❌ Connection failed - Is your LLM server running?")
            except requests.exceptions.Timeout:
                print("❌ Request timed out - Check your LLM_TIMEOUT setting")
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Complete!")
    print("\nNext steps:")
    print("1. If tests passed, your LLM integration should work")
    print("2. Run the bot with: python recipe_genie_bot_enhanced.py")
    print("\nIf tests failed:")
    if LLM_PROVIDER.lower() == "openrouter":
        print("1. Check your OpenRouter API key is set correctly")
        print("2. Verify your internet connection")
        print("3. Check the OpenRouter model name in config.py")
    else:
        print("1. Check your local LLM server is running")
        print("2. Verify the endpoint URL in config.py")
        print("3. Check your LLM API format and update accordingly")

def test_local_function():
    """Test if you have a local LLM function available."""
    print("\n🔍 Testing for local LLM function...")
    
    # Common local LLM imports to try
    possible_imports = [
        'transformers',
        'torch',
        'llama_cpp',
        'ctransformers',
        'sentence_transformers'
    ]
    
    for module in possible_imports:
        try:
            __import__(module)
            print(f"✅ Found {module} - You might be able to use direct function calls")
        except ImportError:
            print(f"❌ {module} not found")
    
    print("\n💡 If you have a local LLM function, you can use it like this:")
    print("""
def generate_recipe(prompt: str) -> str:
    from your_llm_module import generate_text
    return generate_text(prompt)
    """)

if __name__ == "__main__":
    print("🍳 Recipe Genie LLM Integration Tester")
    print("=" * 50)
    
    test_llm_connection()
    test_local_function()