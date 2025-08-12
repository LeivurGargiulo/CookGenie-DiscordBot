# Recipe Genie Discord Bot

A Discord bot that provides recipe suggestions using a local LLM, converted from the original Telegram bot. Supports both English and Spanish localization with full async/await functionality.

## Features

- 🍳 **Recipe Generation**: Get recipe suggestions based on ingredients or specific dish requests
- 🌍 **Bilingual Support**: Automatic language detection for English and Spanish
- 🤖 **LLM Integration**: Support for both local LLM (LMStudio) and OpenRouter
- 📊 **Bot Statistics**: Track usage, errors, and performance metrics
- 🔧 **Debug Commands**: Monitor bot health and status
- ⚡ **Async Performance**: Fully asynchronous for optimal performance
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🎨 **Rich Embeds**: Beautiful Discord embeds for all responses

## Commands

| Command | Description |
|---------|-------------|
| `!start` | Show welcome message and bot introduction |
| `!help` | Display help information and usage examples |
| `!debug` | Show bot statistics, uptime, and error logs |
| `!ping` | Check bot latency |
| `!stats` | Display usage statistics |
| `!recipe <query>` | Explicitly request a recipe |

## Message Handling

The bot automatically processes messages that don't start with the command prefix:

- **Ingredient-based requests**: Send a list of ingredients like "tomato, chicken, rice"
- **Specific recipe requests**: Ask for specific dishes like "pancake recipe"
- **Automatic language detection**: Supports both English and Spanish

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- (Optional) Local LLM server (LMStudio) or OpenRouter API key

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd recipe-genie-discord

# Install dependencies
pip install -r requirements_discord.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!
MAX_INPUT_LENGTH=500
LOG_LEVEL=INFO

# LLM Configuration (Local)
LLM_PROVIDER=local
LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
LLM_API_KEY=
LLM_MODEL=your_model_name_here
LLM_TIMEOUT=30
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.7

# LLM Configuration (OpenRouter)
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=your_openrouter_api_key_here
# OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
# OPENROUTER_MODEL=anthropic/claude-3-haiku
# OPENROUTER_TIMEOUT=30
# OPENROUTER_MAX_TOKENS=500
# OPENROUTER_TEMPERATURE=0.7
```

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable the following intents:
   - Message Content Intent
   - Server Members Intent
6. Add the bot to your server with appropriate permissions

### 5. Running the Bot

#### Option 1: Single File Version
```bash
python recipe_genie_discord_bot.py
```

#### Option 2: Modular Version (Recommended)
```bash
python recipe_genie_discord_modular.py
```

## Architecture

The modular version is organized into the following structure:

```
discord_bot/
├── __init__.py          # Package initialization
├── config.py            # Configuration settings
├── utils.py             # Utility functions (language detection, etc.)
├── llm_provider.py      # LLM integration (local and OpenRouter)
├── embeds.py            # Discord embed creation utilities
├── commands.py          # Command handlers
└── events.py            # Event handlers
```

## Key Conversion Features

### From Telegram to Discord

1. **Command Handling**: Converted `/start`, `/help`, `/debug` to `!start`, `!help`, `!debug`
2. **Message Processing**: Adapted message handlers to Discord's event system
3. **Error Handling**: Implemented Discord-specific error handling with embeds
4. **Async Operations**: Full async/await implementation for optimal performance
5. **UI Adaptation**: Converted Telegram message formatting to Discord embeds
6. **Background Tasks**: Implemented Discord.py background tasks for maintenance

### Enhanced Features

- **Rich Embeds**: Beautiful, formatted responses with colors and fields
- **Typing Indicators**: Shows when the bot is processing requests
- **Guild Management**: Handles bot joining/leaving servers
- **Statistics Tracking**: Comprehensive bot usage metrics
- **Modular Design**: Clean, maintainable code structure

## Usage Examples

### Basic Recipe Requests

```
User: tomato, chicken, rice
Bot: 🍳 Quick Recipe Idea: Simple Stir-Fry...

User: pancake recipe
Bot: 🍽️ Recipe: Ingredients: 2 cups flour...

User: receta de brownies
Bot: 🍽️ Receta: Ingredientes: 2 tazas de harina...
```

### Commands

```
!start    - Welcome message and introduction
!help     - Usage examples and tips
!debug    - Bot statistics and health
!ping     - Check bot latency
!stats    - Usage statistics
!recipe chocolate cake - Explicit recipe request
```

## Error Handling

The bot includes comprehensive error handling:

- **Input Validation**: Checks message length and content
- **LLM Failures**: Graceful fallback responses when LLM is unavailable
- **Network Issues**: Timeout handling and retry logic
- **Permission Errors**: User-friendly permission error messages
- **Logging**: Detailed error logging for debugging

## Performance Features

- **Async Operations**: Non-blocking I/O for all operations
- **Background Tasks**: Periodic maintenance and cleanup
- **Connection Management**: Proper session handling for HTTP requests
- **Memory Management**: Automatic cleanup of old error logs

## Deployment

### Local Development
```bash
python recipe_genie_discord_modular.py
```

### Production Deployment
```bash
# Using systemd (Linux)
sudo systemctl enable recipe-genie-discord
sudo systemctl start recipe-genie-discord

# Using Docker
docker build -t recipe-genie-discord .
docker run -d --name recipe-genie-discord recipe-genie-discord
```

### Environment Variables for Production
```bash
export DISCORD_TOKEN="your_production_token"
export LLM_PROVIDER="openrouter"
export OPENROUTER_API_KEY="your_api_key"
export LOG_LEVEL="WARNING"
```

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if the bot has proper permissions
2. **LLM not working**: Verify your LLM endpoint or API key
3. **Language detection issues**: Ensure `langdetect` is properly installed
4. **Permission errors**: Check bot permissions in Discord server settings

### Debug Commands

Use `!debug` to check:
- Bot uptime and latency
- Total commands and messages processed
- Recent error logs
- Guild and user counts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the debug logs using `!debug`
- Review the error handling documentation

---

**Note**: This Discord bot is a complete conversion of the original Telegram bot, maintaining all functionality while adapting to Discord's API and conventions. The modular architecture makes it easy to extend and maintain.