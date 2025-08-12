"""
LLM provider for Recipe Genie Discord Bot.
Supports local LLM (LMStudio) and OpenRouter APIs with caching and error handling.
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any, List
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM response data class."""
    content: str
    tokens_used: int
    model: str
    response_time: float
    cached: bool = False


class LLMProvider:
    """
    LLM provider supporting multiple backends.
    
    Features:
    - Local LLM (LMStudio) support
    - OpenRouter API support
    - Request caching
    - Rate limiting
    - Error handling
    - Response validation
    """
    
    def __init__(self, config, cache_manager=None):
        self.config = config
        self.cache_manager = cache_manager
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_response_time": 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize the LLM provider."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config.llm.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info(f"LLM provider initialized ({self.config.llm.provider})")
    
    async def close(self) -> None:
        """Close the LLM provider."""
        if self.session:
            await self.session.close()
            logger.info("LLM provider closed")
    
    async def generate_recipe(self, prompt: str, language: str = "en") -> Optional[LLMResponse]:
        """
        Generate a recipe using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            language: Language code ('en' or 'es')
            
        Returns:
            LLMResponse object or None if failed
        """
        # Check cache first
        cache_key = f"recipe:{language}:{hash(prompt)}"
        if self.cache_manager:
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for recipe generation: {cache_key}")
                return LLMResponse(
                    content=cached_response["content"],
                    tokens_used=cached_response["tokens_used"],
                    model=cached_response["model"],
                    response_time=cached_response["response_time"],
                    cached=True
                )
        
        # Generate response
        async with self.request_semaphore:
            start_time = time.time()
            
            try:
                if self.config.llm.provider == "openrouter":
                    response = await self._generate_openrouter(prompt, language)
                else:
                    response = await self._generate_local(prompt, language)
                
                if response:
                    response.response_time = time.time() - start_time
                    
                    # Cache the response
                    if self.cache_manager:
                        cache_data = {
                            "content": response.content,
                            "tokens_used": response.tokens_used,
                            "model": response.model,
                            "response_time": response.response_time
                        }
                        await self.cache_manager.set(cache_key, cache_data, ttl=3600)  # 1 hour
                    
                    # Update statistics
                    self.stats["total_requests"] += 1
                    self.stats["successful_requests"] += 1
                    self.stats["total_tokens"] += response.tokens_used
                    self.stats["total_response_time"] += response.response_time
                    
                    logger.info(f"Recipe generated successfully in {response.response_time:.2f}s "
                              f"({response.tokens_used} tokens)")
                    
                    return response
                
            except Exception as e:
                self.stats["total_requests"] += 1
                self.stats["failed_requests"] += 1
                logger.error(f"Failed to generate recipe: {e}")
                return None
    
    async def _generate_local(self, prompt: str, language: str) -> Optional[LLMResponse]:
        """
        Generate recipe using local LLM (LMStudio).
        
        Args:
            prompt: The prompt to send
            language: Language code
            
        Returns:
            LLMResponse object or None if failed
        """
        # Build the prompt based on language
        system_prompt = self._get_system_prompt(language)
        
        payload = {
            "model": self.config.llm.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.llm.max_tokens,
            "temperature": self.config.llm.temperature,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.config.llm.api_key:
            headers["Authorization"] = f"Bearer {self.config.llm.api_key}"
        
        try:
            async with self.session.post(
                self.config.llm.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_local_response(data)
                else:
                    error_text = await response.text()
                    logger.error(f"Local LLM API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Local LLM request timed out")
            return None
        except Exception as e:
            logger.error(f"Local LLM request failed: {e}")
            return None
    
    async def _generate_openrouter(self, prompt: str, language: str) -> Optional[LLMResponse]:
        """
        Generate recipe using OpenRouter API.
        
        Args:
            prompt: The prompt to send
            language: Language code
            
        Returns:
            LLMResponse object or None if failed
        """
        # Build the prompt based on language
        system_prompt = self._get_system_prompt(language)
        
        payload = {
            "model": self.config.llm.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.llm.max_tokens,
            "temperature": self.config.llm.temperature
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.llm.api_key}",
            "HTTP-Referer": "https://recipe-genie-bot.com",
            "X-Title": "Recipe Genie Bot"
        }
        
        try:
            async with self.session.post(
                self.config.llm.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_openrouter_response(data)
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("OpenRouter request timed out")
            return None
        except Exception as e:
            logger.error(f"OpenRouter request failed: {e}")
            return None
    
    def _get_system_prompt(self, language: str) -> str:
        """
        Get system prompt based on language.
        
        Args:
            language: Language code ('en' or 'es')
            
        Returns:
            System prompt string
        """
        if language == "es":
            return """Eres un asistente culinario experto que ayuda a crear recetas deliciosas y fáciles de seguir.

Instrucciones:
1. Proporciona recetas claras y detalladas
2. Incluye ingredientes con cantidades específicas
3. Da instrucciones paso a paso
4. Incluye tiempo de preparación y cocción
5. Sugiere variaciones o consejos útiles
6. Usa un tono amigable y motivador
7. Formatea la respuesta de manera clara y legible

Formato de respuesta:
- Título de la receta
- Lista de ingredientes con cantidades
- Instrucciones numeradas
- Tiempo total estimado
- Consejos o variaciones (opcional)"""
        else:
            return """You are an expert culinary assistant who helps create delicious and easy-to-follow recipes.

Instructions:
1. Provide clear and detailed recipes
2. Include ingredients with specific quantities
3. Give step-by-step instructions
4. Include preparation and cooking time
5. Suggest variations or helpful tips
6. Use a friendly and encouraging tone
7. Format the response clearly and readably

Response format:
- Recipe title
- List of ingredients with quantities
- Numbered instructions
- Estimated total time
- Tips or variations (optional)"""
    
    def _parse_local_response(self, data: Dict[str, Any]) -> Optional[LLMResponse]:
        """
        Parse response from local LLM.
        
        Args:
            data: Response data from local LLM
            
        Returns:
            LLMResponse object or None if parsing failed
        """
        try:
            choices = data.get("choices", [])
            if not choices:
                logger.error("No choices in local LLM response")
                return None
            
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            if not content:
                logger.error("No content in local LLM response")
                return None
            
            # Extract token usage
            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.config.llm.model,
                response_time=0.0  # Will be set by caller
            )
            
        except Exception as e:
            logger.error(f"Failed to parse local LLM response: {e}")
            return None
    
    def _parse_openrouter_response(self, data: Dict[str, Any]) -> Optional[LLMResponse]:
        """
        Parse response from OpenRouter API.
        
        Args:
            data: Response data from OpenRouter
            
        Returns:
            LLMResponse object or None if parsing failed
        """
        try:
            choices = data.get("choices", [])
            if not choices:
                logger.error("No choices in OpenRouter response")
                return None
            
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            if not content:
                logger.error("No content in OpenRouter response")
                return None
            
            # Extract token usage
            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.config.llm.model,
                response_time=0.0  # Will be set by caller
            )
            
        except Exception as e:
            logger.error(f"Failed to parse OpenRouter response: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get LLM provider statistics.
        
        Returns:
            Dictionary with statistics
        """
        avg_response_time = (
            self.stats["total_response_time"] / self.stats["successful_requests"]
            if self.stats["successful_requests"] > 0 else 0
        )
        
        success_rate = (
            self.stats["successful_requests"] / self.stats["total_requests"] * 100
            if self.stats["total_requests"] > 0 else 0
        )
        
        cache_hit_rate = (
            self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["successful_requests"]) * 100
            if (self.stats["cache_hits"] + self.stats["successful_requests"]) > 0 else 0
        )
        
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": round(success_rate, 2),
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": round(cache_hit_rate, 2),
            "total_tokens": self.stats["total_tokens"],
            "avg_response_time": round(avg_response_time, 3),
            "provider": self.config.llm.provider,
            "model": self.config.llm.model
        }