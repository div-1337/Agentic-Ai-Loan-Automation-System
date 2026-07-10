# ui/sidebar.py — Live Agent Dashboard

import streamlit as st

AGENT_INFO = {
    "MasterAgent":       {"icon": "🎯", "role": "Orchestrator"},
    "SalesAgent":        {"icon": "💬", "role": "Negotiator"},
    "SentimentAgent":    {"icon": "🧠", "role": "Emotion Analyzer"},
    "VerificationAgent": {"icon": "🔍", "role": "KYC Checker"},
    "UnderwritingAgent": {"icon": "📊", "role": "Credit Judge"},
    "SanctionGenerator": {"icon": "📄", "role": "PDF Printer"},
    "LTVAgent":          {"icon": "🌟", "role": "LTV Manager"},
}

def format_amount(amount: float) -> str:
    """Display amounts in Indian format — lakhs/crores"""
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.1f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.1f} Lakh"
    else:
        return f"₹{amount:,.0f}"

def render_sidebar(agent):
    with st.sidebar:

        # Logo
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 14px;">
            <div style="font-family:'Syne',sans-serif; font-size:20px; font-weight:800;
                        color:#CC0000; letter-spacing:3px;">TATA CAPITAL</div>
            <div style="font-size:10px; color:#444460; letter-spacing:1.5px;
                        text-transform:uppercase; margin-top:4px;">
                Agentic AI Platform v1.0
            </div>
        </div>
        <hr style="border:none; border-top:1px solid rgba(180,0,0,0.2); margin:0 0 14px;">
        """, unsafe_allow_html=True)

        # Agent Control Center
        st.markdown("""
        <div style="font-size:10px; font-weight:700; letter-spacing:2px;
                    text-transform:uppercase; color:#CC0000; margin-bottom:10px;">
            🤖 Agent Control Center
        </div>
        """, unsafe_allow_html=True)

        state = agent.state

        agent_states = {
            "MasterAgent":       "ACTIVE",
            "SalesAgent":        ("ACTIVE" if state == "SALES"
                                   else "DONE"  if state not in ["GREETING", "SALES"]
                                   else "IDLE"),
            "SentimentAgent":    ("ACTIVE" if state in ["SALES", "KYC_COLLECTION"]
                                   else "IDLE"),
            "VerificationAgent": ("ACTIVE" if state == "VERIFICATION"
                                   else "DONE"  if state not in ["GREETING", "SALES",
                                                                   "KYC_COLLECTION", "VERIFICATION"]
                                   else "IDLE"),
            "UnderwritingAgent": ("ACTIVE" if state == "UNDERWRITING"
                                   else "DONE"  if state in ["POST_SANCTION", "DONE", "REJECTED"]
                                   else "IDLE"),
            "SanctionGenerator": ("DONE" if agent.pdf_path else "IDLE"),
            "LTVAgent":          ("DONE" if state in ["POST_SANCTION", "DONE"] and agent.pdf_path
                                   else "IDLE"),
        }

        dot_map     = {"ACTIVE": "dot-active", "IDLE": "dot-idle", "DONE": "dot-done"}
        status_map  = {"ACTIVE": "Running",    "IDLE": "Standby",  "DONE": "Complete"}

        for name, status in agent_states.items():
            info       = AGENT_INFO[name]
            dot_class  = dot_map[status]
            status_lbl = status_map[status]
            st.markdown(f"""
            <div class="agent-row">
                <div class="{dot_class}"></div>
                <div class="agent-icon">{info['icon']}</div>
                <div class="agent-info">
                    <div class="agent-name">{name}</div>
                    <div class="agent-role">{info['role']} · {status_lbl}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:14px 0;'>", unsafe_allow_html=True)

        # Session Context
        st.markdown("""
        <div style="font-size:10px; font-weight:700; letter-spacing:2px;
                    text-transform:uppercase; color:#CC0000; margin-bottom:10px;">
            📋 Session Context
        </div>
        """, unsafe_allow_html=True)

        ctx = agent.ctx

        if ctx.get("loan_amount"):
            st.metric("Loan Requested", format_amount(ctx["loan_amount"]))

        if ctx.get("tenure_months"):
            t = ctx["tenure_months"]
            years  = t // 12
            months = t % 12
            if months == 0:
                tenure_display = f"{years} yr ({t} mo)"
            else:
                tenure_display = f"{years} yr {months} mo ({t} mo)"
            st.metric("Tenure", tenure_display)

        if ctx.get("customer"):
            c = ctx["customer"]
            st.metric("Customer", c["name"])
            st.metric("Pre-Approved", format_amount(c["pre_approved_limit"]))

        if agent.loan_purpose:
            st.metric("Loan Purpose", agent.loan_purpose.title())

        if agent.current_lang != "en":
            from config import SUPPORTED_LANGUAGES
            lang_name = SUPPORTED_LANGUAGES.get(agent.current_lang, {}).get("name", "")
            if lang_name:
                st.metric("Language", lang_name)

        # Sentiment Monitor
        frustration = agent.sentiment_state.get("frustration_level", "none")
        if frustration != "none":
            st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:10px 0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:10px; font-weight:700; letter-spacing:2px;
                        text-transform:uppercase; color:#CC0000; margin-bottom:8px;">
                🧠 Sentiment Monitor
            </div>
            """, unsafe_allow_html=True)
            color = {"mild": "#F59E0B", "high": "#EF4444"}.get(frustration, "#22C55E")
            st.markdown(f"<p style='color:{color}; font-size:12px; margin:0;'>● Frustration: <b>{frustration.title()}</b></p>", unsafe_allow_html=True)
            action = agent.sentiment_state.get("action", "continue")
            st.markdown(f"<p style='color:#666680; font-size:11px; margin:4px 0 0;'>→ Mode: {action.replace('_', ' ').title()}</p>", unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:14px 0;'>", unsafe_allow_html=True)

        # KPIs
        st.markdown("""
        <div style="font-size:10px; font-weight:700; letter-spacing:2px;
                    text-transform:uppercase; color:#CC0000; margin-bottom:10px;">
            📈 Target KPIs
        </div>
        <div style="font-size:12px; color:#A0A0C0; line-height:2;">
            ✅ Conversion Rate: <b style="color:#22C55E;">+15%</b><br>
            ✅ Time-to-Sanction: <b style="color:#22C55E;">-30%</b><br>
            ✅ Drop-off Rate: <b style="color:#22C55E;">-10%</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:14px 0;'>", unsafe_allow_html=True)

        # Footer — no personal names
        st.markdown("""
        <div style="text-align:center; font-size:10px; color:#333348; line-height:1.8;">
            EY Techathon 6.0<br>
            BFSI Track · Agentic AI<br>
            © 2025 Tata Capital Limited
        </div>
        """, unsafe_allow_html=True)

        