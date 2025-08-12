"""
Language utilities for Recipe Genie Discord Bot.
Handles language detection, intent detection, and prompt building.
"""

import re
import logging
from typing import Tuple, List
from langdetect import detect, LangDetectException

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
        logger.warning(f"Language detection failed for text: {text[:50]}...")
        return 'en'


def detect_intent(message: str, language: str, config) -> Tuple[str, str]:
    """
    Detect whether the user is asking for a specific recipe or providing ingredients.
    
    Args:
        message (str): User's message
        language (str): Language code ('en' or 'es')
        config: Bot configuration object
        
    Returns:
        Tuple[str, str]: (intent_type, cleaned_query)
    """
    message_lower = message.lower().strip()
    
    # Select appropriate keywords based on language
    if language == 'es':
        recipe_keywords = config.recipe_keywords_es
        dish_names = config.dish_names_es
    else:
        recipe_keywords = config.recipe_keywords_en
        dish_names = config.dish_names_en
    
    # Check for recipe-related keywords
    for keyword in recipe_keywords:
        if keyword in message_lower:
            return "recipe_request", message
    
    # Check for specific dish names
    for dish in dish_names:
        if dish in message_lower:
            return "recipe_request", message
    
    # Check if it looks like a list of ingredients
    if _looks_like_ingredients(message_lower, language):
        return "ingredients_list", message
    
    # Default to recipe request
    return "recipe_request", message


def _looks_like_ingredients(text: str, language: str) -> bool:
    """
    Check if text looks like a list of ingredients.
    
    Args:
        text (str): Text to analyze
        language (str): Language code
        
    Returns:
        bool: True if text looks like ingredients list
    """
    # Check for common ingredient separators
    separators = [',', 'and', 'y', 'with', 'con']
    separator_count = sum(1 for sep in separators if sep in text)
    
    # Check for ingredient-like patterns
    ingredient_patterns = [
        r'\d+\s*(cup|cups|taza|tazas|tbsp|tsp|oz|g|kg|lb|gramo|gramos|kilo|kilos)',
        r'\d+\s*(piece|pieces|pieza|piezas|slice|slices|rebanada|rebanadas)',
        r'\d+\s*(clove|cloves|diente|dientes|bunch|manojo)',
        r'(fresh|freshly|fresco|fresca|dried|seco|seca|frozen|congelado|congelada)',
        r'(organic|organico|organica|whole|entero|entera|ground|molido|molida)'
    ]
    
    pattern_matches = sum(1 for pattern in ingredient_patterns if re.search(pattern, text, re.IGNORECASE))
    
    # If we have multiple separators or ingredient patterns, it's likely ingredients
    return separator_count >= 2 or pattern_matches >= 2


def build_prompt(query: str, intent: str, language: str) -> str:
    """
    Build a prompt for the LLM based on intent and language.
    
    Args:
        query (str): User's query
        intent (str): Detected intent
        language (str): Language code
        
    Returns:
        str: Formatted prompt for LLM
    """
    if language == "es":
        if intent == "ingredients_list":
            return f"Crear una receta deliciosa usando estos ingredientes: {query}. Proporciona una receta completa con instrucciones paso a paso."
        else:
            return f"Crear una receta para: {query}. Proporciona una receta completa y detallada con ingredientes e instrucciones."
    else:
        if intent == "ingredients_list":
            return f"Create a delicious recipe using these ingredients: {query}. Provide a complete recipe with step-by-step instructions."
        else:
            return f"Create a recipe for: {query}. Provide a complete and detailed recipe with ingredients and instructions."


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks and improve processing.
    
    Args:
        text (str): Raw user input
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially dangerous characters (keep basic punctuation)
    text = re.sub(r'[<>{}[\]\\|`~!@#$%^&*+=]', '', text)
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000] + "..."
    
    return text


def extract_ingredients(text: str, language: str) -> List[str]:
    """
    Extract ingredients from text.
    
    Args:
        text (str): Text containing ingredients
        language (str): Language code
        
    Returns:
        List[str]: List of extracted ingredients
    """
    # Split by common separators
    separators = [',', 'and', 'y', 'with', 'con', 'plus', 'más']
    
    # Replace separators with commas for consistent splitting
    processed_text = text.lower()
    for sep in separators:
        processed_text = processed_text.replace(sep, ',')
    
    # Split and clean
    ingredients = [ingredient.strip() for ingredient in processed_text.split(',')]
    
    # Remove empty entries and common non-ingredient words
    non_ingredient_words = {
        'en': ['the', 'a', 'an', 'some', 'any', 'all', 'each', 'every', 'this', 'that', 'these', 'those'],
        'es': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'alguno', 'alguna', 'todo', 'cada', 'este', 'esta', 'estos', 'estas']
    }
    
    filtered_ingredients = []
    for ingredient in ingredients:
        if ingredient and len(ingredient) > 2:  # Minimum length
            # Remove common non-ingredient words
            words = ingredient.split()
            filtered_words = [word for word in words if word not in non_ingredient_words.get(language, [])]
            if filtered_words:
                filtered_ingredients.append(' '.join(filtered_words))
    
    return filtered_ingredients


def format_recipe_text(text: str, language: str) -> str:
    """
    Format recipe text for better readability.
    
    Args:
        text (str): Raw recipe text
        language (str): Language code
        
    Returns:
        str: Formatted recipe text
    """
    if not text:
        return ""
    
    # Split into sections
    sections = text.split('\n\n')
    formatted_sections = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Check if it's a title (usually in caps or has special formatting)
        if section.isupper() or section.startswith('**'):
            formatted_sections.append(f"**{section}**")
        # Check if it's ingredients list
        elif any(keyword in section.lower() for keyword in ['ingredients', 'ingredientes']):
            formatted_sections.append(f"**{section}**")
        # Check if it's instructions
        elif any(keyword in section.lower() for keyword in ['instructions', 'directions', 'instrucciones', 'direcciones']):
            formatted_sections.append(f"**{section}**")
        else:
            formatted_sections.append(section)
    
    return '\n\n'.join(formatted_sections)


def validate_language_code(language: str) -> bool:
    """
    Validate if a language code is supported.
    
    Args:
        language (str): Language code to validate
        
    Returns:
        bool: True if supported, False otherwise
    """
    supported_languages = ['en', 'es']
    return language.lower() in supported_languages


def get_language_name(language_code: str) -> str:
    """
    Get the full name of a language from its code.
    
    Args:
        language_code (str): Language code
        
    Returns:
        str: Full language name
    """
    language_names = {
        'en': 'English',
        'es': 'Spanish'
    }
    return language_names.get(language_code.lower(), 'Unknown')