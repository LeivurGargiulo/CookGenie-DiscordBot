# Recipe Genie Discord Bot

A production-ready Discord bot that generates delicious recipes using AI/LLM technology. Built with modern Python practices, comprehensive error handling, and performance optimizations.

## 🚀 Features

### Core Functionality
- **AI-Powered Recipe Generation**: Generate recipes from ingredients or dish names
- **Multi-Language Support**: English and Spanish support with automatic language detection
- **Quick Recipe Mode**: Create recipes from available ingredients
- **Recipe Translation**: Translate recipes between English and Spanish

### Technical Features
- **Async Architecture**: Efficient non-blocking operations
- **Rate Limiting**: Per-user and per-guild rate limiting to prevent abuse
- **Caching System**: In-memory and Redis caching for improved performance
- **Database Integration**: SQLite and PostgreSQL support with connection pooling
- **Comprehensive Logging**: Structured logging with file rotation
- **Error Handling**: User-friendly error messages with detailed logging
- **Security**: Input sanitization and permission-based access control
- **Monitoring**: Built-in statistics and health monitoring

## 📋 Requirements

- Python 3.8+
- Discord Bot Token
- LLM Provider (Local LMStudio or OpenRouter)

### Optional Dependencies
- Redis (for enhanced caching)
- PostgreSQL (for production database)
- psutil (for system monitoring)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the bot directory:
   ```env
   # Required
   DISCORD_TOKEN=your_discord_bot_token_here
   
   # Bot Configuration
   COMMAND_PREFIX=!
   MAX_INPUT_LENGTH=500
   LOG_LEVEL=INFO
   
   # LLM Configuration (Choose one)
   # For Local LLM (LMStudio)
   LLM_PROVIDER=local
   LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
   LLM_MODEL=your_model_name_here
   LLM_API_KEY=your_api_key_here
   
   # For OpenRouter
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3-haiku
   
   # Database Configuration
   DATABASE_URL=sqlite:///bot_data.db
   # For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/dbname
   
   # Cache Configuration (Optional)
   REDIS_URL=redis://localhost:6379
   CACHE_TTL=3600
   CACHE_MAX_SIZE=1000
   
   # Rate Limiting
   RATE_LIMIT_COMMANDS_PER_MINUTE=10
   RATE_LIMIT_MESSAGES_PER_MINUTE=30
   RATE_LIMIT_BURST_LIMIT=5
   
   # Security
   ADMIN_USERS=123456789,987654321
   ALLOWED_GUILDS=123456789,987654321
   
   # Performance
   MAX_CONCURRENT_REQUESTS=10
   REQUEST_TIMEOUT=30
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 🎮 Commands

### Recipe Commands
- `!recipe <query>` - Generate a recipe from ingredients or dish name
- `!quick <ingredients>` - Create a quick recipe from available ingredients
- `!translate <language> <recipe>` - Translate a recipe to another language

### Utility Commands
- `!help [command]` - Show help information
- `!ping` - Check bot latency and status
- `!stats` - Show bot statistics
- `!userstats [user]` - Show user statistics
- `!serverinfo` - Show server information
- `!invite` - Get bot invite link
- `!support` - Show support information

### Admin Commands (Admin users only)
- `!admin stats` - Detailed bot statistics
- `!admin cache [info|clear|cleanup]` - Cache management
- `!admin rate [user_id]` - Rate limit information
- `!admin reload` - Reload configuration
- `!admin topusers [limit]` - Show top users
- `!admin resetrate <user_id>` - Reset user rate limits
- `!admin health` - System health check

## 🔧 Configuration

### Environment Variables

#### Required
- `DISCORD_TOKEN`: Your Discord bot token

#### Bot Configuration
- `COMMAND_PREFIX`: Bot command prefix (default: !)
- `MAX_INPUT_LENGTH`: Maximum input length (default: 500)
- `LOG_LEVEL`: Logging level (default: INFO)

#### LLM Configuration
- `LLM_PROVIDER`: Provider type (local/openrouter)
- `LLM_ENDPOINT`: API endpoint for local LLM
- `LLM_MODEL`: Model name
- `LLM_API_KEY`: API key (if required)
- `LLM_TIMEOUT`: Request timeout in seconds
- `LLM_MAX_TOKENS`: Maximum tokens for responses
- `LLM_TEMPERATURE`: Response creativity (0.0-2.0)

#### Database Configuration
- `DATABASE_URL`: Database connection string
- `DB_POOL_SIZE`: Connection pool size
- `DB_MAX_OVERFLOW`: Maximum overflow connections
- `DB_POOL_TIMEOUT`: Pool timeout in seconds

#### Cache Configuration
- `REDIS_URL`: Redis connection URL (optional)
- `CACHE_TTL`: Cache time-to-live in seconds
- `CACHE_MAX_SIZE`: Maximum cache entries

#### Rate Limiting
- `RATE_LIMIT_COMMANDS_PER_MINUTE`: Commands per minute limit
- `RATE_LIMIT_MESSAGES_PER_MINUTE`: Messages per minute limit
- `RATE_LIMIT_BURST_LIMIT`: Burst limit

#### Security
- `ADMIN_USERS`: Comma-separated list of admin user IDs
- `ALLOWED_GUILDS`: Comma-separated list of allowed guild IDs (empty = all)

## 🏗️ Architecture

### Core Components

#### Main Bot (`main.py`)
- Bot initialization and lifecycle management
- Event handling and command processing
- Statistics tracking

#### Configuration (`core/config.py`)
- Environment variable management
- Configuration validation
- Type-safe configuration access

#### Logging (`core/logger.py`)
- Structured logging with rotation
- Multiple log levels and handlers
- Performance and error tracking

#### Rate Limiting (`core/rate_limiter.py`)
- Sliding window rate limiting
- Per-user and per-guild limits
- Automatic cleanup

#### Caching (`core/cache.py`)
- In-memory and Redis caching
- TTL-based expiration
- Cache statistics

#### Database (`core/database.py`)
- SQLite and PostgreSQL support
- Connection pooling
- Async operations

#### LLM Provider (`core/llm_provider.py`)
- Multiple LLM backend support
- Request caching
- Error handling and retries

### Cogs

#### Recipe Cog (`cogs/recipe_cog.py`)
- Recipe generation commands
- Language detection
- Intent recognition

#### Utility Cog (`cogs/utility_cog.py`)
- Help and information commands
- Statistics and monitoring
- User and server information

#### Admin Cog (`cogs/admin_cog.py`)
- Administrative commands
- System monitoring
- Cache and rate limit management

## 🔒 Security Features

- **Input Sanitization**: All user input is sanitized to prevent injection attacks
- **Rate Limiting**: Prevents abuse and spam
- **Permission-Based Access**: Admin commands require specific user IDs
- **Guild Restrictions**: Optional guild whitelisting
- **Secure Configuration**: Environment variables for sensitive data
- **Error Handling**: Comprehensive error handling without exposing sensitive information

## 📊 Monitoring and Statistics

### Built-in Statistics
- Command usage tracking
- Recipe generation statistics
- Cache performance metrics
- Rate limit monitoring
- Error tracking and reporting

### Health Monitoring
- Database connection health
- Cache system status
- LLM provider status
- Memory usage monitoring
- Response time tracking

## 🚀 Performance Optimizations

### Caching
- Recipe response caching
- Language detection caching
- Database query caching
- Multi-level caching (memory + Redis)

### Async Operations
- Non-blocking I/O operations
- Concurrent request handling
- Efficient database operations
- Background cleanup tasks

### Rate Limiting
- Sliding window algorithm
- Per-user and per-guild limits
- Automatic cleanup of old entries
- Configurable limits

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check if the bot token is correct
2. Verify bot permissions in Discord
3. Check log files for errors
4. Ensure the bot is online

#### LLM Not Working
1. Verify LLM provider configuration
2. Check API keys and endpoints
3. Test LLM connectivity
4. Review LLM provider logs

#### Database Errors
1. Check database connection string
2. Verify database permissions
3. Ensure database is running
4. Check database logs

#### Rate Limiting Issues
1. Check rate limit configuration
2. Monitor user activity
3. Adjust limits if needed
4. Use admin commands to reset limits

### Log Files
- Main logs: `logs/bot.log`
- Error logs: `logs/bot.error.log`
- Log rotation: 10MB files, 5 backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the `!help` command in Discord
2. Review the troubleshooting section
3. Check the logs for error details
4. Contact the bot administrator

## 🔄 Updates

To update the bot:
1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt`
3. Restart the bot
4. Check the changelog for breaking changes

---

**Recipe Genie Bot** - Making cooking easier with AI! 🍳✨