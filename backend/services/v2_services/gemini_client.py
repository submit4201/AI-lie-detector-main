"""GeminiClientV2 using the `google-genai` SDK (google_genai).

This client prefers the `google_genai` package and uses its client
surface when available. Blocking SDK calls are delegated to a thread
pool so the interface is async-friendly.

The implementation attempts commonly-used SDK entrypoints but does not
depend on `google.generativeai` or any hand-rolled HTTP calls.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List

try:
    import google_genai as genai  # type: ignore[import-not-found]
except Exception:
    try:
        from google import genai  # type: ignore[import-not-found]
    except Exception:
        genai = None

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL_TRANSCRIBE,
    GEMINI_MODEL_ANALYSIS,
    GEMINI_MODEL_STRUCTURED,
    GEMINI_FALLBACK_MODELS,
)
from backend.services.json_utils import parse_gemini_response, extract_text_from_gemini_response, create_fallback_response

logger = logging.getLogger(__name__)


class GeminiClientV2:
    """Async wrapper around the google-genai SDK.

    Construction will raise a helpful RuntimeError if the `google-genai`
    package is not installed. The module itself is safe to import.
    """

    def __init__(self, *, api_key: Optional[str] = None, timeout: float = 120.0, max_retries: int = 2, backoff_base: float = 0.5, max_workers: int = 4):
        if genai is None:
            raise RuntimeError("google-genai (google_genai) is required. Install with `pip install google-genai`.")

        self.api_key = api_key or GEMINI_API_KEY
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # Build SDK client if available; fall back to module object when needed
        if hasattr(genai, "Client"):
            try:
                self._sdk_client = genai.Client(api_key=self.api_key)
            except Exception:
                self._sdk_client = genai
        else:
            self._sdk_client = genai

    async def _run_blocking(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: fn(*args, **kwargs))

    def _sync_list_models(self):
        client = self._sdk_client
        try:
            if hasattr(client, "list_models"):
                return client.list_models()
            if hasattr(client, "models") and hasattr(client.models, "list"):
                return client.models.list()
            if hasattr(client, "available_models"):
                return client.available_models()
        except Exception:
            logger.debug("list_models sync call failed", exc_info=True)
        return []

    async def list_available_models(self) -> List[str]:
        raw = await self._run_blocking(self._sync_list_models)
        names: List[str] = []
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("id") or item.get("model")
                    if name:
                        names.append(name.split("/")[-1])
                elif isinstance(item, str):
                    names.append(item.split("/")[-1])
        return names

    async def choose_model(self, preferred: Optional[str]) -> str:
        pref = preferred or GEMINI_MODEL_ANALYSIS
        available = await self.list_available_models()
        if not available:
            return pref
        if pref in available:
            return pref
        for fb in GEMINI_FALLBACK_MODELS:
            if fb in available:
                logger.info(f"Falling back to model: {fb}")
                return fb
        return available[0]

    def _sync_generate(self, client, model: str, prompt: str):
        # Prefer the google-genai SDK surface: client.models.generate_content
        try:
            # If the SDK exposes `models.generate_content`, use it with a simple
            # contents list. We wrap the prompt string into a list as required.
            if hasattr(client, "models") and hasattr(client.models, "generate_content"):
                contents = prompt if isinstance(prompt, list) else [prompt]
                # Pass a light default generation config; callers may override by
                # performing a direct SDK call if they need advanced options.
                try:
                    return client.models.generate_content(model=model, contents=contents)
                except TypeError:
                    # Some SDK variants accept `contents` as a single value
                    return client.models.generate_content(model=model, contents=contents[0])

            # Fall back to other historically-used method names
            if hasattr(client, "generate_text"):
                return client.generate_text(model=model, input=prompt)
            if hasattr(client, "responses") and hasattr(client.responses, "generate"):
                return client.responses.generate(model=model, input=prompt)
            if hasattr(client, "generate"):
                return client.generate(model=model, prompt=prompt)
            if hasattr(client, "predict"):
                return client.predict(model=model, prompt=prompt)
        except Exception:
            logger.debug("_sync_generate attempt failed", exc_info=True)
        raise RuntimeError("Incompatible google-genai SDK surface: no known generate entrypoint")

    async def _generate_with_retries(self, model: str, prompt: str):
        attempt = 0
        last_exc = None
        client = self._sdk_client
        while attempt <= self.max_retries:
            attempt += 1
            try:
                raw = await asyncio.wait_for(self._run_blocking(self._sync_generate, client, model, prompt), timeout=self.timeout)
                return raw
            except Exception as e:
                last_exc = e
                logger.warning(f"Gemini generate attempt {attempt} failed: {e}")
                if attempt <= self.max_retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.1))
                    continue
                break
        raise last_exc

    async def query_json(self, prompt: str, *, model_hint: Optional[str] = None, max_output_tokens: int = 2048) -> Dict[str, Any]:
        model_pref = model_hint or GEMINI_MODEL_ANALYSIS
        model = await self.choose_model(model_pref)
        try:
            raw = await self._generate_with_retries(model, prompt)
        except Exception as e:
            logger.error("Gemini query failed", exc_info=True)
            return create_fallback_response(str(e))

        # If the SDK returned a mapped/dict object, return it directly
        if isinstance(raw, dict):
            return raw

        # Try to extract text from common response shapes
        text = None
        if hasattr(raw, "text"):
            text = getattr(raw, "text")
        else:
            try:
                if isinstance(raw, dict) and "candidates" in raw:
                    cand = raw.get("candidates", [])
                    if cand:
                        first = cand[0]
                        if isinstance(first, dict):
                            text = first.get("content") or first.get("output") or first.get("text")
                        else:
                            text = str(first)
            except Exception:
                text = None

        if text is None:
            text = str(raw)

        text = text.strip() if isinstance(text, str) else text
        if not text:
            return {}

        # If looks like JSON, try to parse
        if isinstance(text, str) and (text.startswith("{") or text.startswith("[")):
            try:
                return json.loads(text)
            except Exception:
                pass

        return {"text": text}

    async def query_json_schema(self, prompt: str, json_schema: Dict[str, Any], *, model_hint: Optional[str] = None, max_output_tokens: int = 2048) -> Dict[str, Any]:
        """Query Gemini and request a structured JSON response using a JSON schema.
        
        This method sets response_mime_type to application/json and passes the provided
        JSON schema to Gemini so the model returns a well-formed JSON object.
        """
        model_pref = model_hint or GEMINI_MODEL_STRUCTURED
        model = await self.choose_model(model_pref)
        client = self._sdk_client
        
        try:
            # Prefer the native SDK call with structured output config
            if hasattr(client, "models") and hasattr(client.models, "generate_content"):
                # Build generation config with JSON mime type and schema
                config = {
                    "response_mime_type": "application/json",
                    "response_json_schema": json_schema,
                    "max_output_tokens": max_output_tokens,
                }
                # Some SDK variants expect generation_config as a separate arg
                try:
                    raw = await self._run_blocking(
                        client.models.generate_content,
                        model,
                        prompt,
                        config
                    )
                except TypeError:
                    # Try with named args
                    raw = await self._run_blocking(
                        lambda: client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=config
                        )
                    )
            else:
                # Fallback to generic generate path (won't have structured output)
                raw = await self._generate_with_retries(model, prompt)
                
            # Parse the response text as JSON
            if hasattr(raw, "text"):
                text = raw.text
            else:
                text = str(raw)
                
            try:
                return json.loads(text)
            except Exception:
                logger.warning("Failed to parse structured response as JSON")
                return {"raw_text": text}
                
        except Exception as e:
            logger.error("Gemini structured query failed", exc_info=True)
            return create_fallback_response(str(e))

    async def transcribe(self, audio_bytes: bytes, *, model_hint: Optional[str] = None, mime_type: Optional[str] = None) -> str:
        if not audio_bytes:
            return ""
        model = await self.choose_model(model_hint or GEMINI_MODEL_TRANSCRIBE)
        mime = mime_type or "audio/wav"

        # If the SDK exposes a types.Part.from_bytes helper, prefer using the
        # native inline-file parts API. Otherwise fall back to an encoded prompt.
        client = self._sdk_client
        if hasattr(client, "types") and hasattr(client.types, "Part") and hasattr(client.types.Part, "from_bytes"):
            part = client.types.Part.from_bytes(data=audio_bytes, mime_type=mime)
            contents = ["Please transcribe this audio. Return only the raw transcript text.", part]
            try:
                raw = await self._run_blocking(client.models.generate_content, model, contents)
            except Exception:
                # Some SDK variants expect named args
                raw = await self._run_blocking(lambda: client.models.generate_content(model=model, contents=contents))
            resp = raw
        else:
            b64 = base64.b64encode(audio_bytes).decode("ascii")
            prompt = f"<AUDIO:BASE64 mime={mime}>{b64}</AUDIO>\nPlease transcribe the audio above and return ONLY the transcript text."
            resp = await self.query_json(prompt, model_hint=model)
        if isinstance(resp, dict):
            for k in ("transcript", "transcription", "text", "result"):
                if k in resp:
                    return resp[k]
            # fallback to extracting from parsed JSON text
            if "text" in resp:
                return resp.get("text")
        return str(resp)

    async def analyze_audio(self, audio_bytes: Optional[bytes], transcript: Optional[str], prompt: str, *, model_hint: Optional[str] = None, mime_type: Optional[str] = None) -> Dict[str, Any]:
        if not transcript:
            transcript = await self.transcribe(audio_bytes or b"", model_hint=model_hint, mime_type=mime_type)
        full_prompt = f"Transcript:\n{transcript}\n\n{prompt}"
        return await self.query_json(full_prompt, model_hint=model_hint)


def create_client(**kwargs) -> GeminiClientV2:
    return GeminiClientV2(**kwargs)
