# rag/knowledge_base.py
# Tata Capital product knowledge — fed into RAG for Sales Agent

KNOWLEDGE_DOCUMENTS = [
    # ── Product Docs ─────────────────────────────────────────────
    {
        "id": "pl_overview",
        "text": """Tata Capital Personal Loan: India's most trusted personal loan with no collateral required.
        Loan amount: ₹50,000 to ₹25,00,000. Tenure: 12 to 60 months. Interest rate: 10.99% to 14.99% per annum.
        Processing fee: 2.5% of loan amount. Zero hidden charges. Digital KYC in 5 minutes.
        Disbursement within 24 hours of approval. Pre-closure allowed after 6 months.""",
        "metadata": {"category": "product", "type": "personal_loan"}
    },
    {
        "id": "pl_eligibility",
        "text": """Personal Loan Eligibility at Tata Capital: Minimum age 21 years, maximum 58 years.
        Salaried individuals with minimum ₹20,000 monthly income. Self-employed with 3 years business vintage.
        Minimum credit score 700 out of 900. Indian resident with valid KYC documents.
        Existing Tata Capital customers get instant pre-approval up to their limit without income proof.""",
        "metadata": {"category": "eligibility"}
    },
    {
        "id": "wealth_planning_education",
        "text": """Education Loan as Wealth Investment: Investing in education yields 8-15% annual career growth.
        An engineering degree costs ₹5-8 lakhs. Graduates earn ₹4-8 LPA. EMI of ₹10,000/month vs
        lifetime income growth of ₹3-5 lakhs per year. ROI on education loan: 300-500% over 10 years.
        Use Tata Capital Education Loan to fund your child's future without depleting savings.""",
        "metadata": {"category": "wealth_planning", "purpose": "education"}
    },
    {
        "id": "wealth_planning_home",
        "text": """Home Renovation as Asset Appreciation: A ₹3 lakh renovation increases property value by ₹8-12 lakhs.
        ROI: 167-300%. Monthly EMI of ₹7,000 vs monthly rental savings of ₹12,000 in upgraded home.
        Tata Capital Home Improvement Loan at competitive 10.99% PA is smarter than using fixed deposits
        earning 7% PA — you preserve liquid capital while the asset appreciates.""",
        "metadata": {"category": "wealth_planning", "purpose": "home"}
    },
    {
        "id": "wealth_planning_business",
        "text": """Business Loan as Multiplier: ₹5 lakhs working capital loan at 12% PA costs ₹60,000/year.
        If deployed in inventory with 30% margin, it generates ₹1.5 lakh profit annually — 2.5x return.
        Tata Capital business financing helps MSMEs scale without diluting equity. Use leverage wisely.""",
        "metadata": {"category": "wealth_planning", "purpose": "business"}
    },
    {
        "id": "objection_high_emi",
        "text": """Handling EMI objection: If customer says EMI is too high, offer these solutions:
        1. Extend tenure from 24 to 48 months — reduces EMI by 35%.
        2. Reduce loan amount and top-up later after credit improvement.
        3. Show total interest cost — longer tenure costs more but improves monthly cash flow.
        Example: ₹3 lakh at 12% PA: 24 months = ₹14,130 EMI | 48 months = ₹7,892 EMI.""",
        "metadata": {"category": "sales_objection", "objection": "high_emi"}
    },
    {
        "id": "objection_high_interest",
        "text": """Handling interest rate objection: Tata Capital rates 10.99-14.99% vs market 14-36%.
        Compare to credit card debt at 36-42% per annum — personal loan is 3x cheaper than credit cards.
        For short tenures (12 months), total interest is only 5-8% of loan amount.
        Emphasize: No collateral risk, no asset pledge, fully unsecured — that's the premium.""",
        "metadata": {"category": "sales_objection", "objection": "high_interest"}
    },
    {
        "id": "objection_job_security",
        "text": """Handling job security objection: Tata Capital offers EMI holiday of 1-3 months in genuine hardship.
        Loan insurance (Personal Accident + Job Loss) available at ₹199/month covers EMIs.
        Offer to start with smaller amount that customer is fully comfortable repaying.""",
        "metadata": {"category": "sales_objection", "objection": "job_security"}
    },
    {
        "id": "quick_facts",
        "text": """Tata Capital Quick Facts: Founded 2007. RBI registered NBFC.
        Part of Tata Group — 155 years of trust. 12 million+ customers. 1000+ branches.
        Awards: Best NBFC 2024 by CNBC Awaaz, Most Trusted Financial Brand 2023.
        Digital-first: 80% of loans processed online. Average approval time: 10 minutes.
        Customer satisfaction: 4.2/5 on Google, 4.4/5 on App Store.""",
        "metadata": {"category": "trust_building"}
    },
    {
        "id": "emi_calculator",
        "text": """EMI calculation formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
        where P = Principal, r = monthly rate (annual rate/12/100), n = tenure in months.
        Examples at 12% PA: ₹1L/12m = ₹8,885 | ₹1L/24m = ₹4,707 | ₹2L/36m = ₹6,643
        ₹3L/36m = ₹9,964 | ₹5L/48m = ₹13,154 | ₹10L/60m = ₹22,244""",
        "metadata": {"category": "calculations"}
    },
]
