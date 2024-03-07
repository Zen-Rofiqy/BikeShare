# streamlit run "1_🖥️_Main_Page.py"
# IMPORT
import numpy as np
import pandas as pd
import scipy
import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import sqlalchemy as sqla
import streamlit as st
import time
from sklearn.decomposition import PCA
from scipy import stats
import sys
import io
from babel.numbers import format_currency
import matplotlib.dates as mdates
from PIL import Image, ImageOps, ImageDraw
import requests
from io import BytesIO

sns.set(style='dark')

st.set_page_config(
    page_title="BikeShare",
    page_icon="🚲",
)
# Judul
st.markdown("<h2 style='text-align: center; color: white;'>Analisis <i>Pengaruh</i> Kondisi <i>Lingkungan</i> dan <i>Musim</i> Terhadap Tren <i>Penyewaan Sepeda</i>: Studi Kasus Sistem Capital Bikeshare di Washington D.C.</h2>", unsafe_allow_html=True)
st.image('https://cdn.discordapp.com/attachments/763214382020558858/1214663023310934067/fileKC_Bikes-1024x683.jpg?ex=65f9ee18&is=65e77918&hm=ab8a90a2602c0d6ce28e6c774f649f4f74b087497aed66ea00d2ea2f7824daf3&') 
st.markdown("---")
# DATA
day_df = pd.read_csv("https://raw.githubusercontent.com/Zen-Rofiqy/Bangkit-2024/main/04%20Analisis%20Data%20dng%20Py/%40Proyek-akhir/Bike-sharing-dataset/day.csv")
day_df.head(n=10)

st.session_state["day_df"] = day_df

data = pd.DataFrame(day_df)
data['season'] = data['season'].replace({1: 'M Semi', 2: 'M Panas', 3:"M Gugur", 4:"M Dingin"})
data['yr'] = data['yr'].replace({0: '2011', 1: '2012'})
data['mnth']= data['mnth'].astype('category')
data['holiday'] = data['holiday'].replace({0: 'H Kerja', 1: 'H Libur'})
data['weekday'] = data['weekday'].replace({0: 'Senin', 1: 'Selasa', 2:'Rabu', 3:'Kamis', 4:"Jum'at", 5:"Sabtu", 6:"Minggu"})
data['weathersit'] = data['weathersit'].replace({1: 'Cerah', 2: 'Berkabut', 3:'Salju Ringan', 4:'Hujan Lebat'})
data['windspeed'] = data['windspeed']*67
data['hum'] = data['hum']*100
data['temp'] = data['temp']*41
data['season']= data['season'].astype('category')
data['yr']= data['yr'].astype('category')
data['weekday']= data['weekday'].astype('category')
data['weathersit'] = data['weathersit'].astype('category')
data['dteday'] = pd.to_datetime(data['dteday'])

st.session_state["data"] = data

# Setting
min_date = data["dteday"].min()
max_date = data["dteday"].max()

def count(dates) :
    sumcount = dates['cnt'].sum()
    return sumcount

# Sidebar
with st.sidebar:       
    start, end = st.date_input(
        label='Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Zen Rofiqy</h1>", unsafe_allow_html=True)
# Mengambil gambar dari URL
image_url = "https://avatars.githubusercontent.com/u/114891856?v=4"
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))

# Mendapatkan resolusi asli gambar
original_width, original_height = image.size

# Mengatur ukuran baru untuk gambar
new_width = 500
new_height = 500

# Mengubah ukuran gambar tanpa mengubah resolusi
image = image.resize((new_width, new_height), resample=Image.LANCZOS)

# Membuat gambar menjadi bulat
mask = Image.new('L', (new_width, new_height), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, new_width, new_height), fill=255)
image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
image.putalpha(mask)

# Menampilkan gambar di sidebar
st.sidebar.image(image, use_column_width=True)
st.sidebar.markdown(
    """
    <div>
        <p style="text-align:justify; text-indent: 50px;">
            <span>&#128279; GitHub: <a href="https://github.com/Zen-Rofiqy" target="_blank">Zen-Rofiqy</a></span>
        </p>
    </div>
    <div>
        <p style="text-align:justify; text-indent: 50px;">
            <span>&#128279; Rpubs: <a href="https://rpubs.com/ZenR_Prog/" target="_blank">ZenR_Prog</a></span>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


Hari = data[(data["dteday"] >= str(start)) & (data["dteday"] <= str(end))]
Date = data[(data["dteday"] >= str(start)) & (data["dteday"] <= str(end))]
cor = data[['cnt','temp','atemp', 'hum', 'windspeed', 'casual', 'registered']]

st.session_state["Date"] = Date

# Page 1
# METADATA
st.write("## Metadata")
st.markdown("> 📷**Latarbelakang**")
st.markdown(
    """
    <p style="text-align:justify; text-indent: 40px;">
        <b>Bike sharing</b> atau Sistem berbagi sepeda adalah generasi baru dari <b>penyewaan sepeda tradisional</b> di mana seluruh proses mulai dari <b>keanggotaan</b>, <b>penyewaan</b>, dan <b>pengembalian</b> sepeda menjadi <b>otomatis</b>. Melalui sistem ini, pengguna dapat dengan mudah menyewa sepeda dari posisi tertentu dan mengembalikannya di posisi lain. Saat ini, terdapat <b>lebih dari 500 program</b> berbagi sepeda di seluruh dunia yang terdiri dari <b>lebih dari 500k sepeda</b>. Saat ini, terdapat minat yang besar terhadap sistem ini karena peran penting mereka dalam masalah lalu lintas, lingkungan dan kesehatan. 
    </p>
    <p style="text-align:justify; text-indent: 40px;">
        Terlepas dari aplikasi dunia nyata yang menarik dari sistem berbagi sepeda, <b>karakteristik data</b> yang dihasilkan oleh sistem ini membuatnya menarik untuk penelitian. Berbeda dengan layanan transportasi lain seperti bus atau kereta bawah tanah, <b>durasi perjalanan</b>, <b>posisi keberangkatan</b> dan <b>kedatangan secara eksplisit</b> dicatat dalam sistem ini. Fitur ini mengubah sistem berbagi sepeda menjadi <b>jaringan sensor virtual</b> yang dapat digunakan untuk merasakan mobilitas di kota. Dengan demikian, diharapkan sebagian besar kejadian penting di kota dapat dideteksi melalui pemantauan data ini.
    </p>
    """, unsafe_allow_html=True
)
st.markdown("---")
st.markdown("> 🧮**Data set**")
st.write(
    """
    <p style="text-align:justify; text-indent: 40px;">
        Proses penyewaan sepeda bersama sangat <b>berkorelasi</b> dengan <b>kondisi lingkungan</b> dan <b>musim</b>. Misalnya, <b>kondisi cuaca</b>, <b>curah hujan</b>, <b>hari dalam seminggu</b>, <b>musim</b>, <b>jam dalam sehari</b>, dan lain-lain dapat mempengaruhi perilaku penyewaan. Kumpulan data inti terkait dengan catatan historis selama <b>dua tahun</b> yang berkaitan dengan tahun <b>2011</b> dan <b>2012</b> dari sistem Capital Bikeshare, Washington D.C., Amerika Serikat yang tersedia untuk umum di <a href="http://capitalbikeshare.com/system-data" target="_blank">http://capitalbikeshare.com/system-data</a>. Kami mengumpulkan data tersebut dalam dua basis data <b>per jam</b> dan <b>per hari</b>, kemudian mengekstrak dan menambahkan <b>informasi cuaca</b> dan <b>musim</b> yang sesuai. Informasi cuaca diambil dari <a href="http://www.freemeteo.com" target="_blank">http://www.freemeteo.com</a>.
    </p>
    """, unsafe_allow_html=True
)
st.markdown("---")
st.markdown("> 📝**Tugas terkait**")
st.write(
    """
    <ul>
        <li><b>Regresi</b>:<br>
            <p style="text-align:justify; text-indent: 40px;">
                <b>Prediksi jumlah penyewaan sepeda</b> per jam atau per hari <b>berdasarkan pengaturan lingkungan dan musim</b>.
            </p>
        </li>
        <li><b>Deteksi Peristiwa dan Anomali</b>:<br>
            <p style="text-align:justify; text-indent: 40px;">
                <b>Jumlah sepeda yang disewa</b> juga <b>berkorelasi</b> dengan beberapa <b>peristiwa di kota</b> yang dapat dengan mudah ditelusuri melalui mesin pencari. Sebagai contoh, kueri seperti "2012-10-30 washington d.c." di Google mengembalikan hasil yang terkait dengan <b>Badai Sandy</b>. Beberapa peristiwa penting diidentifikasi dalam <a href="[1]" target="_blank">[1]</a>. Oleh karena itu, data tersebut dapat digunakan untuk <b>validasi algoritma</b> <b>pendeteksi anomali atau kejadian</b>.
            </p>
        </li>
    </ul>
    """, unsafe_allow_html=True
)
st.caption("Mohon maaf sebelumnya, untuk poin 2 saya rasa saya blm mampu untuk mengerjakannya🙏 sekarang.")
st.markdown("---")
st.markdown("> 📚**Karakteristik Dataset**")
st.write(
    """
    Baik hour.csv dan day.csv memiliki bidang berikut, kecuali hr yang tidak tersedia di day.csv
    * `instant`    : indeks catatan
    * `dteday`     : tanggal
    * `season`     : musim (1: musim semi, 2: musim panas, 3: musim gugur, 4: musim dingin)
    * `yr`         : tahun (0: 2011, 1: 2012)
    * `mnth`       : bulan (1 hingga 12)
    * `hr`         : jam (0 hingga 23)
    * `holiday`    : hari cuaca hari libur atau tidak (diambil dari http://dchr.dc.gov/page/holiday-schedule)
    * `weekday`    : hari dalam seminggu
    * `workingday` : jika hari tersebut bukan akhir pekan atau hari libur maka nilainya 1, jika tidak maka nilainya 0.
    * `weathersit` : 
        - 1: Cerah, Sedikit awan, Berawan sebagian, Berawan sebagian
        - 2: Kabut + Mendung, Kabut + Awan pecah, Kabut + Sedikit awan, Kabut
        - 3: Salju Ringan, Hujan Ringan + Badai Petir + Awan berserakan, Hujan Ringan + Awan berserakan
        - 4: Hujan Lebat + Hujan Es + Badai Petir + Kabut, Salju + Kabut
    * `temp`       : Suhu yang dinormalisasi dalam Celcius. Nilai dibagi menjadi 41 (maks)
    * `atemp`      : Suhu perasaan yang dinormalisasi dalam Celcius. Nilai dibagi menjadi 50 (maks)
    * `hum`        : Kelembapan yang dinormalisasi. Nilai dibagi menjadi 100 (maks)
    * `windspeed`  : Kecepatan angin yang dinormalisasi. Nilai dibagi menjadi 67 (maks)
    * `casual`     : jumlah pengguna biasa
    * `registered` : jumlah pengguna terdaftar
    * `cnt`        : jumlah total sepeda yang disewa termasuk yang kasual dan terdaftar
    """
)
st.markdown("---")
st.markdown("<h2 style='text-align: center; color: white;'>Tabel Data</h2>", unsafe_allow_html=True)
st.dataframe(Hari)
st.markdown("---")
st.markdown("> 🤵🏽**Pertanyaan Bisnis**")
st.write(
    """
    1. Bagaimana pola penggunaan sepeda berdasarkan musim dan kondisi cuaca di Washington D.C. selama dua tahun terakhir?
        - **Visualisasi Data:**  
             * Histogram/Density plot jumlah sepeda yang disewa per musim dengan variasi kondisi cuaca sebagai warna atau bentuk yang berbeda-beda. 
             * Line Chart (Time Series) menunjukkan tren penggunaan sepeda selama dua tahun terakhir berdasarkan musim.
    2. Bagaimana pengaruh hari libur terhadap pola penggunaan sepeda di Washington D.C. selama dua tahun terakhir?
        - **Visualisasi Data:**  
             * Bar Chart menunjukkan perbandingan jumlah sepeda yang disewa pada hari libur dan hari kerja selama dua tahun terakhir. 
             * Line Chart menunjukkan tren penggunaan sepeda selama dua tahun terakhir dengan penandaan hari libur yang berbeda.
    """
)