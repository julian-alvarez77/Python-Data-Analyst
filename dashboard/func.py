import pandas as pd
import matplotlib.pyplot as plt

class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state

    def create_revenue_2018_by_state(self):
    # Periksa apakah kolom sudah berupa datetime, jika belum konversi
        if not pd.api.types.is_datetime64_any_dtype(self.df["order_purchase_timestamp"]):
            self.df["order_purchase_timestamp"] = pd.to_datetime(self.df["order_purchase_timestamp"])

        # Filter data untuk tahun 2018
        data_2018 = self.df[self.df["order_purchase_timestamp"].dt.year == 2018]

        # Hitung revenue berdasarkan state
        revenue_2018_by_state = data_2018.groupby("customer_state")["price"].sum().sort_values(ascending=False)

        # Ubah hasil ke DataFrame untuk visualisasi
        revenue_2018_by_state_df = revenue_2018_by_state.reset_index()
        revenue_2018_by_state_df.columns = ["State", "Total Revenue"]

        return revenue_2018_by_state_df
    
    def create_annual_revenue_df(self):
        # Pastikan kolom 'order_approved_at' berbentuk datetime jika belum
        if not pd.api.types.is_datetime64_any_dtype(self.df["order_approved_at"]):
            self.df["order_approved_at"] = pd.to_datetime(self.df["order_approved_at"])

        # Tambahkan kolom tahun dari 'order_approved_at'
        self.df['year'] = self.df['order_approved_at'].dt.year
        
        # Pastikan hanya menggunakan tahun penuh (tanpa angka desimal)
        self.df['year'] = self.df['year'].astype(int)

        # Filter hanya tahun yang sesuai (2016, 2017, dan 2018)
        valid_years = [2016, 2017, 2018]
        self.df = self.df[self.df['year'].isin(valid_years)]

        # Hitung pendapatan per tahun
        annual_revenue_df = self.df.groupby('year').agg({"price": "sum"}).reset_index()

        # Ganti nama kolom agar lebih deskriptif
        annual_revenue_df.rename(columns={"price": "revenue"}, inplace=True)

        return annual_revenue_df 
    
    def create_monthly_revenue_2018(self):
        # Filter data untuk tahun 2018
        data_2018 = self.df[self.df['order_approved_at'].dt.year == 2018]

        # Hitung revenue per bulan
        monthly_revenue_2018 = data_2018.resample('M', on='order_approved_at').agg({
            "price": "sum"
        }).reset_index()

        # Tambahkan nama bulan
        monthly_revenue_2018['month'] = monthly_revenue_2018['order_approved_at'].dt.strftime('%B')

        # Ganti nama kolom untuk memperjelas
        monthly_revenue_2018.rename(columns={"price": "revenue"}, inplace=True)

        return monthly_revenue_2018
    
    def create_payment_type_df(self):
        # Menghitung jumlah unik order berdasarkan jenis pembayaran
        payment_type_df = self.df.groupby("payment_type")["order_id"].nunique().sort_values(ascending=False).reset_index()
        payment_type_df.rename(columns={"order_id": "transaction_count"}, inplace=True)

        return payment_type_df
    
    def create_top_15_products_df(self):
        # Count product sales based on the 'product_category_name_english'
        top_products_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        top_products_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)

        # Sort the product categories by count, descending
        top_products_df = top_products_df.sort_values(by='product_count', ascending=False).head(15)

        return top_products_df
    
class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='maroon')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8,-33.75116944,5.4])
        self.st.pyplot()