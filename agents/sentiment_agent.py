# agents/sentiment_agent.py
# Uses free HuggingFace model — no API key, runs locally

from transformers import pipeline
import re

class SentimentAgent:
    """
    Analyzes customer sentiment in real-time.
    Signals the Master Agent to:
    - Soften approach if frustrated
    - Escalate to human if very angry
    - Accelerate if highly positive/eager
    """

    SENTIMENT_LABELS = {
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "NEUTRAL":  "neutral",
        "LABEL_0":  "negative",   # some models use numeric labels
        "LABEL_1":  "neutral",
        "LABEL_2":  "positive",
    }

    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is None:
            # distilbert-based: fast, free, offline after first download
            self._model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True, max_length=512
            )

    def analyze(self, text: str) -> dict:
        """
        Returns:
        {
            "label": "positive" | "neutral" | "negative",
            "score": 0.0-1.0,
            "frustration_level": "none" | "mild" | "high",
            "action": "continue" | "soften" | "escalate"
        }
        """
        self._load()
        # Check for explicit frustration keywords first (faster than model)
        frustration_keywords = [
            "waste of time", "useless", "terrible", "disgusting", "scam",
            "fraud", "worst", "pathetic", "hate", "speak to human",
            "talk to person", "real agent", "manager", "complaint"
        ]
        text_lower = text.lower()
        explicit_frustration = any(kw in text_lower for kw in frustration_keywords)

        human_escalation = any(kw in text_lower for kw in
                                ["speak to human", "talk to person", "real agent",
                                 "human agent", "customer care", "call me"])

        result = self._model(text[:512])[0]
        raw_label = result["label"]
        score = result["score"]
        label = self.SENTIMENT_LABELS.get(raw_label, "neutral")

        # Override with explicit signals
        if explicit_frustration or (label == "negative" and score > 0.85):
            frustration_level = "high"
        elif label == "negative" and score > 0.65:
            frustration_level = "mild"
        else:
            frustration_level = "none"

        # Determine action for Master Agent
        if human_escalation:
            action = "human_escalation_requested"
        elif frustration_level == "high":
            action = "escalate"
        elif frustration_level == "mild":
            action = "soften"
        else:
            action = "continue"

        return {
            "label": label,
            "score": round(score, 3),
            "frustration_level": frustration_level,
            "action": action,
            "human_escalation_requested": human_escalation,
        }

    def analyze_conversation(self, history: list) -> dict:
        """Analyze the last 3 turns for overall sentiment trend"""
        recent = history[-3:] if len(history) >= 3 else history
        user_texts = " ".join([t.get("user", "") for t in recent])
        if not user_texts.strip():
            return {"label": "neutral", "score": 0.5,
                    "frustration_level": "none", "action": "continue",
                    "human_escalation_requested": False}
        return self.analyze(user_texts)
    
    