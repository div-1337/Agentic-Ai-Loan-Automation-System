# utils/language.py
# Language detection + multilingual instruction generation

from langdetect import detect, DetectorFactory
from config import SUPPORTED_LANGUAGES

DetectorFactory.seed = 42   # Deterministic detection

def detect_language(text: str) -> str:
    """Detect language code from user message. Returns 'en' as fallback."""
    if not text or len(text.strip()) < 5:
        return "en"
    try:
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except:
        return "en"

def get_language_instruction(lang_code: str) -> str:
    """Get LLM instruction for the detected language"""
    lang = SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])
    if lang_code == "en":
        return "Respond in clear, professional Indian English."
    return f"CRITICAL: Respond ONLY in {lang['name']}. Do not switch to English under any circumstances."

def get_gtts_config(lang_code: str) -> dict:
    lang = SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])
    return {"lang": lang["gtts_lang"], "tld": lang["gtts_tld"]}

def format_amount_in_language(amount: float, lang_code: str) -> str:
    """Format ₹ amount in Indian number system (lakhs/crores)"""
    if amount >= 10_00_000:
        return f"₹{amount/10_00_000:.1f} Crore"
    elif amount >= 1_00_000:
        return f"₹{amount/1_00_000:.1f} Lakh"
    else:
        return f"₹{amount:,.0f}"