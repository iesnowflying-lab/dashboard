import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Grade Line Performance",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS CUSTOM (CLEAN UI & NAVY GRADIENT)
# ==========================================
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    header { visibility: hidden !important; height: 0px !important; }

    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 40%, #4682B4 70%, #1E3A5F 100%);
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* Banner Atas Soft Grey */
    .header-banner {
        background-color: rgba(248, 250, 252, 0.6);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(226, 232, 240, 0.4);
    }

    /* Header Section Analisis */
    .section-header {
        background-color: rgba(255, 255, 255, 0.65);
        padding: 12px 20px;
        border-radius: 10px; /* Diubah jadi rounded penuh agar berdiri sendiri */
        border-left: 6px solid #3B82F6;
        font-weight: bold;
        font-size: 1.1rem;
        color: #1E293B;
        margin-bottom: 20px;
    }

    /* Content Area: SEKARANG TRANSPARAN (Tanpa Kotak Putih) */
    .content-area {
        background-color: transparent; /* Menghilangkan kotak putih transparan */
        padding: 0px; 
        margin-bottom: 20px;
    }

    .table-title-container {
        padding-top: 30px;
        padding-bottom: 10px;
    }

    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.65) !important;
        border: 1px solid #E2E8F0 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI LOAD DATA
# ==========================================
@st.cache_data(ttl=60)
def load_grade_data():
    SHEET_ID = "1o1hP5I2IaxNDpe87L754TnYb9M058mDs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(URL)
        cols = [df.columns[0]] + list(df.columns[-3:])
        return df[cols]
    except:
        return pd.DataFrame()

def apply_grade_style(val):
    if not isinstance(val, str): return ''
    v = val.strip().upper()
    if v == 'A': return 'background-color: #dcfce7; color: #166534; font-weight: bold;'
    if v == 'B': return 'background-color: #dbeafe; color: #1e40af; font-weight: bold;'
    if v == 'C': return 'background-color: #ffedd5; color: #9a3412; font-weight: bold;'
    if v == 'D': return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
    return ''

# ==========================================
# 4. TAMPILAN DASHBOARD
# ==========================================
df_raw = load_grade_data()

if not df_raw.empty:
    last_col = df_raw.columns[-1]
    
    # Filter hanya yang ada isinya
    df_clean = df_raw[
        df_raw[last_col].notna() & 
        (df_raw[last_col].astype(str).str.strip() != "") & 
        (df_raw[last_col].astype(str).str.strip() != "-")
    ].copy()

    # --- 1. BANNER HEADER ---
    st.markdown(f"""
        <div class="header-banner">
            <h1 style='margin:0; color: #1E293B; font-size: 2.2rem;'>Grade Line Performance</h1>
            <div style='text-align: right;'>
                <p style='margin:0; font-weight: bold; color: #334155;'>Indonesia Snowflying Garments</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. SECTION ANALISIS PERFORMA ---
    st.markdown('<div class="section-header">📊 Analisis Performa</div>', unsafe_allow_html=True)
    
    # Membungkus col_chart dan col_metrics tanpa kotak putih latar belakang
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    col_chart, col_metrics = st.columns([1.3, 1])

    with col_chart:
        df_pie = df_clean[last_col].astype(str).str.upper().value_counts().reset_index()
        df_pie.columns = ['Grade', 'Total']
        fig = px.pie(
            df_pie, values='Total', names='Grade',
            hole=0.55,
            color='Grade',
            color_discrete_map={'A':'#00B894','B':'#3B82F6','C':'#F1C40F','D':'#E84393'}
        )
        fig.update_traces(textposition='inside', textinfo='label+value+percent', marker=dict(line=dict(color='#FFFFFF', width=1)))
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=350, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_metrics:
        total_filled = len(df_clean)
        st.metric("Total Line", f"{total_filled} Line")
        st.markdown("<div style='margin: 1px 0; border-top: 1px solid rgba(255,255,255,0.9);'></div>", unsafe_allow_html=True)
     
        m1, m2 = st.columns(2)

        m3, m4 = st.columns(2)

        c_a = len(df_clean[df_clean[last_col].astype(str).str.upper() == 'A'])
        c_b = len(df_clean[df_clean[last_col].astype(str).str.upper() == 'B'])
        c_c = len(df_clean[df_clean[last_col].astype(str).str.upper() == 'C'])
        c_d = len(df_clean[df_clean[last_col].astype(str).str.upper() == 'D'])

        m1.metric("Grade A", f"{c_a} Line")
        m2.metric("Grade B", f"{c_b} Line")
        m3.metric("Grade C", f"{c_c} Line")
        m4.metric("Grade D", f"{c_d} Line")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. SECTION TABEL ---
    _, col_t, _ = st.columns([0.8, 2.4, 0.8])
    with col_t:
        st.markdown("""
            <div class="table-title-container">
                <p style='color: cream; font-weight: bold; font-size: 1.1rem; margin: 0;'>📑 Detail Performance Line</p>
            </div>
        """, unsafe_allow_html=True)
        
        df_display = df_raw.fillna("-")
        styled_df = df_display.style.applymap(apply_grade_style, subset=df_display.columns[-3:]) \
                    .set_properties(**{'text-align': 'center', 'font-size': '15px'})

        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=500)

else:
    st.error("Gagal terhubung ke sumber data.")