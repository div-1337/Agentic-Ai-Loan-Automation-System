# app.py — Dark Theme + Auto-Submit Voice Input
# Run: streamlit run app.py

import streamlit as st
import streamlit.components.v1 as components
import time
from master_agent import MasterAgent
from ui.styles import MAIN_CSS
from ui.sidebar import render_sidebar
from utils.voice import text_to_speech
from config import SUPPORTED_LANGUAGES

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Tata Capital | AI Loan Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────
def init_session():
    if "agent" not in st.session_state:
        source = st.query_params.get("source", None)
        st.session_state.agent           = MasterAgent(source=source)
        st.session_state.messages        = []
        st.session_state.greeted         = False
        st.session_state.pdf_bytes       = None
        st.session_state.pdf_path        = None
        st.session_state.require_upload  = False
        st.session_state.show_ltv        = False
        st.session_state.ltv_data        = None
        st.session_state.last_xai        = None
        st.session_state.voice_enabled   = True
        st.session_state.wealth_pitch    = None
        st.session_state.alternatives    = []
        st.session_state.final_decision  = None
        st.session_state.voice_text      = ""
        st.session_state.pending_voice   = ""

init_session()

# ── Helpers ───────────────────────────────────────────────────────
def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def process_message(user_input: str):
    if not user_input or not user_input.strip():
        return
    add_message("user", user_input)
    agent = st.session_state.agent

    with st.spinner(""):
        time.sleep(0.3)
        result = agent.process(user_input)

    add_message("assistant", result["message"])

    if result.get("pdf_path"):
        st.session_state.pdf_path = result["pdf_path"]
        try:
            with open(result["pdf_path"], "rb") as f:
                st.session_state.pdf_bytes = f.read()
        except:
            pass

    if result.get("require_upload"):
        st.session_state.require_upload = True
    else:
        st.session_state.require_upload = False

    if result.get("ltv_data"):
        st.session_state.ltv_data = result["ltv_data"]
        st.session_state.show_ltv = True

    if result.get("xai_breakdown"):
        st.session_state.last_xai = result["xai_breakdown"]

    if result.get("wealth_pitch"):
        st.session_state.wealth_pitch = result["wealth_pitch"]

    if result.get("alternatives"):
        st.session_state.alternatives = result["alternatives"]

    if result.get("decision"):
        st.session_state.final_decision = result["decision"]

    # TTS
    if st.session_state.voice_enabled:
        try:
            audio = text_to_speech(result["message"], agent.current_lang)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
        except:
            pass

    st.rerun()

# ── VOICE INPUT COMPONENT ─────────────────────────────────────────
# This renders an HTML button that:
# 1. Listens to mic using browser Web Speech API
# 2. Shows transcript in real time
# 3. When done speaking → automatically fills a hidden text area
#    and triggers a Streamlit rerun via st.session_state

def render_voice_component(lang_code: str = "en"):
    lang_map = {
        "en": "en-IN", "hi": "hi-IN", "ta": "ta-IN",
        "te": "te-IN", "mr": "mr-IN", "bn": "bn-IN"
    }
    browser_lang = lang_map.get(lang_code, "en-IN")

    voice_html = f"""
    <style>
    .vc-wrap {{
        display: flex; align-items: center; gap: 12px;
        padding: 10px 14px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
    }}
    .vc-btn {{
        display: flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, #CC0000, #8B0000);
        color: white; border: none;
        padding: 9px 20px; border-radius: 10px;
        cursor: pointer; font-size: 13px; font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        transition: all 0.2s; white-space: nowrap;
        box-shadow: 0 2px 12px rgba(180,0,0,0.3);
    }}
    .vc-btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    .vc-btn.listening {{
        background: linear-gradient(135deg, #EF4444, #CC0000);
        box-shadow: 0 2px 16px rgba(239,68,68,0.45);
        animation: vc-pulse 1.2s infinite;
    }}
    @keyframes vc-pulse {{
        0%,100% {{ box-shadow: 0 2px 16px rgba(239,68,68,0.45); }}
        50% {{ box-shadow: 0 2px 24px rgba(239,68,68,0.7); }}
    }}
    .vc-status {{
        font-size: 12px;
        color: #888899;
        font-family: 'DM Sans', sans-serif;
        flex: 1;
    }}
    .vc-status.active {{ color: #22C55E; }}
    .vc-transcript {{
        font-size: 12px;
        color: #CC4444;
        font-style: italic;
        font-family: 'DM Sans', sans-serif;
        margin-top: 2px;
    }}
    </style>

    <div class="vc-wrap">
        <button class="vc-btn" id="vcBtn" onclick="startVC()">
            🎤 Speak
        </button>
        <div>
            <div class="vc-status" id="vcStatus">Click to speak — result auto-sends</div>
            <div class="vc-transcript" id="vcTranscript"></div>
        </div>
    </div>

    <script>
    let vcRecog = null;

    function startVC() {{
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            document.getElementById('vcStatus').innerText = '❌ Use Chrome or Edge for voice';
            return;
        }}

        if (vcRecog) {{ vcRecog.abort(); }}

        vcRecog = new SpeechRecognition();
        vcRecog.lang = '{browser_lang}';
        vcRecog.continuous = false;
        vcRecog.interimResults = true;
        vcRecog.maxAlternatives = 1;

        const btn = document.getElementById('vcBtn');
        const status = document.getElementById('vcStatus');
        const transcript = document.getElementById('vcTranscript');

        vcRecog.onstart = () => {{
            btn.className = 'vc-btn listening';
            btn.innerHTML = '🔴 Listening...';
            status.className = 'vc-status active';
            status.innerText = 'Speak now...';
            transcript.innerText = '';
        }};

        vcRecog.onresult = (event) => {{
            let interim = '';
            let final = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                if (event.results[i].isFinal) {{
                    final += event.results[i][0].transcript;
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            transcript.innerText = interim || final;

            // When we have a final result → send to Streamlit automatically
            if (final.trim()) {{
                status.innerText = '✅ Sending: ' + final.trim();
                transcript.innerText = '';

                // Write to the hidden Streamlit input and trigger submit
                // This uses the Streamlit component messaging API
                const data = {{ type: 'voice_final', text: final.trim() }};
                window.parent.postMessage(JSON.stringify(data), '*');

                // Also try direct DOM injection into chat input
                setTimeout(() => {{
                    // Find Streamlit's chat input textarea
                    const textareas = window.parent.document.querySelectorAll('textarea');
                    let chatInput = null;
                    textareas.forEach(t => {{
                        if (t.placeholder && t.placeholder.toLowerCase().includes('type')) {{
                            chatInput = t;
                        }}
                    }});

                    if (chatInput) {{
                        // Set value using React's synthetic event system
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLTextAreaElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(chatInput, final.trim());
                        chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));

                        // Simulate Enter key press
                        setTimeout(() => {{
                            chatInput.dispatchEvent(new KeyboardEvent('keydown', {{
                                key: 'Enter', code: 'Enter', keyCode: 13,
                                bubbles: true, cancelable: true
                            }}));
                        }}, 150);
                    }}
                }}, 300);
            }}
        }};

        vcRecog.onend = () => {{
            btn.className = 'vc-btn';
            btn.innerHTML = '🎤 Speak';
            status.className = 'vc-status';
            status.innerText = 'Click to speak again';
        }};

        vcRecog.onerror = (e) => {{
            btn.className = 'vc-btn';
            btn.innerHTML = '🎤 Speak';
            const msgs = {{
                'not-allowed': '❌ Mic blocked — allow mic in browser',
                'no-speech': '⚠️ No speech detected, try again',
                'network': '⚠️ Network error',
            }};
            status.innerText = msgs[e.error] || '❌ Error: ' + e.error;
        }};

        vcRecog.start();
    }}
    </script>
    """
    components.html(voice_html, height=80, scrolling=False)

# ── LAYOUT ────────────────────────────────────────────────────────
render_sidebar(st.session_state.agent)

main_col, panel_col = st.columns([3, 2], gap="medium")

with main_col:
    agent = st.session_state.agent

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="tc-header">
        <div class="tc-header-inner">
            <div class="tc-header-left">
                <h1>🏦 Tata Capital — AI Loan Advisor</h1>
                <div class="tagline">Backed by Tata Group &nbsp;·&nbsp; RBI Registered NBFC &nbsp;·&nbsp; 12M+ Customers</div>
            </div>
            <div class="live-badge">
                <div class="live-dot"></div>
                LIVE AI
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Approval Meter ─────────────────────────────────────────────
    pct = agent.approval_pct
    if pct < 40:
        bar_color = "linear-gradient(90deg, #7F1D1D, #DC2626)"
        pct_color = "#EF4444"
    elif pct < 70:
        bar_color = "linear-gradient(90deg, #78350F, #F59E0B)"
        pct_color = "#F59E0B"
    elif pct < 90:
        bar_color = "linear-gradient(90deg, #CC0000, #FF6644)"
        pct_color = "#FF6644"
    else:
        bar_color = "linear-gradient(90deg, #14532D, #22C55E)"
        pct_color = "#22C55E"

    state = agent.state
    stage_labels = {
        "GREETING":       "Welcome",
        "SALES":          "Consultation",
        "KYC_COLLECTION": "Identity Collection",
        "VERIFICATION":   "KYC Verification",
        "UNDERWRITING":   "Credit Assessment",
        "SALARY_UPLOAD":  "Income Verification",
        "POST_SANCTION":  "Loan Approved",
        "DONE":           "Session Complete",
        "REJECTED":       "Application Declined",
        "ESCALATED":      "Human Handoff",
    }

    st.markdown(f"""
    <div class="approval-container">
        <div class="approval-label">📊 Loan Eligibility Score</div>
        <div class="approval-track">
            <div class="approval-fill" style="width:{pct}%; background:{bar_color};"></div>
        </div>
        <div class="approval-footer">
            <div class="approval-pct" style="color:{pct_color};">{pct}%</div>
            <div class="approval-stage">{stage_labels.get(state, state)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chat History ───────────────────────────────────────────────
    for msg in st.session_state.messages:
        avatar = "🏦" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ── Greeting ───────────────────────────────────────────────────
    if not st.session_state.greeted:
        st.session_state.greeted = True
        result = agent.process("__start__")
        add_message("assistant", result["message"])
        if st.session_state.voice_enabled:
            try:
                audio = text_to_speech(result["message"], agent.current_lang)
                if audio:
                    st.audio(audio, format="audio/mp3", autoplay=True)
            except:
                pass
        st.rerun()

    # ── Input Area ────────────────────────────────────────────────
    terminal_states = {"DONE", "REJECTED", "ESCALATED"}
    is_terminal = state in terminal_states

    if not is_terminal:
        # Voice toggle + voice component
        toggle_col, _ = st.columns([1, 4])
        with toggle_col:
            voice_on = st.toggle("🔊 Voice", value=st.session_state.voice_enabled)
            st.session_state.voice_enabled = voice_on

        # ── Voice Input ──────────────────────────────────────────
        # Voice auto-submits via DOM injection into the chat input below
        render_voice_component(agent.current_lang)

        # ── Salary Upload UI ─────────────────────────────────────
        if st.session_state.require_upload and state == "SALARY_UPLOAD":
            st.markdown("""
            <div class="dark-card" style="border-top: 2px solid #F59E0B;">
                <div class="dark-card-title">💼 Income Verification Required</div>
            </div>
            """, unsafe_allow_html=True)

            up_col, sal_col = st.columns(2)
            with up_col:
                uploaded = st.file_uploader(
                    "Upload Salary Slip",
                    type=["pdf", "jpg", "jpeg", "png"]
                )
            with sal_col:
                manual_sal = st.number_input(
                    "Or Enter Monthly Salary (₹)",
                    min_value=10000,
                    max_value=5000000,
                    step=5000,
                    value=80000
                )

            if st.button("✅ Submit & Verify Income", type="primary", use_container_width=True):
                st.session_state.require_upload = False
                process_message(str(int(manual_sal)))

        # ── Normal Chat Input ────────────────────────────────────
        else:
            user_input = st.chat_input(
                placeholder="Type your message... (or use 🎤 Speak above)",
            )
            if user_input:
                process_message(user_input)

    else:
        # Terminal state
        if state == "REJECTED" and st.session_state.alternatives:
            st.markdown("""
            <div class="dark-card">
                <div class="dark-card-title">💡 Your Alternatives</div>
            </div>
            """, unsafe_allow_html=True)
            for alt in st.session_state.alternatives:
                st.markdown(f"<p style='color:#A0A0C0; font-size:13px; padding:4px 0;'>→ {alt}</p>",
                             unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 New Application", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with c2:
            if st.button("📞 Talk to Human", use_container_width=True):
                st.info("📞 1860-267-6060  |  WhatsApp: +91 97799 75000")


# ── RIGHT PANEL ───────────────────────────────────────────────────
with panel_col:

    # ── Language Selector ──────────────────────────────────────────
    lang_options = {f"{v['flag']} {v['name']}": k for k, v in SUPPORTED_LANGUAGES.items()}
    selected = st.selectbox("🌐 Language", options=list(lang_options.keys()), index=0)
    if selected:
        new_lang = lang_options[selected]
        if new_lang != agent.current_lang:
            agent.current_lang = new_lang

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sanction Letter Download ───────────────────────────────────
    if st.session_state.pdf_bytes:
        st.success("🎉 Sanction Letter Ready!")
        st.balloons()
        st.download_button(
            label="📄 Download Sanction Letter",
            data=st.session_state.pdf_bytes,
            file_name=f"TataCapital_SanctionLetter_{agent.ctx.get('phone','')}.pdf",
            mime="application/pdf",
        )
        st.markdown("<hr>", unsafe_allow_html=True)

    # ── XAI Breakdown ──────────────────────────────────────────────
    if st.session_state.last_xai:
        xai = st.session_state.last_xai
        cs  = xai.get("credit_score", {})
        ll  = xai.get("loan_vs_limit", {})
        emi = xai.get("emi_check", {})
        bd  = xai.get("bureau_details", {})

        cs_class  = "pass" if "✅" in str(cs.get("status",""))  else "fail"
        ll_class  = "pass" if "Instant" in str(ll.get("status","")) else ("warn" if "Salary" in str(ll.get("status","")) else "fail")
        emi_class = "pass" if "✅" in str(emi.get("status","")) else ("fail" if "❌" in str(emi.get("status","")) else "warn")

        with st.expander("🔍 Credit Decision (XAI)", expanded=True):
            st.markdown(f"""
            <div class="xai-box">
                <div class="xai-title">📊 Why This Decision?</div>
                <div class="xai-row">
                    <span class="xai-key">Credit Score</span>
                    <span class="xai-val {cs_class}">{cs.get('value','?')}/900 &nbsp; {cs.get('status','')}</span>
                </div>
                <div class="xai-row">
                    <span class="xai-key">Loan vs Limit</span>
                    <span class="xai-val {ll_class}">{ll.get('status','N/A')}</span>
                </div>
                <div class="xai-row">
                    <span class="xai-key">EMI/Salary Ratio</span>
                    <span class="xai-val {emi_class}">{emi.get('ratio_pct','N/A')}% &nbsp; {emi.get('status','')}</span>
                </div>
                <div class="xai-row">
                    <span class="xai-key">Active Loans</span>
                    <span class="xai-val" style="color:#C0C0D8;">{bd.get('active_loans','N/A')}</span>
                </div>
                <div class="xai-row">
                    <span class="xai-key">Outstanding Debt</span>
                    <span class="xai-val" style="color:#C0C0D8;">₹{bd.get('outstanding',0):,}</span>
                </div>
                <div class="xai-row">
                    <span class="xai-key">Credit History</span>
                    <span class="xai-val" style="color:#C0C0D8;">{bd.get('credit_age','N/A')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Wealth Planning ─────────────────────────────────────────────
    if st.session_state.wealth_pitch:
        st.markdown(f"""
        <div class="wealth-card">
            <div class="wealth-title">💰 Comparative Wealth Planning</div>
            <div class="wealth-body">{st.session_state.wealth_pitch}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── LTV Panel ──────────────────────────────────────────────────
    if st.session_state.show_ltv and st.session_state.ltv_data:
        ltv = st.session_state.ltv_data

        with st.expander("📅 EMI Schedule", expanded=True):
            for e in ltv.get("emi_schedule", []):
                st.markdown(
                    f"<div style='color:#A0A0C0; font-size:13px; padding:5px 0; "
                    f"border-bottom:1px solid rgba(255,255,255,0.04);'>"
                    f"<span style='color:#CC0000; font-weight:600;'>EMI {e['emi_no']}</span>"
                    f" &nbsp;·&nbsp; {e['due_date']} &nbsp;·&nbsp; "
                    f"<span style='color:#E0E0F0; font-weight:600;'>{e['amount']}</span></div>",
                    unsafe_allow_html=True
                )
            st.caption("💡 Set up NACH auto-debit to protect your credit score")

        with st.expander("🌟 Exclusive Offers", expanded=False):
            for offer in ltv.get("cross_sell_offers", [])[:2]:
                st.markdown(f"""
                <div class="cs-card">
                    <div class="cs-title">{offer['product']}</div>
                    <div class="cs-benefit">✦ {offer['benefit']}</div>
                    <div class="cs-urgency">{offer['urgency']}</div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("💡 Financial Tips", expanded=False):
            for tip in ltv.get("tips", []):
                st.markdown(
                    f"<p style='color:#A0A0C0; font-size:13px; padding:6px 0; "
                    f"border-bottom:1px solid rgba(255,255,255,0.04);'>{tip}</p>",
                    unsafe_allow_html=True
                )

    # ── Why Tata Capital (shown early in journey) ──────────────────
    if state in ["GREETING", "SALES", "KYC_COLLECTION"]:
        st.markdown("""
        <div class="info-panel">
            <div class="info-panel-title">🏦 Why Tata Capital?</div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>Tata Group — 155 years of trust</span>
            </div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>12 million+ satisfied customers</span>
            </div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>Loan approved in 10 minutes</span>
            </div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>No collateral required</span>
            </div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>100% digital, paperless process</span>
            </div>
            <div class="info-panel-item">
                <div class="info-dot"></div>
                <span>Amount: ₹50,000 to ₹25 Lakh</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


        