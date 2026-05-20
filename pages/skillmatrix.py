import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Skill Matrix Dashboard", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# CSS UNTUK TAMPILAN
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    header {
        visibility: hidden;
        height: 0px;
    }
    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 12%, #4682B4 80%, #1E3A5F 100%);
        background-attachment: fixed;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    .custom-header {
        background-color: #e2e8f0; 
        padding: 0px 40px;
        border-radius: 15px;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        border: 1px solid #94a3b8;
        height: 140px;
    }
    .title-text { color: #000000 !important; font-size: 35px; font-weight: 800; margin: 0; }
    .header-logo { height: 90px; width: auto; object-fit: contain; }
    .section-title {
        background-color: #e2e8f0; 
        color: #000000;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        margin-bottom: 20px;
        border-left: 5px solid #3b82f6;
    }
    [data-testid="stMetric"] {
        background-color: #e2e8f0;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
    }
    .streamlit-expanderHeader {
        background-color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI LOAD LOGO & DATA
# ==========================================
@st.cache_data
def get_base64_logo(url):
    try:
        if 'drive.google.com' in url:
            file_id = url.split('/')[-2]
            direct_url = f'https://drive.google.com/uc?export=download&id={file_id}'
        else:
            direct_url = url
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(direct_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
        return ""
    except Exception:
        return ""

@st.cache_data
def load_data():
    try:
        SHEET_URL = "https://docs.google.com/spreadsheets/d/1D2fWEf08Oks6XFvz5KBgHHUjxJiM38Z0/export?format=csv"
        df_raw = pd.read_csv(SHEET_URL, header=None)
        
        header_row_index = 0
        for i, row in df_raw.iterrows():
            if 'Final Grade' in row.values:
                header_row_index = i
                break
        
        df_raw.columns = df_raw.iloc[header_row_index]
        df_clean = df_raw.iloc[header_row_index + 1:].reset_index(drop=True)
        df_clean.columns = df_clean.columns.str.strip()
        
        # Kolom yang diambil dari database
        SELECTED_COLUMNS = ['Building', 'SPV', 'Line', 'Name Opt', 'ID NO', 'Style', 'Process Part', 'Name Process (Bahasa)', 'Grade Process', 'Grade Countif', 'Grade Quality', 'Final Grade']
        df_final = df_clean[[c for c in SELECTED_COLUMNS if c in df_clean.columns]].copy()
        
        # --- PERBAIKAN URUTAN DATA MERGED CELLS ---
        # 1. Jalankan ffill terlebih dahulu agar data induk 'Building' terisi penuh ke bawah
        cols_to_fill = ['Building', 'SPV', 'Line', 'Name Opt', 'ID NO', 'Final Grade']
        df_final[cols_to_fill] = df_final[cols_to_fill].ffill()
        
        # 2. Hapus baris sisa yang benar-benar tidak ada operatornya
        df_final = df_final.dropna(subset=['Name Opt', 'ID NO'], how='all')
        
        # 3. Standardisasi string data teks
        df_final['ID NO'] = df_final['ID NO'].astype(str).str.strip()
        df_final['Name Opt'] = df_final['Name Opt'].astype(str).str.strip()
        if 'Building' in df_final.columns:
            df_final['Building'] = df_final['Building'].astype(str).str.strip()
        
        # 4. Filter akhir membersihkan nilai 'nan' sisa konversi
        df_final = df_final[df_final['ID NO'] != 'nan']
        if 'Building' in df_final.columns:
            df_final = df_final[df_final['Building'] != 'nan']
        
        return df_final
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

# ==========================================
# 3. PERSIAPAN LOGO
# ==========================================
logo_url = "https://drive.google.com/file/d/1oS09AXFGtqWtB7b_llMa4uWFjoK8qwzG/view?usp=sharing"
logo_data = get_base64_logo(logo_url)

# HEADER HTML
logo_html = f'<img src="data:image/png;base64,{logo_data}" class="header-logo">' if logo_data else ""
st.markdown(f'<div class="custom-header"><div class="title-text">Skill Matrix Dashboard</div>{logo_html}</div>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN LOGIC
# ==========================================
try:
    df_logic = load_data()
    
    if not df_logic.empty:
        # --- FILTER PANEL ---
        with st.expander("🔍 Filter Pencarian Cepat", expanded=True):
            f0, f1, f2, f3, f4 = st.columns(5)
            
            with f0:
                if 'Building' in df_logic.columns:
                    buildings_list = sorted([str(b) for b in df_logic['Building'].unique() if b != ''])
                    sel_building = st.selectbox("Building:", ["Semua"] + buildings_list)
                else:
                    sel_building = "Semua"
                    st.warning("Kolom 'Building' tidak ditemukan")
            
            with f1: s_name = st.text_input("Nama:")
            with f2: s_id = st.text_input("ID NO:")
            
            with f3:
                # Filter pilihan line dinamis mengikuti gedung
                if sel_building != "Semua":
                    df_line_filtered = df_logic[df_logic['Building'] == sel_building].copy()
                else:
                    df_line_filtered = df_logic.copy()
                    
                df_line_filtered['Line'] = pd.to_numeric(df_line_filtered['Line'], errors='coerce')
                lines_list = sorted(df_line_filtered['Line'].dropna().unique().astype(int))
                sel_line = st.selectbox("Line:", ["Semua"] + [str(l) for l in lines_list])
                
            with f4:
                # Filter pilihan SPV dinamis mengikuti gedung
                if sel_building != "Semua":
                    df_spv_filtered = df_logic[df_logic['Building'] == sel_building]
                else:
                    df_spv_filtered = df_logic
                spvs = sorted([str(s) for s in df_spv_filtered['SPV'].unique() if pd.notna(s)])
                sel_spv = st.selectbox("SPV:", ["Semua"] + spvs)

        # --- APPLY FILTERS ---
        mask = pd.Series([True] * len(df_logic))
        if sel_building != "Semua": mask &= df_logic['Building'] == sel_building
        if s_name: mask &= df_logic['Name Opt'].str.contains(s_name, case=False, na=False)
        if s_id: mask &= df_logic['ID NO'].str.contains(s_id, case=False, na=False)
        if sel_line != "Semua": mask &= df_logic['Line'].astype(str) == str(sel_line)
        if sel_spv != "Semua": mask &= df_logic['SPV'] == sel_spv
        
        df_filtered = df_logic[mask]
        
        # --- PERHITUNGAN TOTAL OPERATOR (UNIK BERDASARKAN ID NO) ---
        df_unique = df_filtered.drop_duplicates(subset=['ID NO'])
        total_op = len(df_unique)
        
        color_map = {'A':'#10b981','B':'#3b82f6','C':'#f59e0b','D':'#ef4444'}

        if not df_unique.empty:
            st.markdown('<div class="section-title">📊 Analisis Performa</div>', unsafe_allow_html=True)
            
            # ROW 1: PIE & METRICS
            col_left, col_right = st.columns([1.5, 1])
            with col_left:
                counts = df_unique['Final Grade'].value_counts().reset_index()
                counts.columns = ['Grade', 'Jumlah']
                counts['Label'] = counts.apply(lambda x: f"Grade {x['Grade']}<br>{x['Jumlah']} Org ({(x['Jumlah']/total_op*100):.1f}%)", axis=1)
                
                fig_pie = px.pie(counts, values='Jumlah', names='Grade', hole=0.5, color='Grade', color_discrete_map=color_map)
                fig_pie.update_traces(textinfo='text', text=counts['Label'], textposition='inside')
                fig_pie.update_layout(showlegend=False, height=450, margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_right:
                st.metric("Total Operator", f"{total_op} Orang")
                st.write("")
                m_col1, m_col2 = st.columns(2)
                for i, g in enumerate(['A', 'B', 'C', 'D']):
                    count = len(df_unique[df_unique['Final Grade'] == g])
                    with (m_col1 if i % 2 == 0 else m_col2):
                        st.metric(label=f"Grade {g}", value=f"{count} Org")

            # ROW 2: BAR CHART (DINAMIS & TERURUT)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Memastikan Line terbaca sebagai angka agar sorting-nya urut secara numerik
            df_bar_data = df_unique.copy()
            df_bar_data['Line'] = pd.to_numeric(df_bar_data['Line'], errors='coerce')
            df_bar_data = df_bar_data.dropna(subset=['Line'])
            
            # Proses pengelompokan (grouping) data untuk grafik batang
            line_data = df_bar_data.groupby(['Line', 'Final Grade']).size().reset_index(name='Count')
            line_total = df_bar_data.groupby('Line').size().reset_index(name='Total')
            line_data = line_data.merge(line_total, on='Line')
            
            # Mengurutkan berdasarkan nomor Line asli (1, 2, 3... dst)
            line_data = line_data.sort_values(by='Line')
            
            line_data['Percent'] = (line_data['Count'] / line_data['Total'] * 100).round(1)
            line_data['Line_Label'] = "Line " + line_data['Line'].astype(int).astype(str)
            line_data['Bar_Label'] = line_data.apply(lambda x: f"{x['Final Grade']}: {x['Percent']}%", axis=1)

            # Gambar Chart dengan batasan urutan kategori sumbu X sesuai urutan sorting 'Line_Label'
            fig_bar = px.bar(
                line_data, 
                x='Line_Label', 
                y='Count', 
                color='Final Grade', 
                color_discrete_map=color_map, 
                barmode='stack', 
                text='Bar_Label',
                category_orders={"Line_Label": line_data['Line_Label'].unique()}
            )
            fig_bar.update_traces(textposition='inside', textfont=dict(color='white'))
            fig_bar.update_layout(
                height=400, 
                showlegend=False, 
                xaxis={'title': None, 'tickfont': {'color': 'white'}}, 
                yaxis={'visible': False}, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # ROW 3: DETAIL DATA
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">📑 Detail Data ({len(df_filtered)} Baris)</div>', unsafe_allow_html=True)
            
            def apply_color_grade(val):
                colors = {'A': 'background-color: #dcfce7; color: #166534;', 
                          'B': 'background-color: #dbeafe; color: #1e40af;',
                          'C': 'background-color: #ffedd5; color: #9a3412;',
                          'D': 'background-color: #fee2e2; color: #991b1b;'}
                return colors.get(val, '')

            df_final_view = df_filtered.fillna("")
            styled_df = df_final_view.style.map(apply_color_grade, subset=['Final Grade'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("Data tidak ditemukan.")
except Exception as e:
    st.error(f"Terjadi Kesalahan: {e}")
