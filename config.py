# config.py — Single source of truth for all constants

# ── Loan Rules (from Problem Statement) ─────────────────────────
LOAN_CONFIG = {
    "min_amount": 50_000,
    "max_amount": 25_00_000,
    "min_tenure_months": 12,
    "max_tenure_months": 60,
    "min_credit_score": 700,
    "emi_to_salary_limit": 0.50,    # EMI must be ≤ 50% of salary
    "interest_rates": {             # Based on credit score bands
        800: 10.99,
        750: 11.99,
        720: 12.99,
        700: 13.99,
        0:   14.99,
    },
    "processing_fee_pct": 2.5,      # % of loan amount
    "default_tenure": 36,
}

# ── Tata Capital Loan Products ───────────────────────────────────
LOAN_PRODUCTS = {
    "personal": {
        "name": "Personal Loan",
        "min": 50_000, "max": 25_00_000,
        "rate_range": "10.99% - 14.99%",
        "tenure": "12-60 months",
        "usp": "No collateral, instant approval"
    },
    "home_improvement": {
        "name": "Home Improvement Loan",
        "min": 1_00_000, "max": 25_00_000,
        "rate_range": "10.99% - 13.99%",
        "tenure": "12-84 months",
        "usp": "Lower rates for home renovation"
    },
    "medical": {
        "name": "Medical Emergency Loan",
        "min": 50_000, "max": 10_00_000,
        "rate_range": "10.99% - 12.99%",
        "tenure": "6-48 months",
        "usp": "Disbursed within 4 hours"
    },
    "education": {
        "name": "Education Loan",
        "min": 1_00_000, "max": 20_00_000,
        "rate_range": "9.99% - 12.99%",
        "tenure": "12-84 months",
        "usp": "Moratorium period available"
    },
    "wedding": {
        "name": "Wedding Loan",
        "min": 2_00_000, "max": 25_00_000,
        "rate_range": "11.99% - 14.99%",
        "tenure": "12-60 months",
        "usp": "Quick disbursal, flexible EMIs"
    },
    "travel": {
        "name": "Travel Loan",
        "min": 50_000, "max": 5_00_000,
        "rate_range": "11.99% - 14.99%",
        "tenure": "12-36 months",
        "usp": "Includes travel insurance option"
    },
}

# ── Entry Point → Loan Purpose Mapping ──────────────────────────
ENTRY_POINT_MAP = {
    "education_ad":    {"purpose": "education", "product": "education", "greeting_hook": "education financing"},
    "medical_ad":      {"purpose": "medical",   "product": "medical",   "greeting_hook": "medical emergency funds"},
    "home_ad":         {"purpose": "home",      "product": "home_improvement", "greeting_hook": "home renovation"},
    "wedding_ad":      {"purpose": "wedding",   "product": "wedding",   "greeting_hook": "wedding financing"},
    "travel_ad":       {"purpose": "travel",    "product": "travel",    "greeting_hook": "travel financing"},
    "email_campaign":  {"purpose": "personal",  "product": "personal",  "greeting_hook": "your pre-approved loan offer"},
    "sms_campaign":    {"purpose": "personal",  "product": "personal",  "greeting_hook": "your exclusive loan offer"},
    "direct":          {"purpose": None,        "product": "personal",  "greeting_hook": "your financial goals"},
}

# ── Languages ────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": {"name": "English",    "gtts_lang": "en", "gtts_tld": "co.in", "flag": "🇮🇳"},
    "hi": {"name": "हिन्दी",      "gtts_lang": "hi", "gtts_tld": "com",   "flag": "🇮🇳"},
    "ta": {"name": "தமிழ்",       "gtts_lang": "ta", "gtts_tld": "com",   "flag": "🇮🇳"},
    "te": {"name": "తెలుగు",      "gtts_lang": "te", "gtts_tld": "com",   "flag": "🇮🇳"},
    "mr": {"name": "मराठी",       "gtts_lang": "mr", "gtts_tld": "com",   "flag": "🇮🇳"},
    "bn": {"name": "বাংলা",       "gtts_lang": "bn", "gtts_tld": "com",   "flag": "🇮🇳"},
}

# ── Approval Score Weights ───────────────────────────────────────
# Real-time approval meter calculation (not just progress steps)
APPROVAL_SCORE_WEIGHTS = {
    "credit_score_800_plus":     40,
    "credit_score_750_799":      35,
    "credit_score_720_749":      28,
    "credit_score_700_719":      20,
    "within_preapproved":        25,
    "within_2x_preapproved":     15,
    "kyc_verified":              20,
    "emi_within_40pct_salary":   15,
    "emi_within_50pct_salary":   10,
    "existing_customer":          5,
    "base":                      10,    # Everyone starts at 10%
}

# ── Cross-Sell Products (Post-Sanction LTV) ──────────────────────
CROSS_SELL_PRODUCTS = [
    {
        "name": "Tata Capital Credit Card",
        "benefit": "Earn 5X rewards on loan EMI payments",
        "urgency": "Limited time offer for loan customers"
    },
    {
        "name": "Personal Accident Insurance",
        "benefit": "EMI protection up to ₹50L at ₹199/month",
        "urgency": "Protect your family from loan liability"
    },
    {
        "name": "Tata Capital Home Loan Top-Up",
        "benefit": "Additional funds at your current rate",
        "urgency": "Exclusive for existing Tata Capital customers"
    },
]

# ── Mock API URLs ────────────────────────────────────────────────
CRM_URL    = "http://localhost:8001"
BUREAU_URL = "http://localhost:8002"

# ── LLM Config ───────────────────────────────────────────────────
LLM_MODEL_FAST   = "llama-3.1-8b-instant"       # For sales chat (fast responses)
LLM_MODEL_SMART  = "llama-3.3-70b-versatile"    # For complex reasoning
LLM_TEMPERATURE  = 0.72
LLM_MAX_TOKENS   = 350

