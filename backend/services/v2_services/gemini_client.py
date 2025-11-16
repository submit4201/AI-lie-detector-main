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

        try:
            # Try the standard configure method if it exists
            if hasattr(genai, 'configure'):
                genai.configure(api_key=self.api_key)
            else:
                # Fallback for different versions of the library
                genai.API_KEY = self.api_key
        except Exception:
            # If all else fails, set the API key as an attribute
            genai.API_KEY = self.api_key

        # Build SDK client if available; fall back to module object when needed
        if hasattr(genai, "GenerativeModel"):
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

    def _sync_generate(self, client, model: str, prompt: str, generation_config: Optional[Dict[str, Any]] = None):
        # Prefer the google-genai SDK surface: client.models.generate_content
        try:
            # If the SDK exposes `models.generate_content`, use it with a simple
            # contents list. We wrap the prompt string into a list as required.
            if hasattr(client, "models") and hasattr(client.models, "generate_content"):
                contents = prompt if isinstance(prompt, list) else [prompt]
                # Pass a light default generation config; callers may override by
                # performing a direct SDK call if they need advanced options.
                try:
                    return client.models.generate_content(
                        model=model,
                        contents=contents,
                        generation_config=generation_config
                    )
                except TypeError:
                    # Some SDK variants accept `contents` as a single value
                    return client.models.generate_content(
                        model=model,
                        contents=contents[0],
                        generation_config=generation_config
                    )

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

    async def _generate_with_retries(self, model: str, prompt: str, generation_config: Optional[Dict[str, Any]] = None):
        """Generate content using the SDK with retries and multi-surface support.

        Supports two major SDK surfaces:
        - genai.GenerativeModel(model) -> model.generate_content(...) (newer SDK variants)
        - client.models.generate_content(...) or client.responses.generate(...) (older SDKs)

        Falls back to a generic _sync_generate wrapper when needed.
        """
        attempt = 0
        last_exc = None

        # Try the newer GenerativeModel surface if available
        if hasattr(genai, "GenerativeModel"):
            while attempt <= self.max_retries:
                attempt += 1
                try:
                    model_instance = genai.GenerativeModel(model)
                    # Newer SDKs accept (contents, generation_config)
                    raw = await asyncio.wait_for(
                        self._run_blocking(model_instance.generate_content, prompt, generation_config=generation_config),
                        timeout=self.timeout,
                    )
                    return raw
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Gemini generate attempt {attempt} failed on GenerativeModel surface: {e}")
                    if attempt <= self.max_retries:
                        await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.1))
                        continue
                    break

        # Fall back to the client-level generation surface
        # Use the _sync_generate helper within the executor
        while attempt <= self.max_retries:
            attempt += 1
            try:
                raw = await asyncio.wait_for(
                    self._run_blocking(self._sync_generate, self._sdk_client, model, prompt, generation_config),
                    timeout=self.timeout,
                )
                return raw
            except Exception as e:
                last_exc = e
                logger.warning(f"Gemini generate attempt {attempt} failed on client surface: {e}")
                if attempt <= self.max_retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.1))
                    continue
                break

        raise last_exc

    async def query_json(self, prompt: str, *, model_hint: Optional[str] = None, max_output_tokens: int = 2048) -> Dict[str, Any]:
        model_pref = model_hint or GEMINI_MODEL_ANALYSIS
        model = await self.choose_model(model_pref)
        try:
            generation_config = {"max_output_tokens": max_output_tokens}
            raw = await self._generate_with_retries(model, prompt, generation_config)
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
        
        try:
            generation_config = {
                "response_mime_type": "application/json",
                "max_output_tokens": max_output_tokens,
            }
            if json_schema:
                generation_config["response_schema"] = json_schema

            raw = await self._generate_with_retries(model, prompt, generation_config)
                
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

    async def json_stream(
        self,
        prompt: str,
        *,
        schema: Optional[Dict[str, Any]] = None,
        audio_bytes: Optional[bytes] = None,
        context: Optional[Dict[str, Any]] = None,
        model_hint: Optional[str] = None,
    ):
        """Stream structured JSON responses from Gemini.
        
        If Live JSON streaming is available, use it for real-time results.
        Otherwise, simulate streaming by chunking a batch response.
        
        Args:
            prompt: The prompt text
            schema: Optional JSON schema for structured output
            audio_bytes: Optional audio data to include
            context: Optional context dict for enrichment
            model_hint: Optional model preference
            
        Yields:
            Dicts with {"data": partial_json, "chunk_index": i, "done": bool}
        """
        model_name = await self.choose_model(model_hint or GEMINI_MODEL_STRUCTURED)
        
        # Try Live streaming if available
        try:
            client = None
            if hasattr(self._sdk_client, 'aio'):
                client = self._sdk_client
            elif hasattr(genai, 'Client'):
                client = genai.Client(api_key=self.api_key)
                
            if client and hasattr(client, 'aio') and hasattr(client.aio, 'live') and hasattr(client.aio.live, 'chat'):
                _types = getattr(client, 'types', None) or getattr(genai, 'types', None)
                
                # Build generation config with JSON schema if provided
                config = {"response_mime_type": "application/json"}
                if schema:
                    config["response_schema"] = schema
                
                async with client.aio.live.chat.connect(model=model_name, config=config) as session:
                    # Prepare content parts
                    parts = []
                    if _types:
                        parts.append(_types.Content(parts=[_types.Part(text=prompt)]))
                        if audio_bytes:
                            blob = _types.Blob(mime_type='audio/wav', data=audio_bytes)
                            parts.append(_types.Content(parts=[blob]))
                    else:
                        parts.append(prompt)
                    
                    await session.send_message(contents=parts)
                    
                    chunk_index = 0
                    async for message in session.receive():
                        if message.candidates:
                            for candidate in message.candidates:
                                if candidate.content and candidate.content.parts:
                                    for part in candidate.content.parts:
                                        if getattr(part, 'text', None):
                                            text = part.text.strip()
                                            try:
                                                data = json.loads(text)
                                                yield {
                                                    "data": data,
                                                    "chunk_index": chunk_index,
                                                    "done": False
                                                }
                                                chunk_index += 1
                                            except json.JSONDecodeError:
                                                # Partial JSON, yield as-is
                                                yield {
                                                    "data": {"raw": text},
                                                    "chunk_index": chunk_index,
                                                    "done": False
                                                }
                                                chunk_index += 1
                    
                    # Final done marker
                    yield {"data": {}, "chunk_index": chunk_index, "done": True}
                    return
        except Exception:
            logger.debug("Live JSON streaming not available, falling back to simulated streaming", exc_info=True)
        
        # Fallback: simulate streaming with batch response
        try:
            if schema:
                result = await self.query_json_schema(prompt, schema, model_hint=model_hint)
            else:
                result = await self.query_json(prompt, model_hint=model_hint)
            
            # Split result into 3-5 chunks to simulate streaming
            if isinstance(result, dict):
                keys = list(result.keys())
                num_chunks = min(len(keys), 5)
                chunk_size = max(1, len(keys) // num_chunks)
                
                for i in range(num_chunks):
                    start_idx = i * chunk_size
                    end_idx = start_idx + chunk_size if i < num_chunks - 1 else len(keys)
                    chunk_keys = keys[start_idx:end_idx]
                    chunk_data = {k: result[k] for k in chunk_keys}
                    
                    yield {
                        "data": chunk_data,
                        "chunk_index": i,
                        "done": False
                    }
                    
                    # Small delay to simulate streaming
                    await asyncio.sleep(0.1)
                
                # Final chunk with all data
                yield {
                    "data": result,
                    "chunk_index": num_chunks,
                    "done": True
                }
            else:
                # Non-dict result, yield as single chunk
                yield {
                    "data": result,
                    "chunk_index": 0,
                    "done": True
                }
        except Exception as e:
            logger.error(f"JSON streaming failed: {e}", exc_info=True)
            yield {
                "data": {"error": str(e)},
                "chunk_index": 0,
                "done": True
            }

    async def transcribe(self, audio_bytes: bytes, *, model_hint: Optional[str] = None, mime_type: Optional[str] = None) -> str:
        if not audio_bytes:
            return ""
        model_name = await self.choose_model(model_hint or GEMINI_MODEL_TRANSCRIBE)
        mime = mime_type or "audio/wav"

        try:
            logger.info(f"Transcribing with model: {model_name}")

            # If the SDK supports file uploads, use it for better performance
            if hasattr(genai, "upload_file") and hasattr(genai, "delete_file"):
                audio_file = await self._run_blocking(genai.upload_file, audio_bytes, "temp_audio_file", mime)
                try:
                    if hasattr(genai, "GenerativeModel"):
                        model = genai.GenerativeModel(model_name)
                        response = await self._run_blocking(model.generate_content, ["Please transcribe this audio.", audio_file])
                    else:
                        # Fall back to client models API
                        response = await self._run_blocking(self._sync_generate, self._sdk_client, model_name, ["Please transcribe this audio.", audio_file])
                finally:
                    try:
                        await self._run_blocking(genai.delete_file, audio_file.name)
                    except Exception:
                        logger.debug("Failed to delete temporary audio file from SDK storage", exc_info=True)

                return extract_text_from_gemini_response(response)

            # Otherwise use inline base64 prompt fallback
            b64 = base64.b64encode(audio_bytes).decode("ascii")
            prompt = f"<AUDIO:BASE64 mime={mime}>{b64}</AUDIO>\nPlease transcribe the audio above and return ONLY the transcript text."
            resp = await self.query_json(prompt, model_hint=model_name)
            if isinstance(resp, dict):
                for k in ("transcript", "transcription", "text", "result"):
                    if k in resp:
                        return resp[k]
                if "text" in resp:
                    return resp.get("text")
            return str(resp)
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return f"Transcription failed: {e}"

    async def transcribe_stream(self, audio_bytes: bytes, *, model_hint: Optional[str] = None, mime_type: Optional[str] = None, context_prompt: Optional[str] = None):
        """Attempt to stream transcription results as they become available.

        Yields dict events: {'interim': True, 'partial_transcript': '...'} and a final
        {'interim': False, 'transcript': '...'} at the end. Fall back to the synchronous
        `transcribe` method if streaming is not supported by the installed SDK.
        """
        if not audio_bytes:
            yield {"interim": False, "transcript": ""}
            return

        # Prefer a 'live chat' streaming surface if available
        try:
            # Prefer using the configured SDK client instance when possible
            client = None
            if hasattr(self._sdk_client, 'aio'):
                client = self._sdk_client
            elif hasattr(genai, 'Client'):
                client = genai.Client(api_key=self.api_key)

            if client and hasattr(client, 'aio') and hasattr(client.aio, 'live') and hasattr(client.aio.live, 'chat'):
                # Structured streaming: send a small instruction plus the audio blob
                # Use the SDK's types surface if available. This mirrors the example file.
                # Prefer types attached to the chosen client; otherwise fall back to the global module
                _types = getattr(client, 'types', None) or getattr(genai, 'types', None)

                instruction = (
                    context_prompt
                    or "Please transcribe the audio in short, incremental JSON lines. Return only the transcript text field as 'transcription' or 'transcript'."
                )

                blob = _types.Blob(mime_type=mime_type or 'audio/wav', data=audio_bytes) if _types is not None else None
                model_name = await self.choose_model(model_hint or GEMINI_MODEL_TRANSCRIBE)
                async with client.aio.live.chat.connect(model=model_name) as session:
                    # send the instruction first and then the audio blob (if we can construct it)
                    if _types is not None:
                        instruction_content = _types.Content(parts=[_types.Part(text=instruction)])
                    else:
                        instruction_content = instruction

                    parts = [instruction_content]
                    if blob is not None:
                        parts.append(_types.Content(parts=[blob]))
                    await session.send_message(contents=parts)

                    final_yielded = False
                    async for message in session.receive():
                        if message.candidates:
                            for candidate in message.candidates:
                                if candidate.content and candidate.content.parts:
                                    for part in candidate.content.parts:
                                        # If the part has text, try to parse structured JSON first
                                        if getattr(part, 'text', None):
                                            text = part.text.strip()
                                            try:
                                                    j = json.loads(text)
                                                    if isinstance(j, dict):
                                                        # Accept both 'transcription' and 'transcript' keys
                                                        transcript_val = j.get('transcription') or j.get('transcript')
                                                        if transcript_val:
                                                            # Yield the transcript update for the normal transcript flow
                                                            yield {"interim": True, "partial_transcript": transcript_val}
                                                        # Yield any additional structured analysis keys (manipulation, argument, etc.) as independent events
                                                        for service_key in ("manipulation", "argument", "analysis"):
                                                            if service_key in j:
                                                                yield {"interim": True, "service_name": service_key, "payload": j[service_key]}
                                                        # Skip the plain text fallback, we've handled JSON
                                                        continue
                                            except Exception:
                                                # Not JSON — fall through to yield plain text
                                                pass

                                            # yield plain text interim output
                                            yield {"interim": True, "partial_transcript": text}

                                        # If non-text parts occur (e.g., structured metadata), ignore for now

                    # After streaming finishes, ensure we provide a final unified transcript
                    # Avoid duplication if the service already pushed a final transcript in stream
                    if not final_yielded:
                        final = await self.transcribe(audio_bytes, model_hint=model_hint, mime_type=mime_type)
                        yield {"interim": False, "transcript": final}
                        return
        except Exception:
            logger.debug("Live streaming transcription not available, falling back to batch transcription", exc_info=True)

        # Fallback: not supported; yield a simple interim and then final
        yield {"interim": True, "partial_transcript": ""}
        final = await self.transcribe(audio_bytes, model_hint=model_hint, mime_type=mime_type)
        yield {"interim": False, "transcript": final}

    async def analyze_audio(self, audio_bytes: Optional[bytes], transcript: Optional[str], prompt: str, *, model_hint: Optional[str] = None, mime_type: Optional[str] = None) -> Dict[str, Any]:
        if not transcript and audio_bytes:
            transcript = await self.transcribe(audio_bytes, model_hint=model_hint, mime_type=mime_type)
        
        if not transcript:
            logger.warning("No transcript available for audio analysis.")
            return create_fallback_response("Transcription failed or was not provided.")

        full_prompt = f"Transcript:\n{transcript}\n\n{prompt}"
        return await self.query_json(full_prompt, model_hint=model_hint)


def create_client(**kwargs) -> GeminiClientV2:
    return GeminiClientV2(**kwargs)
