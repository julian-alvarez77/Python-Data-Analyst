import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as mtick
import seaborn as sns
import streamlit as st
import io
import urllib
from urllib.request import urlopen
from PIL import Image
from babel.numbers import format_currency
from func import DataAnalyzer, BrazilMapPlotter
from setuptools import distutils

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", 
                 "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("C:/Laragon/www/proyek_analisis_data/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv("C:/Laragon/www/proyek_analisis_data/geolocation.csv")
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    st.title("Raka Juliandra - AQUOS IDN")
    st.image("img/Frame23.png")
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
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

sum_order_items_df = function.create_sum_order_items_df()
state, most_common_state = function.create_bystate_df()

# Inisialisasi DataAnalyzer
function = DataAnalyzer(main_df)

# Hitung pendapatan tahunan menggunakan metode baru
annual_revenue_df = function.create_annual_revenue_df()

# Title
st.header("E-Commerce Dashboard :convenience_store:")

# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2, tab3 = st.tabs(["State", "Geolocation", "Revenue"])


with tab1:
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(geolocation['geolocation_lng'], geolocation['geolocation_lat'], alpha=0.3, s=0.3, c='maroon')
    ax.axis('off')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write('Sesuai dengan grafik yang sudah dibuat, ada lebih banyak pelanggan di bagian tenggara dan selatan. Informasi lainnya, ada lebih banyak pelanggan di kota-kota yang merupakan ibu kota (São Paulo, Rio de Janeiro, Porto Alegre, dan lainnya).')

with tab2:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"State dengan jumlah Customer Paling banyak: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )

    plt.title("Jumlah Customers berdasarkan State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Jumlah Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write(
                    """
                    Dapat diketahui bahwa 3 State yang memiliki Pengguna terbanyak adalah:
                    1. Sao Paulo dengan jumlah user sebanyak 40267 MG         
                    2. Rio de Janeiro dengan jumlah user sebanyak 12353 
                    3. Minas Gerais dengan jumlah user sebanyak 11248.
                    """
                )

with tab3:
    # Ambil data revenue per state dari fungsi baru di func.py
    revenue_2018_by_state_df = function.create_revenue_2018_by_state()

    # Buat visualisasi bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # Menambahkan kolom revenue dalam juta (millions)
    revenue_2018_by_state_df['Total Revenue (M)'] = revenue_2018_by_state_df['Total Revenue'] / 1_000_000

    bars = ax.bar(revenue_2018_by_state_df['State'], 
                  revenue_2018_by_state_df['Total Revenue (M)'], 
                  color='skyblue')

    # Format sumbu Y dalam format "R$Xm"
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'R${x:.1f}M'))

    # Judul, label, dan rotasi
    ax.set_title("Total Revenue berdasarkan State di 2018", fontsize=15)
    ax.set_xlabel("State", fontsize=12)
    ax.set_ylabel("Total Revenue (dalam jutaan)", fontsize=12)
    ax.tick_params(axis='x', rotation=45, labelsize=10)

    # Menyesuaikan layout
    plt.tight_layout()

    # Tampilkan plot di streamlit
    st.pyplot(fig)
    
    with st.expander("See Explanation"):
        st.write(
                    """
                    Dapat diketahui bahwa 3 State yang memiliki Revenue terbesar adalah:
                    1. Sao Paulo dengan jumlah revenue sebanyak R$3M 
                    2. Rio de Janeiro dengan jumlah revenue sebanyak R$937K 
                    3. Minas Gerais dengan jumlah revenue sebanyak R$877K.
                    """
                )

# ---------------------------------------------------------------------------------------------

# Total Revenue per Years
st.subheader("Total Revenue per Year")
st.markdown(f"Total Revenue 2016: **R$50,415**")
st.markdown(f"Total Revenue 2017: **R$6,447,800**")
st.markdown(f"Total Revenue 2018: **R$7,637,140**")

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(annual_revenue_df['year'], annual_revenue_df['revenue'], color='skyblue')

# Tambahkan keterangan angka di atas setiap batang dengan format BRL
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,  # Posisi x di tengah batang
        height,                             # Posisi y di atas batang
        f'R${height:,.2f}',                 # Format angka dengan simbol BRL
        ha='center',                        # Horizontal alignment
        va='bottom',                        # Vertical alignment
        fontsize=10                         # Ukuran font
    )

# Menyesuaikan sumbu X agar hanya menampilkan tahun tanpa nilai desimal
ax.set_xticks(annual_revenue_df['year'].astype(int))  # Pastikan sumbu X hanya menampilkan integer penuh

# Atur estetika grafik
ax.set_title("Pendapatan Per Tahun (Brazil Real)", fontsize=16)
ax.set_xlabel("Tahun", fontsize=12)
ax.set_ylabel("Pendapatan (Revenue)", fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Tampilkan grafik
st.pyplot(fig)

# Detail Pendapatan di Tahun 2018
# Buat DataFrame revenue per bulan di tahun 2018
monthly_revenue_2018 = function.create_monthly_revenue_2018()

# Visualisasi Pendapatan per Bulan 2018
st.subheader("Detail Pendapatan di 2018 (Tahun Terakhir)")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_revenue_2018['month'], monthly_revenue_2018['revenue'], marker='o', color='skyblue', linestyle='-', linewidth=2)
ax.set_title("Pendapatan Per Bulan di Tahun 2018", fontsize=16)
ax.set_xlabel("Bulan", fontsize=12)
ax.set_ylabel("Pendapatan (in Millions)", fontsize=12)
plt.xticks(rotation=45)  # Rotasi nama bulan agar lebih mudah dibaca
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Tambahkan nilai pendapatan di atas titik-titik grafik
for i, value in enumerate(monthly_revenue_2018['revenue']):
    ax.text(i, value, f'R${value:,.2f}', ha='center', va='bottom', fontsize=10)

# Tampilkan grafik
st.pyplot(fig)

with st.expander("See Explanation"):
    st.write("Dapat diketahui untuk Jumlah Transaksi Sementara pada Tahun 2018 ini adalah Penjualan paling banyak terdapat pada bulan May yaitu : Sebesar R$1,046,939")

# ------------------------------------------------------------------------------------------------

# Jumlah Metode pembayaran yang digunakan
# Dapatkan DataFrame yang berisi jumlah transaksi berdasarkan jenis pembayaran
payment_type_df = function.create_payment_type_df()

# Visualisasi Metode Pembayaran
st.subheader("Jumlah Metode Pembayaran yang Digunakan")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="transaction_count", y="payment_type", data=payment_type_df, palette="viridis", ax=ax)

# Menambahkan angka pada setiap bar
for index, value in enumerate(payment_type_df["transaction_count"]):
    ax.text(value + 500, index, str(value), va='center', fontsize=10, color='black')

plt.title("Jumlah Transaksi Berdasarkan Metode Pembayaran", fontsize=14)
plt.xlabel("Jumlah Transaksi", fontsize=12)
plt.ylabel("Metode Pembayaran", fontsize=12)
plt.tight_layout()

# Menampilkan plot
st.pyplot(fig)

# Dengan penjelasan di bawah ini, jika diinginkan
with st.expander("See Explanation"):
    st.write(
        """
        Dapat diketahui 
        - sebanyak 76.505 pengguna yang menggunakan Credit Card untuk Pembayaran
        - sebanyak 25.181 pengguna tidak menggunakan Credit Card untuk Pembayaran
        """
    )

# -----------------------------------------------------------------------------------------------

# Top 15 Produk Paling Laris
# Fetch Top 15 Selling Products
top_15_products_df = function.create_top_15_products_df()

# Display top 15 products using a bar plot
st.subheader("Top 15 Selling Products")
fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(x="product_count", y="product_category_name_english", data=top_15_products_df, palette="viridis", ax=ax)
ax.set_xlabel("Sales Count", fontsize=12)
ax.set_ylabel("Product Categories", fontsize=12)
ax.set_title("Top 15 Penjualan Produk", fontsize=16)

# Show Plot in Streamlit
st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

with st.expander("See Explanation"):
    st.write("Dapat diketahui bahwa Kategori produk yang paling banyak Terjual adalah bed_bath_table dengan jumlah terjual yaitu : 13542")
# -----------------------------------------------------------------------------------------------

st.caption('Copyright (C) Raka Juliandra 2025')
