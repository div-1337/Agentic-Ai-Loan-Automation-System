# agents/ltv_agent.py
# Post-Sanction LTV Management: EMI Calendar + Cross-Sell Recommendations

from datetime import date
from dateutil.relativedelta import relativedelta
from config import CROSS_SELL_PRODUCTS, LOAN_PRODUCTS

class LTVAgent:
    """
    Maximizes Customer Lifetime Value after loan approval.
    Features:
    - Personalized cross-sell recommendations based on loan purpose
    - EMI reminder schedule (first 3 months)
    - Smart product bundling (insurance + loan)
    - Re-engagement triggers
    """

    def generate_post_sanction_dashboard(self, customer: dict,
                                          loan_details: dict,
                                          loan_purpose: str = "personal") -> dict:
        """Complete post-sanction engagement package"""
        return {
            "emi_schedule": self._generate_emi_schedule(loan_details, months=3),
            "cross_sell_offers": self._get_cross_sell_offers(loan_purpose, loan_details),
            "milestone_messages": self._get_milestone_messages(customer, loan_details),
            "tips": self._get_financial_tips(loan_details),
        }

    def _generate_emi_schedule(self, ld: dict, months: int = 3) -> list:
        """Next N months EMI dates and amounts"""
        schedule = []
        base_date = date.today().replace(day=5)   # EMI on 5th of each month
        if base_date <= date.today():
            base_date = (base_date + relativedelta(months=1))

        for i in range(months):
            due_date = base_date + relativedelta(months=i)
            schedule.append({
                "emi_no": i + 1,
                "due_date": due_date.strftime("%d %B %Y"),
                "amount": f"₹{ld['emi']:,.2f}",
                "note": "Set up auto-debit to avoid late charges"
            })
        return schedule

    def _get_cross_sell_offers(self, purpose: str, ld: dict) -> list:
        """Context-aware cross-sell based on loan purpose"""
        offers = []
        # Always offer insurance for loan protection
        offers.append({
            "product": "Loan Protection Insurance",
            "tagline": "Secure your family from EMI liability",
            "premium": "₹199/month",
            "benefit": f"Covers ₹{ld['loan_amount']:,.0f} loan in case of job loss or accident",
            "urgency": "🔴 Limited offer — valid 7 days from sanction",
        })
        # Purpose-based cross-sell
        if purpose in ["education", "career"]:
            offers.append({
                "product": "Tata Capital Study Card",
                "tagline": "Education spending rewards",
                "premium": "No annual fee",
                "benefit": "5% cashback on books, courses, and online learning",
                "urgency": "✅ Pre-approved for you",
            })
        elif purpose in ["home", "renovation"]:
            offers.append({
                "product": "Home Maintenance Plan",
                "tagline": "Keep your renovated home in top shape",
                "premium": "₹499/month",
                "benefit": "Annual electrical + plumbing inspection included",
                "urgency": "✅ Exclusive for home loan customers",
            })
        elif purpose in ["medical", "health"]:
            offers.append({
                "product": "Tata AIG Health Insurance",
                "tagline": "Never face a medical crisis unprepared again",
                "premium": "₹350/month",
                "benefit": "₹5L coverage, cashless at 10,000+ hospitals",
                "urgency": "🔴 No waiting period for loan customers",
            })
        # Always add credit card
        offers.append({
            "product": "Tata Capital Platinum Credit Card",
            "tagline": "Earn while you spend",
            "premium": "₹999/year (waived on ₹1L spend)",
            "benefit": "5X rewards on loan EMI, 3X on shopping",
            "urgency": "✅ Pre-approved for existing loan customers",
        })
        return offers

    def _get_milestone_messages(self, customer: dict, ld: dict) -> list:
        return [
            {"trigger": "Day 1", "message": f"Welcome aboard, {customer['name'].split()[0]}! 🎉 Your loan of ₹{ld['loan_amount']:,.0f} is on its way. Set up auto-debit today to never miss an EMI."},
            {"trigger": "EMI 1", "message": "Great start! ✅ Your first EMI is paid. You're on track to build an excellent credit profile."},
            {"trigger": "EMI 3", "message": "3 EMIs done! 💪 Your credit score is improving. You may already be eligible for a top-up loan if needed."},
            {"trigger": "EMI 6", "message": "6-month milestone! 🏆 Pre-closure is now available. Also, check out our new product offers curated for you."},
        ]

    def _get_financial_tips(self, ld: dict) -> list:
        return [
            f"💡 Pay ₹{ld['emi'] + 500:,.0f}/month instead of ₹{ld['emi']:,.0f} and reduce tenure by ~3 months.",
            "💡 Set up NACH auto-debit to never miss an EMI — maintains your 750+ credit score.",
            "💡 After 12 EMIs, your credit score will typically rise by 20-40 points.",
            f"💡 Total interest you'll save if you pre-close at EMI 24: ₹{ld['total_interest'] * 0.35:,.0f}",
        ]