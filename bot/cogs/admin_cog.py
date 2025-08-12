"""
Admin Cog for Recipe Genie Discord Bot.
Provides administrative commands for bot management and monitoring.
"""

import logging
import asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class AdminCog(commands.Cog):
    """
    Cog for administrative commands and bot management.
    
    Features:
    - Detailed bot statistics
    - Cache management
    - Rate limit monitoring
    - Configuration management
    - System health monitoring
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        """Check if user has admin permissions."""
        return self.bot.config.is_admin_user(ctx.author.id)
    
    @commands.group(name="admin", invoke_without_command=True)
    async def admin_group(self, ctx: commands.Context) -> None:
        """Admin command group."""
        await ctx.send_help(ctx.command)
    
    @admin_group.command(name="stats")
    async def admin_stats_command(self, ctx: commands.Context) -> None:
        """Show detailed bot statistics for administrators."""
        embed = discord.Embed(
            title="📊 Detailed Bot Statistics",
            description="Comprehensive statistics for administrators",
            color=0xff6b6b,
            timestamp=discord.utils.utcnow()
        )
        
        # System stats
        if self.bot.stats["start_time"]:
            uptime = datetime.utcnow() - self.bot.stats["start_time"]
            uptime_str = str(uptime).split('.')[0]
        else:
            uptime_str = "Unknown"
        
        embed.add_field(
            name="🖥️ System",
            value=f"""
            **Uptime:** {uptime_str}
            **Servers:** {len(self.bot.guilds)}
            **Users:** {len(self.bot.users)}
            **Latency:** {round(self.bot.latency * 1000)}ms
            **Memory Usage:** {self._get_memory_usage()}
            """,
            inline=False
        )
        
        # Command stats
        embed.add_field(
            name="📝 Commands",
            value=f"""
            **Total Commands:** {self.bot.stats['total_commands']}
            **Total Messages:** {self.bot.stats['total_messages']}
            **Errors:** {len(self.bot.stats['errors'])}
            **Last Error:** {self.bot.stats.get('last_error', 'None')}
            """,
            inline=True
        )
        
        # Recipe stats
        recipe_cog = self.bot.get_cog("RecipeCog")
        if recipe_cog:
            recipe_stats = recipe_cog.get_stats()
            llm_stats = recipe_stats.get('llm_stats', {})
            
            embed.add_field(
                name="🍳 Recipes",
                value=f"""
                **Generated:** {recipe_stats['recipes_generated']}
                **Language Detections:** {recipe_stats['language_detections']}
                **Cache Hits:** {recipe_stats['cache_hits']}
                **LLM Requests:** {llm_stats.get('total_requests', 0)}
                **LLM Success Rate:** {llm_stats.get('success_rate', 0)}%
                """,
                inline=True
            )
        
        # Cache stats
        cache_stats = self.bot.cache.get_stats()
        embed.add_field(
            name="💾 Cache",
            value=f"""
            **Hits:** {cache_stats['hits']}
            **Misses:** {cache_stats['misses']}
            **Hit Rate:** {cache_stats['hit_rate']}%
            **Size:** {cache_stats['size']}/{cache_stats['max_size']}
            **Redis:** {'Enabled' if cache_stats['redis_enabled'] else 'Disabled'}
            """,
            inline=True
        )
        
        embed.set_footer(text="Admin Statistics | Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @admin_group.command(name="cache")
    async def admin_cache_command(self, ctx: commands.Context, action: str = "info") -> None:
        """
        Manage bot cache.
        
        Usage:
            !admin cache info - Show cache information
            !admin cache clear - Clear all cache
            !admin cache cleanup - Clean up expired entries
        """
        if action == "info":
            await self._show_cache_info(ctx)
        elif action == "clear":
            await self._clear_cache(ctx)
        elif action == "cleanup":
            await self._cleanup_cache(ctx)
        else:
            await ctx.send("❌ Invalid action. Use: `info`, `clear`, or `cleanup`")
    
    async def _show_cache_info(self, ctx: commands.Context) -> None:
        """Show detailed cache information."""
        cache_stats = self.bot.cache.get_stats()
        
        embed = discord.Embed(
            title="💾 Cache Information",
            color=0x4ecdc4,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Performance",
            value=f"""
            **Hits:** {cache_stats['hits']}
            **Misses:** {cache_stats['misses']}
            **Hit Rate:** {cache_stats['hit_rate']}%
            **Sets:** {cache_stats['sets']}
            **Deletes:** {cache_stats['deletes']}
            """,
            inline=False
        )
        
        embed.add_field(
            name="Storage",
            value=f"""
            **Current Size:** {cache_stats['size']}
            **Max Size:** {cache_stats['max_size']}
            **Usage:** {cache_stats['size'] / cache_stats['max_size'] * 100:.1f}%
            **Redis:** {'✅ Enabled' if cache_stats['redis_enabled'] else '❌ Disabled'}
            """,
            inline=True
        )
        
        embed.set_footer(text="Cache Information | Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    async def _clear_cache(self, ctx: commands.Context) -> None:
        """Clear all cache."""
        try:
            await self.bot.cache.clear()
            await ctx.send("✅ Cache cleared successfully!")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            await ctx.send("❌ Failed to clear cache.")
    
    async def _cleanup_cache(self, ctx: commands.Context) -> None:
        """Clean up expired cache entries."""
        try:
            cleaned = await self.bot.cache.cleanup_expired()
            await ctx.send(f"✅ Cleaned up {cleaned} expired cache entries!")
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
            await ctx.send("❌ Failed to cleanup cache.")
    
    @admin_group.command(name="rate")
    async def admin_rate_command(self, ctx: commands.Context, user_id: int = None) -> None:
        """
        Show rate limit information.
        
        Usage:
            !admin rate - Show general rate limit info
            !admin rate <user_id> - Show user-specific rate limits
        """
        if user_id:
            await self._show_user_rate_limits(ctx, user_id)
        else:
            await self._show_general_rate_limits(ctx)
    
    async def _show_general_rate_limits(self, ctx: commands.Context) -> None:
        """Show general rate limit information."""
        embed = discord.Embed(
            title="⏰ Rate Limit Information",
            color=0xffa500,
            timestamp=discord.utils.utcnow()
        )
        
        # Get rate limit stats
        user_count = len(self.bot.rate_limiter.user_limits)
        guild_count = len(self.bot.rate_limiter.guild_limits)
        
        embed.add_field(
            name="Active Limits",
            value=f"""
            **Users:** {user_count}
            **Guilds:** {guild_count}
            **Window Size:** {self.bot.rate_limiter.window_size}s
            """,
            inline=False
        )
        
        embed.add_field(
            name="Default Limits",
            value=f"""
            **Commands:** {self.bot.rate_limiter.default_limits['command']}/min
            **Messages:** {self.bot.rate_limiter.default_limits['message']}/min
            **Recipes:** {self.bot.rate_limiter.default_limits['recipe']}/min
            **Help:** {self.bot.rate_limiter.default_limits['help']}/min
            **Ping:** {self.bot.rate_limiter.default_limits['ping']}/min
            """,
            inline=True
        )
        
        embed.set_footer(text="Rate Limit Information | Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    async def _show_user_rate_limits(self, ctx: commands.Context, user_id: int) -> None:
        """Show user-specific rate limits."""
        user_stats = self.bot.rate_limiter.get_user_stats(user_id)
        
        embed = discord.Embed(
            title=f"⏰ Rate Limits - User {user_id}",
            color=0xffa500,
            timestamp=discord.utils.utcnow()
        )
        
        if user_stats:
            for action, count in user_stats.items():
                limit = self.bot.rate_limiter.default_limits.get(action, 10)
                embed.add_field(
                    name=f"{action.title()}",
                    value=f"**{count}/{limit}** uses in current window",
                    inline=True
                )
        else:
            embed.add_field(
                name="No Activity",
                value="This user has no recent activity.",
                inline=False
            )
        
        embed.set_footer(text="User Rate Limits | Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    @admin_group.command(name="reload")
    async def admin_reload_command(self, ctx: commands.Context) -> None:
        """Reload bot configuration."""
        try:
            # Reload configuration
            self.bot.config = self.bot.config.__class__()
            await ctx.send("✅ Configuration reloaded successfully!")
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            await ctx.send(f"❌ Failed to reload configuration: {e}")
    
    @admin_group.command(name="topusers")
    async def admin_topusers_command(self, ctx: commands.Context, limit: int = 10) -> None:
        """
        Show top users by command usage.
        
        Usage:
            !admin topusers [limit] - Show top users (default: 10)
        """
        try:
            top_users = await self.bot.db.get_top_users(limit)
            
            embed = discord.Embed(
                title=f"🏆 Top Users (Top {len(top_users)})",
                color=0xffd700,
                timestamp=discord.utils.utcnow()
            )
            
            for i, user_stats in enumerate(top_users, 1):
                embed.add_field(
                    name=f"#{i} - User {user_stats.user_id}",
                    value=f"""
                    **Commands:** {user_stats.commands_used}
                    **Recipes:** {user_stats.recipes_requested}
                    **Last Seen:** <t:{int(user_stats.last_seen.timestamp())}:R>
                    """,
                    inline=False
                )
            
            embed.set_footer(text="Top Users | Recipe Genie Bot")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to get top users: {e}")
            await ctx.send("❌ Failed to get top users.")
    
    @admin_group.command(name="resetrate")
    async def admin_resetrate_command(self, ctx: commands.Context, user_id: int) -> None:
        """
        Reset rate limits for a specific user.
        
        Usage:
            !admin resetrate <user_id> - Reset rate limits for user
        """
        try:
            self.bot.rate_limiter.reset_user_limits(user_id)
            await ctx.send(f"✅ Rate limits reset for user {user_id}!")
        except Exception as e:
            logger.error(f"Failed to reset rate limits: {e}")
            await ctx.send("❌ Failed to reset rate limits.")
    
    @admin_group.command(name="health")
    async def admin_health_command(self, ctx: commands.Context) -> None:
        """Show system health information."""
        embed = discord.Embed(
            title="🏥 System Health",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # Database health
        try:
            # Test database connection
            await self.bot.db.get_user_stats(0)  # This should return None, not raise an error
            db_status = "✅ Healthy"
        except Exception as e:
            db_status = f"❌ Error: {str(e)[:50]}"
        
        # Cache health
        try:
            cache_stats = self.bot.cache.get_stats()
            cache_status = "✅ Healthy"
        except Exception as e:
            cache_status = f"❌ Error: {str(e)[:50]}"
        
        # LLM health
        try:
            recipe_cog = self.bot.get_cog("RecipeCog")
            if recipe_cog:
                llm_stats = recipe_cog.get_stats().get('llm_stats', {})
                success_rate = llm_stats.get('success_rate', 0)
                if success_rate > 80:
                    llm_status = f"✅ Healthy ({success_rate}% success)"
                elif success_rate > 50:
                    llm_status = f"⚠️ Warning ({success_rate}% success)"
                else:
                    llm_status = f"❌ Poor ({success_rate}% success)"
            else:
                llm_status = "❌ Not available"
        except Exception as e:
            llm_status = f"❌ Error: {str(e)[:50]}"
        
        embed.add_field(
            name="Services",
            value=f"""
            **Database:** {db_status}
            **Cache:** {cache_status}
            **LLM:** {llm_status}
            """,
            inline=False
        )
        
        # Memory and performance
        embed.add_field(
            name="Performance",
            value=f"""
            **Memory Usage:** {self._get_memory_usage()}
            **Latency:** {round(self.bot.latency * 1000)}ms
            **Uptime:** {self._get_uptime()}
            """,
            inline=True
        )
        
        embed.set_footer(text="System Health | Recipe Genie Bot")
        await ctx.send(embed=embed)
    
    def _get_memory_usage(self) -> str:
        """Get memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            return f"{memory_mb:.1f} MB"
        except ImportError:
            return "Unknown (psutil not available)"
    
    def _get_uptime(self) -> str:
        """Get bot uptime."""
        if self.bot.stats["start_time"]:
            uptime = datetime.utcnow() - self.bot.stats["start_time"]
            return str(uptime).split('.')[0]
        return "Unknown"
    
    @admin_group.error
    async def admin_group_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors in admin commands."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use admin commands.")
        else:
            await ctx.send("❌ An error occurred while processing the admin command.")
            logger.error(f"Admin command error: {error}", exc_info=True)