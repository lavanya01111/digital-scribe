# ai_service/app/models/lang_detect.py
# Detects the language of a text string.
# Uses langdetect (free, no API key).
# Supports 55+ languages.

from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    """
    Returns ISO 639-1 language code e.g. "en", "fr", "ar", "de".
    Falls back to "en" if detection fails.
    """
    try:
        return detect(text)
    except LangDetectException:
        # If text is too short or ambiguous, default to English
        return "en"
