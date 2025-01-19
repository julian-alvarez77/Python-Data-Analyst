import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import io
from babel.numbers import format_currency
import matplotlib.image as mpimg
from PIL import Image
from urllib.request import urlopen

sns.set(style='dark')

# Baca gambar dari URL menggunakan Pillow
url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
try:
    response = urlopen(url)
    img_data = response.read()
    brazil = Image.open(io.BytesIO(img_data))
    brazil = brazil.convert("RGBA")  # Konversi ke format yang kompatibel jika perlu
except Exception as e:
    print(f"Kesalahan saat membaca gambar: {e}")
    brazil = None

# Menampilkan gambar (jika berhasil)
if brazil:
    plt.imshow(brazil)
    plt.axis('off')
    plt.show()


# Load cleaned data
all_df = pd.read_csv("all_data.csv")

# Geolocation Dataset
geolocation = pd.read_csv("C:/Laragon/www/proyek_analisis_data/geolocation.csv")

datetime_columns = ["order_date", "delivery_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_date"] >= str(start_date)) & 
                 (all_df["order_date"] <= str(end_date))]

# --- Sebaran Pengguna ---
st.header('E-Commerce Dataset - Dashboard :sparkles:')
st.subheader('1. Sebaran Pengguna di Seluruh Brazil')

fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(geolocation['geolocation_lng'], geolocation['geolocation_lat'], alpha=0.3, s=0.3, c='maroon')
ax.axis('off')
ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
st.pyplot(fig)

# --- Performa Penjualan ---
st.subheader('2. Performa Penjualan dan Revenue')

daily_orders_df = main_df.resample('D', on='order_date').agg({
    "order_id": "nunique",
    "total_price": "sum"
}).reset_index()

daily_orders_df.rename(columns={"order_id": "order_count", "total_price": "revenue"}, inplace=True)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_date"], daily_orders_df["order_count"], marker='o', color="#90CAF9")
ax.set_title("Performa Penjualan Harian", fontsize=20)
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Pesanan")
st.pyplot(fig)

revenue_last_year = daily_orders_df[daily_orders_df['order_date'].dt.year == daily_orders_df['order_date'].dt.year.max()]
fig, ax = plt.subplots(figsize=(16, 8))
ax.bar(revenue_last_year['order_date'], revenue_last_year['revenue'], color="#FFA726")
ax.set_title("Revenue Per Bulan di Tahun Terakhir", fontsize=20)
ax.set_xlabel("Bulan")
ax.set_ylabel("Revenue")
st.pyplot(fig)

# --- Pengguna Kartu Kredit ---
st.subheader('3. Pengguna Kartu Kredit')
credit_card_users = main_df[main_df['payment_type'] == 'credit_card']['customer_id'].nunique()
st.metric("Jumlah Pengguna Kartu Kredit", credit_card_users)

# --- Produk yang Paling Sering Terjual ---
st.subheader('4. Produk Paling Sering Terjual')

top_products = main_df.groupby('product_name').quantity_x.sum().sort_values(ascending=False).reset_index().head(5)
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=top_products, x='quantity_x', y='product_name', palette='viridis', ax=ax)
ax.set_title("Top Produk Terlaris", fontsize=20)
ax.set_xlabel("Jumlah Terjual")
ax.set_ylabel("Nama Produk")
st.pyplot(fig)



def process_data(self):
    """
    Memproses data untuk menambahkan kolom tahun dan menghitung pendapatan tahunan.

    Args:
        all_df (pd.DataFrame): Dataframe input dengan kolom 'order_approved_at' dan 'price'.

    Returns:
        pd.DataFrame: Dataframe dengan pendapatan per tahun.
    """
    # Pastikan kolom 'order_approved_at' berbentuk datetime
    self['order_approved_at'] = pd.to_datetime(self['order_approved_at'])

    # Tambahkan kolom tahun dari 'order_approved_at'
    self['year'] = self['order_approved_at'].dt.year

    # Hitung pendapatan per tahun
    annual_revenue_df = self.groupby('year').agg({"price": "sum"}).reset_index()

    # Ganti nama kolom agar lebih deskriptif
    annual_revenue_df.rename(columns={"price": "revenue"}, inplace=True)

    return annual_revenue_df

def visualize_revenue(annual_revenue_df):
    """
    Membuat visualisasi pendapatan tahunan menggunakan matplotlib.

    Args:
        annual_revenue_df (pd.DataFrame): Dataframe dengan kolom 'year' dan 'revenue'.
    """
    # Visualisasi menggunakan Matplotlib
    plt.figure(figsize=(10, 6))
    bars = plt.bar(annual_revenue_df['year'], annual_revenue_df['revenue'], color='skyblue')

    # Tambahkan keterangan angka di atas setiap batang dengan format BRL
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Posisi x di tengah batang
            height,                             # Posisi y di atas batang
            f'R${height:,.2f}',                 # Format angka dengan simbol BRL
            ha='center',                        # Horizontal alignment
            va='bottom',                        # Vertical alignment
            fontsize=10                         # Ukuran font
        )

    # Atur estetika grafik
    plt.title("Pendapatan Per Tahun (Brazil Real)", fontsize=16)
    plt.xlabel("Tahun", fontsize=12)
    plt.ylabel("Pendapatan (Revenue)", fontsize=12)
    plt.xticks(annual_revenue_df['year'], rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Tampilkan grafik
    plt.show()