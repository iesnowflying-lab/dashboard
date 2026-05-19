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

# CSS UNTUK BACKGROUND ABU-ABU MUDA & HAPUS SIDEBAR
st.markdown("""
    <style>
    /* 1. Menghilangkan Sidebar & Navigasi secara permanen */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* 2. Menghilangkan Header Default Streamlit */
    header {
        visibility: hidden;
        height: 0px;
    }

    /* Background Gradient Fixed */
    .stApp {
        background: linear-gradient(to bottom, #FFFFFF 0%, #B0E0E6 12%, #4682B4 80%, #1E3A5F 100%);
        background-attachment: fixed;
    }

    /* 4. Penyesuaian margin konten */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    /* 5. Style Header Dashboard */
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

    /* 6. Metric Styling (Dibuat putih agar kontras dengan background abu-abu) */
    [data-testid="stMetric"] {
        background-color: #e2e8f0;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Styling Expander agar putih */
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
        # Link CSV dari Google Sheets Anda
        SHEET_URL = "https://docs.google.com/spreadsheets/d/1D2fWEf08Oks6XFvz5KBgHHUjxJiM38Z0/export?format=csv"
        
        # Baca semua data tanpa header terlebih dahulu
        df_raw = pd.read_csv(SHEET_URL, header=None)
        
        # Cari di baris mana kata 'Final Grade' berada untuk menentukan header
        header_row_index = 0
        for i, row in df_raw.iterrows():
            if 'Final Grade' in row.values:
                header_row_index = i
                break
        
        # Tetapkan baris tersebut sebagai header dan ambil data di bawahnya
        df_raw.columns = df_raw.iloc[header_row_index]
        df_clean = df_raw.iloc[header_row_index + 1:].reset_index(drop=True)
        
        # Bersihkan spasi di nama kolom
        df_clean.columns = df_clean.columns.str.strip()
        
        SELECTED_COLUMNS = ['SPV', 'Line', 'Name Opt', 'ID NO', 'Style', 'Process Part', 'Name Process (Bahasa)', 'Grade Process', 'Grade Countif', 'Grade Quality', 'Final Grade']
        
        # Filter hanya kolom yang ada
        df_final = df_clean[[c for c in SELECTED_COLUMNS if c in df_clean.columns]].copy()
        
        # Hapus baris yang kosong pada kolom kunci
        df_final = df_final.dropna(subset=['Name Opt'], how='all').reset_index(drop=True)
        
        return df_final
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

# ==========================================
# 3. PERSIAPAN VARIABEL LOGO
# ==========================================
logo_url = "https://drive.google.com/file/d/1oS09AXFGtqWtB7b_llMa4uWFjoK8qwzG/view?usp=sharing"
logo_data = get_base64_logo(logo_url)

# ==========================================
# 4. INJECT HEADER
# ==========================================
logo_html = f'<img src="data:image/png;base64,{logo_data}" class="header-logo">' if logo_data else ""
st.markdown(f'''
    <div class="custom-header">
        <div class="title-text">Skill Matrix Dashboard</div>
        {logo_html}
    </div>
    ''', unsafe_allow_html=True)

# ==========================================
# 5. LOGIC DASHBOARD
# ==========================================
try:
    df_display = load_data()
    if not df_display.empty:
        # --- FILTER ---
        with st.expander("🔍 Filter Pencarian Cepat", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1: s_name = st.text_input("Nama:")
            with f2: s_id = st.text_input("ID NO:")
            with f3:
                df_display['Line'] = pd.to_numeric(df_display['Line'].ffill(), errors='coerce')
                lines_list = sorted(df_display['Line'].dropna().unique().astype(int))
                sel_line = st.selectbox("Line:", ["Semua"] + [str(l) for l in lines_list])
            with f4:
                spvs = df_display['SPV'].ffill().unique()
                sel_spv = st.selectbox("SPV:", ["Semua"] + sorted([str(s) for s in spvs if pd.notna(s)]))

        # --- LOGIC FILTERING ---
        df_logic = df_display.copy()
        df_logic[['SPV', 'Line', 'Name Opt', 'ID NO', 'Final Grade']] = df_logic[['SPV', 'Line', 'Name Opt', 'ID NO', 'Final Grade']].ffill()
        
        mask = pd.Series([True] * len(df_logic))
        if s_name: mask &= df_logic['Name Opt'].str.contains(s_name, case=False, na=False)
        if s_id: mask &= df_logic['ID NO'].astype(str).str.contains(s_id, case=False, na=False)
        if sel_line != "Semua": mask &= df_logic['Line'].astype(str) == str(sel_line)
        if sel_spv != "Semua": mask &= df_logic['SPV'] == sel_spv
        
        df_filt_calc = df_logic[mask.values]
        df_unique = df_filt_calc.drop_duplicates(subset=['ID NO'])
        color_map = {'A':'#10b981','B':'#3b82f6','C':'#f59e0b','D':'#ef4444'}

        if not df_unique.empty:
            st.markdown('<div class="section-title">📊 Analisis Performa</div>', unsafe_allow_html=True)
            
            # --- ROW 1: PIE & METRICS ---
            col_left, col_right = st.columns([1.5, 1])
            with col_left:
                counts = df_unique['Final Grade'].value_counts().reset_index()
                counts.columns = ['Grade', 'Jumlah']
                total_op_pie = counts['Jumlah'].sum()
                counts['Custom_Label'] = counts.apply(lambda x: f"Grade {x['Grade']} / {x['Jumlah']} / {(x['Jumlah']/total_op_pie*100):.1f}%", axis=1)
                fig_pie = px.pie(counts, values='Jumlah', names='Grade', hole=0.5, color='Grade', color_discrete_map=color_map)
                fig_pie.update_traces(textinfo='text', text=counts['Custom_Label'])
                fig_pie.update_layout(showlegend=False, height=450, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_right:
                st.metric("Total Operator", f"{len(df_unique)} Orang")
                st.write("")
                m_col1, m_col2 = st.columns(2)
                for i, g in enumerate(['A', 'B', 'C', 'D']):
                    count = df_unique[df_unique['Final Grade'] == g].shape[0]
                    with (m_col1 if i % 2 == 0 else m_col2):
                        st.metric(label=f"Grade {g}", value=f"{count} Org")

            # --- ROW 2: BAR CHART ---
            st.markdown("<br>", unsafe_allow_html=True)
            line_data = df_unique.groupby(['Line', 'Final Grade']).size().reset_index(name='Count')
            line_total = df_unique.groupby('Line').size().reset_index(name='Total')
            line_data = line_data.merge(line_total, on='Line')
            line_data['Percent'] = (line_data['Count'] / line_data['Total'] * 100).round(1)
            line_data['Line_Label'] = "Line " + line_data['Line'].astype(int).astype(str)
            line_data['Bar_Label'] = line_data.apply(lambda x: f"{x['Final Grade']}: {x['Percent']}%", axis=1)

            fig_bar = px.bar(line_data, x='Line_Label', y='Count', color='Final Grade', color_discrete_map=color_map, barmode='stack', text='Bar_Label')
            fig_bar.update_layout(height=400, showlegend=False, xaxis={'title': None, 'showticklabels': True, 'showgrid': False,'tickfont': {'color': 'white', 'size': 12}}, yaxis={'visible': False}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- ROW 3: DETAIL DATA ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">📑 Detail Data ({len(df_filt_calc)} Baris)</div>', unsafe_allow_html=True)
            
            def apply_color_grade(val):
                if val == 'A': return 'background-color: #dcfce7; color: #166534;'
                if val == 'B': return 'background-color: #dbeafe; color: #1e40af;'
                if val == 'C': return 'background-color: #ffedd5; color: #9a3412;'
                if val == 'D': return 'background-color: #fee2e2; color: #991b1b;'
                return ''

            df_final_view = df_filt_calc.fillna("")
            styled_df = df_final_view.style.map(apply_color_grade, subset=['Final Grade'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
    else:
        st.info("Data tidak ditemukan.")
        
except Exception as e:
    st.error(f"Terjadi Kesalahan: {e}")

