import asyncio
from typing import Any, Dict, Optional

import httpx

from configs.config_loader import ConfigLoader
from utils.logging import get_logger, log_with_context

logger = get_logger(__name__)


class OllamaClient:
    """
    Production-grade Ollama client with:

    - Concurrency control
    - Retry logic
    - Fallback models
    - Structured logging
    - Config-driven behavior
    """

    def __init__(self):
        self.config = ConfigLoader.load()

        self.base_url = "http://127.0.0.1:11434/api/generate"

        self.semaphore = asyncio.Semaphore(self.config.runtime.max_concurrent_requests)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate response from Ollama with full control layer.
        """

        model = model or self.config.llm.model

        async with self.semaphore:
            return await self._generate_with_retries(
                prompt=prompt,
                model=model,
                trace_id=trace_id,
            )

    # ------------------------------------------------------------------
    # Retry + Fallback Logic
    # ------------------------------------------------------------------

    async def _generate_with_retries(
        self,
        prompt: str,
        model: str,
        trace_id: Optional[str],
    ) -> Dict[str, Any]:

        retries = self.config.llm.max_retries

        for attempt in range(1, retries + 2):  # +1 for initial attempt
            try:
                return await self._call_ollama(prompt, model, trace_id)

            except Exception as e:
                log_with_context(
                    logger,
                    "error",
                    "Ollama request failed",
                    extra={
                        "attempt": attempt,
                        "model": model,
                        "error": str(e),
                    },
                    trace_id=trace_id,
                )

                # Fallback model on final retry
                if (
                    attempt > retries
                    and self.config.features.enable_fallbacks
                    and self.config.llm.fallback_model
                ):
                    fallback_model = self.config.llm.fallback_model

                    log_with_context(
                        logger,
                        "info",
                        "Switching to fallback model",
                        extra={
                            "fallback_model": fallback_model,
                        },
                        trace_id=trace_id,
                    )

                    return await self._call_ollama(
                        prompt,
                        fallback_model,
                        trace_id,
                    )

                await asyncio.sleep(0.5 * attempt)

        raise RuntimeError("Ollama request failed after retries")

    # ------------------------------------------------------------------
    # Core HTTP Call
    # ------------------------------------------------------------------

    async def _call_ollama(
        self,
        prompt: str,
        model: str,
        trace_id: Optional[str],
    ) -> Dict[str, Any]:

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": self.config.runtime.stream,  # 🔥 enforced here
            "options": {
                "temperature": self.config.generation.temperature,
                "top_p": self.config.generation.top_p,
                "num_predict": self.config.generation.max_tokens,
            },
        }

        log_with_context(
            logger,
            "info",
            "Sending request to Ollama",
            extra={
                "model": model,
                "prompt_preview": prompt[:50],
            },
            trace_id=trace_id,
        )

        async with httpx.AsyncClient(timeout=self.config.runtime.timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
            )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama HTTP error {response.status_code}")

        data = response.json()

        # ✅ Normalize response
        return {
            "model": data.get("model"),
            "response": data.get("response"),
            "done": data.get("done", True),
        }
