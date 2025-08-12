"""
Event handlers for Recipe Genie Discord bot
"""

import logging
import discord
from discord.ext import commands, tasks
from .embeds import create_recipe_embed, create_error_embed, create_info_embed
from .utils import detect_language, detect_intent, build_prompt, validate_input_length, sanitize_input
from .llm_provider import generate_recipe
from .config import MAX_INPUT_LENGTH, COMMAND_PREFIX

logger = logging.getLogger(__name__)

class RecipeGenieEvents(commands.Cog):
    """Cog containing all Recipe Genie bot event handlers."""
    
    def __init__(self, bot: commands.Bot, bot_stats: dict):
        self.bot = bot
        self.bot_stats = bot_stats
        self.background_maintenance.start()
    
    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.background_maintenance.cancel()
    
    @tasks.loop(hours=1)
    async def background_maintenance(self):
        """Background task for periodic maintenance."""
        try:
            logger.info("Running background maintenance...")
            
            # Clean up old error logs (keep only last 10)
            if len(self.bot_stats['errors']) > 10:
                self.bot_stats['errors'] = self.bot_stats['errors'][-10:]
            
            # Log current statistics
            logger.info(f"Bot stats - Commands: {self.bot_stats['total_commands']}, Messages: {self.bot_stats['total_messages']}, Errors: {len(self.bot_stats['errors'])}")
            
        except Exception as e:
            logger.error(f"Error in background maintenance: {str(e)}")
    
    @background_maintenance.before_loop
    async def before_background_maintenance(self):
        """Wait until bot is ready before starting background tasks."""
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.bot.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.bot.guilds)} guilds')
        
        # Set bot status
        await self.bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help for recipes"))
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Global error handler for commands."""
        self.bot_stats['total_commands'] += 1
        self.bot_stats['errors'].append(f"{ctx.author.id}: {str(error)}")
        self.bot_stats['last_error'] = str(error)
        
        logger.error(f"Command error: {str(error)}")
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        if isinstance(error, commands.MissingPermissions):
            embed = create_error_embed(
                "❌ Permission Error",
                "You don't have permission to use this command!"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = create_error_embed(
                "❌ Bot Permission Error",
                "I don't have the required permissions to execute this command!"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = create_error_embed(
                "❌ Missing Argument",
                f"Missing required argument: {error.param.name}"
            )
            await ctx.send(embed=embed)
            return
        
        # Generic error message
        embed = create_error_embed(
            "❌ Error",
            "An error occurred while processing your command. Please try again!"
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle incoming messages and generate recipe responses."""
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return
        
        # Process commands first
        await self.bot.process_commands(message)
        
        # Only process non-command messages
        if message.content.startswith(COMMAND_PREFIX):
            return
        
        self.bot_stats['total_messages'] += 1
        user_message = message.content.strip()
        user_id = message.author.id
        
        # Log the incoming message
        logger.info(f"User {user_id} sent: {user_message}")
        
        # Check input length
        if not validate_input_length(user_message, MAX_INPUT_LENGTH):
            embed = create_error_embed(
                "❌ Message Too Long",
                f"Your message is too long! Please keep it under {MAX_INPUT_LENGTH} characters.\n\n¡Tu mensaje es muy largo! Por favor manténlo bajo {MAX_INPUT_LENGTH} caracteres."
            )
            await message.reply(embed=embed)
            return
        
        # Skip empty messages
        if not user_message:
            embed = create_info_embed(
                "📝 Send Ingredients or Recipe Request",
                "Please send me some ingredients or ask for a recipe!\n\n¡Por favor envíame algunos ingredientes o pide una receta!"
            )
            await message.reply(embed=embed)
            return
        
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Sanitize input
                user_message = sanitize_input(user_message)
                
                # Detect language
                language = detect_language(user_message)
                logger.info(f"Detected language: {language} for user {user_id}")
                
                # Detect user intent
                intent, cleaned_query = detect_intent(user_message, language)
                logger.info(f"Detected intent: {intent} for query: {cleaned_query}")
                
                # Build the prompt
                prompt = build_prompt(intent, cleaned_query, language)
                
                # Generate recipe response
                response = await generate_recipe(prompt, language)
                
                # Create embed for response
                embed = create_recipe_embed(response, message.author.display_name)
                
                # Send the response
                await message.reply(embed=embed)
                
                # Log the response
                logger.info(f"Generated response for user {user_id}: {response[:100]}...")
                
        except Exception as e:
            self.bot_stats['errors'].append(f"{user_id}: {str(e)}")
            self.bot_stats['last_error'] = str(e)
            logger.error(f"Error processing message from user {user_id}: {str(e)}")
            
            embed = create_error_embed(
                "😔 Error",
                "Sorry, I encountered an error while generating your recipe. Please try again!\n\nLo siento, encontré un error al generar tu receta. ¡Por favor inténtalo de nuevo!"
            )
            await message.reply(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Try to send a welcome message to the system channel
        if guild.system_channel:
            try:
                embed = create_info_embed(
                    "🍳 Recipe Genie Bot Joined!",
                    f"Thanks for adding me to **{guild.name}**!\n\n"
                    f"Use `{COMMAND_PREFIX}start` to get started, or `{COMMAND_PREFIX}help` for more information.\n\n"
                    "I can help you with recipes in both English and Spanish!"
                )
                await guild.system_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Could not send welcome message to {guild.name}: {str(e)}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

async def setup(bot: commands.Bot, bot_stats: dict):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(RecipeGenieEvents(bot, bot_stats))