#!/usr/bin/env python3
"""
LLM Provider module for Recipe Genie bot
Supports both local LLM (LMStudio) and OpenRouter
"""

import logging
import requests
import json
from typing import Optional
from config import (
    LLM_PROVIDER, LLM_ENDPOINT, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT, 
    LLM_MAX_TOKENS, LLM_TEMPERATURE, OPENROUTER_API_KEY, OPENROUTER_ENDPOINT,
    OPENROUTER_MODEL, OPENROUTER_TIMEOUT, OPENROUTER_MAX_TOKENS, OPENROUTER_TEMPERATURE
)

logger = logging.getLogger(__name__)

class LLMProvider:
    """Base class for LLM providers"""
    
    def generate_response(self, prompt: str) -> str:
        """Generate response from LLM"""
        raise NotImplementedError

class LocalLLMProvider(LLMProvider):
    """Local LLM provider (LMStudio compatible)"""
    
    def generate_response(self, prompt: str) -> str:
        """Generate recipe using local LLM (LMStudio compatible)."""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Add API key if provided
            if LLM_API_KEY:
                headers['Authorization'] = f'Bearer {LLM_API_KEY}'
            
            data = {
                'model': LLM_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': LLM_MAX_TOKENS,
                'temperature': LLM_TEMPERATURE,
                'stream': False
            }
            
            logger.info(f"Sending request to local LLM endpoint: {LLM_ENDPOINT}")
            logger.info(f"Using model: {LLM_MODEL}")
            
            response = requests.post(
                LLM_ENDPOINT,
                headers=headers,
                json=data,
                timeout=LLM_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.info(f"Local LLM response received: {len(content)} characters")
                return content
            else:
                logger.error(f"Unexpected local LLM response format: {result}")
                raise ValueError("Invalid response format from local LLM")
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed to local LLM server: {str(e)}")
            return "😔 Sorry, I can't connect to my local recipe database. Please check if LMStudio is running and try again!"
        except requests.exceptions.Timeout as e:
            logger.error(f"Local LLM request timed out: {str(e)}")
            return "😔 Sorry, my local recipe database is taking too long to respond. Please try again!"
        except requests.exceptions.RequestException as e:
            logger.error(f"Local LLM API request failed: {str(e)}")
            return "😔 Sorry, I'm having trouble connecting to my local recipe database. Please try again later!"
        except Exception as e:
            logger.error(f"Local LLM generation failed: {str(e)}")
            return "😔 Sorry, I encountered an error while generating your recipe. Please try again!"

class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider"""
    
    def generate_response(self, prompt: str) -> str:
        """Generate recipe using OpenRouter API."""
        try:
            if not OPENROUTER_API_KEY:
                logger.error("OpenRouter API key not configured")
                return "😔 Sorry, OpenRouter API key is not configured. Please check your environment variables."
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'HTTP-Referer': 'https://recipe-genie-bot.com',  # Required by OpenRouter
                'X-Title': 'Recipe Genie Bot'  # Optional but recommended
            }
            
            data = {
                'model': OPENROUTER_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': OPENROUTER_MAX_TOKENS,
                'temperature': OPENROUTER_TEMPERATURE,
                'stream': False
            }
            
            logger.info(f"Sending request to OpenRouter endpoint: {OPENROUTER_ENDPOINT}")
            logger.info(f"Using model: {OPENROUTER_MODEL}")
            
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers=headers,
                json=data,
                timeout=OPENROUTER_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.info(f"OpenRouter response received: {len(content)} characters")
                
                # Log usage information if available
                if 'usage' in result:
                    usage = result['usage']
                    logger.info(f"OpenRouter usage - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}, "
                              f"Completion tokens: {usage.get('completion_tokens', 'N/A')}, "
                              f"Total tokens: {usage.get('total_tokens', 'N/A')}")
                
                return content
            else:
                logger.error(f"Unexpected OpenRouter response format: {result}")
                raise ValueError("Invalid response format from OpenRouter")
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed to OpenRouter: {str(e)}")
            return "😔 Sorry, I can't connect to OpenRouter. Please check your internet connection and try again!"
        except requests.exceptions.Timeout as e:
            logger.error(f"OpenRouter request timed out: {str(e)}")
            return "😔 Sorry, OpenRouter is taking too long to respond. Please try again!"
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {str(e)}")
            return "😔 Sorry, I'm having trouble connecting to OpenRouter. Please try again later!"
        except Exception as e:
            logger.error(f"OpenRouter generation failed: {str(e)}")
            return "😔 Sorry, I encountered an error while generating your recipe. Please try again!"

def get_llm_provider() -> LLMProvider:
    """Get the appropriate LLM provider based on configuration."""
    if LLM_PROVIDER.lower() == "openrouter":
        logger.info("Using OpenRouter as LLM provider")
        return OpenRouterProvider()
    else:
        logger.info("Using local LLM as provider")
        return LocalLLMProvider()

def generate_recipe(prompt: str) -> str:
    """
    Generate recipe using the configured LLM provider.
    
    Args:
        prompt (str): The prompt to send to the LLM
        
    Returns:
        str: The LLM-generated response
    """
    provider = get_llm_provider()
    return provider.generate_response(prompt)