#!/usr/bin/env python3
"""
Recipe Genie - A Modular Discord bot that provides recipe suggestions using a local LLM
Supports both English and Spanish localization
Converted from Telegram bot to Discord using discord.py with modular architecture
"""

import asyncio
import logging
import os
from datetime import datetime
import discord
from discord.ext import commands

# Import our modules
from discord_bot.config import DISCORD_TOKEN, COMMAND_PREFIX, LOG_LEVEL
from discord_bot.commands import setup as setup_commands
from discord_bot.events import setup as setup_events

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper())
)
logger = logging.getLogger(__name__)

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

async def setup_bot():
    """Setup the bot with all cogs and extensions."""
    logger.info("Setting up Recipe Genie Discord bot...")
    
    # Setup commands and events cogs
    await setup_commands(bot, bot_stats)
    await setup_events(bot, bot_stats)
    
    logger.info("Bot setup completed successfully!")

async def main():
    """Main function to run the bot."""
    logger.info("Starting Recipe Genie Discord bot (Modular Version)...")
    
    # Validate token
    if DISCORD_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.error("Please set your Discord bot token in the DISCORD_TOKEN environment variable!")
        return
    
    try:
        # Setup the bot
        await setup_bot()
        
        # Start the bot
        await bot.start(DISCORD_TOKEN)
        
    except discord.LoginFailure:
        logger.error("Failed to login: Invalid token!")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())