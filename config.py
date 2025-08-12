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

# Recipe-related keywords for intent detection (English)
RECIPE_KEYWORDS_EN: List[str] = [
    'recipe', 'how to make', 'how to cook', 'instructions', 'directions',
    'ingredients', 'steps', 'method', 'preparation', 'cooking'
]

# Recipe-related keywords for intent detection (Spanish)
RECIPE_KEYWORDS_ES: List[str] = [
    'receta', 'cómo hacer', 'cómo cocinar', 'instrucciones', 'direcciones',
    'ingredientes', 'pasos', 'método', 'preparación', 'cocinar', 'cocción'
]

# Common dish names for better intent detection (English)
DISH_NAMES_EN: List[str] = [
    'pancake', 'pancakes', 'brownie', 'brownies', 'cake', 'cookies', 'bread',
    'pasta', 'pizza', 'soup', 'salad', 'stew', 'curry', 'stir fry', 'roast',
    'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise', 'lasagna',
    'spaghetti', 'burger', 'sandwich', 'taco', 'burrito', 'sushi', 'ramen',
    'noodles', 'rice', 'quinoa', 'oatmeal', 'cereal', 'smoothie', 'juice'
]

# Common dish names for better intent detection (Spanish)
DISH_NAMES_ES: List[str] = [
    'panqueque', 'panqueques', 'brownie', 'brownies', 'pastel', 'galletas', 'pan',
    'pasta', 'pizza', 'sopa', 'ensalada', 'estofado', 'curry', 'salteado', 'asado',
    'parrilla', 'horneado', 'frito', 'hervido', 'vapor', 'salteado', 'braseado', 'lasaña',
    'espagueti', 'hamburguesa', 'sándwich', 'taco', 'burrito', 'sushi', 'ramen',
    'fideos', 'arroz', 'quinua', 'avena', 'cereal', 'batido', 'jugo'
]

# Common ingredients for better pattern matching (English)
COMMON_INGREDIENTS_EN: List[str] = [
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

# Common ingredients for better pattern matching (Spanish)
COMMON_INGREDIENTS_ES: List[str] = [
    'tomate', 'tomates', 'pollo', 'res', 'cerdo', 'pescado', 'salmón', 'atún',
    'arroz', 'pasta', 'cebolla', 'ajo', 'queso', 'huevo', 'huevos', 'leche',
    'harina', 'azúcar', 'sal', 'pimienta', 'aceite', 'mantequilla', 'crema', 'yogur',
    'limón', 'lima', 'zanahoria', 'papa', 'papas', 'espinaca', 'lechuga',
    'pepino', 'pimiento', 'champiñón', 'champiñones', 'brócoli', 'coliflor',
    'calabacín', 'berenjena', 'aguacate', 'plátano', 'manzana', 'naranja', 'fresa',
    'arándano', 'frambuesa', 'chocolate', 'vainilla', 'canela', 'nuez moscada',
    'orégano', 'albahaca', 'tomillo', 'romero', 'perejil', 'cilantro', 'jengibre',
    'cúrcuma', 'comino', 'pimentón', 'chile', 'jalapeño', 'pimiento morrón'
]

# Legacy support - keep original lists for backward compatibility
RECIPE_KEYWORDS = RECIPE_KEYWORDS_EN
DISH_NAMES = DISH_NAMES_EN
COMMON_INGREDIENTS = COMMON_INGREDIENTS_EN

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