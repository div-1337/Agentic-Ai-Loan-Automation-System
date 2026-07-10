# agents/underwriting_agent.py
# Full business logic + XAI explainer + Dynamic Risk Workflow

import requests
from config import BUREAU_URL, LOAN_CONFIG

class UnderwritingAgent:
    """
    The Judge — Full credit evaluation with:
    - Exact problem statement business rules
    - XAI: Explainable rejection breakdown
    - Dynamic Risk Workflow: tries alternatives before final rejection
    - Real-time approval confidence score calculation
    """

    def run(self, phone: str, loan_amount: float,
            pre_approved_limit: float,
            monthly_salary: float = None,
            tenure_months: int = 36) -> dict:

        # ── Step 1: Fetch Credit Report ──────────────────────────
        bureau_data = self._fetch_credit_report(phone)
        credit_score = bureau_data["credit_score"]
        conf = LOAN_CONFIG

        # ── Step 2: Build XAI Evaluation Table ──────────────────
        xai = self._build_xai_table(
            credit_score=credit_score,
            loan_amount=loan_amount,
            pre_approved_limit=pre_approved_limit,
            monthly_salary=monthly_salary,
            tenure_months=tenure_months,
            bureau_data=bureau_data,
        )

        # ── Step 3: Apply Business Rules ─────────────────────────

        # RULE A: Credit score below 700 → Reject (hard reject)
        if credit_score < conf["min_credit_score"]:
            xai["final_decision"] = "REJECTED"
            # Dynamic: suggest when they can reapply
            months_to_improve = max(3, int((conf["min_credit_score"] - credit_score) / 5))
            return {
                "decision": "REJECTED",
                "rejection_type": "CREDIT_SCORE",
                "credit_score": credit_score,
                "bureau_data": bureau_data,
                "xai_breakdown": xai,
                "reason": f"Credit score {credit_score}/900 is below minimum threshold of 700.",
                "alternatives": [
                    f"Pay all existing EMIs on time for {months_to_improve} months",
                    "Reduce credit utilization below 30%",
                    f"Avoid new loan applications for {min(months_to_improve, 6)} months",
                    f"Estimated re-application date: {months_to_improve} months from today",
                ],
                "dynamic_suggestion": self._get_lower_amount_suggestion(
                    loan_amount, pre_approved_limit, credit_score, tenure_months
                ),
            }

        # RULE B: Loan > 2x pre-approved limit → Reject (soft reject — suggest lower amount)
        if loan_amount > 2 * pre_approved_limit:
            xai["final_decision"] = "REJECTED"
            max_eligible = 2 * pre_approved_limit
            return {
                "decision": "REJECTED",
                "rejection_type": "EXCEEDS_MAX_LIMIT",
                "credit_score": credit_score,
                "bureau_data": bureau_data,
                "xai_breakdown": xai,
                "reason": f"Requested ₹{loan_amount:,.0f} exceeds maximum eligible ₹{max_eligible:,.0f}.",
                "alternatives": [
                    f"Apply for ₹{pre_approved_limit:,.0f} — instant approval, no documents",
                    f"Apply for ₹{max_eligible:,.0f} with salary slip verification",
                    "Build credit profile and apply for higher amount in 6 months",
                ],
                "dynamic_suggestion": {
                    "instant_approval_amount": pre_approved_limit,
                    "max_with_salary": max_eligible,
                },
            }

        # RULE C: Loan ≤ pre-approved limit → Instant approval
        if loan_amount <= pre_approved_limit:
            rate = self._get_rate(credit_score)
            emi = self._calc_emi(loan_amount, rate, tenure_months)
            processing_fee = round(loan_amount * conf["processing_fee_pct"] / 100, 2)
            xai["final_decision"] = "APPROVED"
            return {
                "decision": "APPROVED",
                "approval_type": "INSTANT",
                "credit_score": credit_score,
                "bureau_data": bureau_data,
                "loan_amount": loan_amount,
                "tenure_months": tenure_months,
                "interest_rate": rate,
                "emi": emi,
                "processing_fee": processing_fee,
                "total_payable": round(emi * tenure_months, 2),
                "total_interest": round((emi * tenure_months) - loan_amount, 2),
                "disbursement_eta": "Within 24 hours",
                "xai_breakdown": xai,
            }

        # RULE D: pre-approved < loan ≤ 2x pre-approved → Need salary slip
        if loan_amount <= 2 * pre_approved_limit:
            if monthly_salary is None:
                xai["final_decision"] = "PENDING_SALARY"
                return {
                    "decision": "NEED_SALARY",
                    "credit_score": credit_score,
                    "bureau_data": bureau_data,
                    "reason": "Loan exceeds instant pre-approval limit. Income verification required.",
                    "xai_breakdown": xai,
                }
            # EMI-to-salary check
            rate = self._get_rate(credit_score)
            emi = self._calc_emi(loan_amount, rate, tenure_months)
            emi_ratio = emi / monthly_salary

            if emi_ratio <= conf["emi_to_salary_limit"]:
                processing_fee = round(loan_amount * conf["processing_fee_pct"] / 100, 2)
                xai["final_decision"] = "APPROVED"
                return {
                    "decision": "APPROVED",
                    "approval_type": "SALARY_VERIFIED",
                    "credit_score": credit_score,
                    "bureau_data": bureau_data,
                    "loan_amount": loan_amount,
                    "tenure_months": tenure_months,
                    "interest_rate": rate,
                    "emi": emi,
                    "monthly_salary": monthly_salary,
                    "emi_to_salary_ratio": round(emi_ratio * 100, 1),
                    "processing_fee": processing_fee,
                    "total_payable": round(emi * tenure_months, 2),
                    "total_interest": round((emi * tenure_months) - loan_amount, 2),
                    "disbursement_eta": "Within 48 hours",
                    "xai_breakdown": xai,
                }
            else:
                xai["final_decision"] = "REJECTED"
                # Dynamic: calculate what tenure would make EMI ≤ 50% of salary
                suggested_tenure = self._find_viable_tenure(
                    loan_amount, rate, monthly_salary, conf["emi_to_salary_limit"]
                )
                suggested_amount = self._find_viable_amount(
                    monthly_salary, rate, tenure_months, conf["emi_to_salary_limit"]
                )
                return {
                    "decision": "REJECTED",
                    "rejection_type": "EMI_EXCEEDS_SALARY",
                    "credit_score": credit_score,
                    "bureau_data": bureau_data,
                    "loan_amount": loan_amount,
                    "emi": emi,
                    "monthly_salary": monthly_salary,
                    "emi_to_salary_ratio": round(emi_ratio * 100, 1),
                    "xai_breakdown": xai,
                    "reason": f"EMI ₹{emi:,.0f} is {emi_ratio*100:.1f}% of salary ₹{monthly_salary:,.0f} (max 50%).",
                    "alternatives": [
                        f"Extend tenure to {suggested_tenure} months → EMI becomes viable",
                        f"Reduce loan to ₹{suggested_amount:,.0f} at current tenure",
                        f"Apply for ₹{pre_approved_limit:,.0f} (instant approval, no salary check)",
                    ],
                    "dynamic_suggestion": {
                        "viable_tenure": suggested_tenure,
                        "viable_amount": suggested_amount,
                        "instant_approval_amount": pre_approved_limit,
                    },
                }

    # ── Helpers ──────────────────────────────────────────────────

    def _fetch_credit_report(self, phone: str) -> dict:
        try:
            r = requests.get(f"{BUREAU_URL}/bureau/score/{phone}", timeout=5)
            return r.json()
        except:
            return {"credit_score": 720, "active_loans": 0, "total_outstanding": 0,
                    "payment_history": "Good", "credit_age_years": 3, "hard_inquiries_6m": 1}

    def _get_rate(self, score: int) -> float:
        for threshold, rate in sorted(LOAN_CONFIG["interest_rates"].items(), reverse=True):
            if score >= threshold:
                return rate
        return LOAN_CONFIG["interest_rates"][0]

    def _calc_emi(self, p: float, annual_rate: float, n: int) -> float:
        r = annual_rate / 1200
        return round(p * r * (1 + r)**n / ((1 + r)**n - 1), 2)

    def _build_xai_table(self, credit_score, loan_amount, pre_approved_limit,
                          monthly_salary, tenure_months, bureau_data) -> dict:
        """Build the Explainable AI breakdown that shows customer exactly how decision was made"""
        rate = self._get_rate(credit_score) if credit_score >= 700 else 14.99
        emi = self._calc_emi(loan_amount, rate, tenure_months)
        emi_ratio = (emi / monthly_salary * 100) if monthly_salary else None

        return {
            "credit_score": {
                "value": credit_score,
                "max": 900,
                "status": "✅ Pass" if credit_score >= 700 else "❌ Fail",
                "threshold": "≥ 700",
                "detail": bureau_data.get("payment_history", "N/A")
            },
            "loan_vs_limit": {
                "requested": loan_amount,
                "pre_approved": pre_approved_limit,
                "max_eligible": 2 * pre_approved_limit,
                "status": ("✅ Instant" if loan_amount <= pre_approved_limit
                            else "🟡 Needs Salary" if loan_amount <= 2*pre_approved_limit
                            else "❌ Exceeds Max"),
                "detail": f"{loan_amount/pre_approved_limit:.1f}x of pre-approved limit"
            },
            "emi_check": {
                "emi_amount": emi,
                "monthly_salary": monthly_salary,
                "ratio_pct": round(emi_ratio, 1) if emi_ratio else "N/A (salary not provided)",
                "status": ("✅ Pass" if emi_ratio and emi_ratio <= 50
                            else "❌ Fail" if emi_ratio
                            else "⏳ Pending salary"),
                "threshold": "EMI ≤ 50% of salary"
            },
            "bureau_details": {
                "active_loans": bureau_data.get("active_loans", "N/A"),
                "outstanding": bureau_data.get("total_outstanding", "N/A"),
                "credit_age": f"{bureau_data.get('credit_age_years', 0)} years",
                "hard_inquiries": bureau_data.get("hard_inquiries_6m", "N/A"),
            },
            "final_decision": "PENDING",
        }

    def _get_lower_amount_suggestion(self, loan_amount, pre_approved_limit,
                                      credit_score, tenure_months) -> dict:
        """Even on credit rejection, suggest what they CAN get when score improves"""
        return {
            "note": "Once your credit score crosses 700, you'll be eligible for:",
            "instant_amount": pre_approved_limit,
            "max_amount": 2 * pre_approved_limit,
        }

    def _find_viable_tenure(self, loan_amount, rate, salary, max_ratio) -> int:
        """Find minimum tenure where EMI ≤ max_ratio of salary"""
        for t in range(12, 61, 6):
            emi = self._calc_emi(loan_amount, rate, t)
            if emi / salary <= max_ratio:
                return t
        return 60

    def _find_viable_amount(self, salary, rate, tenure, max_ratio) -> float:
        """Find maximum loan amount where EMI ≤ max_ratio of salary"""
        max_emi = salary * max_ratio
        # Reverse EMI formula to find principal
        r = rate / 1200
        p = max_emi * ((1 + r)**tenure - 1) / (r * (1 + r)**tenure)
        return round(p / 1000) * 1000   # Round to nearest 1000