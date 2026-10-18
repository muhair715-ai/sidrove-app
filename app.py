import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sidrove - Servis Darurat & BI", page_icon="🚗", layout="wide")

FILE_PATH = "data_sidrove.xlsx"

# --- FUNGSI BACA & SIMPAN DATA ---
def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH, sheet_name="Lembar1")
        return df
    else:
        return pd.DataFrame(columns=['ID_Order', 'Tanggal', 'Jam', 'Kecamatan', 'Kendaraan', 'Kerusakan', 'Biaya', 'Status'])

def save_data(df):
    with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Lembar1", index=False)

# --- FUNGSI GENERATE DATA DUMMY UNTUK BI ---
def generate_dummy_data(n=500):
    kecamatan_list = ["Sukolilo", "Gubeng", "Wonokromo", "Rungkut", "Tegalsari", "Sawahan"]
    # Memberi bobot agar kecamatan tertentu terlihat lebih rawan mogok di grafik BI
    kecamatan_weights = [0.30, 0.25, 0.15, 0.12, 0.10, 0.08]
    
    kendaraan_list = ["Motor", "Mobil"]
    kerusakan_motor = ["Ban Bocor", "Mesin Mati", "Aki Soak", "Putus Rantai/V-Belt", "Kehabisan Bensin"]
    kerusakan_mobil = ["Aki Soak", "Ban Bocor", "Mesin Overheat", "Mesin Mati", "Kunci Tertinggal"]
    
    biaya_map = {
        "Ban Bocor": (25000, 75000),
        "Mesin Mati": (75000, 250000),
        "Aki Soak": (50000, 150000),
        "Putus Rantai/V-Belt": (50000, 120000),
        "Kehabisan Bensin": (20000, 50000),
        "Mesin Overheat": (100000, 300000),
        "Kunci Tertinggal": (75000, 200000)
    }

    data = []
    start_date = datetime.now() - timedelta(days=180) # Data 6 bulan terakhir

    for i in range(1, n + 1):
        id_order = f"ORD-{1000 + i}"
        random_days = random.randint(0, 180)
        tanggal = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        # Jam dibuat lebih sering terjadi di jam berangkat/pulang kerja & malam
        jam_pilihan = random.choices(
            population=list(range(0, 24)),
            weights=[2,1,1,1,1,2, 6,9,8,5,4,4, 4,4,5,6,9,10, 8,7,6,5,4,3],
            k=1
        )[0]
        jam = f"{jam_pilihan:02d}:{random.randint(0,59):02d}"
        
        kecamatan = random.choices(kecamatan_list, weights=kecamatan_weights, k=1)[0]
        kendaraan = random.choices(kendaraan_list, weights=[0.65, 0.35], k=1)[0]
        
        if kendaraan == "Motor":
            kerusakan = random.choices(kerusakan_motor, weights=[0.45, 0.20, 0.15, 0.10, 0.10], k=1)[0]
        else:
            kerusakan = random.choices(kerusakan_mobil, weights=[0.35, 0.25, 0.20, 0.15, 0.05], k=1)[0]
            
        min_b, max_b = biaya_map[kerusakan]
        # Biaya mobil sedikit lebih mahal
        multiplier = 1.5 if kendaraan == "Mobil" else 1.0
        biaya = int(random.randint(min_b, max_b) * multiplier // 5000 * 5000)
        
        status = random.choices(["Selesai", "Menunggu Montir"], weights=[0.96, 0.04], k=1)[0]
        if status == "Menunggu Montir":
            biaya = 0
            
        data.append([id_order, tanggal, jam, kecamatan, kendaraan, kerusakan, biaya, status])

    df_dummy = pd.DataFrame(data, columns=['ID_Order', 'Tanggal', 'Jam', 'Kecamatan', 'Kendaraan', 'Kerusakan', 'Biaya', 'Status'])
    save_data(df_dummy)
    return df_dummy

# Muat data saat ini
df = load_data()

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🚗 Navigasi Sidrove")
menu = st.sidebar.radio(
    "Pilih Peran / Halaman:",
    ["📱 1. Aplikasi Driver (Order)", "🔧 2. Aplikasi Montir (Mitra)", "📊 3. Dashboard BI (Admin)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Panel Simulasi Data")
st.sidebar.caption("Gunakan tombol ini jika file Excel masih kosong agar grafik BI langsung terisi otomatis.")
if st.sidebar.button("✨ Generate 500 Data Dummy"):
    df = generate_dummy_data(500)
    st.sidebar.success("Berhasil mengisi 500 baris data ke data_sidrove.xlsx!")
    st.rerun()

# ==========================================================
# HALAMAN 1: SISI DRIVER (PEMESANAN DARURAT)
# ==========================================================
if menu == "📱 1. Aplikasi Driver (Order)":
    st.title("📱 Sidrove - Panggil Montir Darurat")
    st.write("Kendaraan mogok di jalan? Isi form di bawah ini untuk memanggil montir terdekat ke lokasimu.")
    
    with st.form("form_order"):
        col1, col2 = st.columns(2)
        with col1:
            kendaraan = st.selectbox("Jenis Kendaraan", ["Motor", "Mobil"])
            kecamatan = st.selectbox("Lokasi Kecamatan Saat Ini", ["Sukolilo", "Gubeng", "Wonokromo", "Rungkut", "Tegalsari", "Sawahan"])
        with col2:
            kerusakan = st.selectbox("Keluhan / Jenis Kerusakan", [
                "Ban Bocor", "Mesin Mati", "Aki Soak", "Putus Rantai/V-Belt", 
                "Kehabisan Bensin", "Mesin Overheat", "Kunci Tertinggal"
            ])
            catatan = st.text_input("Patokan Lokasi (Opsional)", placeholder="Contoh: Depan Indomaret Jl. Raya...")
            
        submit = st.form_submit_button("🚨 Panggil Montir Sekarang!")
        
        if submit:
            new_id = f"ORD-{1001 + len(df)}"
            now = datetime.now()
            tgl_skrg = now.strftime("%Y-%m-%d")
            jam_skrg = now.strftime("%H:%M")
            
            new_row = pd.DataFrame([[new_id, tgl_skrg, jam_skrg, kecamatan, kendaraan, kerusakan, 0, "Menunggu Montir"]], 
                                   columns=['ID_Order', 'Tanggal', 'Jam', 'Kecamatan', 'Kendaraan', 'Kerusakan', 'Biaya', 'Status'])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"Pesanan Darurat berhasil dibuat dengan ID: **{new_id}**! Montir sedang menuju lokasimu di Kecamatan **{kecamatan}**.")

    st.markdown("---")
    st.subheader("📋 Status Pesanan Terbaru")
    if not df.empty:
        st.dataframe(df.tail(5).iloc[::-1], use_container_width=True)
    else:
        st.info("Belum ada data pesanan.")

# ==========================================================
# HALAMAN 2: SISI MONTIR (PENYELESAIAN ORDER)
# ==========================================================
elif menu == "🔧 2. Aplikasi Montir (Mitra)":
    st.title("🔧 Sidrove Mitra - Daftar Panggilan Darurat")
    
    df_menunggu = df[df['Status'] == "Menunggu Montir"]
    
    if df_menunggu.empty:
        st.success("🎉 Tidak ada antrean panggilan darurat saat ini. Semua kendaraan sudah tertangani!")
    else:
        st.warning(f"Terdapat **{len(df_menunggu)}** panggilan darurat yang menunggu penanganan!")
        st.dataframe(df_menunggu, use_container_width=True)
        
        st.markdown("### ✅ Selesaikan Pekerjaan Servis")
        with st.form("form_montir"):
            pilih_id = st.selectbox("Pilih ID Order yang sudah selesai diperbaiki:", df_menunggu['ID_Order'].tolist())
            input_biaya = st.number_input("Masukkan Total Biaya Servis (Rp):", min_value=15000, step=5000, value=50000)
            btn_selesai = st.form_submit_button("Simpan & Selesaikan Order")
            
            if btn_selesai:
                df.loc[df['ID_Order'] == pilih_id, 'Biaya'] = input_biaya
                df.loc[df['ID_Order'] == pilih_id, 'Status'] = "Selesai"
                save_data(df)
                st.success(f"Order **{pilih_id}** berhasil diselesaikan dengan biaya Rp {input_biaya:,}!")
                st.rerun()

# ==========================================================
# HALAMAN 3: DASHBOARD BUSINESS INTELLIGENCE (ADMIN)
# ==========================================================
elif menu == "📊 3. Dashboard BI (Admin)":
    st.title("📊 Executive Business Intelligence - Sidrove")
    st.write("Dashboard analitik untuk pengambilan keputusan strategis manajemen operasional Sidrove.")
    
    if df.empty:
        st.warning("⚠️ Data masih kosong! Silakan klik tombol **'✨ Generate 500 Data Dummy'** di menu sebelah kiri (Sidebar) terlebih dahulu.")
    else:
        # Filter Interaktif di Atas Dashboard
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_kendaraan = st.multiselect("Filter Jenis Kendaraan:", options=df['Kendaraan'].unique(), default=df['Kendaraan'].unique())
        with col_f2:
            filter_status = st.multiselect("Filter Status Order:", options=df['Status'].unique(), default=["Selesai"])
            
        df_filtered = df[(df['Kendaraan'].isin(filter_kendaraan)) & (df['Status'].isin(filter_status))].copy()
        
        # --- BARIS 1: KPI CARDS ---
        total_order = len(df_filtered)
        total_pendapatan = df_filtered['Biaya'].sum()
        rata_biaya = df_filtered['Biaya'].mean() if total_order > 0 else 0
        kec_terpadat = df_filtered['Kecamatan'].mode()[0] if total_order > 0 else "-"
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Order Ditangani", f"{total_order:,} Order")
        kpi2.metric("Total Transaksi (GMV)", f"Rp {total_pendapatan:,.0f}")
        kpi3.metric("Rata-rata Biaya Servis", f"Rp {rata_biaya:,.0f}")
        kpi4.metric("Wilayah Paling Rawan", kec_terpadat)
        
        st.markdown("---")
        
        # --- BARIS 2: GRAFIK KECAMATAN & JENIS KERUSAKAN ---
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("📍 Peta Permintaan per Kecamatan")
            kec_count = df_filtered['Kecamatan'].value_counts().reset_index()
            kec_count.columns = ['Kecamatan', 'Jumlah Order']
            fig_kec = px.bar(kec_count, x='Kecamatan', y='Jumlah Order', color='Jumlah Order', 
                             color_continuous_scale='Blues', text_auto=True)
            st.plotly_chart(fig_kec, use_container_width=True)
            st.caption("💡 **Insight BI:** Alokasikan rekrutmen mitra bengkel/montir lebih banyak di 2 kecamatan teratas untuk memangkas waktu tunggu pelanggan.")

        with col_c2:
            st.subheader("🛠️ Proporsi Jenis Kerusakan")
            rusak_count = df_filtered['Kerusakan'].value_counts().reset_index()
            rusak_count.columns = ['Kerusakan', 'Jumlah Kasus']
            fig_rusak = px.pie(rusak_count, names='Kerusakan', values='Jumlah Kasus', hole=0.4)
            st.plotly_chart(fig_rusak, use_container_width=True)
            st.caption("💡 **Insight BI:** Gunakan grafik ini untuk menentukan stok *sparepart* darurat (seperti ban dalam atau aki) yang wajib dibawa montir setiap hari.")

        st.markdown("---")
        
        # --- BARIS 3: JAM SIBUK (PEAK HOURS) & PENDAPATAN ---
        col_c3, col_c4 = st.columns(2)
        
        with col_c3:
            st.subheader("⏰ Analisis Jam Rawan Mogok (Peak Hours)")
            df_filtered['Jam_Angka'] = df_filtered['Jam'].astype(str).str.slice(0, 2).astype(int)
            jam_count = df_filtered.groupby('Jam_Angka').size().reset_index(name='Jumlah Kejadian')
            fig_jam = px.line(jam_count, x='Jam_Angka', y='Jumlah Kejadian', markers=True)
            fig_jam.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2, title="Jam (00:00 - 23:00)"))
            st.plotly_chart(fig_jam, use_container_width=True)
            st.caption("💡 **Insight BI:** Terapkan *Surge Pricing* (tarif ekstra) dan insentif bonus bagi montir yang bersedia *standby* pada jam puncak dan tengah malam.")

        with col_c4:
            st.subheader("💰 Total Pendapatan per Jenis Kerusakan")
            rev_rusak = df_filtered.groupby('Kerusakan')['Biaya'].sum().reset_index().sort_values(by='Biaya', ascending=True)
            fig_rev = px.bar(rev_rusak, x='Biaya', y='Kerusakan', orientation='h', color='Biaya', color_continuous_scale='Greens')
            st.plotly_chart(fig_rev, use_container_width=True)
            st.caption("💡 **Insight BI:** Menunjukkan layanan mana yang menyumbang nilai transaksi terbesar bagi pendapatan perusahaan.")