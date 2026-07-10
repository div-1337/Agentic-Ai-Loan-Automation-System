# ui/styles.py — Dark Banking Theme

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0A0A0F !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #E8E8F0 !important;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Main background with subtle grid ───────────────────── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(180,0,0,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(180,0,0,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0D0D14 !important;
    border-right: 1px solid rgba(180,0,0,0.2) !important;
}
[data-testid="stSidebar"] > div {
    background: transparent !important;
}
[data-testid="stSidebar"] * {
    color: #C8C8D8 !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    color: #C8C8D8 !important;
}

/* ── Sidebar Logo Area ──────────────────────────────────── */
.sidebar-logo {
    text-align: center;
    padding: 20px 0 16px;
    border-bottom: 1px solid rgba(180,0,0,0.25);
    margin-bottom: 16px;
}
.sidebar-logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #FF2020 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.sidebar-logo-sub {
    font-size: 10px;
    color: #666680 !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Sidebar Section ─────────────────────────────────────── */
.sidebar-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}
.sidebar-section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #B40000 !important;
    margin-bottom: 12px;
}

/* ── Agent Rows ──────────────────────────────────────────── */
.agent-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.agent-row:last-child { border-bottom: none; }
.agent-icon { font-size: 14px; }
.agent-info { flex: 1; }
.agent-name {
    font-size: 12px;
    font-weight: 600;
    color: #E0E0F0 !important;
}
.agent-role {
    font-size: 10px;
    color: #666680 !important;
}
.dot-active {
    width: 8px; height: 8px;
    background: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 6px #22C55E;
    animation: pulse-green 1.5s infinite;
    flex-shrink: 0;
}
.dot-idle {
    width: 8px; height: 8px;
    background: #333348;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-done {
    width: 8px; height: 8px;
    background: #3B82F6;
    border-radius: 50%;
    box-shadow: 0 0 6px #3B82F6;
    flex-shrink: 0;
}
@keyframes pulse-green {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #22C55E; }
    50% { opacity: 0.6; box-shadow: 0 0 12px #22C55E; }
}

/* ── Main Content Area ───────────────────────────────────── */
.main-content {
    position: relative;
    z-index: 1;
}

/* ── Header ──────────────────────────────────────────────── */
.tc-header {
    background: linear-gradient(135deg, #1A0000 0%, #0D0D14 60%, #0A0A0F 100%);
    border: 1px solid rgba(180,0,0,0.35);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.tc-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #CC0000, #FF4444, #CC0000, transparent);
}
.tc-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(180,0,0,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.tc-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 1;
}
.tc-header-left h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: 0.5px;
    margin: 0 !important;
}
.tc-header-left .tagline {
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    margin-top: 4px;
    letter-spacing: 0.3px;
}
.live-badge {
    background: rgba(34,197,94,0.15);
    border: 1px solid rgba(34,197,94,0.4);
    color: #22C55E;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.live-dot {
    width: 6px; height: 6px;
    background: #22C55E;
    border-radius: 50%;
    animation: pulse-green 1.5s infinite;
}

/* ── Approval Meter ──────────────────────────────────────── */
.approval-container {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.approval-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #666680;
    margin-bottom: 10px;
}
.approval-track {
    background: #1E1E2E;
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
    position: relative;
}
.approval-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}
.approval-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.25) 100%);
    border-radius: 8px;
}
.approval-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
}
.approval-pct {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
}
.approval-stage {
    font-size: 11px;
    color: #444460;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Chat Messages ───────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border-radius: 14px !important;
    padding: 4px 0 !important;
    margin-bottom: 4px !important;
}

/* Bot message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-left: 3px solid #CC0000 !important;
    padding: 14px 18px !important;
    border-radius: 14px !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(180,0,0,0.08) !important;
    border: 1px solid rgba(180,0,0,0.2) !important;
    padding: 14px 18px !important;
    border-radius: 14px !important;
}

/* Message text color */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #E0E0F0 !important;
}

/* ── Chat Input ──────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #E8E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: #CC0000 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #444460 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(180,0,0,0.5) !important;
    box-shadow: 0 0 0 3px rgba(180,0,0,0.1) !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: #1A1A28 !important;
    color: #E0E0F0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(180,0,0,0.15) !important;
    border-color: rgba(180,0,0,0.4) !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #CC0000, #8B0000) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}

/* ── Download Button ─────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.5px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(180,0,0,0.35) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 6px 28px rgba(180,0,0,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Select Box ──────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #E0E0F0 !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] label {
    color: #888899 !important;
    font-size: 12px !important;
}

/* ── Expander ────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: #C0C0D8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 12px 16px !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(255,255,255,0.03) !important;
}
[data-testid="stExpander"] > div > div {
    padding: 0 16px 14px !important;
}

/* ── Metrics ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricLabel"] {
    color: #666680 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stMetricValue"] {
    color: #E8E8F0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* ── Info / Success / Error boxes ────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid !important;
}
.stSuccess {
    background: rgba(34,197,94,0.08) !important;
    border-color: rgba(34,197,94,0.3) !important;
    color: #86EFAC !important;
}
.stInfo {
    background: rgba(59,130,246,0.08) !important;
    border-color: rgba(59,130,246,0.3) !important;
    color: #93C5FD !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border-color: rgba(245,158,11,0.3) !important;
    color: #FCD34D !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border-color: rgba(239,68,68,0.3) !important;
    color: #FCA5A5 !important;
}

/* ── Number Input ────────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background: #111118 !important;
    color: #E8E8F0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}
[data-testid="stNumberInput"] label {
    color: #888899 !important;
}

/* ── File Uploader ───────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #111118 !important;
    border: 1px dashed rgba(180,0,0,0.4) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] label {
    color: #888899 !important;
}

/* ── Toggle ──────────────────────────────────────────────── */
[data-testid="stToggle"] label {
    color: #888899 !important;
    font-size: 12px !important;
}

/* ── Custom Cards ────────────────────────────────────────── */
.dark-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    margin: 8px 0;
}
.dark-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.dark-card-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}
.dark-card p, .dark-card span, .dark-card div {
    color: #A0A0C0 !important;
    font-size: 13px;
    line-height: 1.7;
}

/* ── XAI Table ───────────────────────────────────────────── */
.xai-box {
    background: #0D0D14;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    overflow: hidden;
}
.xai-title {
    background: rgba(180,0,0,0.15);
    border-bottom: 1px solid rgba(180,0,0,0.2);
    padding: 10px 16px;
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #FF6666 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.xai-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 13px;
}
.xai-row:last-child { border-bottom: none; }
.xai-key { color: #888899; font-weight: 500; }
.xai-val { font-weight: 600; }
.pass { color: #22C55E; }
.fail { color: #EF4444; }
.warn { color: #F59E0B; }

/* ── Wealth Card ─────────────────────────────────────────── */
.wealth-card {
    background: linear-gradient(135deg, #0D0D14 0%, #150010 100%);
    border: 1px solid rgba(180,0,0,0.25);
    border-top: 2px solid #CC0000;
    border-radius: 14px;
    padding: 18px 20px;
    margin: 8px 0;
}
.wealth-title {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: #FF6644 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.wealth-body {
    color: #C0C0D8 !important;
    font-size: 13px;
    line-height: 1.7;
}

/* ── Cross-Sell Cards ────────────────────────────────────── */
.cs-card {
    background: #0D0D14;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 16px;
    margin: 6px 0;
    transition: border-color 0.2s;
}
.cs-card:hover { border-color: rgba(180,0,0,0.3); }
.cs-title { font-weight: 600; color: #E0E0F0 !important; font-size: 13px; margin-bottom: 4px; }
.cs-benefit { color: #888899 !important; font-size: 12px; margin: 4px 0; }
.cs-urgency {
    display: inline-block;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: #FCD34D !important;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-top: 6px;
    letter-spacing: 0.3px;
}

/* ── Info Panel (Why Tata Capital) ───────────────────────── */
.info-panel {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
}
.info-panel-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 14px;
    letter-spacing: 0.5px;
}
.info-panel-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 13px;
    color: #A0A0C0 !important;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.info-panel-item:last-child { border-bottom: none; }
.info-dot {
    width: 6px; height: 6px;
    background: #CC0000;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}

/* ── Voice Component ─────────────────────────────────────── */
.voice-wrapper {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 10px 14px;
    margin: 8px 0;
}

/* ── Stage Caption ───────────────────────────────────────── */
.stage-caption {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    color: #666680;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: #CC0000; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #FF2020; }

/* ── Audio player (hide ugly default) ───────────────────── */
audio { display: none !important; }

/* ── Divider ─────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 12px 0 !important;
}

/* ── Caption text ────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #444460 !important;
    font-size: 11px !important;
}
</style>
"""

