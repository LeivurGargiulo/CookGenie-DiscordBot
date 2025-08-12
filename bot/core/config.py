"""
Configuration management for Recipe Genie Discord Bot.
Handles environment variables, validation, and default settings.
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str
    endpoint: str
    api_key: str
    model: str
    timeout: int
    max_tokens: int
    temperature: float


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int
    max_overflow: int
    pool_timeout: int


@dataclass
class CacheConfig:
    """Cache configuration."""
    redis_url: Optional[str]
    ttl: int
    max_size: int


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    commands_per_minute: int
    messages_per_minute: int
    burst_limit: int


class Config:
    """
    Central configuration class for the bot.
    
    Loads configuration from environment variables with sensible defaults.
    Validates critical settings and provides type-safe access to all config values.
    """
    
    def __init__(self):
        # Load environment variables
        self._load_env()
        
        # Bot configuration
        self.discord_token = self._get_required_env("DISCORD_TOKEN")
        self.command_prefix = self._get_env("COMMAND_PREFIX", "!")
        self.max_input_length = self._get_int_env("MAX_INPUT_LENGTH", 500)
        self.log_level = self._get_env("LOG_LEVEL", "INFO")
        
        # LLM configuration
        self.llm = self._setup_llm_config()
        
        # Database configuration
        self.database = self._setup_database_config()
        
        # Cache configuration
        self.cache = self._setup_cache_config()
        
        # Rate limiting configuration
        self.rate_limit = self._setup_rate_limit_config()
        
        # Security configuration
        self.allowed_guilds = self._get_list_env("ALLOWED_GUILDS", [])
        self.admin_users = self._get_list_env("ADMIN_USERS", [])
        
        # Performance configuration
        self.max_concurrent_requests = self._get_int_env("MAX_CONCURRENT_REQUESTS", 10)
        self.request_timeout = self._get_int_env("REQUEST_TIMEOUT", 30)
        
        # Recipe keywords and patterns
        self.recipe_keywords_en = self._get_recipe_keywords_en()
        self.recipe_keywords_es = self._get_recipe_keywords_es()
        self.dish_names_en = self._get_dish_names_en()
        self.dish_names_es = self._get_dish_names_es()
        
        # Validate configuration
        self._validate_config()
    
    def _load_env(self) -> None:
        """Load environment variables from .env file if it exists."""
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
        else:
            load_dotenv()  # Try to load from default location
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env(self, key: str, default: str) -> str:
        """Get an environment variable with a default value."""
        return os.getenv(key, default)
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get an integer environment variable with a default value."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logging.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float) -> float:
        """Get a float environment variable with a default value."""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            logging.warning(f"Invalid float value for {key}, using default: {default}")
            return default
    
    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get a list environment variable with a default value."""
        value = os.getenv(key)
        if not value:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def _setup_llm_config(self) -> LLMConfig:
        """Setup LLM configuration."""
        provider = self._get_env("LLM_PROVIDER", "local")
        
        if provider == "openrouter":
            return LLMConfig(
                provider=provider,
                endpoint=self._get_env("OPENROUTER_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions"),
                api_key=self._get_required_env("OPENROUTER_API_KEY"),
                model=self._get_env("OPENROUTER_MODEL", "anthropic/claude-3-haiku"),
                timeout=self._get_int_env("OPENROUTER_TIMEOUT", 30),
                max_tokens=self._get_int_env("OPENROUTER_MAX_TOKENS", 500),
                temperature=self._get_float_env("OPENROUTER_TEMPERATURE", 0.7)
            )
        else:  # local
            return LLMConfig(
                provider=provider,
                endpoint=self._get_env("LLM_ENDPOINT", "http://localhost:1234/v1/chat/completions"),
                api_key=self._get_env("LLM_API_KEY", ""),
                model=self._get_env("LLM_MODEL", "your_model_name_here"),
                timeout=self._get_int_env("LLM_TIMEOUT", 30),
                max_tokens=self._get_int_env("LLM_MAX_TOKENS", 500),
                temperature=self._get_float_env("LLM_TEMPERATURE", 0.7)
            )
    
    def _setup_database_config(self) -> DatabaseConfig:
        """Setup database configuration."""
        return DatabaseConfig(
            url=self._get_env("DATABASE_URL", "sqlite:///bot_data.db"),
            pool_size=self._get_int_env("DB_POOL_SIZE", 5),
            max_overflow=self._get_int_env("DB_MAX_OVERFLOW", 10),
            pool_timeout=self._get_int_env("DB_POOL_TIMEOUT", 30)
        )
    
    def _setup_cache_config(self) -> CacheConfig:
        """Setup cache configuration."""
        return CacheConfig(
            redis_url=os.getenv("REDIS_URL"),
            ttl=self._get_int_env("CACHE_TTL", 3600),  # 1 hour
            max_size=self._get_int_env("CACHE_MAX_SIZE", 1000)
        )
    
    def _setup_rate_limit_config(self) -> RateLimitConfig:
        """Setup rate limiting configuration."""
        return RateLimitConfig(
            commands_per_minute=self._get_int_env("RATE_LIMIT_COMMANDS_PER_MINUTE", 10),
            messages_per_minute=self._get_int_env("RATE_LIMIT_MESSAGES_PER_MINUTE", 30),
            burst_limit=self._get_int_env("RATE_LIMIT_BURST_LIMIT", 5)
        )
    
    def _get_recipe_keywords_en(self) -> List[str]:
        """Get English recipe keywords."""
        return [
            'recipe', 'how to make', 'how to cook', 'instructions', 'directions',
            'ingredients', 'steps', 'method', 'preparation', 'cooking'
        ]
    
    def _get_recipe_keywords_es(self) -> List[str]:
        """Get Spanish recipe keywords."""
        return [
            'receta', 'cómo hacer', 'cómo cocinar', 'instrucciones', 'direcciones',
            'ingredientes', 'pasos', 'método', 'preparación', 'cocinar', 'cocción'
        ]
    
    def _get_dish_names_en(self) -> List[str]:
        """Get English dish names."""
        return [
            'pancake', 'pancakes', 'brownie', 'brownies', 'cake', 'cookies', 'bread',
            'pasta', 'pizza', 'soup', 'salad', 'stew', 'curry', 'stir fry', 'roast',
            'grill', 'bake', 'fry', 'boil', 'steam', 'sauté', 'braise', 'lasagna',
            'spaghetti', 'burger', 'sandwich', 'taco', 'burrito', 'sushi', 'ramen',
            'noodles', 'rice', 'quinoa', 'oatmeal', 'cereal', 'smoothie', 'juice'
        ]
    
    def _get_dish_names_es(self) -> List[str]:
        """Get Spanish dish names."""
        return [
            'panqueque', 'panqueques', 'brownie', 'brownies', 'pastel', 'galletas', 'pan',
            'pasta', 'pizza', 'sopa', 'ensalada', 'estofado', 'curry', 'salteado', 'asado',
            'parrilla', 'horneado', 'frito', 'hervido', 'vapor', 'salteado', 'braseado', 'lasaña',
            'espagueti', 'hamburguesa', 'sándwich', 'taco', 'burrito', 'sushi', 'ramen',
            'fideos', 'arroz', 'quinua', 'avena', 'cereal', 'batido', 'jugo'
        ]
    
    def _validate_config(self) -> None:
        """Validate critical configuration settings."""
        if not self.discord_token or self.discord_token == "YOUR_DISCORD_BOT_TOKEN_HERE":
            raise ValueError("DISCORD_TOKEN must be set to a valid bot token")
        
        if self.max_input_length <= 0:
            raise ValueError("MAX_INPUT_LENGTH must be positive")
        
        if self.llm.timeout <= 0:
            raise ValueError("LLM timeout must be positive")
        
        if self.llm.max_tokens <= 0:
            raise ValueError("LLM max_tokens must be positive")
        
        if not (0 <= self.llm.temperature <= 2):
            raise ValueError("LLM temperature must be between 0 and 2")
        
        logging.info("Configuration validation passed")
    
    def is_admin_user(self, user_id: int) -> bool:
        """Check if a user is an admin."""
        return str(user_id) in self.admin_users
    
    def is_allowed_guild(self, guild_id: int) -> bool:
        """Check if a guild is allowed."""
        if not self.allowed_guilds:  # Empty list means all guilds allowed
            return True
        return str(guild_id) in self.allowed_guilds