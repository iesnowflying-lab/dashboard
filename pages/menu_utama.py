import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="IE Production Dashboard", page_icon="🏭", initial_sidebar_state="collapsed")

# 2. STYLE CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    header {visibility: hidden;}
    
    /* Menghilangkan Sidebar secara total agar bersih */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 40%, #4682B4 70%, #1E3A5F 100%);
        background-attachment: fixed;
    }
    .main-title { 
        font-size: 1.8rem !important; 
        color: #1E3A5F !important; 
        font-weight: 800;
        margin-top: -15px !important;
        margin-bottom: 5px !important;
    }
    .summary-box {
        background-color: rgba(255, 255, 255, 0.3);
        padding: 15px 20px !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 10px;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 5px !important;
    }
    [data-testid="stExpander"] summary {
        background-color: #1E3A5F !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* STYLE TOMBOL NAVIGASI TAB BARU */
    .nav-link {
        display: block;
        width: 100%;
        height: 32px;
        line-height: 32px;
        background-color: white;
        color: #1E3A5F !important;
        text-align: center;
        text-decoration: none !important;
        font-weight: 700;
        border-radius: 4px;
        border: 1px solid #d3d3d3;
        margin-bottom: 5px;
        font-size: 14px;
    }
    .nav-link:hover {
        background-color: #f0f2f6;
        border-color: #1E3A5F;
    }

    .stButton>button {
        width: 100% !important;
        height: 32px !important;
        background-color: white !important;
        color: #1E3A5F !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 5px 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=30)
def get_efficiency_dataframe(url):
    try:
        file_id = url.split('/')[-2]
        export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        xls = pd.ExcelFile(export_url)
        all_sheets_data = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            p_eff = df.iloc[0, 10] * 100
            a_eff = df.iloc[0, 18] * 100
            p_avail = df.iloc[0, 8]
            p_earned = df.iloc[0, 9]
            a_avail = df.iloc[0, 16]
            a_earned = df.iloc[0, 17]
            
            all_sheets_data.append({
                "Month": sheet, 
                "Plan": round(p_eff, 1), 
                "Actual": round(a_eff, 1),
                "P_Avail": p_avail, "P_Earned": p_earned,
                "A_Avail": a_avail, "A_Earned": a_earned
            })
        return pd.DataFrame(all_sheets_data)
    except: return pd.DataFrame()

df_final = get_efficiency_dataframe("https://docs.google.com/spreadsheets/d/1QN-kgqHSOAcnYqNLXAkfl7sLeT64Qt9p/edit")

# --- HEADER ---
t1, t2 = st.columns([1.1, 2.6], gap="small")
with t1:
    st.markdown("<p class='main-title'>🏭 IE Dashboard</p>", unsafe_allow_html=True)
with t2:
    st.markdown("<div style='padding-left: 20px;'><p class='main-title'>Efficiency Performance</p></div>", unsafe_allow_html=True)

# --- LAYOUT UTAMA ---
col_left, col_right = st.columns([1.1, 2.6], gap="small")

with col_left:
    st.markdown("<p style='font-size:0.85rem; font-weight:bold; color:#1E3A5F; margin-top: -15px;'>Industrial Engineering</p>", unsafe_allow_html=True)
    if not df_final.empty:
        st.markdown(f'<div class="summary-box"><span style="color:#1E3A5F; font-weight:700;">Summary {df_final.iloc[-1]["Month"]}</span></div>', unsafe_allow_html=True)
        last, prev = df_final.iloc[-1], (df_final.iloc[-2] if len(df_final) >= 2 else df_final.iloc[-1])
        m1, m2 = st.columns(2)
        m1.metric("Plan Eff", f"{last['Plan']}%", f"{round(last['Plan']-prev['Plan'],1)}%")
        m2.metric("Actual Eff", f"{last['Actual']}%", f"{round(last['Actual']-prev['Actual'],1)}%")

    # --- NAVIGATION SECTION ---
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    with st.expander("⊚ Production Data"):
        st.markdown('<a href= "/absen" target="_blank" class="nav-link">≫ Data Absen (on progresss) </a>', unsafe_allow_html=True)
        st.markdown('<a href= "https://docs.google.com/spreadsheets/d/1NNVyaEJfiEKLNwoOsusYcGF4q_nQonBu/edit?usp=drive_link&ouid=117491108448694901071&rtpof=true&sd=true" target="_blank" class="nav-link">≫ Data Quality (waiting) </a>', unsafe_allow_html=True)            
        st.markdown('<a href= "" target="_blank" class="nav-link">≫ Data eff (waiting) </a>', unsafe_allow_html=True)
        st.markdown('<a href= "/coptmonth" target="_blank" class="nav-link">≫ COPT Monthly </a>', unsafe_allow_html=True)
        st.markdown('<a href= "" target="_blank" class="nav-link">≫ COPT Line (waiting) </a>', unsafe_allow_html=True)

    with st.expander("⊚ Development Data"):
        st.markdown('<a href= "https://drive.google.com/drive/folders/1ZAUgV0S5w9_3ujglIPyckG5MUX9KROv0?usp=sharing" target="_blank" class="nav-link">≫ Video Training </a>', unsafe_allow_html=True)
    
    with st.expander("⊚ Matrix Skill"):
        st.markdown('<a href="/skillmatrix" target="_blank" class="nav-link">≫ Skill Matrix apk</a>', unsafe_allow_html=True)
        st.markdown('<a href="/gradelineisg" target="_blank" class="nav-link">≫ Grade Line ISG </a>', unsafe_allow_html=True)
        st.markdown('<a href="/skillmatrix" target="_blank" class="nav-link">≫ Skill Matrix Dashboard</a>', unsafe_allow_html=True)

    with st.expander("⊚ Machine"):
        st.markdown('<a href="/sewamesin" target="_blank" class="nav-link">≫ Monitoring Sewa</a>', unsafe_allow_html=True)

# --- BAGIAN KANAN (Grafik) ---
with col_right:
    st.markdown('<div style="padding-left: 20px; margin-top: -35px;">', unsafe_allow_html=True)
    
    if not df_final.empty:
        latest = df_final.iloc[-1]
        
        st.markdown("<p style='font-weight:bold; color:#1E3A5F; text-align: center; margin-bottom: 15px;'>⏱️ Production Minutes Status</p>", unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.metric(label="Plan Available (Mins)", value=f"{int(latest['P_Avail']):,}")
        with col_p2:
            st.metric(label="Plan Earned (Mins)", value=f"{int(latest['P_Earned']):,}")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.metric(label="Actual Available (Mins)", value=f"{int(latest['A_Avail']):,}")
        with col_a2:
            st.metric(label="Actual Earned (Mins)", value=f"{int(latest['A_Earned']):,}")
            
        st.markdown("<hr style='margin: 15px 0 5px 0; border: 0.5px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        
        eff_col1, eff_col2 = st.columns(2)
        with eff_col1:
            st.markdown("<p style='font-weight:bold; color:white; font-size:0.9rem; text-align: center; margin-bottom: -20px;'>📈 Plan Efficiency</p>", unsafe_allow_html=True)
            fig_p = go.Figure()
            fig_p.add_trace(go.Bar(
                x=df_final['Month'], y=df_final['Plan'], 
                marker=dict(color='#ADD8E6', line=dict(color='white', width=1.5)),
                text=df_final['Plan'].apply(lambda x: f"{x}%"),
                textposition='outside', textfont=dict(color='white')
            ))
            fig_p.add_trace(go.Scatter(x=df_final['Month'], y=df_final['Plan'], mode='lines+markers', line=dict(color='#00F2FF', width=3)))
            fig_p.update_layout(yaxis=dict(visible=False, range=[0, 150]), xaxis=dict(tickfont=dict(color='white')), height=210, margin=dict(l=0, r=10, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_p, use_container_width=True)
        
        with eff_col2:
            st.markdown("<p style='font-weight:bold; color:white; font-size:0.9rem; text-align: center; margin-bottom: -20px;'>📈 Actual Efficiency</p>", unsafe_allow_html=True)
            fig_a = go.Figure()
            fig_a.add_trace(go.Bar(
                x=df_final['Month'], y=df_final['Actual'], 
                marker=dict(color='#4682B4', line=dict(color='white', width=1.5)),
                text=df_final['Actual'].apply(lambda x: f"{x}%"),
                textposition='outside', textfont=dict(color='white')
            ))
            fig_a.add_trace(go.Scatter(x=df_final['Month'], y=df_final['Actual'], mode='lines+markers', line=dict(color='#FFD700', width=3)))
            fig_a.update_layout(yaxis=dict(visible=False, range=[0, 150]), xaxis=dict(tickfont=dict(color='white')), height=210, margin=dict(l=10, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_a, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
