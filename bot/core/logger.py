"""
Logging configuration for Recipe Genie Discord Bot.
Provides structured logging with file rotation and proper formatting.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup comprehensive logging for the bot.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("RecipeGenieBot")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Error file handler
    if log_file:
        error_log_file = str(Path(log_file).with_suffix('.error.log'))
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    # Suppress discord.py debug logs unless in debug mode
    if log_level.upper() != "DEBUG":
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized with level: {log_level}")
    return logger


class BotLogger:
    """
    Enhanced logger wrapper with additional functionality for the bot.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.command_stats = {}
        self.error_stats = {}
    
    def log_command(self, command_name: str, user_id: int, guild_id: Optional[int] = None) -> None:
        """Log command usage with statistics."""
        self.logger.info(f"Command '{command_name}' used by user {user_id} in guild {guild_id}")
        
        # Update statistics
        if command_name not in self.command_stats:
            self.command_stats[command_name] = 0
        self.command_stats[command_name] += 1
    
    def log_error(self, error: Exception, context: str = "", user_id: Optional[int] = None) -> None:
        """Log errors with context and user information."""
        error_type = type(error).__name__
        self.logger.error(
            f"Error in {context}: {error_type}: {str(error)} "
            f"(User: {user_id if user_id else 'Unknown'})",
            exc_info=True
        )
        
        # Update error statistics
        if error_type not in self.error_stats:
            self.error_stats[error_type] = 0
        self.error_stats[error_type] += 1
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance metrics."""
        self.logger.info(f"Performance: {operation} took {duration:.3f}s {kwargs}")
    
    def log_security(self, event: str, user_id: Optional[int] = None, **kwargs) -> None:
        """Log security-related events."""
        self.logger.warning(f"Security: {event} (User: {user_id if user_id else 'Unknown'}) {kwargs}")
    
    def get_stats(self) -> dict:
        """Get logging statistics."""
        return {
            "command_stats": self.command_stats.copy(),
            "error_stats": self.error_stats.copy()
        }