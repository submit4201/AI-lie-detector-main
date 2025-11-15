# layer3_feature_vector_assembler.py

from typing import Dict, List, Any
import os
import uuid
from layer2_feature_extraction import extract_features, extract_features_from_data # Added import

def assemble_feature_vector(audio_path: str) -> Dict[str, Any]:
    """
    Extracts acoustic and linguistic features from the given audio path
    and returns a unified feature vector.
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        feature_vector = extract_features(audio_path)
        feature_vector['audio_id'] = str(uuid.uuid4())  # add unique identifier
        return feature_vector

    except Exception as e:
        raise RuntimeError(f"Failed to assemble feature vector: {e}")

def assemble_feature_vector_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """
    Extracts acoustic and linguistic features from the given in-memory audio data
    and returns a unified feature vector.
    """
    try:
        # Use the new function from layer2 that accepts bytes
        feature_vector = extract_features_from_data(audio_data, sample_rate, channels)
        # Add a unique identifier for this chunk/segment if needed, 
        # or this could be handled by the calling orchestrator.
        feature_vector['segment_id'] = str(uuid.uuid4()) 
        return feature_vector
    except Exception as e:
        # Log the exception for better debugging
        # import logging
        # logging.exception("Error assembling feature vector from data")
        raise RuntimeError(f"Failed to assemble feature vector from data: {e}")

# Example usage (for dev/test only)
if __name__ == '__main__':
    path = "path_to_some_audio.wav"
    vector = assemble_feature_vector(path)
    for key, value in vector.items():
        print(f"{key}: {value}")
