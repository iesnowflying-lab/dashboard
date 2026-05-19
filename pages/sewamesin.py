import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Monitoring Peminjaman Mesin - sewa mesin01",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# 2. CUSTOM CSS
st.markdown("""
    <style>
    /* Menghilangkan Sidebar, Tombol Sidebar, dan Header secara total */
    [data-testid="stSidebar"], 
    [data-testid="collapsedControl"], 
    .st-emotion-cache-16ids0d, 
    header, 
    #tabs-b3-tabs-0-tab-0 {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
    }
    
    /* Menghilangkan margin atas akibat header yang hilang */
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
    }

    /* Kartu Metrik Transparan */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.7);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
            
    /* Background Gradient Fixed */
    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 12%, #4682B4 80%, #1E3A5F 100%);
        background-attachment: fixed;
    }
    .stButton button { 
        width: 100%; 
        height: 85px; 
        border-radius: 15px; 
        font-weight: bold; 
    }
    .double-line {
        border-top: 3px solid black;
        border-bottom: 6px solid black;
        height: 12px;
        margin: 5px 0 25px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER & TOMBOL NAVIGASI ---
col_judul, col_back = st.columns([4, 1])

# 3. KONEKSI DATA
url_sheets = "https://docs.google.com/spreadsheets/d/1BvYyCa0DgJrjuMYQzFEL_49_StYhr71rzvNJ8crwHaU/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    return conn.read(spreadsheet=url_sheets, ttl="0")

# --- FUNGSI WARNA KHUSUS KOLOM SISA ---
def color_sisa_only(val):
    try:
        # Mengambil angka dari teks "X Hari"
        num = int(str(val).split()[0])
        if num <= 0:
            return 'background-color: #ffcccc; color: black;' # Merah
        elif 1 <= num <= 7:
            return 'background-color: #fff9c4; color: black;' # Kuning
    except:
        pass
    return ''

# Mapping warna pie agar sama di ISG & IRG
COLOR_MAP_PIE = {
    'Excavator': '#636EFA', 'Bulldozer': '#EF553B', 'Crane': '#00CC96', 
    'Forklift': '#AB63FA', 'Generator': '#FFA15A', 'Welding': '#19D3F3'
}

def create_min_donut(dataframe, site_name):
    df_site = dataframe[dataframe['To'] == site_name].groupby('Jenis_Mesin')['Qty'].sum().reset_index()
    if df_site.empty: return None
    
    fig = px.pie(df_site, values='Qty', names='Jenis_Mesin', hole=0.5,
                 color='Jenis_Mesin', color_discrete_map=COLOR_MAP_PIE)
    
    fig.update_traces(
        textinfo='label+value', 
        textposition='outside',
        textfont=dict(size=14, color="#4B4848"), # Teks Pie Kuning
        marker=dict(line=dict(color='#FFFFFF', width=1.5))
    )
    fig.update_layout(
        showlegend=False, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=site_name, x=0.5, y=0.5, showarrow=False, font=dict(size=30, color="white"))]
    )
    return fig

# 4. HEADER
st.title("📡 Monitoring Peminjaman Mesin")
st.markdown('<div class="double-line"></div>', unsafe_allow_html=True)

try:
    df_raw = load_data()
    df = df_raw.copy()
    df['To'] = df['To'].astype(str).str.strip()
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    df['Akhir_Sewa'] = pd.to_datetime(df['Akhir_Sewa'], errors='coerce').dt.date
    
    hari_ini = datetime.now().date()
    df['Sisa'] = df['Akhir_Sewa'].apply(lambda x: (x - hari_ini).days if pd.notna(x) else 0)
    df_monitor = df[df['Status_Kembali'] == False].sort_values(by='Akhir_Sewa')

    # --- METRICS & REFRESH ---
    m1, m2, m3, m4 = st.columns([1, 1, 1, 0.6])
    total_unit = df_monitor['Qty'].sum()
    m1.metric("Total Unit Disewa", f"{total_unit} Unit")
    m2.metric("Deadline < 7 Hari", f"{df_monitor[df_monitor['Sisa'] <= 7].shape[0]} Mesin")
    m3.metric("Total Lokasi", f"{df_monitor['To'].nunique()} Lokasi")
    with m4:
        st.write("") 
        if st.button('🔄 Refresh Data'):
            st.cache_data.clear()
            st.rerun()

    # --- TABEL ---
    st.subheader("📋 Detail Peminjaman")
    df_table = df_monitor[['Jenis_Mesin', 'Merek', 'Type', 'Qty', 'To', 'Start_Sewa', 'Akhir_Sewa', 'Sisa']].copy()
    
    # Format agar rata kiri dengan menambahkan satuan secara manual
    df_table['Qty'] = df_table['Qty'].astype(str) + " Unit"
    df_table['Sisa'] = df_table['Sisa'].astype(str) + " Hari"
    df_table = df_table.rename(columns={'Sisa': 'Sisa Hari'})
    df_table['Start_Sewa'] = pd.to_datetime(df_table['Start_Sewa'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
    df_table['Akhir_Sewa'] = pd.to_datetime(df_table['Akhir_Sewa'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')

    # Terapkan warna hanya di kolom Sisa Hari agar tidak merusak format tanggal
    styled_df = df_table.style.map(color_sisa_only, subset=['Sisa Hari'])
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # --- DIAGRAM DONUT ---
    st.subheader("📍 Sebaran Unit Berdasarkan Lokasi")
    col_isg, col_irg = st.columns(2)
    with col_isg:
        f_isg = create_min_donut(df_monitor, 'ISG')  # Sudah tanpa argumen ketiga
        if f_isg: st.plotly_chart(f_isg, use_container_width=True)
    with col_irg:
        f_irg = create_min_donut(df_monitor, 'IRG')  # Sudah tanpa argumen ketiga
        if f_irg: st.plotly_chart(f_irg, use_container_width=True)

    st.markdown("---")
    
    # --- DIAGRAM BATANG (Kuning & Cream) ---
    st.subheader("📊 Total Semua Jenis Mesin")
    df_total = df_monitor.groupby('Jenis_Mesin')['Qty'].sum().sort_values(ascending=False).reset_index()
    
    fig_bar = px.bar(df_total, x='Qty', y='Jenis_Mesin', orientation='h')
    
    fig_bar.update_traces(
        marker_color="#FAFAF6",      # Warna Cream
        marker_line_color="#0E0E0D", # Warna Orange Muda (Border)
        marker_line_width=1,
        texttemplate='%{x} Unit', 
        textposition='outside',      # Pindah ke luar agar teks kuning terlihat
        textfont=dict(size=14, color='#FFFDD0') # Tulisan di dalam bar/ujung bar Kuning
    )

    fig_bar.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickfont=dict(size=14, color='#FFFDD0'), # Sumbu X Kuning
            title=None,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            tickfont=dict(size=14, color='#FFFDD0'), # Sumbu Y Kuning
            title=None
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"❌ Kesalahan: {e}")






