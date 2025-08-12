#!/usr/bin/env python3
"""
Recipe Genie Discord Bot - Main Entry Point
A production-ready Discord bot for recipe suggestions with LLM integration.

Features:
- Efficient async event handling
- Comprehensive error handling and logging
- Rate limiting and caching
- Security best practices
- Performance optimizations
- Modular architecture
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

from bot.core.config import Config
from bot.core.logger import setup_logging
from bot.core.database import DatabaseManager
from bot.core.cache import CacheManager
from bot.core.rate_limiter import RateLimiter
from bot.cogs.recipe_cog import RecipeCog
from bot.cogs.admin_cog import AdminCog
from bot.cogs.utility_cog import UtilityCog
from bot.utils.error_handler import ErrorHandler


class RecipeGenieBot(commands.Bot):
    """
    Main bot class with enhanced features for production use.
    
    Features:
    - Automatic error handling and logging
    - Rate limiting per user and guild
    - Caching for improved performance
    - Database integration for statistics
    - Health monitoring
    """
    
    def __init__(self):
        # Load configuration
        self.config = Config()
        
        # Setup logging
        self.logger = setup_logging(self.config.log_level)
        
        # Initialize intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        # Initialize bot with enhanced settings
        super().__init__(
            command_prefix=self.config.command_prefix,
            intents=intents,
            help_command=None,  # Custom help command
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        # Initialize core components
        self.db = DatabaseManager(self.config)
        self.cache = CacheManager()
        self.rate_limiter = RateLimiter()
        self.error_handler = ErrorHandler(self.logger)
        
        # Bot statistics
        self.stats = {
            "start_time": None,
            "total_commands": 0,
            "total_messages": 0,
            "errors": [],
            "last_error": None,
            "uptime": 0
        }
        
        self.logger.info("Bot instance initialized")
    
    async def setup_hook(self) -> None:
        """Setup hook called when the bot is starting up."""
        self.logger.info("Setting up bot components...")
        
        # Initialize database
        await self.db.initialize()
        
        # Load cogs
        await self.load_cogs()
        
        # Setup error handling
        self.error_handler.setup(self)
        
        self.logger.info("Bot setup completed")
    
    async def load_cogs(self) -> None:
        """Load all bot cogs."""
        try:
            await self.add_cog(RecipeCog(self))
            await self.add_cog(AdminCog(self))
            await self.add_cog(UtilityCog(self))
            self.logger.info("All cogs loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load cogs: {e}")
            raise
    
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        self.stats["start_time"] = discord.utils.utcnow()
        
        self.logger.info(f"Bot is ready! Logged in as {self.user}")
        self.logger.info(f"Bot ID: {self.user.id}")
        self.logger.info(f"Connected to {len(self.guilds)} guilds")
        self.logger.info(f"Serving {len(self.users)} users")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{self.config.command_prefix}help for recipes"
        )
        await self.change_presence(activity=activity)
    
    async def on_command(self, ctx: commands.Context) -> None:
        """Called when a command is invoked."""
        self.stats["total_commands"] += 1
        
        # Log command usage
        self.logger.info(
            f"Command '{ctx.command}' used by {ctx.author} "
            f"in {ctx.guild.name if ctx.guild else 'DM'}"
        )
        
        # Check rate limits
        if not await self.rate_limiter.check_rate_limit(ctx.author.id, "command"):
            await ctx.send("⚠️ You're using commands too quickly. Please wait a moment.")
            return
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors."""
        await self.error_handler.handle_command_error(ctx, error)
    
    async def on_message(self, message: discord.Message) -> None:
        """Called when a message is received."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        self.stats["total_messages"] += 1
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self) -> None:
        """Cleanup when the bot is shutting down."""
        self.logger.info("Shutting down bot...")
        
        # Close database connections
        await self.db.close()
        
        # Close cache connections
        await self.cache.close()
        
        await super().close()
        self.logger.info("Bot shutdown complete")


async def main() -> None:
    """Main entry point for the bot."""
    # Ensure we're in the correct directory
    bot_dir = Path(__file__).parent
    if bot_dir.exists():
        sys.path.insert(0, str(bot_dir.parent))
    
    # Create and run bot
    bot = RecipeGenieBot()
    
    try:
        async with bot:
            await bot.start(bot.config.discord_token)
    except KeyboardInterrupt:
        bot.logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        bot.logger.error(f"Fatal error: {e}")
        raise
    finally:
        await bot.close()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())