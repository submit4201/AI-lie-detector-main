"""layer1_input.py
=================
Layer 1 – Raw Audio Capture & Chunker
------------------------------------
Responsible for turning a microphone (or any PyAudio‑ compatible input device)
into an **async stream** of fixed‑size PCM chunks ready for the parallel feature
extractors.

Why async?  We want the rest of the pipeline (DSP + STT + scoring) running in
parallel without blocking the audio callback thread, and an `asyncio.Queue`
gives tight, back‑pressure‑aware hand‑off.

Quick start
~~~~~~~~~~~
>>> import asyncio, layer1_input as l1
>>> q = asyncio.Queue(maxsize=50)
>>> inp = l1.AudioInput(queue=q)
>>> await inp.start()
>>> # elsewhere: await q.get() → (timestamp, pcm_bytes)
>>> await inp.stop()

Dependencies
~~~~~~~~~~~~
* **sounddevice** – lightweight wrapper over PortAudio (`pip install sounddevice`)
* **numpy** – for PCM ↔ ndarray handling (already in most stacks)

If you’re running in a headless Docker container, make sure ALSA/OSS devices are
mapped or swap `sounddevice` for a socket / gRPC audio source in `AudioInput`.
"""

from __future__ import annotations
from typing import AsyncIterator, Optional, Tuple
import asyncio
import time
import numpy as np
import sounddevice as sd
import logging

PCMFrame = Tuple[float, bytes]  # (unix_timestamp, raw_pcm)
logger = logging.getLogger(__name__)


class AudioInput:
    """Microphone → asyncio.Queue of PCM chunks."""

    def __init__(
        self,
        queue: asyncio.Queue[PCMFrame],
        device: Optional[int | str] = None,
        sample_rate: int = 16_000,
        channels: int = 1,
        chunk_ms: int = 20,
        dtype: str = "int16",
    ) -> None:
        self.queue = queue
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_samples = int(sample_rate * chunk_ms / 1000)
        self.dtype = dtype
        self.device = device

        self._stream: Optional[sd.InputStream] = None
        self._loop = asyncio.get_event_loop()
        self._stopping = asyncio.Event()

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    async def start(self) -> None:
        if self._stream is not None and self._stream.active:
            logger.warning("AudioInput stream is already active.")
            return

        self._stopping.clear()
        logger.info(
            f"Starting audio input stream with device: {self.device or 'default'}, "
            f"SR: {self.sample_rate}, Channels: {self.channels}, Chunk: {self.chunk_samples} samples, Dtype: {self.dtype}"
        )
        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_samples,
                device=self.device,
                callback=self._callback,
                loop=self._loop,  # Pass the loop for thread safety with call_soon_threadsafe
            )
            self._stream.start()
            logger.info("Audio input stream started.")
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            self._stream = None  # Ensure stream is None if start failed
            raise

    async def stop(self) -> None:
        logger.info("Attempting to stop audio input stream...")
        self._stopping.set()
        if self._stream is not None:
            if self._stream.active:
                self._stream.stop()
                logger.info("Audio input stream stopped.")
            if not self._stream.closed:
                self._stream.close()
                logger.info("Audio input stream closed.")
            self._stream = None
        # Give a moment for any in-flight callbacks to clear if necessary,
        # though PortAudio callbacks should cease after stop().
        await asyncio.sleep(0.01)
        logger.info("Audio input processing fully stopped.")

    # ------------------------------------------------------------------
    # async helper – expose an iterator if caller prefers
    # ------------------------------------------------------------------
    async def frames(self) -> AsyncIterator[PCMFrame]:
        """Async generator yielding (timestamp, pcm_bytes)."""
        while not self._stopping.is_set() or not self.queue.empty():
            try:
                yield await asyncio.wait_for(self.queue.get(), timeout=0.1)
                self.queue.task_done()  # If using queue.join() elsewhere
            except asyncio.TimeoutError:
                if self._stopping.is_set() and self.queue.empty():
                    break  # Exit if stopping and queue is drained
                continue  # Continue waiting if not stopping or queue might still get items
            except Exception as e:
                logger.error(f"Error getting frame from queue: {e}")
                if self._stopping.is_set():  # Avoid getting stuck if stopping
                    break
        logger.debug("Audio frames iterator finished.")

    # ------------------------------------------------------------------
    # PortAudio callback – runs in a non‑async thread, keep it *fast*.
    # ------------------------------------------------------------------
    def _callback(self, in_data: np.ndarray, frames: int, time_info, status):
        if self._stopping.is_set():
            return  # Don't process new data if stopping

        if status:
            logger.warning(f"PortAudio status: {status}")

        # Deep‑copy to bytes so we can drop the NumPy ref quickly.
        # This is critical as in_data buffer might be reused by PortAudio.
        pcm_bytes = in_data.copy().tobytes()  # Use .copy() before .tobytes()
        timestamp = time.time()  # More accurate timestamp closer to data arrival

        try:
            # Schedule the queue put operation on the event loop thread
            self._loop.call_soon_threadsafe(self._enqueue, timestamp, pcm_bytes)
        except RuntimeError:
            # This can happen if the event loop is closed while the stream is still active.
            logger.warning("Event loop closed, cannot enqueue audio frame.")
            # Consider signaling stop if loop is gone
            if not self._stopping.is_set():
                self._stopping.set()  # Signal to stop processing

    def _enqueue(self, ts: float, pcm: bytes):
        if self._stopping.is_set():
            return  # Don't enqueue if stopping
        try:
            self.queue.put_nowait((ts, pcm))
        except asyncio.QueueFull:
            logger.warning("Audio queue full, dropping frame!")
        except Exception as e:
            logger.error(f"Error enqueuing audio frame: {e}")


# Example usage (for testing this module directly)
async def main_test():
    logging.basicConfig(level=logging.INFO)
    q = asyncio.Queue[PCMFrame](maxsize=100)

    # To list devices:
    # print(sd.query_devices())
    # input_device_index = None # Or specify an index or name

    audio_input = AudioInput(queue=q, chunk_ms=100)  # Larger chunk for easier observation

    async def consume_audio():
        logger.info("Consumer started, waiting for frames...")
        frames_received = 0
        async for timestamp, pcm_data in audio_input.frames():
            frames_received += 1
            logger.info(
                f"Consumed frame {frames_received}: Timestamp {timestamp:.2f}, Size {len(pcm_data)} bytes"
            )
            if frames_received >= 50:  # Consume 50 frames then stop
                logger.info("Consumer reached 50 frames, signaling stop.")
                await audio_input.stop()
                break
        logger.info(f"Consumer finished. Total frames: {frames_received}")

    try:
        await audio_input.start()
        await consume_audio()
    except Exception as e:
        logger.error(f"An error occurred during the test: {e}")
    finally:
        if audio_input._stream and audio_input._stream.active:  # Ensure stop if not stopped by consumer
            logger.info("Ensuring audio input is stopped in finally block.")
            await audio_input.stop()
        logger.info("Test finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user.")
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
