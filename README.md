# Recipe Genie 🍳🧙‍♂️

A Telegram bot that provides recipe suggestions using a local LLM. Recipe Genie can help you find recipes based on available ingredients or provide detailed instructions for specific dishes.

## Features

- **Ingredient-based recipe suggestions**: Send a list of ingredients and get recipe ideas
- **Specific recipe requests**: Ask for detailed recipes for specific dishes
- **Automatic intent detection**: The bot automatically detects whether you're providing ingredients or asking for a specific recipe
- **🌍 Spanish localization**: Full support for Spanish language with automatic detection
- **Multiple LLM providers**: Support for both local LLM (LMStudio) and OpenRouter
- **Async processing**: Handles multiple users efficiently
- **Error handling**: Graceful error handling and user feedback
- **Logging**: Comprehensive logging for debugging and monitoring

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))
- A local LLM setup (optional for testing)

### 2. Installation

```bash
# Clone or download the project files
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy the example environment file and configure your settings:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

Required settings in `.env`:
- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `LLM_PROVIDER`: Choose "local" for local LLM or "openrouter" for OpenRouter

For Local LLM (LMStudio):
- `LLM_ENDPOINT`: LMStudio API endpoint (default: http://localhost:1234/v1/chat/completions)
- `LLM_MODEL`: Your model name in LMStudio

For OpenRouter:
- `OPENROUTER_API_KEY`: Your OpenRouter API key from https://openrouter.ai/keys
- `OPENROUTER_MODEL`: Model to use (default: anthropic/claude-3-haiku)

Optional settings:
- `LLM_API_KEY`: API key if required by your local setup
- `LLM_TIMEOUT` / `OPENROUTER_TIMEOUT`: Request timeout in seconds (default: 30)
- `LLM_MAX_TOKENS` / `OPENROUTER_MAX_TOKENS`: Maximum tokens for responses (default: 500)
- `LLM_TEMPERATURE` / `OPENROUTER_TEMPERATURE`: Response creativity (default: 0.7)
- `MAX_INPUT_LENGTH`: Maximum user input length (default: 500)
- `LOG_LEVEL`: Logging level (default: INFO)

### 4. Run the Bot

```bash
# Basic version
python recipe_genie_bot.py

# Enhanced version (recommended)
python recipe_genie_bot_enhanced.py

# OpenRouter optimized version
python recipe_genie_bot_openrouter.py
```

### Quick Provider Switching

Use the provider switcher to easily change between local LLM and OpenRouter:

```bash
# Switch to OpenRouter
python switch_provider.py openrouter

# Switch to Local LLM
python switch_provider.py local

# Check current configuration
python switch_provider.py status
```

## Usage Examples

### Ingredient-based Queries

Send the bot a list of ingredients:

```
tomato, chicken, rice
```

The bot will respond with a recipe idea using those ingredients.

### Specific Recipe Requests

Ask for a specific dish:

```
pancake recipe
how to make brownies
chicken curry recipe
```

The bot will provide detailed instructions for the requested dish.

## 🌍 Spanish Localization

Recipe Genie now supports Spanish language with automatic detection! Users can interact with the bot in both English and Spanish.

### Spanish Usage Examples

**Ingredient-based queries:**
```
tomate, pollo, arroz
huevos, leche, harina, azúcar
res, cebolla, ajo, papas
```

**Specific recipe requests:**
```
receta de panqueques
cómo hacer brownies
receta de curry de pollo
```

### Features
- **Automatic language detection**: The bot detects whether messages are in English or Spanish
- **Bilingual responses**: All bot messages and recipes are provided in the detected language
- **Seamless switching**: Users can switch between languages in the same conversation
- **Bilingual keywords**: Recipe keywords, dish names, and ingredients are recognized in both languages

For detailed information about the Spanish localization features, see [README_SPANISH_LOCALIZATION.md](README_SPANISH_LOCALIZATION.md).

## LLM Provider Integration

The bot supports multiple LLM providers. Choose the one that best fits your needs:

### OpenRouter Integration (Recommended)

OpenRouter provides access to multiple AI models through a single API. This is the easiest way to get started.

#### 1. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for a free account
3. Get your API key from the [keys page](https://openrouter.ai/keys)

#### 2. Configure Environment Variables

In your `.env` file:

```bash
BOT_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku  # Popular models: anthropic/claude-3-haiku, openai/gpt-3.5-turbo, meta-llama/llama-3.1-8b-instruct
OPENROUTER_TIMEOUT=30
OPENROUTER_MAX_TOKENS=500
OPENROUTER_TEMPERATURE=0.7
```

#### 3. Test the Integration

Run the test script to verify your OpenRouter setup:

```bash
python test_llm_integration.py
```

#### Popular OpenRouter Models

- `anthropic/claude-3-haiku` - Fast, cost-effective (default)
- `openai/gpt-3.5-turbo` - Reliable and well-tested
- `meta-llama/llama-3.1-8b-instruct` - Good performance
- `google/gemini-flash-1.5` - Fast and accurate
- `anthropic/claude-3.5-sonnet` - High quality (more expensive)

You can browse all available models at [OpenRouter Models](https://openrouter.ai/models).

### Local LLM Integration (LMStudio)

The bot is configured to work with LMStudio's OpenAI-compatible API. Here's how to set it up:

#### 1. Install and Configure LMStudio

1. Download and install [LMStudio](https://lmstudio.ai/)
2. Load your preferred model in LMStudio
3. Start the local server in LMStudio (usually on port 1234)
4. Note your model name for the configuration

#### 2. Configure Environment Variables

In your `.env` file:

```bash
BOT_TOKEN=your_telegram_bot_token
LLM_PROVIDER=local
LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
LLM_MODEL=your_model_name_here
LLM_API_KEY=  # Leave empty if not required
LLM_TIMEOUT=30
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.7
```

#### 3. Test the Integration

Run the test script to verify your LMStudio setup:

```bash
python test_llm_integration.py
```

## Alternative LLM Integration

If you're using a different local LLM setup, you can customize the `generate_recipe()` function:

### Option 1: HTTP API Server

If your LLM runs as an HTTP server:

```python
def generate_recipe(prompt: str) -> str:
    response = requests.post(
        "http://localhost:8000/generate",
        json={'prompt': prompt},
        timeout=30
    )
    response.raise_for_status()
    return response.json()['response']
```

### Option 2: Direct Function Call

If you have a local LLM function:

```python
def generate_recipe(prompt: str) -> str:
    from your_llm_module import generate_text
    return generate_text(prompt)
```

### Option 3: OpenAI-compatible API

For local LLMs that use OpenAI-compatible APIs:

```python
def generate_recipe(prompt: str) -> str:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("LLM_API_KEY", "")}'
    }
    data = {
        'model': 'your-local-model',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 500,
        'temperature': 0.7
    }
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
```

## Configuration Options

### Bot Settings

- `BOT_TOKEN`: Your Telegram bot token
- `MAX_INPUT_LENGTH`: Maximum length for user input (default: 500)

### LLM Settings

- `LLM_ENDPOINT`: URL for your local LLM API (default: "http://localhost:1234/v1/chat/completions")
- `LLM_MODEL`: Model name for your local LLM
- `LLM_API_KEY`: API key if required by your setup
- `LLM_TIMEOUT`: Timeout for LLM requests in seconds (default: 30)
- `LLM_MAX_TOKENS`: Maximum tokens for responses (default: 500)
- `LLM_TEMPERATURE`: Response creativity (default: 0.7)

### Intent Detection

The bot uses several lists to detect user intent:

- `RECIPE_KEYWORDS`: Words that indicate a specific recipe request
- `DISH_NAMES`: Common dish names
- `COMMON_INGREDIENTS`: Common ingredients for pattern matching

You can customize these lists in `config.py` to improve intent detection.

## File Structure

```
recipe-genie/
├── recipe_genie_bot.py              # Basic bot implementation
├── recipe_genie_bot_enhanced.py     # Enhanced version with multi-provider support
├── recipe_genie_bot_openrouter.py   # OpenRouter optimized version
├── llm_providers.py                 # LLM provider abstraction layer
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── test_llm_integration.py          # LLM integration test script
├── switch_provider.py               # Provider switching utility
└── README.md                       # This file
```

## Commands

- `/start` - Welcome message and usage instructions
- `/help` - Help information and examples
- `/status` - Show current LLM provider status (OpenRouter version only)

## Error Handling

The bot includes comprehensive error handling:

- Input validation (length limits, empty messages)
- LLM connection errors
- General exception handling
- Graceful user feedback

## Logging

The bot logs:
- User interactions
- Intent detection results
- LLM responses
- Errors and exceptions

Logs are formatted with timestamps and include relevant context.

## Testing

### Test LLM Integration

Before running the full bot, test your LMStudio integration:

```bash
python test_llm_integration.py
```

This will test the connection to your local LLM and verify the API format.

### Test Bot Functionality

1. Set up a Telegram bot with @BotFather
2. Configure your `.env` file
3. Start LMStudio and load your model
4. Run the bot: `python recipe_genie_bot_enhanced.py`
5. Send test messages to verify functionality

## Customization

### Adding New Dish Types

Edit the `DISH_NAMES` list in `config.py`:

```python
DISH_NAMES = [
    # ... existing dishes ...
    'your_new_dish',
    'another_dish'
]
```

### Adding New Ingredients

Edit the `COMMON_INGREDIENTS` list in `config.py`:

```python
COMMON_INGREDIENTS = [
    # ... existing ingredients ...
    'your_new_ingredient',
    'another_ingredient'
]
```

### Customizing Prompts

Modify the `build_prompt()` function to customize how prompts are sent to your LLM.

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check your bot token and internet connection
2. **LLM errors**: Verify your local LLM is running and accessible
3. **Intent detection issues**: Review and customize the keyword lists in `config.py`

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Support

For support, please open an issue in the project repository or contact the maintainers.