"""
Command handlers for Recipe Genie Discord bot
"""

import logging
import discord
from discord.ext import commands
from .embeds import create_welcome_embed, create_help_embed, create_debug_embed
from .utils import detect_language, detect_intent, build_prompt, validate_input_length, sanitize_input
from .llm_provider import generate_recipe
from .config import MAX_INPUT_LENGTH

logger = logging.getLogger(__name__)

class RecipeGenieCommands(commands.Cog):
    """Cog containing all Recipe Genie bot commands."""
    
    def __init__(self, bot: commands.Bot, bot_stats: dict):
        self.bot = bot
        self.bot_stats = bot_stats
    
    @commands.command(name='start')
    async def start_command(self, ctx: commands.Context):
        """Handle the !start command with bilingual support."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used start command")
        
        embed = create_welcome_embed()
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Handle the !help command with bilingual support."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used help command")
        
        embed = create_help_embed()
        await ctx.send(embed=embed)
    
    @commands.command(name='debug')
    async def debug_command(self, ctx: commands.Context):
        """Handle the !debug command to show bot status."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used debug command")
        
        embed = create_debug_embed(
            self.bot_stats,
            self.bot.latency,
            len(self.bot.guilds),
            len(self.bot.users)
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping_command(self, ctx: commands.Context):
        """Handle the !ping command to check bot latency."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used ping command")
        
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    async def stats_command(self, ctx: commands.Context):
        """Handle the !stats command to show user statistics."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used stats command")
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            description="Current bot usage statistics",
            color=0x0099ff
        )
        
        embed.add_field(
            name="Commands Used",
            value=f"Total: {self.bot_stats['total_commands']}",
            inline=True
        )
        
        embed.add_field(
            name="Messages Processed",
            value=f"Total: {self.bot_stats['total_messages']}",
            inline=True
        )
        
        embed.add_field(
            name="Errors",
            value=f"Total: {len(self.bot_stats['errors'])}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='recipe')
    async def recipe_command(self, ctx: commands.Context, *, query: str):
        """Handle the !recipe command for explicit recipe requests."""
        self.bot_stats['total_commands'] += 1
        logger.info(f"User {ctx.author.id} used recipe command: {query}")
        
        # Validate input
        if not validate_input_length(query, MAX_INPUT_LENGTH):
            embed = discord.Embed(
                title="❌ Message Too Long",
                description=f"Your query is too long! Please keep it under {MAX_INPUT_LENGTH} characters.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Sanitize input
        query = sanitize_input(query)
        
        try:
            # Show typing indicator
            async with ctx.typing():
                # Detect language
                language = detect_language(query)
                logger.info(f"Detected language: {language} for user {ctx.author.id}")
                
                # Detect user intent
                intent, cleaned_query = detect_intent(query, language)
                logger.info(f"Detected intent: {intent} for query: {cleaned_query}")
                
                # Build the prompt
                prompt = build_prompt(intent, cleaned_query, language)
                
                # Generate recipe response
                response = await generate_recipe(prompt, language)
                
                # Create embed for response
                embed = discord.Embed(
                    title="🍳 Recipe Genie Response",
                    description=response,
                    color=0x00ff00
                )
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                
                # Send the response
                await ctx.send(embed=embed)
                
                # Log the response
                logger.info(f"Generated response for user {ctx.author.id}: {response[:100]}...")
                
        except Exception as e:
            self.bot_stats['errors'].append(f"{ctx.author.id}: {str(e)}")
            self.bot_stats['last_error'] = str(e)
            logger.error(f"Error processing recipe command from user {ctx.author.id}: {str(e)}")
            
            embed = discord.Embed(
                title="😔 Error",
                description="Sorry, I encountered an error while generating your recipe. Please try again!",
                color=0xff0000
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot, bot_stats: dict):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(RecipeGenieCommands(bot, bot_stats))