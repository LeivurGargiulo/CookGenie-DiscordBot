"""
Configuration settings for Recipe Genie bot
"""

import os
from typing import List

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
MAX_INPUT_LENGTH = 500

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

# LLM configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8000/generate")
LLM_TIMEOUT = 30  # seconds