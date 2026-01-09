import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Konfigurasi Halaman (WAJIB PALING ATAS)
st.set_page_config(page_title="Daily Absen Sewing 2026", layout="wide")

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
                 
                </style>
    """, unsafe_allow_html=True)

# 3. Fitur Auto-Refresh
st_autorefresh(interval=300000, key="datarefresh")

# --- HEADER & TOMBOL KEMBALI ---
col_judul, col_back = st.columns([4, 1])
with col_judul:
    st.title("📊 Daily Absen Sewing 2026")
st.info("Dashboard ini akan memperbarui data secara otomatis setiap 5 menit.")

def load_data():
    url = "https://docs.google.com/spreadsheets/d/1NNVyaEJfiEKLNwoOsusYcGF4q_nQonBu/export?format=xlsx"
    
    try:
        # Kita baca tanpa header dulu untuk cek baris mana yang sebenarnya berisi judul
        df_raw = pd.read_excel(url, sheet_name='Daily Absen Sewing_2026')
        
        # Bersihkan spasi di nama kolom
        df_raw.columns = df_raw.columns.astype(str).str.strip()

        # --- VALIDASI KOLOM (SANGAT PENTING) ---
        # Cek apakah 'Tgl' ada, jika tidak, coba cari 'Tanggal'
        col_tgl = 'Tgl' if 'Tgl' in df_raw.columns else ('Tanggal' if 'Tanggal' in df_raw.columns else None)
        col_line = 'Line' if 'Line' in df_raw.columns else None
        
        if col_tgl is None or col_line is None:
            st.error(f"Kolom 'Tgl' atau 'Line' tidak ditemukan. Kolom yang ada: {list(df_raw.columns)}")
            return None

        # --- PROSES DATA ---
        df = df_raw.copy()
        
        # Filter Buyer agar baris kosong/libur hilang
        if 'Buyer' in df.columns:
            df = df.dropna(subset=['Buyer'])
            df = df[df['Buyer'].astype(str).str.strip() != ""]

        # Pastikan angka bersih
        cols_to_numeric = ['Sakit', 'Ijin', 'Tanpa Keterangan', 'Total Direct', 'Resign']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        df['Total tidak hadir'] = df['Sakit'] + df['Ijin'] + df['Tanpa Keterangan']
        
        # Format Tanggal
        df[col_tgl] = pd.to_datetime(df[col_tgl], errors='coerce').dt.strftime('%d-%m-%Y')

        # Ambil kolom yang dibutuhkan saja (Gunakan variabel col_tgl dan col_line)
        df_display = df[[col_tgl, col_line, 'Total Direct', 'Total tidak hadir', 'Resign']].copy()
        df_display.columns = ['Tanggal', 'Line', 'Total Direct', 'Total tidak hadir', 'Total Resign']

        return df_display

    except Exception as e:
        st.error(f"Detail Error: {e}")
        return None

# --- TAMPILAN TABEL ---
data = load_data()

if data is not None and not data.empty:
    # Kalkulasi Grand Total
    total_direct = data['Total Direct'].sum()
    total_absen = data['Total tidak hadir'].sum()
    total_resign = data['Total Resign'].sum()

    # Baris Total
    total_row = pd.DataFrame({
        'Tanggal': ['GRAND TOTAL'], 'Line': [''],
        'Total Direct': [total_direct],
        'Total tidak hadir': [total_absen],
        'Total Resign': [total_resign]
    })

    df_final = pd.concat([data, total_row], ignore_index=True)
    st.dataframe(df_final, use_container_width=True, hide_index=True)
    
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Grand Total Direct", f"{int(total_direct)} Org")
    c2.metric("Total Tidak Hadir", f"{int(total_absen)} Org")
    c3.metric("Total Resign", f"{int(total_resign)} Org")