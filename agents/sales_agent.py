# agents/sales_agent.py
# Full-featured: RAG-backed, wealth planning, multilingual, sentiment-adaptive

from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from rag.rag_engine import rag_engine
from config import LLM_MODEL_FAST, LLM_TEMPERATURE, LLM_MAX_TOKENS, LOAN_PRODUCTS
from dotenv import load_dotenv
import re

load_dotenv()

class SalesAgent:
    """
    The Negotiator — Heart of the sales process.
    Features:
    - RAG-backed product knowledge
    - Comparative Wealth Planning
    - Predictive Need Analysis
    - Sentiment-adaptive tone
    - Multilingual
    - Best Loan Product Recommendation
    - Dynamic EMI objection handling
    """

    BASE_PERSONA = """You are Aryan, an elite Personal Loan Advisor at Tata Capital — India's most trusted NBFC backed by the Tata Group's 155-year legacy.

YOUR CORE PERSONALITY:
- You are warm, empathetic, and genuinely care about customers' financial wellbeing
- You are a FINANCIAL ADVISOR, not a salesperson — you solve problems with money
- You speak like a knowledgeable friend, not a corporate robot
- You use short sentences. Natural rhythm. Real language.
- You NEVER sound scripted or use canned phrases like "Certainly!" or "Absolutely!"

YOUR SALES INTELLIGENCE:
1. PREDICTIVE NEED ANALYSIS: Infer the loan purpose early. If customer says "daughter's admission" → education. "My knee surgery" → medical. "Flat renovation" → home improvement. "Buy a car" → personal loan (we don't do auto loans separately).
2. BEST PRODUCT RECOMMENDATION: Match purpose to the right Tata Capital product.
3. COMPARATIVE WEALTH PLANNING: Frame loans as financial tools, not debt.
4. OBJECTION HANDLING: respond to exact objections with data from your knowledge base.
5. EMOTIONAL INTELLIGENCE: Respond to stress/urgency with compassion first.

IMPORTANT LOAN RULES TO COMMUNICATE:
- Maximum tenure is 60 months (5 years) for personal loans
- If customer asks for more than 5 years, explain the max is 60 months and suggest that
- Loan amount: ₹50,000 to ₹25,00,000
- Interest Rate: 10.99% to 14.99% per annum

RESPONSE RULES:
- Maximum 3-4 sentences per response. Be crisp.
- Always end with ONE clear question or ONE clear next step
- When the customer agrees to amount AND tenure → say EXACTLY: "Perfect! Let me now verify your identity. Please share your 10-digit registered mobile number with Tata Capital."
- Respond in the SAME LANGUAGE as the customer
- NEVER make up interest rates, fees, or product details"""

    TONE_ADJUSTMENTS = {
        "none":  "Maintain your warm, professional tone.",
        "mild":  "The customer seems a little hesitant. Be extra empathetic. Acknowledge their concern before answering.",
        "high":  "The customer is frustrated. Start with: 'I completely understand your concern, and I apologize if I wasn't clear.' Then gently offer a solution or human escalation.",
    }

    def __init__(self):
        self.llm = ChatGroq(
            model=LLM_MODEL_FAST,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        rag_engine.initialize()

    def chat(self, user_message: str, history: list,
             entry_point_context: str = "",
             sentiment_state: dict = None,
             language: str = "en") -> dict:
        """
        Full sales conversation with RAG context injection.
        Returns: {response, loan_amount, tenure_months, ready_to_proceed}
        """
        # 1. Get relevant knowledge from RAG
        rag_context = rag_engine.query(user_message, n_results=3)

        # 2. Tone instruction based on sentiment
        frustration = (sentiment_state or {}).get("frustration_level", "none")
        tone_instruction = self.TONE_ADJUSTMENTS.get(frustration, self.TONE_ADJUSTMENTS["none"])

        # 3. Language instruction
        lang_instruction = ""
        if language != "en":
            lang_names = {
                "hi": "Hindi", "ta": "Tamil",
                "te": "Telugu", "mr": "Marathi", "bn": "Bengali"
            }
            lang_instruction = f"\nIMPORTANT: Respond ONLY in {lang_names.get(language, 'English')}."

        # 4. Build system prompt
        system = f"""{self.BASE_PERSONA}

CURRENT TONE INSTRUCTION: {tone_instruction}
{lang_instruction}

ENTRY CONTEXT (from customer source): {entry_point_context or 'Direct visitor'}

RELEVANT KNOWLEDGE BASE CONTEXT:
{rag_context}
"""
        # 5. Build message chain
        messages = [SystemMessage(content=system)]
        for turn in history[-8:]:
            messages.append(HumanMessage(content=turn["user"]))
            if turn.get("bot"):
                messages.append(AIMessage(content=turn["bot"]))
        messages.append(HumanMessage(content=user_message))

        # 6. Get LLM response
        response = self.llm.invoke(messages)
        response_text = response.content

        # 7. Extract structured data
        full_history = history + [{"user": user_message, "bot": response_text}]
        loan_amount = self._extract_loan_amount(full_history)
        tenure      = self._extract_tenure(full_history)
        ready       = self._detect_ready_to_proceed(response_text)

        return {
            "response":         response_text,
            "loan_amount":      loan_amount,
            "tenure_months":    tenure,
            "ready_to_proceed": ready,
        }

    def generate_wealth_planning_pitch(self, purpose: str, loan_amount: float,
                                        tenure_months: int, rate: float) -> str:
        """Generate a customized Comparative Wealth Planning narrative"""
        emi = self._calc_emi(loan_amount, rate, tenure_months)
        total_interest = (emi * tenure_months) - loan_amount
        rag_context = rag_engine.query(f"wealth planning investment {purpose}", n_results=2)

        prompt = f"""Based on this financial context: {rag_context}

Generate a 3-sentence Comparative Wealth Planning pitch for:
- Purpose: {purpose}
- Loan Amount: ₹{loan_amount:,.0f}
- Monthly EMI: ₹{emi:,.0f}
- Total Interest Cost: ₹{total_interest:,.0f}

Show the INVESTMENT angle — what does the customer GAIN vs what they pay in interest.
Be specific with numbers. Be compelling but honest. Max 3 sentences."""

        result = self.llm.invoke([HumanMessage(content=prompt)])
        return result.content

    def recommend_product(self, purpose: str, loan_amount: float) -> dict:
        """Recommend the best Tata Capital loan product"""
        purpose_map = {
            "education": "education", "school": "education", "college": "education",
            "medical":   "medical",   "surgery": "medical",  "hospital": "medical",
            "home":      "home_improvement", "renovation": "home_improvement",
            "wedding":   "wedding",   "marriage": "wedding",  "shaadi": "wedding",
            "travel":    "travel",    "trip": "travel",       "vacation": "travel",
        }
        product_key = "personal"
        for kw, pk in purpose_map.items():
            if kw in purpose.lower():
                product_key = pk
                break
        product = LOAN_PRODUCTS.get(product_key, LOAN_PRODUCTS["personal"])
        if loan_amount < product["min"] or loan_amount > product["max"]:
            product = LOAN_PRODUCTS["personal"]
        return {"key": product_key, **product}

    # ── Private Helpers ───────────────────────────────────────────

    def _calc_emi(self, p: float, annual_rate: float, n: int) -> float:
        r = annual_rate / 1200
        return round(p * r * (1 + r)**n / ((1 + r)**n - 1), 2)

    def _extract_loan_amount(self, history: list) -> float | None:
        """Extract loan amount from full conversation history"""
        combined = " ".join([
            t.get("user", "") + " " + t.get("bot", "")
            for t in history
        ])

        patterns = [
            # "10 lakh", "2.5 lakh", "10 lakhs"
            (r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|lakhs?)\b', 100_000),
            # "₹2,00,000" or "₹200000"
            (r'₹\s*([\d,]+)', 1),
            # plain 5-7 digit number like "200000"
            (r'\b(\d{5,7})\b', 1),
        ]

        for pattern, multiplier in patterns:
            for m in re.finditer(pattern, combined, re.IGNORECASE):
                try:
                    val = float(m.group(1).replace(',', '')) * multiplier
                    if 50_000 <= val <= 25_00_000:
                        return val
                except:
                    pass
        return None

    def _extract_tenure(self, history: list) -> int | None:
        """
        Extract tenure from conversation history.
        Caps at 60 months (5 years) — max allowed for personal loans.
        """
        combined = " ".join([
            t.get("user", "") + " " + t.get("bot", "")
            for t in history
        ])

        # Match months first: "24 months", "36 mahine"
        m = re.search(
            r'(\d+)\s*(?:months?|mahine|महीने)\b',
            combined, re.IGNORECASE
        )
        if m:
            val = int(m.group(1))
            val = min(val, 60)   # ← CAP at 60 months
            if val >= 12:
                return val

        # Match years: "2 years", "5 saal", "10 yr"
        m = re.search(
            r'(\d+)\s*(?:years?|saal|साल|yr)\b',
            combined, re.IGNORECASE
        )
        if m:
            val = int(m.group(1)) * 12
            val = min(val, 60)   # ← CAP at 60 months
            if val >= 12:
                return val

        return None

    def _detect_ready_to_proceed(self, bot_response: str) -> bool:
        """Detect if Sales Agent has collected all info and is handing over to KYC"""
        trigger = "please share your 10-digit registered mobile"
        return trigger.lower() in bot_response.lower()
    
    