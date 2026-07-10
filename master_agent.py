# master_agent.py — The Orchestrator. Routes everything.

import re
from agents.sales_agent import SalesAgent
from agents.sentiment_agent import SentimentAgent
from agents.verification_agent import VerificationAgent
from agents.underwriting_agent import UnderwritingAgent
from agents.sanction_generator import SanctionLetterGenerator
from agents.ltv_agent import LTVAgent
from utils.language import detect_language
from utils.entry_point import get_entry_context, build_personalized_greeting
from config import APPROVAL_SCORE_WEIGHTS

class MasterAgent:
    """
    The Orchestrator.

    State Machine:
    GREETING → SALES → KYC_COLLECTION → VERIFICATION →
    UNDERWRITING → SALARY_UPLOAD → DECISION → POST_SANCTION | REJECTED
    """

    def __init__(self, source: str = None):
        # Initialize all agents
        self.sales         = SalesAgent()
        self.sentiment     = SentimentAgent()
        self.verifier      = VerificationAgent()
        self.underwriter   = UnderwritingAgent()
        self.printer       = SanctionLetterGenerator()
        self.ltv           = LTVAgent()

        # Session state
        self.state         = "GREETING"
        self.ctx           = {}
        self.history       = []
        self.pdf_path      = None
        self.approval_pct  = 5
        self.current_lang  = "en"
        self.entry_context = get_entry_context(source)
        self.sentiment_state = {"action": "continue", "frustration_level": "none"}
        self.agent_log     = []
        self.loan_purpose  = None
        self.alternative_offered = False

    def process(self, user_message: str) -> dict:
        # ── 1. Language Detection ────────────────────────────────
        if user_message and len(user_message) > 4 and user_message != "__start__" and user_message != "__auto__":
            detected = detect_language(user_message)
            if detected != "en":
                self.current_lang = detected

        # ── 2. Sentiment Analysis ────────────────────────────────
        if user_message and self.state in ["SALES", "KYC_COLLECTION"] and user_message not in ["__start__", "__auto__"]:
            self.sentiment_state = self.sentiment.analyze(user_message)
            self._log_agent("SentimentAgent", self.sentiment_state)

            if self.sentiment_state.get("human_escalation_requested"):
                return self._handle_escalation()

        # ── 3. Route to Current State ────────────────────────────
        if self.state == "GREETING":           return self._greeting()
        if self.state == "SALES":              return self._sales(user_message)
        if self.state == "KYC_COLLECTION":     return self._kyc_collect(user_message)
        if self.state == "VERIFICATION":       return self._verify()
        if self.state == "UNDERWRITING":       return self._underwrite()
        if self.state == "SALARY_UPLOAD":      return self._salary_received(user_message)
        if self.state == "POST_SANCTION":      return self._post_sanction_engage(user_message)

        return self._build_response("Session complete. Thank you for choosing Tata Capital!")

    # ── Stage Handlers ───────────────────────────────────────────

    def _greeting(self) -> dict:
        greeting = build_personalized_greeting(self.entry_context)
        self.state = "SALES"
        self.approval_pct = APPROVAL_SCORE_WEIGHTS["base"]
        return self._build_response(
            message=greeting,
            show_approval_meter=True,
            entry_hook=self.entry_context.get("greeting_hook"),
        )

    def _sales(self, user_msg: str) -> dict:
        result = self.sales.chat(
            user_message=user_msg,
            history=self.history,
            entry_point_context=str(self.entry_context),
            sentiment_state=self.sentiment_state,
            language=self.current_lang,
        )
        self._log_agent("SalesAgent", {"ready": result["ready_to_proceed"],
                                        "loan_amount": result["loan_amount"]})

        if result.get("loan_amount"):
            self.ctx["loan_amount"] = result["loan_amount"]
        if result.get("tenure_months"):
            self.ctx["tenure_months"] = result["tenure_months"]

        self.history.append({"user": user_msg, "bot": result["response"]})
        self.approval_pct = min(35, self.approval_pct + 5)

        if not self.loan_purpose:
            self.loan_purpose = self._detect_purpose(user_msg + " " + " ".join(
                [h.get("user", "") for h in self.history[-3:]]
            ))

        if result.get("ready_to_proceed"):
            self.state = "KYC_COLLECTION"
            wealth_pitch = None
            if self.ctx.get("loan_amount") and self.loan_purpose:
                try:
                    wealth_pitch = self.sales.generate_wealth_planning_pitch(
                        purpose=self.loan_purpose,
                        loan_amount=self.ctx["loan_amount"],
                        tenure_months=self.ctx.get("tenure_months", 36),
                        rate=12.99,
                    )
                except:
                    wealth_pitch = None

            return self._build_response(
                message=result["response"],
                stage_change="KYC_COLLECTION",
                wealth_pitch=wealth_pitch,
                show_approval_meter=True,
            )

        return self._build_response(
            message=result["response"],
            show_approval_meter=True,
            sentiment=self.sentiment_state,
        )

    def _kyc_collect(self, user_msg: str) -> dict:
        phone = re.sub(r'\D', '', user_msg)
        if len(phone) == 10:
            self.ctx["phone"] = phone
            self.state = "VERIFICATION"
            # ── FIXED: directly call _verify() instead of auto_proceed ──
            return self._verify()
        elif len(phone) > 0 and len(phone) != 10:
            return self._build_response(
                message=f"That looks like it has {len(phone)} digits. Please enter your **10-digit** registered mobile number.",
            )
        return self._build_response(
            message="Please share your **10-digit registered mobile number** to proceed.",
        )

    def _verify(self) -> dict:
        result = self.verifier.run(self.ctx["phone"])
        self._log_agent("VerificationAgent", result)

        if result["status"] == "VERIFIED":
            self.ctx["customer"] = result["customer"]
            self.ctx["pre_approved_limit"] = result["customer"]["pre_approved_limit"]
            is_existing = result.get("is_existing", False)

            self.approval_pct += APPROVAL_SCORE_WEIGHTS["kyc_verified"]
            if is_existing:
                self.approval_pct += APPROVAL_SCORE_WEIGHTS["existing_customer"]

            # ── FIXED: directly call _underwrite() instead of auto_proceed ──
            self.state = "UNDERWRITING"
            return self._underwrite()

        else:
            self.state = "DONE"
            return self._build_response(
                message=(f"⚠️ **Verification Issue:** {result['message']}\n\n"
                          f"**What to do:** {result.get('suggestion', 'Please contact our helpline.')}\n\n"
                          f"📞 Helpline: **1860-267-6060** | Available 9 AM – 9 PM"),
                stage_change="FAILED",
                decision="FAILED",
            )

    def _underwrite(self) -> dict:
        if not self.ctx.get("loan_amount"):
            self.ctx["loan_amount"] = self.ctx.get("pre_approved_limit", 200000)
        if not self.ctx.get("tenure_months"):
            self.ctx["tenure_months"] = 36

        result = self.underwriter.run(
            phone=self.ctx["phone"],
            loan_amount=self.ctx["loan_amount"],
            pre_approved_limit=self.ctx["pre_approved_limit"],
            monthly_salary=self.ctx.get("monthly_salary"),
            tenure_months=self.ctx["tenure_months"],
        )
        self._log_agent("UnderwritingAgent", {"decision": result["decision"]})
        self.ctx["uw_result"] = result

        # ── APPROVED ─────────────────────────────────────────────
        if result["decision"] == "APPROVED":
            score = result["credit_score"]
            if score >= 800:   self.approval_pct = 100
            elif score >= 750: self.approval_pct = 95
            else:              self.approval_pct = 90

            self.pdf_path = self.printer.run(
                customer=self.ctx["customer"],
                loan_details=result,
                output_path=f"sanction_{self.ctx['phone']}.pdf",
            )
            self.state = "POST_SANCTION"
            cust = self.ctx["customer"]
            approval_type_msg = ("⚡ *Instant Approval* — No documents needed!"
                                  if result.get("approval_type") == "INSTANT"
                                  else "✅ *Approved* — Income verified successfully!")

            return self._build_response(
                message=(
                    f"🎉 **Congratulations, {cust['name'].split()[0]}!**\n\n"
                    f"Your Personal Loan is **APPROVED!** {approval_type_msg}\n\n"
                    f"**📋 Loan Details:**\n"
                    f"- Amount: **₹{result['loan_amount']:,.0f}**\n"
                    f"- Monthly EMI: **₹{result['emi']:,.2f}**\n"
                    f"- Interest Rate: **{result['interest_rate']}% p.a.**\n"
                    f"- Tenure: **{result['tenure_months']} months**\n"
                    f"- Credit Score: **{result['credit_score']}/900** ⭐\n"
                    f"- Total Interest: ₹{result.get('total_interest', 0):,.0f}\n\n"
                    f"📄 Your **Sanction Letter** is ready to download!"
                ),
                stage_change="POST_SANCTION",
                decision="APPROVED",
                pdf_path=self.pdf_path,
                xai_breakdown=result.get("xai_breakdown"),
                uw_result=result,
                show_approval_meter=True,
            )

        # ── NEED SALARY ───────────────────────────────────────────
        elif result["decision"] == "NEED_SALARY":
            self.approval_pct = 65
            self.state = "SALARY_UPLOAD"
            return self._build_response(
                message=(
                    f"📊 **Credit Score: {result['credit_score']}/900** ✅ — Great score!\n\n"
                    f"Your loan of **₹{self.ctx['loan_amount']:,.0f}** slightly exceeds your instant "
                    f"pre-approval limit of ₹{self.ctx['pre_approved_limit']:,.0f}. "
                    f"This is completely normal and just needs a quick income verification.\n\n"
                    f"Please **upload your latest salary slip** or enter your monthly salary below."
                ),
                stage_change="SALARY_UPLOAD",
                require_upload=True,
                xai_breakdown=result.get("xai_breakdown"),
                show_approval_meter=True,
            )

        # ── REJECTED ─────────────────────────────────────────────
        else:
            self.approval_pct = 0
            self.state = "DONE"
            alternatives = result.get("alternatives", [])
            dynamic_suggestion = result.get("dynamic_suggestion", {})

            alternative_msg = ""
            if dynamic_suggestion and not self.alternative_offered:
                self.alternative_offered = True
                if dynamic_suggestion.get("instant_approval_amount"):
                    amt = dynamic_suggestion["instant_approval_amount"]
                    alternative_msg = (
                        f"\n\n**💡 However!** You qualify for an **instant approval of "
                        f"₹{amt:,.0f}** with no additional documents. "
                        f"Would you like to proceed with this amount?"
                    )

            return self._build_response(
                message=(
                    f"😔 I'm sorry, we're unable to approve this specific loan request.\n\n"
                    f"**Reason:** {result['reason']}"
                    f"{alternative_msg}"
                ),
                stage_change="REJECTED",
                decision="REJECTED",
                xai_breakdown=result.get("xai_breakdown"),
                alternatives=alternatives,
                dynamic_suggestion=dynamic_suggestion,
                show_approval_meter=True,
            )

    def _salary_received(self, user_msg: str) -> dict:
        salary_digits = re.sub(r'[^\d]', '', user_msg)
        if salary_digits and int(salary_digits) > 5000:
            self.ctx["monthly_salary"] = float(salary_digits)
        else:
            self.ctx["monthly_salary"] = 80000

        self.state = "UNDERWRITING"
        return self._underwrite()

    def _post_sanction_engage(self, user_msg: str) -> dict:
        try:
            ltv_data = self.ltv.generate_post_sanction_dashboard(
                customer=self.ctx["customer"],
                loan_details=self.ctx["uw_result"],
                loan_purpose=self.loan_purpose or "personal",
            )
        except:
            ltv_data = None

        self.state = "DONE"
        return self._build_response(
            message=(
                "🌟 **One More Thing Before You Go!**\n\n"
                "We've prepared your EMI schedule and some exclusive offers. "
                "Setting up auto-debit today ensures you never miss a payment!"
            ),
            ltv_data=ltv_data,
            pdf_path=self.pdf_path,
        )

    def _handle_escalation(self) -> dict:
        self.state = "ESCALATED"
        return self._build_response(
            message=(
                "👤 **Connecting you to a Human Advisor...**\n\n"
                "I completely understand — sometimes it's better to speak with a person.\n\n"
                "**Contact Options:**\n"
                "📞 Call us: **1860-267-6060** (9 AM – 9 PM)\n"
                "💬 WhatsApp: **+91 97799 75000**\n"
                "📧 Email: **customercare@tatacapital.com**"
            ),
            stage_change="ESCALATED",
            human_escalation=True,
        )

    # ── Helpers ──────────────────────────────────────────────────

    def _build_response(self, message: str, **kwargs) -> dict:
        return {
            "message": message,
            "state": self.state,
            "approval_pct": min(100, max(0, self.approval_pct)),
            "current_lang": self.current_lang,
            "agent_log": self.agent_log.copy(),
            "sentiment": self.sentiment_state,
            **kwargs,
        }

    def _log_agent(self, agent_name: str, result: dict):
        self.agent_log.append({"agent": agent_name, "result": result})

    def _detect_purpose(self, text: str) -> str:
        keywords = {
            "education": ["education", "college", "school", "degree", "course", "fees", "admission", "study"],
            "medical":   ["medical", "surgery", "hospital", "health", "treatment", "doctor", "operation", "emergency"],
            "home":      ["home", "house", "renovation", "repair", "interior", "kitchen", "bathroom", "flat"],
            "wedding":   ["wedding", "marriage", "shaadi", "ceremony", "reception", "function"],
            "travel":    ["travel", "trip", "vacation", "holiday", "tour", "abroad", "international"],
            "business":  ["business", "shop", "startup", "inventory", "working capital", "office"],
        }
        text_lower = text.lower()
        for purpose, words in keywords.items():
            if any(w in text_lower for w in words):
                return purpose
        return "personal"
    

    