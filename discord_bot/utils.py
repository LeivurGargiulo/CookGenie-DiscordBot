"""
Utility functions for Recipe Genie Discord bot
"""

import re
import logging
from typing import Tuple
from langdetect import detect, LangDetectException
from .config import (
    RECIPE_KEYWORDS_EN, RECIPE_KEYWORDS_ES,
    DISH_NAMES_EN, DISH_NAMES_ES,
    COMMON_INGREDIENTS_EN, COMMON_INGREDIENTS_ES
)

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: Language code ('es' for Spanish, 'en' for English, default to 'en')
    """
    try:
        lang = detect(text)
        return lang if lang in ['es', 'en'] else 'en'
    except LangDetectException:
        return 'en'

def detect_intent(message: str, language: str = 'en') -> Tuple[str, str]:
    """
    Detect whether the user is asking for a specific recipe or providing ingredients.
    
    Args:
        message (str): User's message
        language (str): Language code ('en' or 'es')
        
    Returns:
        Tuple[str, str]: (intent_type, cleaned_query)
    """
    message_lower = message.lower().strip()
    
    # Select appropriate keywords based on language
    if language == 'es':
        recipe_keywords = RECIPE_KEYWORDS_ES
        dish_names = DISH_NAMES_ES
    else:
        recipe_keywords = RECIPE_KEYWORDS_EN
        dish_names = DISH_NAMES_EN
    
    # Check for recipe-related keywords
    has_recipe_keywords = any(keyword in message_lower for keyword in recipe_keywords)
    
    # Check for dish names
    has_dish_names = any(dish in message_lower for dish in dish_names)
    
    # Check if it looks like a list of ingredients (contains common ingredients)
    ingredient_patterns = [
        r'\b(tomato|tomatoes|chicken|beef|pork|fish|rice|pasta|onion|garlic|cheese|egg|eggs|milk|flour|sugar|salt|pepper|oil|butter|tomate|tomates|pollo|res|cerdo|pescado|arroz|pasta|cebolla|ajo|queso|huevo|huevos|leche|harina|azúcar|sal|pimienta|aceite|mantequilla)\b',
        r'[,\s]+(and\s+)?[a-z]+',  # Pattern for comma-separated items
        r'[,\s]+(y\s+)?[a-z]+',    # Pattern for comma-separated items in Spanish
    ]
    
    looks_like_ingredients = any(re.search(pattern, message_lower) for pattern in ingredient_patterns)
    
    # Decision logic
    if has_recipe_keywords or has_dish_names:
        return "specific_recipe", message.strip()
    elif looks_like_ingredients and not has_recipe_keywords:
        return "ingredient_based", message.strip()
    else:
        # Default to ingredient-based if unclear
        return "ingredient_based", message.strip()

def build_prompt(intent: str, query: str, language: str = 'en') -> str:
    """
    Build the appropriate prompt for the LLM based on user intent and language.
    
    Args:
        intent (str): The detected intent ('specific_recipe' or 'ingredient_based')
        query (str): The user's query
        language (str): Language code ('en' or 'es')
        
    Returns:
        str: The formatted prompt for the LLM
    """
    if language == 'es':
        if intent == "ingredient_based":
            return f"""Eres un asistente de cocina amigable. Sugiere una receta o idea de comida sencilla usando estos ingredientes: {query}. Incluye sustituciones o consejos rápidos si es posible."""
        else:  # specific_recipe
            return f"""Eres un asistente de cocina útil. Proporciona una receta clara y fácil de seguir para: {query}. Incluye ingredientes, cantidades y pasos simples. Mantén un tono casual y conciso."""
    else:
        if intent == "ingredient_based":
            return f"""You are a friendly cooking assistant. Suggest a simple recipe or meal idea using these ingredients: {query}. Include substitutions or quick tips if possible. Keep the response casual and easy to follow."""
        else:  # specific_recipe
            return f"""You are a helpful cooking assistant. Provide a clear, easy-to-follow recipe for: {query}. Include ingredients, measurements, and simple instructions. Keep it casual and concise."""

def validate_input_length(text: str, max_length: int) -> bool:
    """
    Validate if the input text is within the maximum allowed length.
    
    Args:
        text (str): The text to validate
        max_length (int): Maximum allowed length
        
    Returns:
        bool: True if valid, False otherwise
    """
    return len(text) <= max_length

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent potential issues.
    
    Args:
        text (str): The text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove potentially dangerous characters (basic sanitization)
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()