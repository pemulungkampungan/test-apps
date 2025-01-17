from datetime import date
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import time
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules, apriori
from sklearn.preprocessing import MinMaxScaler

def normalize_data(df):
    scaler = MinMaxScaler()
    df[['Tanggal', 'Bulan', 'Tahun']] = scaler.fit_transform(df[['Tanggal', 'Bulan', 'Tahun']])
    return df

def preprocess_data(df, tanggal, sep, dateformat):
    df = prep_date(df, tanggal, sep, dateformat)
    df = normalize_data(df)
    return df

def prep_date(df, tanggal, sep, dateformat):
    if dateformat == 'ddmmyy':
        df['Tanggal'] = df[tanggal].apply(lambda x: int(x.split(sep)[0]))
        df['Bulan'] = df[tanggal].apply(lambda x: int(x.split(sep)[1]))
        df['Tahun'] = df[tanggal].apply(lambda x: int(x.split(sep)[2]))
    elif dateformat == 'mmddyy':
        df['Tanggal'] = df[tanggal].apply(lambda x: int(x.split(sep)[1]))
        df['Bulan'] = df[tanggal].apply(lambda x: int(x.split(sep)[0]))
        df['Tahun'] = df[tanggal].apply(lambda x: int(x.split(sep)[2]))
    elif dateformat == 'yymmdd':
        df['Tanggal'] = df[tanggal].apply(lambda x: int(x.split(sep)[2]))
        df['Bulan'] = df[tanggal].apply(lambda x: int(x.split(sep)[1]))
        df['Tahun'] = df[tanggal].apply(lambda x: int(x.split(sep)[0]))
    return df

def dataset_settings(df, pembeli, tanggal, produk):
    c1, c2 = st.columns((2, 1))
    year_list = ['Semua']
    year_list = np.append(year_list, df['Tahun'].unique())
    by_year = c1.selectbox('Tahun ', (year_list))
    if by_year != 'Semua':
        df = df[df['Tahun'] == int(by_year)]
        by_month = c2.slider('Bulan', 1, 12, (1, 12))
        df = df[df['Bulan'].between(int(by_month[0]), int(by_month[1]), inclusive="both")]
    return df

def show_transaction_info(df, produk, pembeli):
    try:
        col1, col2 = st.columns(2)
        st.subheader(f'Informasi Transaksi:')
        total_produk = df[produk].nunique()
        total_transaksi = df[pembeli].nunique()
        total_barang_terjual = df[produk].sum()  # Menghitung jumlah total barang terjual
        total_frekuensi_produk = len(df)  # Menghitung frekuensi total dari semua produk
        col1.info(f'Produk terjual     : {total_produk}')
        col2.info(f'Total transaksi  : {total_transaksi}')
        col2.info(f'Frekuensi total produk terjual  : {total_frekuensi_produk}')  # Menampilkan frekuensi total produk terjual
        sort = col1.radio('Tentukan kategori produk', ('Terlaris', 'Kurang Laris'))
        jumlah = col2.slider('Tentukan jumlah produk', 0, total_produk, 10)
        if sort == 'Terlaris':
            most_sold = df[produk].value_counts().head(jumlah)
        else:
            most_sold = df[produk].value_counts().tail(jumlah)
            most_sold = most_sold.sort_values(ascending=True)
        if not most_sold.empty:
            c1, c2 = st.columns((2, 1))
            plt.figure(figsize=(8, 4)) 
            most_sold.plot(kind='bar')
            plt.title('Grafik Penjualan')
            c1.pyplot(plt)
            c2.write(most_sold)
        else:
            st.warning("Tidak ada data yang sesuai dengan kriteria yang dipilih.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menampilkan informasi transaksi: {str(e)}")
        
def data_summary(df, pembeli, tanggal, produk):
    st.header('Ringkasan Dataset')
    col1, col2 = st.columns(2)
    sep_option = col1.radio('Tentukan separator tanggal', options=[('-', 'Dash'), ('/', 'Slash')])
    sep = sep_option[0]
    dateformat = col2.radio('Tentukan format urutan tanggal', ('ddmmyy', 'mmddyy', 'yymmdd'))
    try:
        df = prep_date(df, tanggal, sep, dateformat)
    except ValueError:
        st.warning('Format tanggal tidak sesuai! Silakan cek kembali dan pastikan format yang benar.')
        st.stop()
    except IndexError:
        st.warning('Separator tanggal salah! Silakan cek kembali dan pastikan pemisah yang benar.')
        st.stop()
    st.write('Setelan Tampilan Dataset:')
    df = dataset_settings(df, pembeli, tanggal, produk)
    st.dataframe(df.sort_values(by=['Tahun', 'Bulan', 'Tanggal'], ascending=True))
    show_transaction_info(df, produk, pembeli)
    return df

def prep_frozenset(rules):
    temp = re.sub(r'frozenset\({', '', str(rules))
    temp = re.sub(r'}\)', '', temp)
    return temp

def MBA(df, pembeli, produk, min_support, min_confidence):
    st.header('Association Rule Mining Menggunakan Apriori')
    if st.button("Mulai Perhitungan Asosiasi"):
        start_time = time.time()
        transaction_list = [list(set(df[df[pembeli] == i][produk])) for i in df[pembeli].unique()]
        te = TransactionEncoder()
        te_ary = te.fit(transaction_list).transform(transaction_list)
        df2 = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df2, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=min_confidence)
        
        end_time = time.time()
        processing_time = end_time - start_time
        col1, col2 = st.columns(2)
        col1.subheader('Hasil Rules (Pola Pembelian Pelanggan)')
        st.write('Total rules yang dihasilkan:', len(rules))
        col1.write(f'Waktu yang dibutuhkan untuk memproses rule: {processing_time:.2f} detik')
        
        if len(rules) == 0:
            st.write("Tidak ada aturan yang dihasilkan.")
        else:
            # Tampilkan rincian rules dan informasi tambahan
            pass  # Tambahkan kode untuk menampilkan rules di sini

        return rules  # 
