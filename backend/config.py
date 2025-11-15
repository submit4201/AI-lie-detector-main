import os
import logging
import dotenv
from pathlib import Path

# Load environment variables from a .env file if present (fall back to repo root)
repo_env = Path(__file__).resolve().parents[1] / '.env'
print(f"Looking for .env file at: {repo_env}")
if repo_env.exists():
    dotenv.load_dotenv(str(repo_env))
else:
    # fallback to default search behavior
    dotenv.load_dotenv()

# Set up logging for config module
logger = logging.getLogger(__name__)

# Gemini API Key Configuration
# IMPORTANT: It's highly recommended to set your actual API key as an environment variable
# and not hardcode it here, especially for production.
# The fallback key "your_fallback_key_here_or_None" is a placeholder and should be replaced
# or removed if you ensure the environment variable is always set.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Gemini model selection (override via environment variable if needed)
# Common options include: "gemini-1.5", "gemini-1.5-research", "text-bison-001" depending on availability.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

# Per-task Gemini model configuration (can be overridden via environment variables)
# Recommended defaults based on project guidance:
# - Transcription: gemini-3.5-flash (fast, audio-capable)
# - Structured/analysis: gemini-2.5 (strong structured output)
GEMINI_MODEL_TRANSCRIBE = os.getenv("GEMINI_MODEL_TRANSCRIBE", "gemini-2.5-flash-lite")
GEMINI_MODEL_ANALYSIS = os.getenv("GEMINI_MODEL_ANALYSIS", "gemini-2.5-pro")
GEMINI_MODEL_STRUCTURED = os.getenv("GEMINI_MODEL_STRUCTURED", "gemini-2.5-pro")

# Comma-separated list of fallback models to try (in order) when preferred model is unavailable.
# Put pro first, then flash-lite, then flash, then general aliases.
_fallback_env = os.getenv(
    "GEMINI_FALLBACK_MODELS",
    "gemini-2.5-pro,gemini-2.5-flash-lite,gemini-2.5-flash,gemini-flash-latest,gemini-2.5,gemini-1.5",
)
GEMINI_FALLBACK_MODELS = [m.strip() for m in _fallback_env.split(",") if m.strip()]

# Initialize the emotion classifier pipeline lazily and make the import optional
# so the backend can be imported even if `transformers` isn't installed.
EMOTION_CLASSIFIER = None
try:
    from transformers import pipeline

    # Set transformers to offline mode if TRANSFORMERS_OFFLINE environment variable is set
    if os.environ.get('TRANSFORMERS_OFFLINE', '0') == '1':
        logger.info("TRANSFORMERS_OFFLINE is set, skipping emotion classifier initialization.")
        EMOTION_CLASSIFIER = None
    else:
        try:
            EMOTION_CLASSIFIER = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=7,
                return_all_scores=True,
            )
        except Exception as e:
            logger.error(f"Error initializing Hugging Face emotion classifier: {e}")
            logger.warning("Emotion analysis will not be available. Ensure the model is accessible and transformers library is correctly installed.")
            EMOTION_CLASSIFIER = None
except ImportError:
    logger.warning("transformers not installed; EMOTION_CLASSIFIER will be None.")
    EMOTION_CLASSIFIER = None

if not GEMINI_API_KEY: # Check if API key is set
    logger.warning("GEMINI_API_KEY is not set. Gemini API calls may fail.")

# Note on top_k vs return_all_scores:
# In Hugging Face pipelines, if return_all_scores=True, it returns scores for all classes.
# top_k then would mean it returns all scores but perhaps limits the list to k items if k is less than total classes.
# The original main.py had `top_k=7, return_all_scores=True`. This usually means it will return all scores for the 7 classes
# if the model has more than 7 classes, or all classes if it has <= 7.
# For 'j-hartmann/emotion-english-distilroberta-base', it typically has 7 emotions (anger, disgust, fear, joy, neutral, sadness, surprise).
# So, `return_all_scores=True` effectively does what `top_k=7` would do if the model indeed has exactly 7 classes.
# Keeping both for consistency with the original code's apparent intent.
# If the model "j-hartmann/emotion-english-distilroberta-base" has exactly 7 labels,
# then `return_all_scores=True` is sufficient, and `top_k=7` is redundant but harmless.
# If it had, say, 20 labels, `top_k=7` would restrict the output to the top 7, even with `return_all_scores=True`.
# For this specific model, it outputs 7 emotions, so `return_all_scores=True` is fine.
# I'll keep `return_all_scores=True` and remove `top_k=7` for clarity as it's effectively returning all.
# Re-checking main.py: it was `top_k=None` implicitly if not set, and `return_all_scores=True` was used.
# The transformers docs say:
# top_k (:obj:`int`, `optional`, defaults to 1): The number of top labels that will be returned by the pipeline.
# If the provided number is `None`, the number of labels is determined by the model's configuration.
# return_all_scores (:obj:`bool`, `optional`, defaults to :obj:`False`): Whether or not to return all scores of all labels.
# The original code in main.py had:
# emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=7, return_all_scores=True)
# This is slightly confusing. If return_all_scores is True, top_k is usually ignored or means something else.
# For clarity and standard usage, typically you use one or the other.
# Given the model has 7 emotions, `return_all_scores=True` will return all 7.
# Let's stick to what was in main.py for now.
EMOTION_CLASSIFIER_CONFIG = {
    "pipeline_task": "text-classification",
    "model_name": "j-hartmann/emotion-english-distilroberta-base",
    "top_k": 7, # As it was in main.py
    "return_all_scores": True # As it was in main.py
}

# The emotion classifier pipeline is initialized in the try block above using EMOTION_CLASSIFIER_CONFIG.
logging.info("Configuration module loaded successfully.")
# import models
logging.info(f"Gemini API Key Loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
logging.info(f"Emotion Classifier Loaded: {'Yes' if EMOTION_CLASSIFIER else 'No'}")
