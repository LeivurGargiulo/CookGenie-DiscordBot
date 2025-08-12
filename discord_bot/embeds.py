"""
Embed creation utilities for Recipe Genie Discord bot
"""

import discord
from datetime import datetime
from typing import Dict, Any

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

def create_debug_embed(bot_stats: Dict[str, Any], bot_latency: float, guild_count: int, user_count: int) -> discord.Embed:
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
        value=f"**Latency:** {round(bot_latency * 1000)}ms\n**Guilds:** {guild_count}\n**Users:** {user_count}",
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

def create_recipe_embed(response: str, author_name: str) -> discord.Embed:
    """Create an embed for recipe responses."""
    embed = discord.Embed(
        title="🍳 Recipe Genie Response",
        description=response,
        color=0x00ff00
    )
    embed.set_footer(text=f"Requested by {author_name}")
    
    return embed

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xff0000
    )
    
    return embed

def create_info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x0099ff
    )
    
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x00ff00
    )
    
    return embed