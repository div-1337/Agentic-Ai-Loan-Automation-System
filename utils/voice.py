# utils/voice.py
# TTS output using gTTS (free) + Browser STT bridge via HTML component

from gtts import gTTS
import tempfile, os, re
import streamlit as st
import streamlit.components.v1 as components

def text_to_speech(text: str, lang_code: str = "en") -> bytes | None:
    """Convert text to MP3 bytes using gTTS (free Google TTS)"""
    # Clean text for TTS (remove markdown, emojis)
    clean = re.sub(r'\*+|#+|`+', '', text)
    clean = re.sub(r'[^\w\s₹.,!?%\-\'\"()]', '', clean)
    clean = clean.strip()[:400]   # TTS limit
    if not clean:
        return None
    try:
        from config import SUPPORTED_LANGUAGES
        lang_config = SUPPORTED_LANGUAGES.get(lang_code, {"gtts_lang": "en", "gtts_tld": "co.in"})
        tts = gTTS(text=clean, lang=lang_config["gtts_lang"],
                   tld=lang_config["gtts_tld"], slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            with open(f.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
            os.unlink(f.name)
        return audio_bytes
    except Exception as e:
        return None

def render_voice_input_component(lang_code: str = "en") -> None:
    """
    Renders a voice input button using browser's native Web Speech API.
    No API key needed. Works in Chrome/Edge.
    Result is stored in st.session_state.voice_input
    """
    lang_map = {"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN",
                "te": "te-IN", "mr": "mr-IN", "bn": "bn-IN"}
    browser_lang = lang_map.get(lang_code, "en-IN")

    voice_html = f"""
    <style>
    .voice-container {{
        display: flex; align-items: center; gap: 10px;
        padding: 8px 12px;
        background: #fff8f8; border: 1px solid #e0c0c0;
        border-radius: 10px; margin: 4px 0;
    }}
    .voice-btn {{
        background: linear-gradient(135deg, #C00000, #8B0000);
        color: white; border: none; padding: 8px 18px;
        border-radius: 8px; cursor: pointer; font-size: 14px;
        transition: all 0.2s; font-weight: 600;
    }}
    .voice-btn:hover {{ opacity: 0.85; transform: scale(1.02); }}
    .voice-btn.listening {{
        background: linear-gradient(135deg, #ff4444, #cc0000);
        animation: pulse 1s infinite;
    }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.7}} }}
    .voice-status {{ font-size: 13px; color: #666; }}
    .voice-result {{ font-size: 12px; color: #C00000; font-style: italic; }}
    </style>

    <div class="voice-container">
        <button id="voiceBtn" class="voice-btn" onclick="startListening()">🎤 Speak</button>
        <div>
            <div id="voiceStatus" class="voice-status">Click to speak in {lang_code.upper()}</div>
            <div id="voiceResult" class="voice-result"></div>
        </div>
    </div>

    <script>
    let recognition;
    function startListening() {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            document.getElementById('voiceStatus').innerText = '❌ Voice not supported. Use Chrome or Edge.';
            return;
        }}
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = '{browser_lang}';
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = () => {{
            document.getElementById('voiceBtn').className = 'voice-btn listening';
            document.getElementById('voiceBtn').innerText = '🔴 Listening...';
            document.getElementById('voiceStatus').innerText = 'Speak now...';
        }};
        recognition.onresult = (event) => {{
            const transcript = Array.from(event.results)
                .map(r => r[0].transcript).join('');
            document.getElementById('voiceResult').innerText = '📝 ' + transcript;
            if (event.results[0].isFinal) {{
                // Pass to Streamlit via URL trick
                window.parent.postMessage({{type: 'voice_input', text: transcript}}, '*');
            }}
        }};
        recognition.onend = () => {{
            document.getElementById('voiceBtn').className = 'voice-btn';
            document.getElementById('voiceBtn').innerText = '🎤 Speak';
            document.getElementById('voiceStatus').innerText = 'Click to speak again';
        }};
        recognition.onerror = (e) => {{
            document.getElementById('voiceStatus').innerText = '❌ Error: ' + e.error;
            document.getElementById('voiceBtn').className = 'voice-btn';
            document.getElementById('voiceBtn').innerText = '🎤 Speak';
        }};
        recognition.start();
    }}
    </script>
    """
    components.html(voice_html, height=75)