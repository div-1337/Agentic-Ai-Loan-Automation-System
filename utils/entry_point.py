# utils/entry_point.py
# Detect user entry point from URL params → personalize greeting

from config import ENTRY_POINT_MAP

def get_entry_context(source: str = None) -> dict:
    """
    Parse URL ?source= parameter to personalize the conversation.
    Example: ?source=education_ad → greet with education loan offer
    """
    if not source:
        return ENTRY_POINT_MAP["direct"]
    return ENTRY_POINT_MAP.get(source.lower(), ENTRY_POINT_MAP["direct"])

def build_personalized_greeting(entry_context: dict,
                                  customer_name: str = None) -> str:
    hook = entry_context.get("greeting_hook", "your financial goals")
    purpose = entry_context.get("purpose")
    name_part = f" {customer_name.split()[0]}" if customer_name else ""

    if purpose:
        product_hints = {
            "education": "We have special education financing at rates starting 9.99% PA.",
            "medical":   "We offer medical emergency loans disbursed within 4 hours.",
            "home":      "Our home improvement loan starts at 10.99% with no collateral.",
            "wedding":   "We offer wedding loans up to ₹25 lakhs with flexible EMIs.",
            "travel":    "Our travel loan comes with complimentary travel insurance.",
        }
        hint = product_hints.get(purpose, "")
        return (f"Hello{name_part}! 🙏 I'm Aryan from Tata Capital. I see you're interested in "
                f"{hook}. {hint} I'd love to help you find the perfect solution — what's on your mind?")
    else:
        return (f"Hello{name_part}! 🙏 I'm Aryan, your Personal Loan Advisor at Tata Capital — "
                f"India's most trusted NBFC backed by the Tata Group. You have an exclusive pre-approved "
                f"loan offer waiting for you. May I know what you'd like to use the funds for?")