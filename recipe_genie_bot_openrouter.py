#!/usr/bin/env python3
"""
Recipe Genie - OpenRouter Enhanced Telegram bot
Optimized for OpenRouter API with advanced features
"""

import asyncio
import logging
import re
import json
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import *
from llm_providers import generate_recipe, get_llm_provider

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def detect_intent(message: str) -> Tuple[str, str]:
    """
    Detect whether the user is asking for a specific recipe or providing ingredients.
    
    Args:
        message (str): User's message
        
    Returns:
        Tuple[str, str]: (intent_type, cleaned_query)
    """
    message_lower = message.lower().strip()
    
    # Check for recipe-related keywords
    has_recipe_keywords = any(keyword in message_lower for keyword in RECIPE_KEYWORDS)
    
    # Check for dish names
    has_dish_names = any(dish in message_lower for dish in DISH_NAMES)
    
    # Check if it looks like a list of ingredients
    ingredient_patterns = [
        r'\b(' + '|'.join(COMMON_INGREDIENTS) + r')\b',
        r'[,\s]+(and\s+)?[a-z]+',  # Pattern for comma-separated items
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

def build_prompt(intent: str, query: str) -> str:
    """
    Build the appropriate prompt for the LLM based on user intent.
    
    Args:
        intent (str): The detected intent ('specific_recipe' or 'ingredient_based')
        query (str): The user's query
        
    Returns:
        str: The formatted prompt for the LLM
    """
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
    """Handle the /start command."""
    provider = get_llm_provider()
    provider_name = "OpenRouter" if LLM_PROVIDER.lower() == "openrouter" else "Local LLM"
    
    welcome_message = f"""
🍳 *Welcome to Recipe Genie!* 🧙‍♂️

I'm your AI cooking assistant powered by {provider_name} that can help you with recipes!

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
/status - Show current LLM provider status

Let's start cooking! 🎉
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_message = """
🍳 *Recipe Genie Help* 🧙‍♂️

*Usage Examples:*

*Ingredient-based:*
• "tomato, chicken, rice"
• "eggs, milk, flour, sugar"
• "beef, onion, garlic, potatoes"

*Specific recipes:*
• "pancake recipe"
• "how to make brownies"
• "chicken curry recipe"
• "pasta carbonara"
• "beef stir fry"

*Tips:*
• Be specific with ingredients for better suggestions
• Include cooking preferences (vegetarian, quick, etc.)
• Ask for substitutions if needed

*Commands:*
/start - Welcome message
/help - This help message
/status - Show LLM provider status

Need more help? Just ask! 😊
"""
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

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
    """Handle incoming messages and generate recipe responses."""
    user_message = update.message.text.strip()
    user_id = update.effective_user.id
    
    logger.info(f"User {user_id} sent: {user_message}")
    
    # Input validation
    if not user_message:
        await update.message.reply_text("Please send me some ingredients or ask for a recipe! 😊")
        return
    
    if len(user_message) > MAX_INPUT_LENGTH:
        await update.message.reply_text(f"Your message is too long! Please keep it under {MAX_INPUT_LENGTH} characters. 😅")
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Detect intent
        intent, query = detect_intent(user_message)
        logger.info(f"Detected intent: {intent} for query: {query}")
        
        # Build prompt
        prompt = build_prompt(intent, query)
        
        # Generate recipe
        response = generate_recipe(prompt)
        
        # Send response
        await update.message.reply_text(response)
        logger.info(f"Successfully generated recipe for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {str(e)}")
        await update.message.reply_text("😔 Sorry, I encountered an error while processing your request. Please try again!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    if update and hasattr(update, 'message'):
        await update.message.reply_text("😔 Sorry, something went wrong. Please try again later!")

def main() -> None:
    """Start the bot."""
    # Validate configuration
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Bot token not configured! Please set BOT_TOKEN in your environment variables.")
        return
    
    if LLM_PROVIDER.lower() == "openrouter" and not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not configured! Please set OPENROUTER_API_KEY in your environment variables.")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Log startup information
    provider = get_llm_provider()
    provider_name = "OpenRouter" if LLM_PROVIDER.lower() == "openrouter" else "Local LLM"
    logger.info(f"Starting Recipe Genie bot with {provider_name} provider")
    
    if LLM_PROVIDER.lower() == "openrouter":
        logger.info(f"OpenRouter Model: {OPENROUTER_MODEL}")
        logger.info(f"OpenRouter Endpoint: {OPENROUTER_ENDPOINT}")
    else:
        logger.info(f"Local LLM Model: {LLM_MODEL}")
        logger.info(f"Local LLM Endpoint: {LLM_ENDPOINT}")
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()