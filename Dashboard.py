import streamlit as st
import os
import base64
import pandas as pd
from googletrans import Translator # <--- INTEGRASI BARU

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Snowflying Portal", 
    page_icon="🏭", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. INITIALIZE TRANSLATOR & SESSION STATE ---
if 'translator' not in st.session_state:
    st.session_state.translator = Translator()
if 'lang_code' not in st.session_state:
    st.session_state.lang_code = 'id' # Default Indonesia

# Fungsi Helper untuk Terjemah Otomatis
def translate_text(text):
    if st.session_state.lang_code == 'id':
        return text
    try:
        return st.session_state.translator.translate(text, dest=st.session_state.lang_code).text
    except:
        return text # Jika gagal, tampilkan teks asli

# --- 3. SETTINGS & ASSETS ---
logo_path = "LOGO_ISG.png"
bg_image_path = "biru.jpg"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1Tu6B-gmjPgFA-CFPfzyM7qbwoddGd4InjCUT-kmpTxzhhXK1xBriSOgWg2oq8EedCIebED2Nfqsz/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)
def load_user_database(url):
    try:
        df = pd.read_csv(url)
        return dict(zip(df['Username'].astype(str), df['Password'].astype(str)))
    except Exception as e:
        st.error(f"Koneksi Database Gagal: {e}")
        return {}

def get_base64_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

logo_base64 = get_base64_image(logo_path)
bg_base64 = get_base64_image(bg_image_path)
USER_DB = load_user_database(SHEET_URL)

# --- 4. LOGIKA AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 5. CSS CUSTOM ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {{
        display: none !important;
    }}
    header {{visibility: hidden;}}
    .main .block-container {{padding: 0 !important; max-width: 100% !important;}}
    .stApp {{
        background: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .full-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100vh;
        background: linear-gradient(to left, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.3) 65%, rgba(0,0,0,0) 0%);
        z-index: 1; pointer-events: none;
    }}
    .text-container {{
        position: fixed;
        right: 5%; top: 50%; transform: translateY(-50%);
        color: white; z-index: 2; text-align: left;
    }}
    .welcome-title {{
        font-size: 70px !important; font-weight: 900 !important;
        margin-bottom: 0 !important; line-height: 1.1 !important;
    }}
    .sub-title {{
        font-size: 28px !important; font-weight: 400 !important;
        margin-top: 15px !important; opacity: 0.95; font-style: italic;
    }}
    .login-section {{ position: relative; z-index: 30; padding-left: 15%; padding-top: 10vh; }}
    div[data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 40px !important;
        width: 420px !important;
    }}
    </style>
    <div class="full-overlay"></div>
    <div class="text-container">
        <h1 class="welcome-title">{translate_text("INDUSTRIAL ENGINEERING")}</h1>
        <p class="sub-title">{translate_text("A commitment to integrity and continuous improvement")}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 6. TAMPILAN LOGIN ---
if not st.session_state["authenticated"]:
    st.markdown('<div class="login-section">', unsafe_allow_html=True)
    col1, _ = st.columns([1.5, 2.3])
    with col1:
        # Pemilih Bahasa di luar Form agar responsif (atau di dalam sidebar tersembunyi)
        lang_sel = st.selectbox("🌐 Language", ["Bahasa Indonesia", "English", "日本語", "中文"], label_visibility="collapsed")
        lang_map = {"Bahasa Indonesia": "id", "English": "en", "日本語": "ja", "中文": "zh-cn"}
        st.session_state.lang_code = lang_map[lang_sel]

        with st.form("login_box"):
            if logo_base64:
                st.markdown(f'<div style="text-align: center; margin-bottom: 25px;"><img src="data:image/png;base64,{logo_base64}" width="150"></div>', unsafe_allow_html=True)
            
            # Teks Input yang diterjemahkan otomatis
            username = st.text_input(translate_text("Username"), placeholder=translate_text("Your ID"))
            password = st.text_input(translate_text("Password"), type="password", placeholder="••••••••")
            
            submitted = st.form_submit_button(translate_text("LOGIN"))
            st.markdown(f'<div style="text-align:center; color:white; font-size:11px; margin-top:10px;">@2025</div>', unsafe_allow_html=True)

    if submitted:
        if not USER_DB:
            st.error(translate_text("Database tidak tersedia."))
        else:
            if username in USER_DB and str(USER_DB[username]) == password:
                st.session_state["authenticated"] = True
                st.success(translate_text("Akses Diterima!"))
                st.rerun()
            else:
                st.error(translate_text("Username atau Password Salah"))
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.switch_page("pages/menu_utama.py")
