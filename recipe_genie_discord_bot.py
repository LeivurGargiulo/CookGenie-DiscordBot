#!/usr/bin/env python3
"""
Recipe Genie - A Discord bot that provides recipe suggestions using a local LLM
Supports both English and Spanish localization
Converted from Telegram bot to Discord using discord.py
"""

import asyncio
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
import discord
from discord.ext import commands, tasks
from langdetect import detect, LangDetectException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
COMMAND_PREFIX = "!"
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

# Bot statistics
bot_stats = {
    "start_time": datetime.now(),
    "total_commands": 0,
    "total_messages": 0,
    "errors": [],
    "last_error": None
}

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
    'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise', 'lasagna',
    'spaghetti', 'burger', 'sandwich', 'taco', 'burrito', 'sushi', 'ramen',
    'noodles', 'rice', 'quinoa', 'oatmeal', 'cereal', 'smoothie', 'juice'
]

# Common dish names for better intent detection (Spanish)
DISH_NAMES_ES = [
    'panqueque', 'panqueques', 'brownie', 'brownies', 'pastel', 'galletas', 'pan',
    'pasta', 'pizza', 'sopa', 'ensalada', 'estofado', 'curry', 'salteado', 'asado',
    'parrilla', 'horneado', 'frito', 'hervido', 'vapor', 'salteado', 'braseado', 'lasaña',
    'espagueti', 'hamburguesa', 'sándwich', 'taco', 'burrito', 'sushi', 'ramen',
    'fideos', 'arroz', 'quinua', 'avena', 'cereal', 'batido', 'jugo'
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

def create_welcome_embed() -> discord.Embed:
    """Create a welcome embed message."""
    embed = discord.Embed(
        title="🍳 Welcome to Recipe Genie! 🧙‍♂️",
        description="I'm your AI cooking assistant that can help you with recipes using a local LLM.",
        color=0x00ff00
    )
    
    embed.add_field(
        name="📝 Ingredient-based recipes:",
        value="Send me a list of ingredients like:\n• tomato, chicken, rice\n• eggs, milk, flour\n• beef, onion, potatoes",
        inline=False
    )
    
    embed.add_field(
        name="🍽️ Specific recipe requests:",
        value="Ask for specific dishes like:\n• pancake recipe\n• how to make brownies\n• chicken curry recipe",
        inline=False
    )
    
    embed.add_field(
        name="Commands:",
        value="`!start` - Show this welcome message\n`!help` - Show help information\n`!debug` - Show bot status",
        inline=False
    )
    
    embed.add_field(
        name="🍳 ¡Bienvenido a Recipe Genie! 🧙‍♂️",
        value="¡Soy tu asistente de cocina con IA que puede ayudarte con recetas usando un LLM local!",
        inline=False
    )
    
    embed.add_field(
        name="📝 Recetas basadas en ingredientes:",
        value="Envíame una lista de ingredientes como:\n• tomate, pollo, arroz\n• huevos, leche, harina\n• res, cebolla, papas",
        inline=False
    )
    
    embed.add_field(
        name="🍽️ Solicitudes de recetas específicas:",
        value="Pide platos específicos como:\n• receta de panqueques\n• cómo hacer brownies\n• receta de curry de pollo",
        inline=False
    )
    
    embed.set_footer(text="Let's start cooking! 🎉 | ¡Empecemos a cocinar! 🎉")
    
    return embed

def create_help_embed() -> discord.Embed:
    """Create a help embed message."""
    embed = discord.Embed(
        title="🍳 Recipe Genie Help 🧙‍♂️",
        description="Here's how to use me effectively!",
        color=0x0099ff
    )
    
    embed.add_field(
        name="Usage Examples:",
        value="**Ingredient-based:**\n• tomato, chicken, rice\n• eggs, milk, flour, sugar\n• beef, onion, garlic, potatoes\n\n**Specific recipes:**\n• pancake recipe\n• how to make chocolate cake\n• chicken stir fry recipe",
        inline=False
    )
    
    embed.add_field(
        name="Tips:",
        value="• Keep your ingredient lists simple\n• Be specific with recipe requests\n• I'll suggest substitutions when possible",
        inline=False
    )
    
    embed.add_field(
        name="Ejemplos de Uso:",
        value="**Basado en ingredientes:**\n• tomate, pollo, arroz\n• huevos, leche, harina, azúcar\n• res, cebolla, ajo, papas\n\n**Recetas específicas:**\n• receta de panqueques\n• cómo hacer pastel de chocolate\n• receta de salteado de pollo",
        inline=False
    )
    
    embed.add_field(
        name="Consejos:",
        value="• Mantén tus listas de ingredientes simples\n• Sé específico con las solicitudes de recetas\n• Sugeriré sustituciones cuando sea posible",
        inline=False
    )
    
    embed.set_footer(text="Need help? Just send me ingredients or ask for a recipe! | ¿Necesitas ayuda? ¡Solo envíame ingredientes o pide una receta!")
    
    return embed

def create_debug_embed() -> discord.Embed:
    """Create a debug embed with bot statistics."""
    uptime = datetime.now() - bot_stats["start_time"]
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    
    embed = discord.Embed(
        title="🔧 Recipe Genie Debug Info",
        description="Bot status and statistics",
        color=0xff9900
    )
    
    embed.add_field(
        name="📊 Statistics",
        value=f"**Uptime:** {uptime_str}\n**Total Commands:** {bot_stats['total_commands']}\n**Total Messages:** {bot_stats['total_messages']}\n**Errors:** {len(bot_stats['errors'])}",
        inline=False
    )
    
    embed.add_field(
        name="🤖 Bot Info",
        value=f"**Latency:** {round(bot.latency * 1000)}ms\n**Guilds:** {len(bot.guilds)}\n**Users:** {len(bot.users)}",
        inline=False
    )
    
    if bot_stats['last_error']:
        embed.add_field(
            name="⚠️ Last Error",
            value=f"```{bot_stats['last_error'][:1000]}...```" if len(bot_stats['last_error']) > 1000 else f"```{bot_stats['last_error']}```",
            inline=False
        )
    
    embed.set_footer(text=f"Recipe Genie v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return embed

# Background task for periodic maintenance
@tasks.loop(hours=1)
async def background_maintenance():
    """Background task for periodic maintenance."""
    try:
        logger.info("Running background maintenance...")
        
        # Clean up old error logs (keep only last 10)
        if len(bot_stats['errors']) > 10:
            bot_stats['errors'] = bot_stats['errors'][-10:]
        
        # Log current statistics
        logger.info(f"Bot stats - Commands: {bot_stats['total_commands']}, Messages: {bot_stats['total_messages']}, Errors: {len(bot_stats['errors'])}")
        
    except Exception as e:
        logger.error(f"Error in background maintenance: {str(e)}")

@background_maintenance.before_loop
async def before_background_maintenance():
    """Wait until bot is ready before starting background tasks."""
    await bot.wait_until_ready()

# Bot events
@bot.event
async def on_ready():
    """Called when the bot is ready."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Start background tasks
    background_maintenance.start()
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!help for recipes"))

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    bot_stats['total_commands'] += 1
    bot_stats['errors'].append(f"{datetime.now()}: {str(error)}")
    bot_stats['last_error'] = str(error)
    
    logger.error(f"Command error: {str(error)}")
    
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
        return
    
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to execute this command!")
        return
    
    # Generic error message
    embed = discord.Embed(
        title="❌ Error",
        description="An error occurred while processing your command. Please try again!",
        color=0xff0000
    )
    await ctx.send(embed=embed)

# Bot commands
@bot.command(name='start')
async def start_command(ctx):
    """Handle the !start command with bilingual support."""
    bot_stats['total_commands'] += 1
    logger.info(f"User {ctx.author.id} used start command")
    
    embed = create_welcome_embed()
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Handle the !help command with bilingual support."""
    bot_stats['total_commands'] += 1
    logger.info(f"User {ctx.author.id} used help command")
    
    embed = create_help_embed()
    await ctx.send(embed=embed)

@bot.command(name='debug')
async def debug_command(ctx):
    """Handle the !debug command to show bot status."""
    bot_stats['total_commands'] += 1
    logger.info(f"User {ctx.author.id} used debug command")
    
    embed = create_debug_embed()
    await ctx.send(embed=embed)

# Message handling
@bot.event
async def on_message(message):
    """Handle incoming messages and generate recipe responses."""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Only process non-command messages
    if message.content.startswith(COMMAND_PREFIX):
        return
    
    bot_stats['total_messages'] += 1
    user_message = message.content.strip()
    user_id = message.author.id
    
    # Log the incoming message
    logger.info(f"User {user_id} sent: {user_message}")
    
    # Check input length
    if len(user_message) > MAX_INPUT_LENGTH:
        embed = discord.Embed(
            title="❌ Message Too Long",
            description=f"Your message is too long! Please keep it under {MAX_INPUT_LENGTH} characters.\n\n¡Tu mensaje es muy largo! Por favor manténlo bajo {MAX_INPUT_LENGTH} caracteres.",
            color=0xff0000
        )
        await message.reply(embed=embed)
        return
    
    # Skip empty messages
    if not user_message:
        embed = discord.Embed(
            title="📝 Send Ingredients or Recipe Request",
            description="Please send me some ingredients or ask for a recipe!\n\n¡Por favor envíame algunos ingredientes o pide una receta!",
            color=0x0099ff
        )
        await message.reply(embed=embed)
        return
    
    try:
        # Show typing indicator
        async with message.channel.typing():
            # Detect language
            language = detect_language(user_message)
            logger.info(f"Detected language: {language} for user {user_id}")
            
            # Detect user intent
            intent, cleaned_query = detect_intent(user_message, language)
            logger.info(f"Detected intent: {intent} for query: {cleaned_query}")
            
            # Build the prompt
            prompt = build_prompt(intent, cleaned_query, language)
            
            # Generate recipe response
            response = generate_recipe(prompt, language)
            
            # Create embed for response
            embed = discord.Embed(
                title="🍳 Recipe Genie Response",
                description=response,
                color=0x00ff00
            )
            embed.set_footer(text=f"Requested by {message.author.display_name}")
            
            # Send the response
            await message.reply(embed=embed)
            
            # Log the response
            logger.info(f"Generated response for user {user_id}: {response[:100]}...")
            
    except Exception as e:
        bot_stats['errors'].append(f"{datetime.now()}: {str(e)}")
        bot_stats['last_error'] = str(e)
        logger.error(f"Error processing message from user {user_id}: {str(e)}")
        
        embed = discord.Embed(
            title="😔 Error",
            description="Sorry, I encountered an error while generating your recipe. Please try again!\n\nLo siento, encontré un error al generar tu receta. ¡Por favor inténtalo de nuevo!",
            color=0xff0000
        )
        await message.reply(embed=embed)

async def main():
    """Main function to run the bot."""
    logger.info("Starting Recipe Genie Discord bot...")
    
    # Validate token
    if DISCORD_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.error("Please set your Discord bot token in the DISCORD_TOKEN environment variable!")
        return
    
    try:
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to login: Invalid token!")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())