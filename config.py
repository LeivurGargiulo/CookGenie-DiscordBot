"""
Configuration settings for Recipe Genie bot
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Recipe-related keywords for intent detection
RECIPE_KEYWORDS: List[str] = [
    'recipe', 'how to make', 'how to cook', 'instructions', 'directions',
    'ingredients', 'steps', 'method', 'preparation', 'cooking'
]

# Common dish names for better intent detection
DISH_NAMES: List[str] = [
    'pancake', 'pancakes', 'brownie', 'brownies', 'cake', 'cookies', 'bread',
    'pasta', 'pizza', 'soup', 'salad', 'stew', 'curry', 'stir fry', 'roast',
    'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise', 'lasagna',
    'spaghetti', 'burger', 'sandwich', 'taco', 'burrito', 'sushi', 'ramen',
    'noodles', 'rice', 'quinoa', 'oatmeal', 'cereal', 'smoothie', 'juice'
]

# Common ingredients for better pattern matching
COMMON_INGREDIENTS: List[str] = [
    'tomato', 'tomatoes', 'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna',
    'rice', 'pasta', 'onion', 'garlic', 'cheese', 'egg', 'eggs', 'milk',
    'flour', 'sugar', 'salt', 'pepper', 'oil', 'butter', 'cream', 'yogurt',
    'lemon', 'lime', 'carrot', 'potato', 'potatoes', 'spinach', 'lettuce',
    'cucumber', 'bell pepper', 'mushroom', 'mushrooms', 'broccoli', 'cauliflower',
    'zucchini', 'eggplant', 'avocado', 'banana', 'apple', 'orange', 'strawberry',
    'blueberry', 'raspberry', 'chocolate', 'vanilla', 'cinnamon', 'nutmeg',
    'oregano', 'basil', 'thyme', 'rosemary', 'parsley', 'cilantro', 'ginger',
    'turmeric', 'cumin', 'paprika', 'chili', 'jalapeño', 'bell pepper'
]

# LLM configuration (LMStudio compatible)
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:1234/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "your_model_name_here")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# OpenRouter configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")  # "local" or "openrouter"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_ENDPOINT = os.getenv("OPENROUTER_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")  # Default model
OPENROUTER_TIMEOUT = int(os.getenv("OPENROUTER_TIMEOUT", "30"))
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "500"))
OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))