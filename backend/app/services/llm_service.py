"""
LLM Service для анализа сообщений через llm.codenrock.com API.
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Сервис для работы с LLM API (llm.codenrock.com - OpenAI-compatible).
    """

    def __init__(self):
        self.api_url = settings.LLM_API_URL.rstrip('/')
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT

        # Cache для результатов (in-memory, простая реализация)
        # В production лучше использовать Redis
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(hours=1)

    def _get_cache_key(self, operation: str, *args) -> str:
        """Генерация ключа кэша."""
        return f"{operation}:{hash(str(args))}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Получение из кэша."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                # Expired
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        """Сохранение в кэш."""
        self._cache[key] = (value, datetime.utcnow())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        """
        Базовый метод для вызова LLM API.

        Args:
            system_prompt: Системный промпт (инструкции для модели)
            user_prompt: Пользовательский промпт (входные данные)
            temperature: Температура генерации (0-2)
            max_tokens: Максимальное количество токенов в ответе

        Returns:
            str: Текст ответа от LLM

        Raises:
            httpx.HTTPError: При ошибке HTTP запроса
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                logger.debug(f"LLM API call successful. Tokens used: {result.get('usage', {})}")
                return content.strip()

        except httpx.HTTPError as e:
            logger.error(f"LLM API error: {str(e)}")
            raise

    async def analyze_message(self, message_text: str, rule_description: str) -> Dict[str, Any]:
        """
        Анализирует сообщение на соответствие правилу.

        Args:
            message_text: Текст сообщения из Telegram
            rule_description: Описание правила (промпт от пользователя)

        Returns:
            Dict с результатами:
            {
                "is_match": bool,
                "confidence": float (0.0-1.0),
                "reasoning": str
            }
        """
        # Проверяем кэш
        cache_key = self._get_cache_key("analyze", message_text, rule_description)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        system_prompt = """Ты - ассистент для анализа сообщений из Telegram.
Твоя задача - определить, соответствует ли сообщение заданному критерию.

ВАЖНО: Отвечай ТОЛЬКО в формате JSON без дополнительного текста:
{
    "is_match": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "краткое объяснение (1-2 предложения)"
}"""

        user_prompt = f"""Критерий поиска:
{rule_description}

Анализируемое сообщение:
{message_text}

Соответствует ли сообщение критерию? Ответь в формате JSON."""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=300
            )

            # Парсим JSON ответ
            logger.debug(f"LLM raw response: {response}")
            result = json.loads(response)

            # Валидация структуры
            if not all(k in result for k in ["is_match", "confidence", "reasoning"]):
                raise ValueError("Invalid response structure from LLM")

            # Сохраняем в кэш
            self._set_cache(cache_key, result)

            logger.info(
                f"Message analyzed: is_match={result['is_match']}, "
                f"confidence={result['confidence']:.2f}, reasoning='{result['reasoning'][:50]}...'"
            )

            return result

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            # Fallback: если LLM вернул некорректный JSON
            return {
                "is_match": False,
                "confidence": 0.0,
                "reasoning": f"Error parsing LLM response: {str(e)}"
            }

    async def extract_entities(self, message_text: str) -> Dict[str, Any]:
        """
        Извлекает сущности из сообщения (контакты, ключевые слова, бюджет и т.д.).

        Args:
            message_text: Текст сообщения

        Returns:
            Dict со структурированными данными:
            {
                "contacts": ["email", "phone", "telegram"],
                "keywords": ["keyword1", "keyword2"],
                "budget": "extracted budget info or null",
                "deadline": "extracted deadline or null",
                "summary": "краткое описание (2-3 предложения)"
            }
        """
        # Проверяем кэш
        cache_key = self._get_cache_key("extract_entities", message_text)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        system_prompt = """Ты - ассистент для извлечения структурированных данных из текста.
Извлеки следующую информацию из сообщения:
- Контакты (email, телефон, Telegram username)
- Ключевые слова и фразы
- Бюджет (если упоминается)
- Дедлайн/сроки (если упоминаются)
- Краткое описание сути (2-3 предложения)

ВАЖНО: Отвечай ТОЛЬКО в формате JSON без дополнительного текста:
{
    "contacts": ["contact1", "contact2"],
    "keywords": ["keyword1", "keyword2"],
    "budget": "string or null",
    "deadline": "string or null",
    "summary": "краткое описание"
}"""

        user_prompt = f"""Сообщение для анализа:
{message_text}

Извлеки структурированные данные в формате JSON."""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=500
            )

            result = json.loads(response)

            # Валидация и дефолтные значения
            result.setdefault("contacts", [])
            result.setdefault("keywords", [])
            result.setdefault("budget", None)
            result.setdefault("deadline", None)
            result.setdefault("summary", "")

            # Сохраняем в кэш
            self._set_cache(cache_key, result)

            logger.info(f"Entities extracted: {len(result['contacts'])} contacts, {len(result['keywords'])} keywords")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse entity extraction response: {str(e)}")
            return {
                "contacts": [],
                "keywords": [],
                "budget": None,
                "deadline": None,
                "summary": message_text[:200] + "..." if len(message_text) > 200 else message_text
            }

    async def generate_summary(self, message_text: str, max_length: int = 150) -> str:
        """
        Генерирует краткое описание сообщения для отображения в списке лидов.

        Args:
            message_text: Текст сообщения
            max_length: Максимальная длина саммари в символах

        Returns:
            str: Краткое описание (1-2 предложения)
        """
        # Проверяем кэш
        cache_key = self._get_cache_key("summary", message_text, max_length)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        system_prompt = f"""Ты - ассистент для создания кратких описаний сообщений.
Создай краткое описание (1-2 предложения, максимум {max_length} символов), которое передаёт суть сообщения.
Фокусируйся на главном: кто, что ищет/предлагает, какие условия.

Отвечай только текстом описания, без дополнительных комментариев."""

        user_prompt = f"""Сообщение:
{message_text}

Краткое описание:"""

        try:
            summary = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=100
            )

            # Обрезаем до max_length если нужно
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."

            # Сохраняем в кэш
            self._set_cache(cache_key, summary)

            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            # Fallback: первые N символов оригинального текста
            fallback = message_text[:max_length-3] + "..." if len(message_text) > max_length else message_text
            return fallback

    def clear_cache(self):
        """Очистка кэша (для тестирования или периодической очистки)."""
        self._cache.clear()
        logger.info("LLM cache cleared")


# Глобальный экземпляр сервиса
llm_service = LLMService()
