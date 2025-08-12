#!/usr/bin/env python3
"""
Recipe Genie - Enhanced Telegram bot that provides recipe suggestions using a local LLM
"""

import asyncio
import logging
import re
import requests
import json
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import *

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def generate_recipe(prompt: str) -> str:
    """
    Generate recipe using local LLM (LMStudio compatible).
    This function is configured for LMStudio's OpenAI-compatible API.
    
    Args:
        prompt (str): The prompt to send to the LLM
        
    Returns:
        str: The LLM-generated response
    """
    try:
        # LMStudio OpenAI-compatible API call
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
        
        logger.info(f"Sending request to LLM endpoint: {LLM_ENDPOINT}")
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
            logger.info(f"LLM response received: {len(content)} characters")
            return content
        else:
            logger.error(f"Unexpected LLM response format: {result}")
            raise ValueError("Invalid response format from LLM")
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection failed to LLM server: {str(e)}")
        return "😔 Sorry, I can't connect to my recipe database. Please check if LMStudio is running and try again!"
    except requests.exceptions.Timeout as e:
        logger.error(f"LLM request timed out: {str(e)}")
        return "😔 Sorry, my recipe database is taking too long to respond. Please try again!"
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM API request failed: {str(e)}")
        return "😔 Sorry, I'm having trouble connecting to my recipe database. Please try again later!"
    except Exception as e:
        logger.error(f"LLM generation failed: {str(e)}")
        return "😔 Sorry, I encountered an error while generating your recipe. Please try again!"

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
• "how to make chocolate cake"
• "chicken stir fry recipe"

*Tips:*
• Keep your ingredient lists simple
• Be specific with recipe requests
• I'll suggest substitutions when possible
• Maximum input length: 500 characters

Need help? Just send me ingredients or ask for a recipe!
"""
    
    await update.message.reply_text(help_message, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} requested help")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and generate recipe responses."""
    user_message = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Log the incoming message
    logger.info(f"User {user_id} sent: {user_message}")
    
    # Check input length
    if len(user_message) > MAX_INPUT_LENGTH:
        await update.message.reply_text(
            f"❌ Your message is too long! Please keep it under {MAX_INPUT_LENGTH} characters."
        )
        return
    
    # Skip empty messages
    if not user_message:
        await update.message.reply_text("Please send me some ingredients or ask for a recipe!")
        return
    
    try:
        # Detect user intent
        intent, cleaned_query = detect_intent(user_message)
        logger.info(f"Detected intent: {intent} for query: {cleaned_query}")
        
        # Build the prompt
        prompt = build_prompt(intent, cleaned_query)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate recipe response
        response = generate_recipe(prompt)
        
        # Send the response
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Log the response
        logger.info(f"Generated response for user {user_id}: {response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {str(e)}")
        await update.message.reply_text(
            "😔 Sorry, I encountered an error while generating your recipe. Please try again!"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors gracefully."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to send an error message to the user if possible
    if update and hasattr(update, 'effective_chat') and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="😔 Sorry, something went wrong. Please try again later!"
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {str(e)}")

def main() -> None:
    """Start the bot."""
    # Validate bot token
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Please set your bot token in config.py or as BOT_TOKEN environment variable")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Recipe Genie bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()