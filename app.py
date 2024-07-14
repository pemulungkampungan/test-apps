import pandas as pd
import streamlit as st
from PIL import Image
from komputasi import data_summary, MBA

# Set layout halaman
st.set_page_config(layout="wide")

# Tampilkan navbar
st.markdown(
    """
    <style>
    .navbar {
        background-color: #333;
        overflow: hidden;
    }
    .navbar a {
        float: left;
        display: block;
        color: #f2f2f2;
        text-align: center;
        padding: 14px 20px;
        text-decoration: none;
        font-size: 17px;
    }
    .navbar a:hover {
        background-color: #ddd;
        color: black;
    }
    .navbar a.active {
        background-color: #04AA6D;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="navbar">
        <a class="active" href="#" onclick="showPage('Home')">Home</a>
    </div>
    <script>
    function showPage(page) {
        window.location.hash = page;
        window.location.reload();
    }
    </script>
    """,
    unsafe_allow_html=True
)

def show_page(page):
    if page == "Home":
        st.write("Selamat datang di Aplikasi Analisis Toko Tanaman Hias dengan Metode Apriori.")

        # Input untuk minimum support dan confidence
        min_support = st.number_input('Masukkan Minimum Support:', min_value=0.0, max_value=1.0, value=0.1, step=0.01)
        min_confidence = st.number_input('Masukkan Minimum Confidence:', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        
        # File uploader
        st.session_state.dataset_file = st.file_uploader("Pilih file CSV", type=['csv'])
        
        if st.button("Analisis Data"):
            # Pastikan dataset sudah diunggah
            if st.session_state.dataset_file is not None:
                try:
                    df = pd.read_csv(st.session_state.dataset_file)
                    if df.empty:
                        st.warning("Dataset kosong. Mohon unggah dataset yang valid.")
                    else:
                        pembeli, tanggal, produk = df.columns[0], df.columns[1], df.columns[2]
                        df = data_summary(df, pembeli, tanggal, produk)
                        MBA(df, pembeli, produk, min_support, min_confidence)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses dataset: {str(e)}")

# Mendapatkan halaman yang dipilih
page = st.session_state.get("page", "Home")
show_page(page)
