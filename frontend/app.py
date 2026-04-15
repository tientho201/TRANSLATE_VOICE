import streamlit as st
import requests
import io
import os 
from dotenv import load_dotenv, find_dotenv

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎙️ Voice Translator",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* Hide default Streamlit header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Hero Section ── */
    .hero-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(12px);
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #a78bfa;
        margin-bottom: 0.5rem;
    }

    /* ── Result boxes ── */
    .result-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 0.6rem;
        min-height: 70px;
        white-space: pre-wrap;
    }
    .result-box.translated {
        border-color: rgba(96, 165, 250, 0.35);
        background: rgba(96, 165, 250, 0.07);
        font-size: 1.15rem;
        font-weight: 500;
        color: #bae6fd;
    }

    /* ── Step badges ── */
    .step-badge {
        display: inline-block;
        background: rgba(167,139,250,0.2);
        border: 1px solid rgba(167,139,250,0.4);
        border-radius: 50px;
        padding: 0.18rem 0.75rem;
        font-size: 0.72rem;
        font-weight: 600;
        color: #c4b5fd;
        letter-spacing: 0.08em;
        margin-bottom: 0.85rem;
    }

    /* Selectbox & button */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(255,255,255,0.18) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124, 58, 237, 0.6) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.04);
        border: 2px dashed rgba(167,139,250,0.4);
        border-radius: 14px;
        padding: 0.5rem;
        transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(167,139,250,0.7);
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.08) !important; }

    /* Custom Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(167,139,250,0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
load_dotenv(find_dotenv())
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

LANGUAGES = {
    "🇻🇳 Vietnamese": "vi",
    "🇺🇸 English": "en",
    "🇨🇳 Chinese": "zh",
    "🇯🇵 Japanese": "ja",
    "🇰🇷 Korean": "ko",
    "🇫🇷 French": "fr",
    "🇩🇪 German": "de",
    "🇪🇸 Spanish": "es",
    "🇹🇭 Thai": "th",
    "🇷🇺 Russian": "ru",
    "🇸🇦 Arabic": "ar",
    "🇵🇹 Portuguese": "pt",
    "🇮🇹 Italian": "it",
    "🇮🇳 Hindi": "hi",
}

LANG_NAMES = list(LANGUAGES.keys())
LANG_CODES = list(LANGUAGES.values())


# ── Helpers ───────────────────────────────────────────────────────────────────
def call_translate_api(audio_bytes: bytes, filename: str, src_code: str, tgt_code: str):
    """POST to FastAPI /api/v1/translate and return JSON response."""
    files = {"audio_file": (filename, io.BytesIO(audio_bytes), "audio/mpeg")}
    data = {"source_language": src_code, "target_language": tgt_code}
    response = requests.post(f"{BACKEND_URL}/api/v1/translate", files=files, data=data, timeout=120)
    response.raise_for_status()
    return response.json()

def call_tts_api(text: str, src_code: str, tgt_code: str):
    """POST to FastAPI /api/v1/tts and return JSON response."""
    data = {"text": text, "source_language": src_code, "target_language": tgt_code}
    response = requests.post(f"{BACKEND_URL}/api/v1/tts", data=data, timeout=120)
    response.raise_for_status()
    return response.json()

# ── UI ────────────────────────────────────────────────────────────────────────
# Hero
st.markdown('<h1 class="hero-title">🌐 Voice Translator</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Upload audio → Transcribe → Translate — powered by Groq AI & Edge TTS</p>',
    unsafe_allow_html=True,
)

tab_stt, tab_tts = st.tabs(["🎙️ Dịch Giọng Nói (STT)", "🔊 Tạo Giọng Lồng Tiếng (TTS)"])

# ==============================================================================
# TAB 1: STT
# ==============================================================================
with tab_stt:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 1 — LANGUAGE</div>', unsafe_allow_html=True)

        col1, col_arrow, col2 = st.columns([5, 1, 5])
        with col1:
            st.markdown('<div class="section-label">🎤 Ngôn ngữ nguồn</div>', unsafe_allow_html=True)
            src_lang_name = st.selectbox(
                label="source_lang",
                options=LANG_NAMES,
                index=0,
                key="src_lang",
                label_visibility="collapsed",
            )
        with col_arrow:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center;font-size:1.5rem;color:#a78bfa;'>→</div>", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="section-label">🌍 Ngôn ngữ đích</div>', unsafe_allow_html=True)
            available_targets = [n for n in LANG_NAMES if n != src_lang_name]
            tgt_lang_name = st.selectbox(
                label="target_lang",
                options=available_targets,
                index=0,
                key="tgt_lang",
                label_visibility="collapsed",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    src_code = LANGUAGES[src_lang_name]
    tgt_code = LANGUAGES[tgt_lang_name]

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 2 — AUDIO</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📁 Nguồn âm thanh</div>', unsafe_allow_html=True)
        input_method = st.radio("Nguồn âm thanh", ["Tải lên file", "Nhập URL"], horizontal=True, label_visibility="collapsed", key="stt_input")
        
        uploaded_file = None
        audio_url = ""
        if input_method == "Tải lên file":
            uploaded_file = st.file_uploader(
                label="audio_uploader",
                type=["mp3", "mp4", "wav", "m4a", "webm", "ogg", "flac", "mpeg", "mpga", "aac", "wma", "amr"],
                label_visibility="collapsed",
                key="audio_upload",
            )
            if uploaded_file:
                st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        else:
            audio_url = st.text_input("Audio URL", placeholder="https://example.com/audio.mp3", label_visibility="collapsed", key="stt_url")
            if audio_url:
                st.audio(audio_url)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 3 — TRANSLATE</div>', unsafe_allow_html=True)
        translate_btn = st.button("🚀 Transcribe & Translate", use_container_width=True, key="stt_btn")

        if translate_btn:
            if input_method == "Tải lên file" and uploaded_file is None:
                st.warning("⚠️ Vui lòng tải lên file âm thanh trước.")
            elif input_method == "Nhập URL" and not audio_url:
                st.warning("⚠️ Vui lòng nhập URL âm thanh trước.")
            else:
                with st.spinner("🔄 Đang xử lý audio..."):
                    try:
                        if input_method == "Nhập URL":
                            dl_res = requests.get(audio_url, timeout=30)
                            dl_res.raise_for_status()
                            audio_bytes = dl_res.content
                            filename = audio_url.split("/")[-1]
                            if not filename or "." not in filename:
                                filename = "audio_from_url.mp3"
                        else:
                            audio_bytes = uploaded_file.getvalue()
                            filename = uploaded_file.name

                        result = call_translate_api(audio_bytes, filename, src_code, tgt_code)
                        st.session_state["last_result"] = result
                        st.success("✅ Dịch thành công!")

                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                        st.session_state.pop("last_result", None)
        st.markdown("</div>", unsafe_allow_html=True)

    if "last_result" in st.session_state:
        res = st.session_state["last_result"]
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">RESULT</div>', unsafe_allow_html=True)
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f'<div class="section-label">🎙️ Transcription ({res.get("source_language", "")})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{res.get("transcribed_text", "")}</div>', unsafe_allow_html=True)
        with col_r2:
            st.markdown(f'<div class="section-label">🌍 Translation ({res.get("target_language", "")})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box translated">{res.get("translated_text", "")}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 Copy text"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.text_area("Transcription", value=res.get("transcribed_text", ""), height=120, key="copy_src")
            with col_c2:
                st.text_area("Translation", value=res.get("translated_text", ""), height=120, key="copy_tgt")
        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB 2: TTS
# ==============================================================================
with tab_tts:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 1 — LANGUAGE</div>', unsafe_allow_html=True)

        col1_tts, col_arrow_tts, col2_tts = st.columns([5, 1, 5])
        with col1_tts:
            st.markdown('<div class="section-label">⌨️ Ngôn ngữ nhập</div>', unsafe_allow_html=True)
            src_lang_name_tts = st.selectbox(
                label="source_lang_tts",
                options=LANG_NAMES,
                index=0,
                key="src_lang_tts",
                label_visibility="collapsed",
            )
        with col_arrow_tts:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center;font-size:1.5rem;color:#a78bfa;'>→</div>", unsafe_allow_html=True)
        with col2_tts:
            st.markdown('<div class="section-label">🔊 Tiếng nói tạo ra</div>', unsafe_allow_html=True)
            # Default target = English
            default_tgt = LANG_NAMES[1] if LANG_NAMES[0] == src_lang_name_tts else LANG_NAMES[0]
            tgt_lang_name_tts = st.selectbox(
                label="target_lang_tts",
                options=LANG_NAMES,   # Here they can be the same if they just want TTS directly
                index=LANG_NAMES.index(default_tgt) if default_tgt in LANG_NAMES else 0,
                key="tgt_lang_tts",
                label_visibility="collapsed",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    src_code_tts = LANGUAGES[src_lang_name_tts]
    tgt_code_tts = LANGUAGES[tgt_lang_name_tts]

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 2 — TEXT</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✍️ Nhập nội dung văn bản</div>', unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Nhập nội dung văn bản để chuyển thành giọng nói", 
            placeholder="Nhập nội dung tại đây...", 
            label_visibility="collapsed",
            height=120,
            key="tts_text"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">STEP 3 — GENERATE</div>', unsafe_allow_html=True)
        
        tts_btn = st.button("🚀 Chuyển đổi sang Giọng Nói", use_container_width=True, key="tts_btn")

        if tts_btn:
            if not text_input.strip():
                st.warning("⚠️ Vui lòng nhập văn bản.")
            else:
                with st.spinner("🔄 Đang xử lý giọng nói..."):
                    try:
                        result_tts = call_tts_api(text_input, src_code_tts, tgt_code_tts)
                        st.session_state["last_tts_result"] = result_tts
                        st.success("✅ Tạo giọng nói thành công!")
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                        st.session_state.pop("last_tts_result", None)
        st.markdown("</div>", unsafe_allow_html=True)

    if "last_tts_result" in st.session_state:
        res_tts = st.session_state["last_tts_result"]
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-badge">RESULT</div>', unsafe_allow_html=True)
        
        if src_code_tts != tgt_code_tts:
            st.markdown(f'<div class="section-label">🌍 Translation ({res_tts.get("target_language", "")})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box translated">{res_tts.get("translated_text", "")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown('<div class="section-label">🔊 Audio Generated</div>', unsafe_allow_html=True)
        audio_url = f'{BACKEND_URL}{res_tts.get("audio_url")}'
        
        st.audio(audio_url)
        
        # Action Links
        col_down1, col_down2 = st.columns([1,1])
        with col_down1:
            st.markdown(f'<a href="{audio_url}" target="_blank" style="text-decoration: none; padding: 10px 15px; background: rgba(96, 165, 250, 0.2); color: #bae6fd; border-radius: 8px; display: inline-block;">🔗 Mở Audio trong tab mới (Copy URL)</a>', unsafe_allow_html=True)
        with col_down2:
            st.markdown(f'<a href="{audio_url}" download="tts_audio.mp3" style="text-decoration: none; padding: 10px 15px; background: rgba(167, 139, 250, 0.2); color: #c4b5fd; border-radius: 8px; display: inline-block;">💾 Tải xuống Audio file</a>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <hr>
    <div style="text-align:center;color:#475569;font-size:0.8rem;padding:0.5rem 0 1.5rem;">
        Powered by <strong style="color:#a78bfa;">Groq</strong> ·
        <strong style="color:#60a5fa;">Whisper Large v3</strong> ·
        <strong style="color:#34d399;">LLaMA 3.3 70B</strong> ·
        <strong style="color:#f472b6;">Edge TTS</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
