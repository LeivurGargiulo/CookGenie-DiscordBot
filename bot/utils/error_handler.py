"""
Error handling system for Recipe Genie Discord Bot.
Provides user-friendly error messages and comprehensive logging.
"""

import logging
import traceback
from typing import Optional
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Comprehensive error handler for Discord bot commands and events.
    
    Features:
    - User-friendly error messages
    - Detailed logging for debugging
    - Rate limit handling
    - Permission error handling
    - Custom error responses
    """
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
        
        # Error message templates
        self.error_messages = {
            "CommandNotFound": "❌ Command not found. Use `!help` to see available commands.",
            "MissingRequiredArgument": "❌ Missing required argument. Check the command usage with `!help <command>`.",
            "TooManyArguments": "❌ Too many arguments provided. Check the command usage with `!help <command>`.",
            "BadArgument": "❌ Invalid argument provided. Please check your input and try again.",
            "MissingPermissions": "🔒 You don't have permission to use this command.",
            "BotMissingPermissions": "🔒 I don't have the required permissions to execute this command.",
            "NoPrivateMessage": "❌ This command can only be used in servers, not in DMs.",
            "PrivateMessageOnly": "❌ This command can only be used in DMs, not in servers.",
            "CheckFailure": "❌ You don't have permission to use this command.",
            "CommandOnCooldown": "⏰ This command is on cooldown. Please wait before trying again.",
            "MaxConcurrencyReached": "⏰ Too many instances of this command are running. Please wait.",
            "UserInputError": "❌ Invalid input provided. Please check your input and try again.",
            "ConversionError": "❌ Could not convert your input. Please check the format and try again.",
            "ExtensionError": "❌ There was an error loading a bot extension.",
            "ExtensionNotFound": "❌ The requested extension was not found.",
            "ExtensionAlreadyLoaded": "❌ The extension is already loaded.",
            "ExtensionFailed": "❌ The extension failed to load.",
            "ExtensionNotLoaded": "❌ The extension is not loaded.",
            "NoEntryPointError": "❌ The extension does not have a setup function.",
            "default": "❌ An unexpected error occurred. Please try again later."
        }
    
    def setup(self, bot: commands.Bot) -> None:
        """Setup error handling for the bot."""
        bot.add_listener(self.on_command_error, "on_command_error")
        bot.add_listener(self.on_error, "on_error")
        self.logger.info("Error handler setup completed")
    
    async def handle_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """
        Handle command errors with appropriate responses.
        
        Args:
            ctx: Command context
            error: The error that occurred
        """
        # Log the error with context
        self._log_error(error, ctx)
        
        # Get appropriate error message
        error_message = self._get_error_message(error)
        
        # Send error response
        await self._send_error_response(ctx, error_message, error)
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors."""
        await self.handle_command_error(ctx, error)
    
    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """Handle general errors."""
        error = traceback.format_exc()
        self.logger.error(f"Error in {event_method}: {error}")
    
    def _log_error(self, error: Exception, ctx: Optional[commands.Context] = None) -> None:
        """
        Log error with context information.
        
        Args:
            error: The error that occurred
            ctx: Optional command context
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Build log message
        log_parts = [f"Error: {error_type}: {error_msg}"]
        
        if ctx:
            log_parts.extend([
                f"User: {ctx.author} ({ctx.author.id})",
                f"Guild: {ctx.guild.name if ctx.guild else 'DM'} ({ctx.guild.id if ctx.guild else 'N/A'})",
                f"Channel: {ctx.channel.name if hasattr(ctx.channel, 'name') else 'DM'} ({ctx.channel.id})",
                f"Command: {ctx.command.name if ctx.command else 'Unknown'}",
                f"Message: {ctx.message.content}"
            ])
        
        # Log with appropriate level
        if isinstance(error, (commands.CommandNotFound, commands.CommandOnCooldown)):
            self.logger.warning(" | ".join(log_parts))
        else:
            self.logger.error(" | ".join(log_parts), exc_info=True)
    
    def _get_error_message(self, error: commands.CommandError) -> str:
        """
        Get user-friendly error message for the error.
        
        Args:
            error: The error that occurred
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        
        # Check for specific error messages
        if error_type in self.error_messages:
            return self.error_messages[error_type]
        
        # Handle specific error types with custom messages
        if isinstance(error, commands.CommandOnCooldown):
            return f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f} seconds."
        
        if isinstance(error, commands.MissingRequiredArgument):
            return f"❌ Missing required argument: `{error.param.name}`. Use `!help {error.command.name}` for usage."
        
        if isinstance(error, commands.BadArgument):
            return f"❌ Invalid argument: {str(error)}"
        
        if isinstance(error, commands.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            return f"🔒 You need the following permissions: {missing_perms}"
        
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            return f"🔒 I need the following permissions: {missing_perms}"
        
        # Return default message
        return self.error_messages["default"]
    
    async def _send_error_response(self, ctx: commands.Context, message: str, error: Exception) -> None:
        """
        Send error response to the user.
        
        Args:
            ctx: Command context
            message: Error message to send
            error: The original error
        """
        try:
            # Create error embed
            embed = self._create_error_embed(message, error)
            
            # Send the error message
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            # Bot doesn't have permission to send messages
            self.logger.error(f"Cannot send error message in channel {ctx.channel.id}: Forbidden")
        except discord.HTTPException as e:
            # Discord API error
            self.logger.error(f"Failed to send error message: {e}")
        except Exception as e:
            # Unexpected error while sending error message
            self.logger.error(f"Error while sending error message: {e}")
    
    def _create_error_embed(self, message: str, error: Exception) -> discord.Embed:
        """
        Create an error embed for the user.
        
        Args:
            message: Error message
            error: The original error
            
        Returns:
            Discord embed with error information
        """
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=0xff0000,  # Red color for errors
            timestamp=discord.utils.utcnow()
        )
        
        # Add error type for debugging (only in debug mode)
        if self.logger.level <= logging.DEBUG:
            embed.add_field(
                name="Error Type",
                value=f"`{type(error).__name__}`",
                inline=True
            )
        
        # Add footer with support information
        embed.set_footer(text="If this error persists, contact an administrator")
        
        return embed
    
    async def handle_rate_limit_error(self, ctx: commands.Context, retry_after: float) -> None:
        """
        Handle rate limit errors specifically.
        
        Args:
            ctx: Command context
            retry_after: Time to wait before retrying
        """
        message = f"⏰ Rate limit exceeded. Please wait {retry_after:.1f} seconds before trying again."
        
        embed = discord.Embed(
            title="⏰ Rate Limited",
            description=message,
            color=0xffa500,  # Orange color for warnings
            timestamp=discord.utils.utcnow()
        )
        
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send rate limit message: {e}")
    
    async def handle_permission_error(self, ctx: commands.Context, missing_permissions: list) -> None:
        """
        Handle permission errors specifically.
        
        Args:
            ctx: Command context
            missing_permissions: List of missing permissions
        """
        perms_str = ", ".join(missing_permissions)
        message = f"🔒 Missing permissions: {perms_str}"
        
        embed = discord.Embed(
            title="🔒 Permission Denied",
            description=message,
            color=0xffa500,  # Orange color for warnings
            timestamp=discord.utils.utcnow()
        )
        
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send permission error message: {e}")
    
    def log_security_event(self, event: str, user_id: int, guild_id: Optional[int] = None, **kwargs) -> None:
        """
        Log security-related events.
        
        Args:
            event: Security event description
            user_id: User ID involved
            guild_id: Guild ID involved (optional)
            **kwargs: Additional context
        """
        log_parts = [
            f"Security Event: {event}",
            f"User: {user_id}",
            f"Guild: {guild_id if guild_id else 'N/A'}"
        ]
        
        for key, value in kwargs.items():
            log_parts.append(f"{key}: {value}")
        
        self.logger.warning(" | ".join(log_parts))