#!/usr/bin/env python3
"""
Recipe Genie - A Telegram bot that provides recipe suggestions using a local LLM
Supports both English and Spanish localization
"""

import asyncio
import logging
import re
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langdetect import detect, LangDetectException

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token
MAX_INPUT_LENGTH = 500  # Maximum length for user input

# Recipe-related keywords for intent detection (English)
RECIPE_KEYWORDS_EN = [
    'recipe', 'how to make', 'how to cook', 'instructions', 'directions',
    'ingredients', 'steps', 'method', 'preparation', 'cooking'
]

# Recipe-related keywords for intent detection (Spanish)
RECIPE_KEYWORDS_ES = [
    'receta', 'cómo hacer', 'cómo cocinar', 'instrucciones', 'direcciones',
    'ingredientes', 'pasos', 'método', 'preparación', 'cocinar', 'cocción'
]

# Common dish names for better intent detection (English)
DISH_NAMES_EN = [
    'pancake', 'pancakes', 'brownie', 'brownies', 'cake', 'cookies', 'bread',
    'pasta', 'pizza', 'soup', 'salad', 'stew', 'curry', 'stir fry', 'roast',
    'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise'
]

# Common dish names for better intent detection (Spanish)
DISH_NAMES_ES = [
    'panqueque', 'panqueques', 'brownie', 'brownies', 'pastel', 'galletas', 'pan',
    'pasta', 'pizza', 'sopa', 'ensalada', 'estofado', 'curry', 'salteado', 'asado',
    'parrilla', 'horneado', 'frito', 'hervido', 'vapor', 'salteado', 'braseado'
]

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

def generate_recipe(prompt: str, language: str = 'en') -> str:
    """
    Placeholder function for local LLM integration.
    Replace this with your actual local LLM API call.
    
    Args:
        prompt (str): The prompt to send to the LLM
        language (str): The language of the prompt ('en' or 'es')
        
    Returns:
        str: The LLM-generated response
    """
    # TODO: Replace with actual local LLM integration
    # Example implementation:
    # import requests
    # response = requests.post('http://localhost:8000/generate', json={'prompt': prompt})
    # return response.json()['response']
    
    # Placeholder responses for testing
    if language == 'es':
        if "ingredientes" in prompt.lower():
            return """🍳 Idea de Receta Rápida:

**Salteado Simple**
- Calienta aceite en una sartén
- Agrega tus ingredientes y saltea por 5-7 minutos
- Sazona con sal, pimienta y tus especias favoritas
- ¡Sirve caliente!

💡 Consejo: ¡Agrega ajo y jengibre para más sabor!"""
        else:
            return """🍽️ Receta:

**Ingredientes:**
- 2 tazas de harina
- 1 taza de leche
- 2 huevos
- 2 cucharadas de azúcar
- 1 cucharadita de polvo para hornear
- Pizca de sal

**Instrucciones:**
1. Mezcla los ingredientes secos
2. Bate los ingredientes húmedos por separado
3. Combina y cocina a fuego medio
4. Voltea cuando se formen burbujas
5. ¡Sirve con tus toppings favoritos!

¡Disfruta! 😊"""
    else:
        if "ingredients" in prompt.lower():
            return """🍳 Quick Recipe Idea:

**Simple Stir-Fry**
- Heat oil in a pan
- Add your ingredients and stir-fry for 5-7 minutes
- Season with salt, pepper, and your favorite spices
- Serve hot!

💡 Tip: Add garlic and ginger for extra flavor!"""
        else:
            return """🍽️ Recipe:

**Ingredients:**
- 2 cups flour
- 1 cup milk
- 2 eggs
- 2 tbsp sugar
- 1 tsp baking powder
- Pinch of salt

**Instructions:**
1. Mix dry ingredients
2. Whisk wet ingredients separately
3. Combine and cook on medium heat
4. Flip when bubbles form
5. Serve with your favorite toppings!

Enjoy! 😊"""

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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command with bilingual support."""
    welcome_message = """
🍳 *Welcome to Recipe Genie!* 🧙‍♂️

I'm your AI cooking assistant that can help you with recipes using a local LLM.

*How to use me:*

📝 *Ingredient-based recipes:*
Send me a list of ingredients like:
• "tomato, chicken, rice"
• "eggs, milk, flour"
• "beef, onion, potatoes"

🍽️ *Specific recipe requests:*
Ask for specific dishes like:
• "pancake recipe"
• "how to make brownies"
• "chicken curry recipe"

I'll automatically detect what you need and provide helpful cooking suggestions!

*Commands:*
/start - Show this welcome message
/help - Show help information

Let's start cooking! 🎉

---

🍳 *¡Bienvenido a Recipe Genie!* 🧙‍♂️

¡Soy tu asistente de cocina con IA que puede ayudarte con recetas usando un LLM local!

*Cómo usarme:*

📝 *Recetas basadas en ingredientes:*
Envíame una lista de ingredientes como:
• "tomate, pollo, arroz"
• "huevos, leche, harina"
• "res, cebolla, papas"

🍽️ *Solicitudes de recetas específicas:*
Pide platos específicos como:
• "receta de panqueques"
• "cómo hacer brownies"
• "receta de curry de pollo"

¡Detectaré automáticamente lo que necesitas y te daré sugerencias útiles de cocina!

*Comandos:*
/start - Mostrar este mensaje de bienvenida
/help - Mostrar información de ayuda

¡Empecemos a cocinar! 🎉
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command with bilingual support."""
    help_message = """
🍳 *Recipe Genie Help* 🧙‍♂️

*Usage Examples:*

*Ingredient-based:*
• "tomato, chicken, rice"
• "eggs, milk, flour, sugar"
• "beef, onion, garlic, potatoes"

*Specific recipes:*
• "pancake recipe"
• "how to make chocolate cake"
• "chicken stir fry recipe"

*Tips:*
• Keep your ingredient lists simple
• Be specific with recipe requests
• I'll suggest substitutions when possible

Need help? Just send me ingredients or ask for a recipe!

---

🍳 *Ayuda de Recipe Genie* 🧙‍♂️

*Ejemplos de Uso:*

*Basado en ingredientes:*
• "tomate, pollo, arroz"
• "huevos, leche, harina, azúcar"
• "res, cebolla, ajo, papas"

*Recetas específicas:*
• "receta de panqueques"
• "cómo hacer pastel de chocolate"
• "receta de salteado de pollo"

*Consejos:*
• Mantén tus listas de ingredientes simples
• Sé específico con las solicitudes de recetas
• Sugeriré sustituciones cuando sea posible

¿Necesitas ayuda? ¡Solo envíame ingredientes o pide una receta!
"""
    
    await update.message.reply_text(help_message, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} requested help")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and generate recipe responses with language detection."""
    user_message = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Log the incoming message
    logger.info(f"User {user_id} sent: {user_message}")
    
    # Check input length
    if len(user_message) > MAX_INPUT_LENGTH:
        await update.message.reply_text(
            f"❌ Your message is too long! Please keep it under {MAX_INPUT_LENGTH} characters.\n\n"
            f"❌ ¡Tu mensaje es muy largo! Por favor manténlo bajo {MAX_INPUT_LENGTH} caracteres."
        )
        return
    
    # Skip empty messages
    if not user_message:
        await update.message.reply_text(
            "Please send me some ingredients or ask for a recipe!\n\n"
            "¡Por favor envíame algunos ingredientes o pide una receta!"
        )
        return
    
    try:
        # Detect language
        language = detect_language(user_message)
        logger.info(f"Detected language: {language} for user {user_id}")
        
        # Detect user intent
        intent, cleaned_query = detect_intent(user_message, language)
        logger.info(f"Detected intent: {intent} for query: {cleaned_query}")
        
        # Build the prompt
        prompt = build_prompt(intent, cleaned_query, language)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate recipe response
        response = generate_recipe(prompt, language)
        
        # Send the response
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Log the response
        logger.info(f"Generated response for user {user_id}: {response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {str(e)}")
        await update.message.reply_text(
            "😔 Sorry, I encountered an error while generating your recipe. Please try again!\n\n"
            "😔 Lo siento, encontré un error al generar tu receta. ¡Por favor inténtalo de nuevo!"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors gracefully with bilingual support."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to send an error message to the user if possible
    if update and hasattr(update, 'effective_chat') and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="😔 Sorry, something went wrong. Please try again later!\n\n"
                     "😔 Lo siento, algo salió mal. ¡Por favor inténtalo más tarde!"
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {str(e)}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Recipe Genie bot with Spanish localization support...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()