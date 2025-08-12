#!/usr/bin/env python3
"""
Recipe Genie - A Telegram bot that provides recipe suggestions using a local LLM
"""

import asyncio
import logging
import re
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token
MAX_INPUT_LENGTH = 500  # Maximum length for user input

# Recipe-related keywords for intent detection
RECIPE_KEYWORDS = [
    'recipe', 'how to make', 'how to cook', 'instructions', 'directions',
    'ingredients', 'steps', 'method', 'preparation', 'cooking'
]

# Common dish names for better intent detection
DISH_NAMES = [
    'pancake', 'pancakes', 'brownie', 'brownies', 'cake', 'cookies', 'bread',
    'pasta', 'pizza', 'soup', 'salad', 'stew', 'curry', 'stir fry', 'roast',
    'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise'
]

def generate_recipe(prompt: str) -> str:
    """
    Placeholder function for local LLM integration.
    Replace this with your actual local LLM API call.
    
    Args:
        prompt (str): The prompt to send to the LLM
        
    Returns:
        str: The LLM-generated response
    """
    # TODO: Replace with actual local LLM integration
    # Example implementation:
    # import requests
    # response = requests.post('http://localhost:8000/generate', json={'prompt': prompt})
    # return response.json()['response']
    
    # Placeholder response for testing
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
    
    # Check if it looks like a list of ingredients (contains common ingredients)
    ingredient_patterns = [
        r'\b(tomato|tomatoes|chicken|beef|pork|fish|rice|pasta|onion|garlic|cheese|egg|eggs|milk|flour|sugar|salt|pepper|oil|butter)\b',
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
        return f"""You are a friendly cooking assistant. Suggest a simple recipe or meal idea using these ingredients: {query}. Include substitutions or quick tips if possible. Keep the response casual and easy to follow."""
    else:  # specific_recipe
        return f"""You are a helpful cooking assistant. Provide a clear, easy-to-follow recipe for: {query}. Include ingredients, measurements, and simple instructions. Keep it casual and concise."""

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