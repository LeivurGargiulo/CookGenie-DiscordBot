#!/usr/bin/env python3
"""
Recipe Genie - OpenRouter Enhanced Telegram bot
Optimized for OpenRouter API with advanced features
Supports both English and Spanish localization
"""

import asyncio
import logging
import re
import json
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langdetect import detect, LangDetectException
from config import *
from llm_providers import generate_recipe, get_llm_provider

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
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
        common_ingredients = COMMON_INGREDIENTS_ES
    else:
        recipe_keywords = RECIPE_KEYWORDS_EN
        dish_names = DISH_NAMES_EN
        common_ingredients = COMMON_INGREDIENTS_EN
    
    # Check for recipe-related keywords
    has_recipe_keywords = any(keyword in message_lower for keyword in recipe_keywords)
    
    # Check for dish names
    has_dish_names = any(dish in message_lower for dish in dish_names)
    
    # Check if it looks like a list of ingredients
    ingredient_patterns = [
        r'\b(' + '|'.join(common_ingredients) + r')\b',
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
            return f"""Eres un asistente de cocina amigable. Sugiere una receta o idea de comida sencilla usando estos ingredientes: {query}. 

Por favor incluye:
- Un nombre claro para la receta
- Lista de ingredientes con cantidades
- Instrucciones simples paso a paso
- Tiempo de cocción y porciones
- Sustituciones o consejos rápidos si es posible

Mantén la respuesta casual, fácil de seguir y bajo 300 palabras. ¡Usa emojis para hacerla amigable!"""
        else:  # specific_recipe
            return f"""Eres un asistente de cocina útil. Proporciona una receta clara y fácil de seguir para: {query}.

Por favor incluye:
- Lista completa de ingredientes con cantidades
- Instrucciones de cocción paso a paso
- Tiempo de preparación y cocción
- Número de porciones
- Cualquier consejo útil o variaciones

Mantén un tono casual, conciso y bajo 400 palabras. ¡Usa emojis para hacerlo amigable!"""
    else:
        if intent == "ingredient_based":
            return f"""You are a friendly cooking assistant. Suggest a simple recipe or meal idea using these ingredients: {query}. 

Please include:
- A clear recipe name
- List of ingredients with measurements
- Simple step-by-step instructions
- Cooking time and servings
- Substitutions or quick tips if possible

Keep the response casual, easy to follow, and under 300 words. Use emojis to make it friendly!"""
        else:  # specific_recipe
            return f"""You are a helpful cooking assistant. Provide a clear, easy-to-follow recipe for: {query}.

Please include:
- Complete list of ingredients with measurements
- Step-by-step cooking instructions
- Prep time and cook time
- Number of servings
- Any helpful tips or variations

Keep it casual, concise, and under 400 words. Use emojis to make it friendly!"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command with bilingual support."""
    provider = get_llm_provider()
    provider_name = "OpenRouter" if LLM_PROVIDER.lower() == "openrouter" else "Local LLM"
    
    welcome_message = f"""
🍳 *Welcome to Recipe Genie!* 🧙‍♂️

I'm your AI cooking assistant powered by {provider_name} that can help you with recipes.

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

¡Soy tu asistente de cocina con IA impulsado por {provider_name} que puede ayudarte con recetas!

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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command to show current LLM provider status."""
    provider = get_llm_provider()
    provider_name = "OpenRouter" if LLM_PROVIDER.lower() == "openrouter" else "Local LLM"
    
    if LLM_PROVIDER.lower() == "openrouter":
        status_message = f"""
🔧 *LLM Provider Status*

*Provider:* {provider_name}
*Model:* {OPENROUTER_MODEL}
*API Key:* {'✅ Configured' if OPENROUTER_API_KEY else '❌ Not configured'}
*Endpoint:* {OPENROUTER_ENDPOINT}

*Settings:*
• Max Tokens: {OPENROUTER_MAX_TOKENS}
• Temperature: {OPENROUTER_TEMPERATURE}
• Timeout: {OPENROUTER_TIMEOUT}s

*Status:* {'🟢 Ready' if OPENROUTER_API_KEY else '🔴 Not configured'}
"""
    else:
        status_message = f"""
🔧 *LLM Provider Status*

*Provider:* {provider_name}
*Model:* {LLM_MODEL}
*Endpoint:* {LLM_ENDPOINT}
*API Key:* {'✅ Configured' if LLM_API_KEY else '❌ Not required'}

*Settings:*
• Max Tokens: {LLM_MAX_TOKENS}
• Temperature: {LLM_TEMPERATURE}
• Timeout: {LLM_TIMEOUT}s

*Status:* 🟡 Check local server
"""
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

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
        
        # Generate recipe response using the LLM provider
        response = generate_recipe(prompt)
        
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
    # Validate configuration
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Bot token not configured! Please set BOT_TOKEN in your environment variables.")
        return
    
    if LLM_PROVIDER.lower() == "openrouter" and not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not configured! Please set OPENROUTER_API_KEY in your environment variables.")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Recipe Genie OpenRouter bot with Spanish localization support...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()