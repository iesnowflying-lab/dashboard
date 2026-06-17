import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman Web utama
st.set_page_config(page_title="Skill Matrix Dashboard", layout="wide")

# 2. Menyuntikkan CSS untuk Background Gradasi Warna (Tanpa Gambar)
st.markdown(
    """
    <style>
    /* Mengubah background aplikasi menjadi gradasi biru */
    .stApp {
        background: linear-gradient(to bottom, #e0f2fe 0%, #7dbbf1 50%, #3182ce 100%);
        background-attachment: fixed; /* Agar background tidak ikut ter-scroll */
    }
    
    /* Memastikan teks judul dan opsi pilihan tetap tebal dan berwarna hitam */
    h1, label, .stRadio > div {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Menengahkan judul utama aplikasi */
    .stApp > header {
        text-align: center;
    }
    
    h1 {
        text-align: center !important;
        width: 100%;
        display: block;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Judul Aplikasi
st.title("Skill Matrix Dashboard")

# 4. Navigasi Pilihan Factory
sheet_name = st.radio("Factory", ["ISG", "IRG"], horizontal=True)

# 5. Mengambil Data dari Google Sheet
SHEET_ID = "1uehIu5hPO4gJkJJ7MruxD41gMUQOYzu6eD30W_4gNBE"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

try:
    df = pd.read_csv(url)
    
    # Membersihkan data
    df = df.dropna(subset=['Line'])
    df['Grade'] = df['Grade'].fillna('-')
    df[['A', 'B', 'C', 'D']] = df[['A', 'B', 'C', 'D']].fillna(0)
    
    # 6. Membangun Struktur HTML dan CSS secara utuh
    html_content = """
    <style>
        /* Background transparan agar gradasi dari Streamlit terlihat */
        body {
            background-color: transparent !important; 
            margin: 0;
            padding: 10px;
        }
        
        .grid-container {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            font-family: Arial, sans-serif;
        }
        
        .card {
            border: 2px solid black;
            display: flex;
            color: black;
            border-radius: 4px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        }

        .card-left {
            width: 35%;
            border-right: 2px solid black;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 5px;
            text-align: center;
        }

        .card-left .line-text {
            font-size: 22px; 
            font-weight: bold;
            line-height: 1.2;
        }

        .card-right {
            width: 65%;
            display: flex;
            flex-direction: column;
        }

        .row-val {
            display: flex;
            border-bottom: 2px solid black;
        }

        .row-val:last-child {
            border-bottom: none; 
        }

        .col-label {
            width: 30%;
            border-right: 2px solid black;
            padding: 5px;
            text-align: center;
            font-size: 16px; 
            font-weight: bold;
        }

        .col-value {
            width: 70%;
            padding: 5px;
            text-align: center;
            font-size: 16px; 
            font-weight: bold;
        }
        
        /* Pewarnaan Kotak */
        .bg-green { background-color: #00B050; }
        .bg-yellow { background-color: #FFFF00; }
        .bg-orange { background-color: #FFC000; }
        .bg-white { background-color: #FFFFFF; }
    </style>
    
    <div class="grid-container">
    """
    
    # 7. Memasukkan data ke dalam struktur HTML
    for _, row in df.iterrows():
        # Parsing data 
        line_num = str(int(row['Line']))
        grade_val = str(row['Grade']).strip().upper()
        
        val_a = int(row['A'])
        val_b = int(row['B'])
        val_c = int(row['C'])
        val_d = int(row['D'])
        
        # Logika Warna 
        bg_class = "bg-white"
        if grade_val == 'A':
            bg_class = "bg-green"
        elif grade_val == 'B':
            bg_class = "bg-yellow"
        elif grade_val == 'C':
            bg_class = "bg-orange"
            
        # Membuat HTML untuk satu kotak (card) tanpa teks Grade
        card_html = f"""
        <div class="card {bg_class}">
            <div class="card-left">
                <div class="line-text">LINE<br>{line_num}</div>
            </div>
            <div class="card-right">
                <div class="row-val">
                    <div class="col-label">A</div>
                    <div class="col-value">{val_a} Orang</div>
                </div>
                <div class="row-val">
                    <div class="col-label">B</div>
                    <div class="col-value">{val_b} Orang</div>
                </div>
                <div class="row-val">
                    <div class="col-label">C</div>
                    <div class="col-value">{val_c} Orang</div>
                </div>
                <div class="row-val">
                    <div class="col-label">D</div>
                    <div class="col-value">{val_d} Orang</div>
                </div>
            </div>
        </div>
        """
        html_content += card_html
        
    html_content += "</div>"
    
    # 8. Menampilkan ke Streamlit
    st.components.v1.html(html_content, height=2500, scrolling=True)

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")