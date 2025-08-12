"""
Utility Cog for Recipe Genie Discord Bot.
Provides helpful utility commands and information.
"""

import logging
import time
from datetime import datetime, timedelta
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class UtilityCog(commands.Cog):
    """
    Cog for utility commands and helpful functions.
    
    Features:
    - Help command
    - Bot statistics
    - Ping command
    - User statistics
    - Server information
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, command_name: str = None) -> None:
        """
        Show help information for commands.
        
        Usage:
            !help [command_name]
            
        Examples:
            !help
            !help recipe
            !help quick
        """
        if command_name:
            await self._show_command_help(ctx, command_name)
        else:
            await self._show_general_help(ctx)
    
    async def _show_general_help(self, ctx: commands.Context) -> None:
        """Show general help information."""
        embed = discord.Embed(
            title="🍽️ Recipe Genie Bot - Help",
            description="A Discord bot that generates delicious recipes using AI!",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Recipe commands
        embed.add_field(
            name="🍳 Recipe Commands",
            value="""
            `!recipe <query>` - Generate a recipe
            `!quick <ingredients>` - Quick recipe from ingredients
            `!translate <lang> <recipe>` - Translate recipe
            """,
            inline=False
        )
        
        # Utility commands
        embed.add_field(
            name="🔧 Utility Commands",
            value="""
            `!help [command]` - Show this help
            `!ping` - Check bot latency
            `!stats` - Show bot statistics
            `!userstats` - Show your statistics
            `!serverinfo` - Show server information
            """,
            inline=False
        )
        
        # Admin commands (if user is admin)
        if self.bot.config.is_admin_user(ctx.author.id):
            embed.add_field(
                name="⚙️ Admin Commands",
                value="""
                `!admin stats` - Detailed bot statistics
                `!admin cache` - Cache information
                `!admin rate` - Rate limit information
                `!admin reload` - Reload configuration
                """,
                inline=False
            )
        
        # Examples
        embed.add_field(
            name="📝 Examples",
            value="""
            `!recipe chocolate cake`
            `!quick chicken, rice, vegetables`
            `!translate es chocolate cake recipe`
            """,
            inline=False
        )
        
        embed.set_footer(text="Recipe Genie Bot | Use !help <command> for detailed help")
        await ctx.send(embed=embed)
    
    async def _show_command_help(self, ctx: commands.Context, command_name: str) -> None:
        """Show detailed help for a specific command."""
        command = self.bot.get_command(command_name)
        
        if not command:
            await ctx.send(f"❌ Command `{command_name}` not found. Use `!help` to see all commands.")
            return
        
        embed = discord.Embed(
            title=f"Help: {command.name}",
            description=command.help or "No description available.",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Usage
        if command.usage:
            embed.add_field(
                name="Usage",
                value=f"`{self.bot.config.command_prefix}{command.name} {command.usage}`",
                inline=False
            )
        
        # Aliases
        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join([f"`{alias}`" for alias in command.aliases]),
                inline=True
            )
        
        # Cooldown
        if hasattr(command, '_buckets'):
            cooldown = command._buckets._cooldown
            if cooldown:
                embed.add_field(
                    name="Cooldown",
                    value=f"{cooldown.rate} uses per {cooldown.per} seconds",
                    inline=True
                )
        
        embed.set_footer(text="Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @commands.command(name="ping")
    async def ping_command(self, ctx: commands.Context) -> None:
        """Check bot latency and status."""
        start_time = time.time()
        
        # Send initial message
        message = await ctx.send("🏓 Pinging...")
        
        # Calculate latency
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        api_latency = round(self.bot.latency * 1000)
        
        # Create embed
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00 if api_latency < 100 else 0xffa500 if api_latency < 200 else 0xff0000,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Bot Latency",
            value=f"`{latency}ms`",
            inline=True
        )
        
        embed.add_field(
            name="API Latency",
            value=f"`{api_latency}ms`",
            inline=True
        )
        
        # Status indicator
        if api_latency < 100:
            status = "🟢 Excellent"
        elif api_latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"
        
        embed.add_field(
            name="Status",
            value=status,
            inline=True
        )
        
        await message.edit(content=None, embed=embed)
    
    @commands.command(name="stats")
    async def stats_command(self, ctx: commands.Context) -> None:
        """Show bot statistics."""
        # Calculate uptime
        if self.bot.stats["start_time"]:
            uptime = datetime.utcnow() - self.bot.stats["start_time"]
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        else:
            uptime_str = "Unknown"
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # General stats
        embed.add_field(
            name="General",
            value=f"""
            **Servers:** {len(self.bot.guilds)}
            **Users:** {len(self.bot.users)}
            **Uptime:** {uptime_str}
            **Latency:** {round(self.bot.latency * 1000)}ms
            """,
            inline=False
        )
        
        # Command stats
        embed.add_field(
            name="Commands",
            value=f"""
            **Total Commands:** {self.bot.stats['total_commands']}
            **Total Messages:** {self.bot.stats['total_messages']}
            **Errors:** {len(self.bot.stats['errors'])}
            """,
            inline=True
        )
        
        # Recipe stats
        recipe_cog = self.bot.get_cog("RecipeCog")
        if recipe_cog:
            recipe_stats = recipe_cog.get_stats()
            embed.add_field(
                name="Recipes",
                value=f"""
                **Generated:** {recipe_stats['recipes_generated']}
                **Language Detections:** {recipe_stats['language_detections']}
                **Cache Hits:** {recipe_stats['cache_hits']}
                """,
                inline=True
            )
        
        embed.set_footer(text="Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @commands.command(name="userstats")
    async def userstats_command(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """Show user statistics."""
        target_user = user or ctx.author
        
        # Get user stats from database
        user_stats = await self.bot.db.get_user_stats(target_user.id)
        
        embed = discord.Embed(
            title=f"📊 User Statistics - {target_user.display_name}",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        if user_stats:
            embed.add_field(
                name="Commands Used",
                value=f"`{user_stats.commands_used}`",
                inline=True
            )
            
            embed.add_field(
                name="Recipes Requested",
                value=f"`{user_stats.recipes_requested}`",
                inline=True
            )
            
            embed.add_field(
                name="Last Seen",
                value=f"<t:{int(user_stats.last_seen.timestamp())}:R>",
                inline=True
            )
            
            embed.add_field(
                name="Member Since",
                value=f"<t:{int(user_stats.created_at.timestamp())}:D>",
                inline=True
            )
        else:
            embed.add_field(
                name="No Data",
                value="This user hasn't used the bot yet.",
                inline=False
            )
        
        embed.set_footer(text="Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @commands.command(name="serverinfo")
    async def serverinfo_command(self, ctx: commands.Context) -> None:
        """Show server information."""
        guild = ctx.guild
        
        if not guild:
            await ctx.send("❌ This command can only be used in servers.")
            return
        
        embed = discord.Embed(
            title=f"📊 Server Information - {guild.name}",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Server details
        embed.add_field(
            name="General",
            value=f"""
            **Owner:** {guild.owner.mention}
            **Created:** <t:{int(guild.created_at.timestamp())}:D>
            **Members:** {guild.member_count}
            **Channels:** {len(guild.channels)}
            **Roles:** {len(guild.roles)}
            """,
            inline=False
        )
        
        # Bot permissions
        bot_permissions = []
        if guild.me.guild_permissions.send_messages:
            bot_permissions.append("Send Messages")
        if guild.me.guild_permissions.embed_links:
            bot_permissions.append("Embed Links")
        if guild.me.guild_permissions.attach_files:
            bot_permissions.append("Attach Files")
        if guild.me.guild_permissions.read_message_history:
            bot_permissions.append("Read History")
        
        embed.add_field(
            name="Bot Permissions",
            value=", ".join(bot_permissions) if bot_permissions else "None",
            inline=True
        )
        
        # Server features
        if guild.features:
            embed.add_field(
                name="Features",
                value=", ".join(guild.features),
                inline=True
            )
        
        # Server icon
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text="Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @commands.command(name="invite")
    async def invite_command(self, ctx: commands.Context) -> None:
        """Get the bot invite link."""
        embed = discord.Embed(
            title="🔗 Invite Recipe Genie Bot",
            description="Click the link below to invite me to your server!",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Generate invite link
        invite_link = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(
                send_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                use_external_emojis=True
            )
        )
        
        embed.add_field(
            name="Invite Link",
            value=f"[Click here to invite]({invite_link})",
            inline=False
        )
        
        embed.add_field(
            name="Required Permissions",
            value="""
            • Send Messages
            • Embed Links
            • Attach Files
            • Read Message History
            • Use External Emojis
            """,
            inline=False
        )
        
        embed.set_footer(text="Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @commands.command(name="support")
    async def support_command(self, ctx: commands.Context) -> None:
        """Show support information."""
        embed = discord.Embed(
            title="🆘 Support Information",
            description="Need help with Recipe Genie Bot? Here's how to get support:",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Commands",
            value="Use `!help` to see all available commands",
            inline=False
        )
        
        embed.add_field(
            name="Command Help",
            value="Use `!help <command>` for detailed help on a specific command",
            inline=False
        )
        
        embed.add_field(
            name="Bot Status",
            value="Use `!ping` to check if the bot is working properly",
            inline=False
        )
        
        embed.add_field(
            name="Your Statistics",
            value="Use `!userstats` to see your usage statistics",
            inline=False
        )
        
        embed.add_field(
            name="Server Information",
            value="Use `!serverinfo` to see server details and bot permissions",
            inline=False
        )
        
        embed.set_footer(text="Recipe Genie Bot | For additional support, contact the bot administrator")
        await ctx.send(embed=embed)
    
    @help_command.error
    async def help_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in help command."""
        await ctx.send("❌ An error occurred while showing help. Please try again.")
        logger.error(f"Help command error: {error}", exc_info=True)
    
    @ping_command.error
    async def ping_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in ping command."""
        await ctx.send("❌ An error occurred while checking ping. Please try again.")
        logger.error(f"Ping command error: {error}", exc_info=True)
    
    @stats_command.error
    async def stats_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in stats command."""
        await ctx.send("❌ An error occurred while getting statistics. Please try again.")
        logger.error(f"Stats command error: {error}", exc_info=True)