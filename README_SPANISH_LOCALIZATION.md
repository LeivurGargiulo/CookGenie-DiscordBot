# Recipe Genie Bot - Spanish Localization

## Overview

The Recipe Genie Telegram bot has been updated to support Spanish localization, allowing users to interact with the bot in both English and Spanish. The bot automatically detects the language of user messages and responds accordingly.

## Features

### 🌍 Automatic Language Detection
- **Real-time detection**: The bot automatically detects whether messages are in English or Spanish
- **Seamless switching**: Users can switch between languages in the same conversation
- **Fallback handling**: If language detection fails, the bot defaults to English

### 📝 Bilingual Prompts
The bot uses different prompts based on the detected language:

#### English Prompts
- **Ingredient-based queries**: "You are a friendly cooking assistant. Suggest a simple recipe or meal idea using these ingredients: {ingredients}..."
- **Specific recipe requests**: "You are a helpful cooking assistant. Provide a clear, easy-to-follow recipe for: {dish_name}..."

#### Spanish Prompts
- **Ingredient-based queries**: "Eres un asistente de cocina amigable. Sugiere una receta o idea de comida sencilla usando estos ingredientes: {ingredients}..."
- **Specific recipe requests**: "Eres un asistente de cocina útil. Proporciona una receta clara y fácil de seguir para: {dish_name}..."

### 🍳 Bilingual Recipe Keywords
The bot recognizes recipe-related keywords in both languages:

#### English Keywords
- `recipe`, `how to make`, `how to cook`, `instructions`, `directions`, `ingredients`, `steps`, `method`, `preparation`, `cooking`

#### Spanish Keywords
- `receta`, `cómo hacer`, `cómo cocinar`, `instrucciones`, `direcciones`, `ingredientes`, `pasos`, `método`, `preparación`, `cocinar`, `cocción`

### 🍽️ Bilingual Dish Names
Common dish names are recognized in both languages:

#### English Dishes
- `pancake`, `brownie`, `cake`, `cookies`, `bread`, `pasta`, `pizza`, `soup`, `salad`, `stew`, `curry`, etc.

#### Spanish Dishes
- `panqueque`, `brownie`, `pastel`, `galletas`, `pan`, `pasta`, `pizza`, `sopa`, `ensalada`, `estofado`, `curry`, etc.

### 🥕 Bilingual Ingredient Recognition
The bot can recognize common ingredients in both languages:

#### English Ingredients
- `tomato`, `chicken`, `beef`, `rice`, `pasta`, `onion`, `garlic`, `cheese`, `egg`, `milk`, `flour`, etc.

#### Spanish Ingredients
- `tomate`, `pollo`, `res`, `arroz`, `pasta`, `cebolla`, `ajo`, `queso`, `huevo`, `leche`, `harina`, etc.

### 💬 Bilingual User Interface
All bot messages are provided in both languages:

#### Welcome Message (`/start`)
```
🍳 Welcome to Recipe Genie! 🧙‍♂️
[English instructions...]

---

🍳 ¡Bienvenido a Recipe Genie! 🧙‍♂️
[Spanish instructions...]
```

#### Help Message (`/help`)
```
🍳 Recipe Genie Help 🧙‍♂️
[English examples and tips...]

---

🍳 Ayuda de Recipe Genie 🧙‍♂️
[Spanish examples and tips...]
```

#### Error Messages
All error messages are bilingual:
```
❌ Your message is too long! Please keep it under 500 characters.
❌ ¡Tu mensaje es muy largo! Por favor manténlo bajo 500 caracteres.
```

## Technical Implementation

### Dependencies
- `langdetect>=1.0.9` - For automatic language detection
- `python-telegram-bot==20.7` - Telegram bot framework
- `requests>=2.25.0` - HTTP requests
- `python-dotenv>=0.19.0` - Environment variable management

### Language Detection Function
```python
def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: Language code ('es' for Spanish, 'en' for English, default to 'en')
    """
    try:
        lang = detect(text)
        return lang if lang in ['es', 'en'] else 'en'
    except LangDetectException:
        return 'en'
```

### Configuration Updates
The `config.py` file has been updated with bilingual constants:

```python
# Recipe-related keywords for intent detection (English)
RECIPE_KEYWORDS_EN = [...]

# Recipe-related keywords for intent detection (Spanish)
RECIPE_KEYWORDS_ES = [...]

# Common dish names for better intent detection (English)
DISH_NAMES_EN = [...]

# Common dish names for better intent detection (Spanish)
DISH_NAMES_ES = [...]

# Common ingredients for better pattern matching (English)
COMMON_INGREDIENTS_EN = [...]

# Common ingredients for better pattern matching (Spanish)
COMMON_INGREDIENTS_ES = [...]
```

## Usage Examples

### English Interactions
```
User: "tomato, chicken, rice"
Bot: [Generates recipe in English]

User: "how to make pancakes"
Bot: [Generates recipe in English]
```

### Spanish Interactions
```
User: "tomate, pollo, arroz"
Bot: [Generates recipe in Spanish]

User: "cómo hacer panqueques"
Bot: [Generates recipe in Spanish]
```

### Mixed Language Conversations
```
User: "tomato, chicken, rice"
Bot: [Generates recipe in English]

User: "cómo hacer brownies"
Bot: [Generates recipe in Spanish]

User: "eggs, milk, flour"
Bot: [Generates recipe in English]
```

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables in a `.env` file:
```env
BOT_TOKEN=your_telegram_bot_token
LLM_PROVIDER=local  # or openrouter
# ... other configuration
```

3. Run the bot:
```bash
python recipe_genie_bot.py
# or
python recipe_genie_bot_enhanced.py
# or
python recipe_genie_bot_openrouter.py
```

## Testing

Run the language detection test:
```bash
python test_language_detection.py
```

## Limitations

- **Short phrases**: Language detection may be less accurate for very short phrases (less than 3-4 words)
- **Mixed language**: If users mix English and Spanish in the same message, the bot will default to English
- **Regional variations**: The Spanish implementation uses standard Spanish; regional variations may not be fully supported

## Future Enhancements

- Support for additional languages (French, German, Italian, etc.)
- User language preference settings
- Regional Spanish dialect support
- Improved language detection for short phrases
- Bilingual recipe database integration

## Contributing

When adding new features or ingredients, remember to update both English and Spanish versions:

1. Add English keywords/ingredients to `*_EN` lists
2. Add Spanish equivalents to `*_ES` lists
3. Update prompts in both languages
4. Test with both English and Spanish inputs

## Support

For issues or questions about the Spanish localization, please check:
1. Language detection accuracy with `test_language_detection.py`
2. Configuration in `config.py`
3. Prompt templates in the bot files