import streamlit as st
import os
import base64
import pandas as pd

# --- 1. KONFIGURASI HALAMAN (Gabungan & Fix) ---
st.set_page_config(
    page_title="Snowflying Portal", 
    page_icon="🏭", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SETTINGS & ASSETS ---
logo_path = "LOGO_ISG.png"
bg_image_path = "biru.jpg"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1Tu6B-gmjPgFA-CFPfzyM7qbwoddGd4InjCUT-kmpTxzhhXK1xBriSOgWg2oq8EedCIebED2Nfqsz/pub?gid=0&single=true&output=csv"

# Fungsi untuk memuat data user
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

# --- 3. LOGIKA AUTHENTICATION (Kunci Akses) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 4. CSS CUSTOM (FIXED SIDEBAR & VISUAL) ---
st.markdown(f"""
    <style>
    /* PROTEKSI: Menghilangkan Sidebar, Navigasi, dan Tombol Chevron */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarNav"], 
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}
    
    header {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
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
        background: linear-gradient(to left, 
            rgba(0,0,0,0.8) 0%, 
            rgba(0,0,0,0.3) 65%, 
            rgba(0,0,0,0) 0%);
        z-index: 1;
        pointer-events: none;
    }}

    .text-container {{
        position: fixed;
        right: 5%; top: 50%; transform: translateY(-50%);
        color: white; z-index: 2; text-align: left;
    }}

    .welcome-title {{
        font-size: 70px !important; font-weight: 900 !important;
        margin-bottom: 0 !important; line-height: 1.1 !important;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6);
    }}

    .sub-title {{
        font-size: 28px !important; font-weight: 400 !important;
        margin-top: 15px !important; opacity: 0.95;
        text-shadow: 0px 0px 10px rgba(0,0,0,0.5);
        font-style: italic;
    }}

    .login-section {{
        position: relative; z-index: 30;
        padding-left: 15%; padding-top: 10vh;
    }}

    div[data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 40px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5) !important;
        width: 420px !important;
    }}

    .footer-text {{
        text-align: center; color: white; font-size: 11px;
        margin-top: 25px; opacity: 0.8;
    }}
    </style>

    <div class="full-overlay"></div>
    <div class="text-container">
        <h1 class="welcome-title">INDUSTRIAL ENGINEERING</h1>
        <p class="sub-title">A commitment to integrity and continuous improvement</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. TAMPILAN (LOGIN ATAU REDIRECT) ---
if not st.session_state["authenticated"]:
    st.markdown('<div class="login-section">', unsafe_allow_html=True)
    col1, _ = st.columns([1.5, 2.3])
    with col1:
        with st.form("login_box"):
            if logo_base64:
                st.markdown(f'<div style="text-align: center; margin-bottom: 25px;"><img src="data:image/png;base64,{logo_base64}" width="150"></div>', unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Your ID")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("LOGIN")
            st.markdown('<div class="footer-text">@2025</div>', unsafe_allow_html=True)

    if submitted:
        if not USER_DB:
            st.error("Database tidak tersedia.")
        else:
            if username in USER_DB and str(USER_DB[username]) == password:
                st.session_state["authenticated"] = True
                st.success(f"Access Granted!")
                st.rerun() # Merefresh halaman untuk masuk ke logika redirect di bawah
            else:
                st.error("Invalid Username or Password")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Jika sudah login, langsung lempar ke menu utama
    st.switch_page("pages/menu_utama.py")