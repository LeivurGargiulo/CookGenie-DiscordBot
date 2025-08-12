# Recipe Genie 🍳🧙‍♂️

A Telegram bot that provides recipe suggestions using a local LLM. Recipe Genie can help you find recipes based on available ingredients or provide detailed instructions for specific dishes.

## Features

- **Ingredient-based recipe suggestions**: Send a list of ingredients and get recipe ideas
- **Specific recipe requests**: Ask for detailed recipes for specific dishes
- **Automatic intent detection**: The bot automatically detects whether you're providing ingredients or asking for a specific recipe
- **Local LLM integration**: Works with any local LLM setup
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

Edit `config.py` or set environment variables:

```python
# In config.py
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Or set environment variable
export BOT_TOKEN="your_bot_token_here"
```

### 4. Run the Bot

```bash
# Basic version
python recipe_genie_bot.py

# Enhanced version (recommended)
python recipe_genie_bot_enhanced.py
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

## Local LLM Integration

The bot includes a placeholder `generate_recipe()` function that you can customize for your local LLM setup. Here are some common integration patterns:

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

- `LLM_ENDPOINT`: URL for your local LLM API (default: "http://localhost:8000/generate")
- `LLM_TIMEOUT`: Timeout for LLM requests in seconds (default: 30)

### Intent Detection

The bot uses several lists to detect user intent:

- `RECIPE_KEYWORDS`: Words that indicate a specific recipe request
- `DISH_NAMES`: Common dish names
- `COMMON_INGREDIENTS`: Common ingredients for pattern matching

You can customize these lists in `config.py` to improve intent detection.

## File Structure

```
recipe-genie/
├── recipe_genie_bot.py          # Basic bot implementation
├── recipe_genie_bot_enhanced.py # Enhanced version with better LLM integration
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Commands

- `/start` - Welcome message and usage instructions
- `/help` - Help information and examples

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

For testing without a local LLM, the bot includes placeholder responses. You can test the bot by:

1. Setting up a Telegram bot with @BotFather
2. Running the bot with the placeholder responses
3. Sending test messages to verify functionality

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