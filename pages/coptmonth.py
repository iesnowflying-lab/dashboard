import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS GRADIENT
# ==========================================
st.set_page_config(
    page_title="IE Complete Data Viewer", 
    layout="wide", 
    page_icon="🏭",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] { display: none !important; }
    header { visibility: hidden; height: 0px; }
    
    /* BACKGROUND BERGRADASI DASHBOARD IE */
    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 12%, #4682B4 80%, #1E3A5F 100%);
        background-attachment: fixed;
    }
    
    .block-container { padding-top: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    
    .main-title {
        background: linear-gradient(135deg, #71717A 0%, #3F3F46 100%);
        padding: 15px;
        border-radius: 8px;
        color: #FFFFFF;
        text-align: center;
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .building-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* GAYA TABEL DATAFRAME */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* GAYA INSIGHT CARD */
    .insight-card-terendah {
        background-color: rgba(59, 130, 246, 0.25);
        border-left: 6px solid #3B82F6;
        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #FFFFFF;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .insight-card-terbesar {
        background-color: rgba(239, 68, 68, 0.25);
        border-left: 6px solid #EF4444;
        padding: 12px 15px;
        margin-bottom: 20px;
        border-radius: 4px;
        color: #FFFFFF;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADER (MURNI DARI DRIVE)
# ==========================================
@st.cache_data
def load_raw_data():
    try:
        FILE_ID = "1TJHsdyAyAtX1yminIF6-z8UPBcvjVuJT"
        DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(DOWNLOAD_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            st.error(f"Gagal mengunduh file. Status Code: {response.status_code}")
            return pd.DataFrame()
            
        df = pd.read_excel(io.BytesIO(response.content), sheet_name="REKAP COPT")
        return df
    except Exception as e:
        st.error(f"Gagal membaca Excel: {e}")
        return pd.DataFrame()

# ==========================================
# 3. TAMPILAN UTAMA & LOGIKA EKSTRAKSI
# ==========================================
st.markdown('<div class="main-title">📊 COPT PERFORMANCE</div>', unsafe_allow_html=True)

df_raw = load_raw_data()

if not df_raw.empty:
    try:
        # --- STRATEGI KUNCI POSISI KOLOM (BY INDEX) ---
        df_display = pd.DataFrame({
            'Building': df_raw.iloc[:, 1],
            'Month': df_raw.iloc[:, 2],
            'Line': df_raw.iloc[:, 3],
            'Style': df_raw.iloc[:, 4],
            'SMV (Minutes)': df_raw.iloc[:, 5],
            'COPT (Minutes)': df_raw.iloc[:, 7],
            'COPT x SMV': df_raw.iloc[:, 8],
            'Avg COPT_Internal': df_raw.iloc[:, 9]
        }).copy()
        
        # Mengisi baris kosong akibat merged cells bawaan Excel
        df_display = df_display.ffill()
        
        # --- STANDARISASI DATA TEKS ---
        df_display['Building'] = df_display['Building'].astype(str).str.strip().str.upper()
        df_display['Month'] = df_display['Month'].astype(str).str.strip()
        df_display['Style'] = df_display['Style'].astype(str).str.strip()
        
        # Standarisasi kolom Line menjadi string bersih
        df_display['Line'] = pd.to_numeric(df_display['Line'], errors='coerce')
        df_display['Line'] = df_display['Line'].fillna(-999).astype(int).astype(str)
        df_display.loc[df_display['Line'] == '-999', 'Line'] = "-"
        
        # --- STANDARISASI DATA NUMERIK ---
        numeric_cols = ['SMV (Minutes)', 'COPT (Minutes)', 'COPT x SMV', 'Avg COPT_Internal']
        for col in numeric_cols:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce')
            
        # FORMATTING: Mengunci kolom COPT x SMV agar selalu 2 digit di belakang koma
        df_display['COPT x SMV'] = df_display['COPT x SMV'].round(2)
            
        # Hapus baris sisa di bagian bawah tabel
        df_display = df_display.dropna(subset=['Style'])
        df_display = df_display[~df_display['Style'].isin(['nan', '', '-'])]

        # Bersihkan baris bulan jika ada text 'nan'
        df_filtered_base = df_display[df_display['Month'] != 'nan'].copy()

        # URUTAN KRONOLOGIS BULAN: Memastikan urutan menyambung dari tahun sebelumnya
        sort_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August','September', 'October', 'November', 'December']

        def get_sort_index(month_str):
            cleaned = str(month_str).strip()
            month_word = cleaned.split()[0].split('-')[0]
            if month_word in sort_order:
                return sort_order.index(month_word)
            return len(sort_order)

        # ==========================================
        # 4. LAYOUT 2 KOLOM BESAR (ISG vs IRG)
        # ==========================================
        col_isg, col_irg = st.columns(2)

        # ------------------------------------------
        # KOLOM KIRI: AREA ISG
        # ------------------------------------------
        with col_isg:
            st.markdown('<div class="building-header">INDONESIA SNOWFLYING GARMENT</div>', unsafe_allow_html=True)
            df_isg = df_filtered_base[df_filtered_base['Building'] == 'ISG'].copy()
            
            if not df_isg.empty:
                # A. Pembuatan Grafik Kombinasi (Bar + Line) ISG
                trend_isg = df_isg.groupby('Month')['Avg COPT_Internal'].mean().reset_index()
                trend_isg['Sort_Key'] = trend_isg['Month'].apply(get_sort_index)
                trend_isg = trend_isg.sort_values('Sort_Key').drop(columns=['Sort_Key'])
                trend_isg['Avg COPT_Internal'] = trend_isg['Avg COPT_Internal'].round(2)
                
                # Menghitung batas atas sumbu Y agar teks tidak terpotong
                max_y_isg = trend_isg['Avg COPT_Internal'].max() * 1.25

                fig_isg = go.Figure()

                # Tambahkan trace batang (Bar)
                fig_isg.add_trace(go.Bar(
                    x=trend_isg['Month'],
                    y=trend_isg['Avg COPT_Internal'],
                    marker=dict(
                        color='rgba(173, 216, 230, 0.3)', # Biru terang transparan
                        line=dict(color='#FFFFFF', width=1.5) # Border batang putih
                    ),
                    name='Bar'
                ))

                # Tambahkan trace garis dan angka (Line)
                fig_isg.add_trace(go.Scatter(
                    x=trend_isg['Month'],
                    y=trend_isg['Avg COPT_Internal'],
                    mode='lines+markers+text',
                    text=trend_isg['Avg COPT_Internal'],
                    textposition="top center",
                    textfont=dict(size=14, color='#FFFFFF', family="Arial Black"),
                    line=dict(color='#00FFFF', width=3), # Garis Cyan terang
                    marker=dict(size=8, color='#00FFFF'),
                    name='Line'
                ))

                fig_isg.update_layout(
                    title="Average COPT - ISG (SMV X COPT)",
                    title_font=dict(size=16, color='#FFFFFF', family="Arial"),
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    height=320,
                    showlegend=False,
                    xaxis=dict(title=None, tickfont=dict(color='#FFFFFF', size=12, family="Arial", weight="bold"), showgrid=False),
                    yaxis=dict(title=None, visible=False, showgrid=False, range=[0, max_y_isg]),
                    margin=dict(t=50, b=20, l=0, r=0)
                )
                st.plotly_chart(fig_isg, use_container_width=True)
                
                # B. METRIK INSIGHT COPT STYLE - ISG
                idx_max_isg = df_isg['COPT (Minutes)'].idxmax()
                idx_min_isg = df_isg['COPT (Minutes)'].idxmin()
                
                style_max_isg = df_isg.loc[idx_max_isg, 'Style']
                val_max_isg = df_isg.loc[idx_max_isg, 'COPT (Minutes)']
                style_min_isg = df_isg.loc[idx_min_isg, 'Style']
                val_min_isg = df_isg.loc[idx_min_isg, 'COPT (Minutes)']
                
                st.markdown(f"""
                <div class="insight-card-terendah">
                    🔹 <b>STYLE DENGAN COPT TERENDAH :</b> {style_min_isg} ({val_min_isg} Min)
                </div>
                <div class="insight-card-terbesar">
                    🔺 <b>STYLE DENGAN COPT TERLAMA :</b> {style_max_isg} ({val_max_isg} Min)
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.info("Tidak ada data untuk area ISG.")

        # ------------------------------------------
        # KOLOM KANAN: AREA IRG
        # ------------------------------------------
        with col_irg:
            st.markdown('<div class="building-header">INDONESIA RABBONI GARMENT</div>', unsafe_allow_html=True)
            df_irg = df_filtered_base[df_filtered_base['Building'] == 'IRG'].copy()
            
            if not df_irg.empty:
                # A. Pembuatan Grafik Kombinasi (Bar + Line) IRG
                trend_irg = df_irg.groupby('Month')['Avg COPT_Internal'].mean().reset_index()
                trend_irg['Sort_Key'] = trend_irg['Month'].apply(get_sort_index)
                trend_irg = trend_irg.sort_values('Sort_Key').drop(columns=['Sort_Key'])
                trend_irg['Avg COPT_Internal'] = trend_irg['Avg COPT_Internal'].round(2)

                # Menghitung batas atas sumbu Y agar teks tidak terpotong
                max_y_irg = trend_irg['Avg COPT_Internal'].max() * 1.25

                fig_irg = go.Figure()

                # Tambahkan trace batang (Bar)
                fig_irg.add_trace(go.Bar(
                    x=trend_irg['Month'],
                    y=trend_irg['Avg COPT_Internal'],
                    marker=dict(
                        color='rgba(70, 130, 180, 0.4)', # Biru tua transparan
                        line=dict(color='#FFFFFF', width=1.5) # Border batang putih
                    ),
                    name='Bar'
                ))

                # Tambahkan trace garis dan angka (Line)
                fig_irg.add_trace(go.Scatter(
                    x=trend_irg['Month'],
                    y=trend_irg['Avg COPT_Internal'],
                    mode='lines+markers+text',
                    text=trend_irg['Avg COPT_Internal'],
                    textposition="top center",
                    textfont=dict(size=14, color='#FFFFFF', family="Arial Black"),
                    line=dict(color='#FFD700', width=3), # Garis Kuning Emas
                    marker=dict(size=8, color='#FFD700'),
                    name='Line'
                ))

                fig_irg.update_layout(
                    title="Average COPT - IRG (SMV X COPT)",
                    title_font=dict(size=16, color='#FFFFFF', family="Arial"),
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    height=320,
                    showlegend=False,
                    xaxis=dict(title=None, tickfont=dict(color='#FFFFFF', size=12, family="Arial", weight="bold"), showgrid=False),
                    yaxis=dict(title=None, visible=False, showgrid=False, range=[0, max_y_irg]),
                    margin=dict(t=50, b=20, l=0, r=0)
                )
                st.plotly_chart(fig_irg, use_container_width=True)
                
                # B. METRIK INSIGHT COPT STYLE - IRG
                idx_max_irg = df_irg['COPT (Minutes)'].idxmax()
                idx_min_irg = df_irg['COPT (Minutes)'].idxmin()
                
                style_max_irg = df_irg.loc[idx_max_irg, 'Style']
                val_max_irg = df_irg.loc[idx_max_irg, 'COPT (Minutes)']
                style_min_irg = df_irg.loc[idx_min_irg, 'Style']
                val_min_irg = df_irg.loc[idx_min_irg, 'COPT (Minutes)']
                
                st.markdown(f"""
                <div class="insight-card-terendah">
                    🔹 <b>STYLE DENGAN COPT TERENDAH :</b> {style_min_irg} ({val_min_irg} Min)
                </div>
                <div class="insight-card-terbesar">
                    🔺 <b>STYLE DENGAN COPT TERLAMA :</b> {style_max_irg} ({val_max_irg} Min)
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.info("Tidak ada data untuk area IRG.")

        # ==========================================
        # 5. PANEL FILTER MULTISELECT (BAGIAN BAWAH)
        # ==========================================
        st.write("---")
        st.markdown("<h4 style='color:white;'>🔍 Detail Data </h4>", unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            opts_month = sorted(list(df_filtered_base['Month'].unique()), key=get_sort_index)
            selected_months = st.multiselect("Filter Bulan:", options=opts_month, placeholder="Semua Bulan")
            
        with col_f2:
            opts_style = sorted(list(df_filtered_base['Style'].unique()))
            selected_styles = st.multiselect("Filter Style:", options=opts_style, placeholder="Semua Style")
            
        with col_f3:
            opts_line = sorted(list(df_filtered_base['Line'].unique()), key=lambda x: int(x) if str(x).isdigit() else 999)
            selected_lines = st.multiselect("Filter Line:", options=opts_line, placeholder="Semua Line")

        # Proses Filtering Data Tabel
        df_table_filtered = df_filtered_base.copy()
        
        if selected_months:
            df_table_filtered = df_table_filtered[df_table_filtered['Month'].isin(selected_months)]
        if selected_styles:
            df_table_filtered = df_table_filtered[df_table_filtered['Style'].isin(selected_styles)]
        if selected_lines:
            df_table_filtered = df_table_filtered[df_table_filtered['Line'].isin(selected_lines)]

        # Drop kolom internal grafik sebelum render tabel bawah
        df_final_view = df_table_filtered.drop(columns=['Avg COPT_Internal'])

        # Render Tabel Hasil Filter (2 Kolom)
        st.markdown("<br>", unsafe_allow_html=True)
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            df_t_isg = df_final_view[df_final_view['Building'] == 'ISG']
            if not df_t_isg.empty:
                st.dataframe(df_t_isg.fillna("-"), use_container_width=True, hide_index=True)
            else:
                st.info("Tidak ada kecocokan data ISG untuk filter terpilih.")
            
        with col_t2:
            df_t_irg = df_final_view[df_final_view['Building'] == 'IRG']
            if not df_t_irg.empty:
                st.dataframe(df_t_irg.fillna("-"), use_container_width=True, hide_index=True)
            else:
                st.info("Tidak ada kecocokan data IRG untuk filter terpilih.")
        
    except IndexError:
        st.error("⚠️ Struktur kolom di Excel kurang dari standar urutan kolom B sampai I. Pastikan file 'REKAP COPT' sudah benar.")
    except Exception as e:
        st.error(f"Terjadi kendala saat menyusun komponen dashboard: {e}")
        
else:
    st.warning("Database kosong atau sheet 'REKAP COPT' gagal diproses.")
