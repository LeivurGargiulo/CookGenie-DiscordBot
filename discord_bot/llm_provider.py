"""
LLM Provider module for Recipe Genie Discord bot
Handles both local LLM (LMStudio) and OpenRouter integrations
"""

import asyncio
import logging
import aiohttp
import json
from typing import Optional, Dict, Any
from .config import (
    LLM_ENDPOINT, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_TEMPERATURE,
    LLM_PROVIDER, OPENROUTER_API_KEY, OPENROUTER_ENDPOINT, OPENROUTER_MODEL,
    OPENROUTER_TIMEOUT, OPENROUTER_MAX_TOKENS, OPENROUTER_TEMPERATURE
)

logger = logging.getLogger(__name__)

class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_response(self, prompt: str, language: str = 'en') -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

class LocalLLMProvider(LLMProvider):
    """Local LLM provider using LMStudio or similar local endpoints."""
    
    def __init__(self):
        super().__init__()
        self.endpoint = LLM_ENDPOINT
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL
        self.timeout = LLM_TIMEOUT
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
    
    async def generate_response(self, prompt: str, language: str = 'en') -> str:
        """Generate response using local LLM."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with self.session.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    logger.error(f"Local LLM error: {response.status} - {await response.text()}")
                    return self._get_fallback_response(prompt, language)
        
        except asyncio.TimeoutError:
            logger.error("Local LLM request timed out")
            return self._get_fallback_response(prompt, language)
        except Exception as e:
            logger.error(f"Local LLM error: {str(e)}")
            return self._get_fallback_response(prompt, language)
    
    def _get_fallback_response(self, prompt: str, language: str) -> str:
        """Get a fallback response when LLM is unavailable."""
        if language == 'es':
            if "ingredientes" in prompt.lower():
                return """🍳 Idea de Receta Rápida:

**Salteado Simple**
- Calienta aceite en una sartén
- Agrega tus ingredientes y saltea por 5-7 minutos
- Sazona con sal, pimienta y tus especias favoritas
- ¡Sirve caliente!

💡 Consejo: ¡Agrega ajo y jengibre para más sabor!"""
            else:
                return """🍽️ Receta:

**Ingredientes:**
- 2 tazas de harina
- 1 taza de leche
- 2 huevos
- 2 cucharadas de azúcar
- 1 cucharadita de polvo para hornear
- Pizca de sal

**Instrucciones:**
1. Mezcla los ingredientes secos
2. Bate los ingredientes húmedos por separado
3. Combina y cocina a fuego medio
4. Voltea cuando se formen burbujas
5. ¡Sirve con tus toppings favoritos!

¡Disfruta! 😊"""
        else:
            if "ingredients" in prompt.lower():
                return """🍳 Quick Recipe Idea:

**Simple Stir-Fry**
- Heat oil in a pan
- Add your ingredients and stir-fry for 5-7 minutes
- Season with salt, pepper, and your favorite spices
- Serve hot!

💡 Tip: Add garlic and ginger for extra flavor!"""
            else:
                return """🍽️ Recipe:

**Ingredients:**
- 2 cups flour
- 1 cup milk
- 2 eggs
- 2 tbsp sugar
- 1 tsp baking powder
- Pinch of salt

**Instructions:**
1. Mix dry ingredients
2. Whisk wet ingredients separately
3. Combine and cook on medium heat
4. Flip when bubbles form
5. Serve with your favorite toppings!

Enjoy! 😊"""

class OpenRouterLLMProvider(LLMProvider):
    """OpenRouter LLM provider for cloud-based LLM access."""
    
    def __init__(self):
        super().__init__()
        self.endpoint = OPENROUTER_ENDPOINT
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.timeout = OPENROUTER_TIMEOUT
        self.max_tokens = OPENROUTER_MAX_TOKENS
        self.temperature = OPENROUTER_TEMPERATURE
    
    async def generate_response(self, prompt: str, language: str = 'en') -> str:
        """Generate response using OpenRouter."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        if not self.api_key:
            logger.error("OpenRouter API key not configured")
            return self._get_fallback_response(prompt, language)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://recipe-genie-bot.com",
            "X-Title": "Recipe Genie Bot"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with self.session.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    logger.error(f"OpenRouter error: {response.status} - {await response.text()}")
                    return self._get_fallback_response(prompt, language)
        
        except asyncio.TimeoutError:
            logger.error("OpenRouter request timed out")
            return self._get_fallback_response(prompt, language)
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            return self._get_fallback_response(prompt, language)
    
    def _get_fallback_response(self, prompt: str, language: str) -> str:
        """Get a fallback response when OpenRouter is unavailable."""
        # Use the same fallback as local LLM
        local_provider = LocalLLMProvider()
        return local_provider._get_fallback_response(prompt, language)

def get_llm_provider() -> LLMProvider:
    """Get the appropriate LLM provider based on configuration."""
    if LLM_PROVIDER.lower() == "openrouter":
        return OpenRouterLLMProvider()
    else:
        return LocalLLMProvider()

async def generate_recipe(prompt: str, language: str = 'en') -> str:
    """
    Generate a recipe response using the configured LLM provider.
    
    Args:
        prompt (str): The prompt to send to the LLM
        language (str): The language of the prompt ('en' or 'es')
        
    Returns:
        str: The LLM-generated response
    """
    provider = get_llm_provider()
    
    async with provider:
        return await provider.generate_response(prompt, language)