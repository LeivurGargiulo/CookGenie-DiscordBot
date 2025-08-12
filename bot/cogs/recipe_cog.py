"""
Recipe Cog for Recipe Genie Discord Bot.
Handles all recipe-related commands and functionality.
"""

import asyncio
import logging
import time
from typing import Optional, Tuple
import discord
from discord.ext import commands
from langdetect import detect, LangDetectException

from bot.core.llm_provider import LLMProvider
from bot.utils.language_utils import detect_language, detect_intent, build_prompt, sanitize_input

logger = logging.getLogger(__name__)


class RecipeCog(commands.Cog):
    """
    Cog for handling recipe-related commands and functionality.
    
    Features:
    - Recipe generation with LLM
    - Language detection and support
    - Intent detection
    - Rate limiting
    - Caching
    - Error handling
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.llm_provider = LLMProvider(bot.config, bot.cache)
        
        # Command cooldowns
        self.recipe_cooldown = commands.CooldownMapping.from_cooldown(
            rate=3, per=60, type=commands.BucketType.user
        )
        
        # Statistics
        self.stats = {
            "recipes_generated": 0,
            "language_detections": 0,
            "cache_hits": 0
        }
    
    async def cog_load(self) -> None:
        """Called when the cog is loaded."""
        await self.llm_provider.initialize()
        logger.info("Recipe cog loaded")
    
    async def cog_unload(self) -> None:
        """Called when the cog is unloaded."""
        await self.llm_provider.close()
        logger.info("Recipe cog unloaded")
    
    @commands.command(name="recipe")
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def recipe_command(self, ctx: commands.Context, *, query: str) -> None:
        """
        Generate a recipe based on user input.
        
        Usage:
            !recipe <ingredients or dish name>
            
        Examples:
            !recipe chicken pasta
            !recipe chocolate cake
            !recipe tomatoes, onions, garlic
        """
        # Check rate limits
        if not await self.bot.rate_limiter.check_rate_limit(
            ctx.author.id, "recipe", ctx.guild.id if ctx.guild else None
        ):
            await ctx.send("⚠️ You're requesting recipes too quickly. Please wait a moment.")
            return
        
        # Validate input
        if len(query) > self.bot.config.max_input_length:
            await ctx.send(f"❌ Input too long. Please keep it under {self.bot.config.max_input_length} characters.")
            return
        
        # Sanitize input
        query = sanitize_input(query)
        
        # Send typing indicator
        async with ctx.typing():
            try:
                # Detect language
                language = detect_language(query)
                self.stats["language_detections"] += 1
                
                # Detect intent
                intent, cleaned_query = detect_intent(query, language, self.bot.config)
                
                # Build prompt
                prompt = build_prompt(cleaned_query, intent, language)
                
                # Generate recipe
                start_time = time.time()
                response = await self.llm_provider.generate_recipe(prompt, language)
                
                if response:
                    # Record statistics
                    self.stats["recipes_generated"] += 1
                    if response.cached:
                        self.stats["cache_hits"] += 1
                    
                    # Record in database
                    await self.bot.db.record_recipe_request(
                        ctx.author.id, 
                        ctx.guild.id if ctx.guild else None
                    )
                    
                    # Create and send embed
                    embed = await self._create_recipe_embed(
                        response, query, language, time.time() - start_time
                    )
                    await ctx.send(embed=embed)
                    
                else:
                    await ctx.send("❌ Sorry, I couldn't generate a recipe right now. Please try again later.")
                    
            except Exception as e:
                logger.error(f"Error in recipe command: {e}", exc_info=True)
                await ctx.send("❌ An error occurred while generating the recipe. Please try again.")
    
    @commands.command(name="quick")
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def quick_recipe_command(self, ctx: commands.Context, *, ingredients: str) -> None:
        """
        Generate a quick recipe from available ingredients.
        
        Usage:
            !quick <ingredients separated by commas>
            
        Examples:
            !quick chicken, rice, vegetables
            !quick eggs, milk, bread
        """
        # Check rate limits
        if not await self.bot.rate_limiter.check_rate_limit(
            ctx.author.id, "recipe", ctx.guild.id if ctx.guild else None
        ):
            await ctx.send("⚠️ You're requesting recipes too quickly. Please wait a moment.")
            return
        
        # Validate input
        if len(ingredients) > self.bot.config.max_input_length:
            await ctx.send(f"❌ Input too long. Please keep it under {self.bot.config.max_input_length} characters.")
            return
        
        # Sanitize input
        ingredients = sanitize_input(ingredients)
        
        # Send typing indicator
        async with ctx.typing():
            try:
                # Detect language
                language = detect_language(ingredients)
                self.stats["language_detections"] += 1
                
                # Build quick recipe prompt
                if language == "es":
                    prompt = f"Crear una receta rápida y fácil usando estos ingredientes: {ingredients}. La receta debe ser simple y rápida de preparar."
                else:
                    prompt = f"Create a quick and easy recipe using these ingredients: {ingredients}. The recipe should be simple and quick to prepare."
                
                # Generate recipe
                start_time = time.time()
                response = await self.llm_provider.generate_recipe(prompt, language)
                
                if response:
                    # Record statistics
                    self.stats["recipes_generated"] += 1
                    if response.cached:
                        self.stats["cache_hits"] += 1
                    
                    # Record in database
                    await self.bot.db.record_recipe_request(
                        ctx.author.id, 
                        ctx.guild.id if ctx.guild else None
                    )
                    
                    # Create and send embed
                    embed = await self._create_recipe_embed(
                        response, ingredients, language, time.time() - start_time, is_quick=True
                    )
                    await ctx.send(embed=embed)
                    
                else:
                    await ctx.send("❌ Sorry, I couldn't generate a quick recipe right now. Please try again later.")
                    
            except Exception as e:
                logger.error(f"Error in quick recipe command: {e}", exc_info=True)
                await ctx.send("❌ An error occurred while generating the quick recipe. Please try again.")
    
    @commands.command(name="translate")
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def translate_recipe_command(self, ctx: commands.Context, language: str, *, recipe: str) -> None:
        """
        Translate a recipe to another language.
        
        Usage:
            !translate <language> <recipe text>
            
        Examples:
            !translate es chocolate cake recipe
            !translate en receta de pastel de chocolate
        """
        # Validate language
        language = language.lower()
        if language not in ["en", "es"]:
            await ctx.send("❌ Supported languages: `en` (English) or `es` (Spanish)")
            return
        
        # Check rate limits
        if not await self.bot.rate_limiter.check_rate_limit(
            ctx.author.id, "translate", ctx.guild.id if ctx.guild else None
        ):
            await ctx.send("⚠️ You're using translation too quickly. Please wait a moment.")
            return
        
        # Validate input
        if len(recipe) > self.bot.config.max_input_length:
            await ctx.send(f"❌ Recipe text too long. Please keep it under {self.bot.config.max_input_length} characters.")
            return
        
        # Sanitize input
        recipe = sanitize_input(recipe)
        
        # Send typing indicator
        async with ctx.typing():
            try:
                # Build translation prompt
                if language == "es":
                    prompt = f"Traduce esta receta al español, manteniendo el formato y las instrucciones claras:\n\n{recipe}"
                else:
                    prompt = f"Translate this recipe to English, maintaining the format and clear instructions:\n\n{recipe}"
                
                # Generate translation
                start_time = time.time()
                response = await self.llm_provider.generate_recipe(prompt, language)
                
                if response:
                    # Create and send embed
                    embed = await self._create_translation_embed(
                        response, recipe, language, time.time() - start_time
                    )
                    await ctx.send(embed=embed)
                    
                else:
                    await ctx.send("❌ Sorry, I couldn't translate the recipe right now. Please try again later.")
                    
            except Exception as e:
                logger.error(f"Error in translate recipe command: {e}", exc_info=True)
                await ctx.send("❌ An error occurred while translating the recipe. Please try again.")
    
    async def _create_recipe_embed(self, response, query: str, language: str, 
                                 response_time: float, is_quick: bool = False) -> discord.Embed:
        """
        Create a Discord embed for recipe responses.
        
        Args:
            response: LLMResponse object
            query: Original user query
            language: Language code
            response_time: Time taken to generate response
            is_quick: Whether this is a quick recipe
            
        Returns:
            Discord embed
        """
        # Determine title and color
        if is_quick:
            title = "🍳 Quick Recipe" if language == "en" else "🍳 Receta Rápida"
            color = 0x00ff00  # Green
        else:
            title = "🍽️ Recipe" if language == "en" else "🍽️ Receta"
            color = 0x0099ff  # Blue
        
        embed = discord.Embed(
            title=title,
            description=response.content,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add fields
        embed.add_field(
            name="📝 Query" if language == "en" else "📝 Consulta",
            value=f"`{query}`",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Response Time" if language == "en" else "⚡ Tiempo de Respuesta",
            value=f"`{response_time:.2f}s`",
            inline=True
        )
        
        if response.cached:
            embed.add_field(
                name="💾 Cached" if language == "en" else "💾 En Caché",
                value="`Yes`",
                inline=True
            )
        
        embed.add_field(
            name="🤖 Model" if language == "en" else "🤖 Modelo",
            value=f"`{response.model}`",
            inline=True
        )
        
        # Add footer
        footer_text = "Recipe Genie Bot" if language == "en" else "Bot Receta Genio"
        embed.set_footer(text=footer_text)
        
        return embed
    
    async def _create_translation_embed(self, response, original: str, language: str, 
                                      response_time: float) -> discord.Embed:
        """
        Create a Discord embed for translation responses.
        
        Args:
            response: LLMResponse object
            original: Original recipe text
            language: Target language
            response_time: Time taken to generate response
            
        Returns:
            Discord embed
        """
        title = "🌐 Translation" if language == "en" else "🌐 Traducción"
        color = 0xffa500  # Orange
        
        embed = discord.Embed(
            title=title,
            description=response.content,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add fields
        embed.add_field(
            name="📝 Original" if language == "en" else "📝 Original",
            value=f"```{original[:500]}{'...' if len(original) > 500 else ''}```",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Response Time" if language == "en" else "⚡ Tiempo de Respuesta",
            value=f"`{response_time:.2f}s`",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Model" if language == "en" else "🤖 Modelo",
            value=f"`{response.model}`",
            inline=True
        )
        
        # Add footer
        footer_text = "Recipe Genie Bot" if language == "en" else "Bot Receta Genio"
        embed.set_footer(text=footer_text)
        
        return embed
    
    @recipe_command.error
    async def recipe_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in recipe command."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide a recipe query. Usage: `!recipe <ingredients or dish name>`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Please wait {error.retry_after:.1f} seconds before requesting another recipe.")
        else:
            await ctx.send("❌ An error occurred while processing the recipe command.")
            logger.error(f"Recipe command error: {error}", exc_info=True)
    
    @quick_recipe_command.error
    async def quick_recipe_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in quick recipe command."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide ingredients. Usage: `!quick <ingredients separated by commas>`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Please wait {error.retry_after:.1f} seconds before requesting another quick recipe.")
        else:
            await ctx.send("❌ An error occurred while processing the quick recipe command.")
            logger.error(f"Quick recipe command error: {error}", exc_info=True)
    
    @translate_recipe_command.error
    async def translate_recipe_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in translate recipe command."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide language and recipe. Usage: `!translate <language> <recipe text>`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Please wait {error.retry_after:.1f} seconds before translating another recipe.")
        else:
            await ctx.send("❌ An error occurred while processing the translation command.")
            logger.error(f"Translate recipe command error: {error}", exc_info=True)
    
    def get_stats(self) -> dict:
        """Get recipe cog statistics."""
        return {
            "recipes_generated": self.stats["recipes_generated"],
            "language_detections": self.stats["language_detections"],
            "cache_hits": self.stats["cache_hits"],
            "llm_stats": self.llm_provider.get_stats()
        }