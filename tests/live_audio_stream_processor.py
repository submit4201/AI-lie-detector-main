import asyncio
import logging
import time

# Assuming layer_1_input, layer_2_feature_extraction, and layer_3_feature_assembler
# are in the same directory (tests/) or the PYTHONPATH is set up correctly.
from layer_1_input import AudioInput, PCMFrame
from layer_3_feature_assembler import assemble_feature_vector_from_data
# layer_2_feature_extraction is used by layer_3, so direct import here isn't strictly necessary
# unless you want to call its functions directly.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
SAMPLE_RATE = 16000  # Hz
CHANNELS = 1         # Mono
CHUNK_MS = 100       # Milliseconds per chunk for AudioInput
DTYPE = 'int16'      # Data type from AudioInput

# How many PCM frames from AudioInput to batch together before sending to feature extraction
# This depends on how much audio Layer 2/3 needs for meaningful analysis.
# For example, if CHUNK_MS is 20ms, and Layer 2 needs ~1 second of audio:
# BATCH_SIZE_FRAMES = 1000 // CHUNK_MS = 50 frames.
# If CHUNK_MS is 100ms, BATCH_SIZE_FRAMES = 1000 // 100 = 10 frames.
BATCH_DURATION_SECONDS = 1.0 # Desired duration of audio for each feature extraction pass
FRAMES_PER_BATCH = int(BATCH_DURATION_SECONDS * 1000 / CHUNK_MS) 

MAX_STREAM_DURATION_SECONDS = 30 # Stop after this many seconds for testing

async def process_audio_stream():
    """
    Captures audio, processes it in chunks through Layer 1, 2, and 3,
    and logs the assembled features.
    """
    audio_queue = asyncio.Queue[PCMFrame](maxsize=200) # Max 200 raw audio chunks in queue
    audio_input = AudioInput(
        queue=audio_queue,
        sample_rate=SAMPLE_RATE,
        channels=CHANNELS,
        chunk_ms=CHUNK_MS,
        dtype=DTYPE
        # device=DEVICE_INDEX # Optional: specify input device index/name
    )

    logger.info(f"Starting audio stream processor. Batching {FRAMES_PER_BATCH} frames ({BATCH_DURATION_SECONDS}s of audio) for feature extraction.")

    await audio_input.start()
    
    start_time = time.time()
    processed_segments_count = 0
    
    try:
        pcm_byte_buffer = bytearray()
        frames_in_current_buffer = 0

        async for timestamp, pcm_data_chunk in audio_input.frames():
            if time.time() - start_time > MAX_STREAM_DURATION_SECONDS:
                logger.info(f"Max stream duration of {MAX_STREAM_DURATION_SECONDS}s reached. Stopping.")
                break

            pcm_byte_buffer.extend(pcm_data_chunk)
            frames_in_current_buffer += 1

            if frames_in_current_buffer >= FRAMES_PER_BATCH:
                logger.info(f"Collected {frames_in_current_buffer} frames, processing batch ({len(pcm_byte_buffer)} bytes)...")
                
                # We have a batch of audio data
                current_batch_data = bytes(pcm_byte_buffer) # Make immutable copy for processing
                
                # Reset buffer for next batch
                pcm_byte_buffer.clear()
                frames_in_current_buffer = 0
                
                try:
                    # Pass the raw audio data bytes, sample rate, and channels
                    feature_vector = assemble_feature_vector_from_data(
                        audio_data=current_batch_data,
                        sample_rate=SAMPLE_RATE,
                        channels=CHANNELS
                    )
                    processed_segments_count += 1
                    logger.info(f"--- Assembled Feature Vector (Segment {processed_segments_count}) ---")
                    for key, value in feature_vector.items():
                        if isinstance(value, float):
                            logger.info(f"  {key}: {value:.4f}")
                        elif isinstance(value, np.ndarray): # type: ignore
                             logger.info(f"  {key}: array of shape {value.shape}")
                        else:
                            logger.info(f"  {key}: {value}")
                    logger.info("-----------------------------------------------------")

                except RuntimeError as e:
                    logger.error(f"Error processing audio batch: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error during feature assembly for a batch: {e}", exc_info=True)
                
                # Small pause to allow other tasks to run, and to simulate real-time processing gaps
                await asyncio.sleep(0.01) 

    except asyncio.CancelledError:
        logger.info("Audio stream processing was cancelled.")
    except Exception as e:
        logger.error(f"An error occurred in the main processing loop: {e}", exc_info=True)
    finally:
        logger.info("Stopping audio input...")
        await audio_input.stop()
        logger.info("Audio input stopped. Stream processor finished.")

if __name__ == "__main__":
    try:
        asyncio.run(process_audio_stream())
    except KeyboardInterrupt:
        logger.info("Stream processor interrupted by user.")
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}", exc_info=True)
