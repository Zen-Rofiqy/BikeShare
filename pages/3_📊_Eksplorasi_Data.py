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
import base64

# Setting
st.set_page_config(
    page_title="BikeShare",
    page_icon="🚲",
)

data = st.session_state["data"]
day_df = st.session_state["day_df"]
dw_df = st.session_state["dw_df"]

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

# Page3
# EKSPLORASI
st.markdown("<h1 style='text-align: center; color: white;'>📊 Eksplorasi Data</h1>", unsafe_allow_html=True)
st.markdown("---")
st.subheader('Jumlah Total')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("  Total Sepeda yang Disewa", value=count(Date))
with col2:
    st.metric("  Total Pengguna Terdaftar", value=Date['registered'].sum())
with col3:
    st.metric("  Total Pengguna Biasa", value=Date['casual'].sum())
st.markdown("---")

# Sebaran Disktrit
st.write("\n\n")
st.subheader('Sebaran Diskrit')
def plot_disk(data_frame, column, names=None):
    # Mendapatkan kategori unik dan warna untuk plot
    max_value = data_frame[column].value_counts().idxmax()
    categories = data_frame[column].unique()
    colors = ['#1380A1' if x == max_value else '#dddddd' for x in categories]

    # Mendapatkan nama kategori
    category_names = [str(cat) for cat in categories]
    if names:
        category_names = names

    # Membuat countplot
    plt.figure(figsize=(10, 6))
    sns.countplot(x=column, data=data_frame, order=categories, palette=colors)
    plt.title(f'Sebaran {column}')
    plt.xlabel(f'\n{column}')
    plt.ylabel('Banyaknya Hari')

    # Mengatur label pada sumbu x
    plt.xticks(ticks=range(len(categories)), labels=category_names)

    # Menyimpan plot dalam variabel
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Menutup plot untuk plot selanjutnya
    plt.close()

    return buffer

# Menyimpan plot 
c_season = plot_disk(dw_df, 'season', names=['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin'])
c_holiday = plot_disk(dw_df, 'holiday', names=['Hari Lain', 'Hari Libur'])
c_workingday = plot_disk(dw_df, 'workingday', names=['WeekEnd', 'WeekDay'])
c_weathersit = plot_disk(dw_df, 'weathersit', names=['Cerah', 'Berkabut', 'Salju Ringan'])

# Menampilkan plot
# Membuat tiga kolom
c1, c2 = st.columns((1,1))
c3, c4 = st.columns((1,1))

# Mendefinisikan fungsi untuk menampilkan gambar dengan judul dan caption opsional
def img_capt(column, title, image_bytes, button_label, default_caption):
    # Mengubah objek BytesIO menjadi base64
    encoded_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
    
    column.markdown(f"**{title}**")
    column.image(f"data:image/png;base64,{encoded_image}")
    if column.button(button_label):
        column.write(default_caption)

# Menampilkan gambar dengan judul dan caption opsional di setiap kolom
img_capt(c1, "Sebaran Musim", c_season, "Caption1", 'Dalam periode 2 tahun yang diamati, Musim Gugur mencatat jumlah hari terbanyak dibandingkan dengan musim lainnya, dengan total mencapai 188 hari.')
img_capt(c2, "Sebaran Hari Libur Nasional", c_holiday, "Caption2.1", 'Hari Libur Nasional (tidak termasuk weekend) dalam rentang waktu dua tahun terbilang jarang.\nPada hari libur nasional, terdapat hanya 21 hari, sedangkan pada hari biasa, terdapat 710 hari.')
img_capt(c3, "Sebaran Hari WeekEnd & WeekDay", c_workingday, "Caption2.2", 'Hari Libur Nasional (tidak termasuk weekend) dalam rentang waktu dua tahun terbilang jarang.\nPada hari libur nasional, terdapat hanya 21 hari, sedangkan pada hari biasa, terdapat 710 hari.')
img_capt(c4, "Sebaran Cuaca", c_weathersit, "Caption3", 'Selama dua tahun, cuaca sering berkabut.\nTerjadi 247 hari dengan kondisi cuaca berkabut, 463 hari dengan cuaca cerah, dan hanya 21 hari dengan cuaca salju ringan.')

st.markdown("---")

# Sebaran Kontinu
st.write("\n\n")
st.subheader('Sebaran Kontinu')
def plot_kon(data_frame, column):
    # Membuat subplots
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create a list of colors for the boxplots based on the number of features you have
    boxplots_colors = ['#5AC1A2']

    # Boxplot data
    bp = ax.boxplot(data_frame[column], patch_artist=True, vert=False)

    # Change to the desired color and add transparency
    for patch, color in zip(bp['boxes'], boxplots_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.4)

    # Create a list of colors for the violin plots based on the number of features you have
    violin_colors = ['#5AC1A2']

    # Violinplot data
    vp = ax.violinplot(data_frame[column], points=500, showmeans=False, showextrema=False, showmedians=False, vert=False)

    for idx, b in enumerate(vp['bodies']):
        # Get the center of the plot
        m = np.mean(b.get_paths()[0].vertices[:, 0])
        # Modify it so we only see the upper half of the violin plot
        b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], idx+1, idx+2)
        # Change to the desired color
        b.set_color(violin_colors[idx])

        # Create a list of colors for the scatter plots based on the number of features you have
        scatter_colors = ['#5AC1A2']

        # Scatterplot data
        plt.scatter(data_frame[column], np.ones(len(data_frame[column])), s=3, c=scatter_colors[0])

        plt.yticks([1], [''])  # Set text labels.
        plt.xlabel('Values')
        plt.title(f"Sebaran {column}")

        # Menyimpan plot dalam variabel
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Menutup plot untuk plot selanjutnya
        plt.close()

        return buffer


# Menyimpan Plot
c_temp = plot_kon(dw_df, 'temp')
c_atemp = plot_kon(dw_df, 'atemp')
c_hum = plot_kon(dw_df, 'hum')
c_windspeed = plot_kon(dw_df, 'windspeed')
c_casual = plot_kon(dw_df, 'casual')
c_registered = plot_kon(dw_df, 'registered')
c_cnt = plot_kon(dw_df, 'cnt')

# Menampilkan plot
# Membuat tiga kolom
c4, c5, c6 = st.columns((1,1,1))
c7, c8 = st.columns((1,1))
c9, c10 = st.columns((1,1))

img_capt(c4, "Sebaran Temperatur", c_temp, "Caption4", 'Pola distribusi yang bimodal dan simetris menunjukkan variasi suhu yang cukup signifikan. Dengan rata-rata sekitar 20.31, kita bisa melihat bahwa terdapat dua puncak distribusi suhu yang mungkin mencerminkan dua kondisi cuaca yang berbeda.')
img_capt(c5, "Sebaran Suhu Perasaan", c_atemp, "Caption5", 'Distribusi bimodal dengan asimetri menunjukkan adanya variasi signifikan dalam persepsi suhu. Rata-rata suhu perasaan yang lebih rendah mungkin menunjukkan adanya kondisi cuaca yang berpotensi lebih dingin.')
img_capt(c6, "Sebaran Kelembapan", c_hum, "Caption6", 'Distribusi simetris menunjukkan kecenderungan kelembapan yang stabil. Hal ini dapat mempengaruhi persepsi cuaca oleh pengguna, terutama dalam hal kenyamanan.')
img_capt(c7, "Sebaran Kecepatan Angin", c_windspeed, "Caption7", 'Distribusi yang menjulur ke kanan menunjukkan adanya kemungkinan kecepatan angin yang lebih tinggi pada beberapa titik waktu. Hal ini dapat mempengaruhi keamanan dan kenyamanan saat bersepeda.')
img_capt(c8, "Sebaran Pengguna Biasa", c_casual, "Caption8", 'Distribusi data cenderung memiliki ekor panjang ke arah kanan.\nTerdapat 731 data yang diamati, dengan rata-rata sekitar 848.176471 dan standar deviasi sekitar 686.622488. Nilai minimum data adalah 2, sementara nilai maksimumnya mencapai 3410. Distribusi data ini cenderung memiliki ekor panjang ke arah kanan, dengan nilai median (50%) sekitar 713. Quartil pertama (25%) berada di sekitar 315.5, sementara quartil ketiga (75%) berada di sekitar 1096.')
img_capt(c9, "Sebaran Pengguna Terdaftar", c_registered, "Caption9", 'Distribusi yang simetris dan mendekati distribusi normal menunjukkan bahwa pengguna terdaftar memiliki kecenderungan yang lebih merata dalam menggunakan layanan ini. Hal ini bisa mencerminkan kestabilan dalam pola penggunaan sepeda terdaftar.')
img_capt(c10, "Sebaran Total Sepeda yang disewakan", c_cnt, "Caption10", 'Distribusi data menunjukkan pola penyebaran yang simetris dan hampir mendekati distribusi normal. Dengan rata-rata sekitar 4504.35 dan standar deviasi sekitar 1937.21, kita bisa melihat bahwa pola penyebaran data ini menunjukkan kecenderungan simetris dan hampir menyerupai distribusi normal. Hal ini mungkin mencerminkan kestabilan dalam pola penggunaan sepeda yang disewakan, dengan jumlah yang relatif merata di berbagai waktu.')
    
with st.expander("Summary"):
    st.markdown(
    '''
    Summary Sebaran Data:
    1. **Musim Gugur Mendominasi:**
        Dalam rentang dua tahun yang diamati, musim gugur mencatat jumlah hari terbanyak dibandingkan dengan musim lainnya. Hal ini menunjukkan bahwa musim gugur mungkin menjadi waktu yang paling populer bagi pengguna sepeda.
    2. **Cuaca Berkabut yang Sering Terjadi:**
        Dengan 247 hari dengan kondisi cuaca berkabut, hal ini menunjukkan bahwa kabut adalah fenomena cuaca yang cukup umum di wilayah tersebut. Hal ini perlu dipertimbangkan dalam analisis pola penggunaan sepeda.
    3. **Variasi Suhu yang Signifikan:**
        Distribusi bimodal suhu menunjukkan adanya dua kondisi cuaca yang mungkin mempengaruhi penggunaan sepeda. Hal ini menyoroti pentingnya memahami variasi suhu untuk merencanakan kegiatan bersepeda yang nyaman.
    4. **Keterkaitan Antara Kelembapan dan Kenyamanan:**
        Distribusi kelembapan yang stabil menunjukkan bahwa kenyamanan saat bersepeda mungkin dipengaruhi oleh tingkat kelembapan. Informasi ini dapat digunakan untuk menyesuaikan layanan berbagi sepeda agar sesuai dengan preferensi pengguna.
    5. **Perilaku Pengguna:** 
        Distribusi jumlah pengguna biasa yang cenderung lebih sedikit menunjukkan bahwa ada sebagian besar pengguna yang tidak menggunakan layanan secara teratur. Hal ini dapat menjadi titik fokus dalam upaya meningkatkan penggunaan sepeda secara konsisten.
    6. **Stabilitas Pengguna Terdaftar:**
        Distribusi pengguna terdaftar yang merata menunjukkan bahwa pengguna terdaftar cenderung menggunakan layanan secara konsisten. Hal ini menunjukkan pentingnya menjaga kepuasan pengguna terdaftar untuk mempertahankan stabilitas penggunaan.
    7. **Stabilitas Jumlah Sepeda yang Disewakan:**
        Distribusi data yang hampir normal menunjukkan bahwa pola penggunaan sepeda secara keseluruhan relatif stabil selama dua tahun tersebut. Hal ini mencerminkan konsistensi dalam permintaan dan penawaran layanan berbagi sepeda di wilayah tersebut.
    '''
    )

st.markdown("---")

st.markdown("<h1 style=color: white;'>Menjawab Pertanyaan Bisnis</h1>", unsafe_allow_html=True)

st.write("\n\n")
st.subheader('Sebaran `cnt` per Musim tiap kondisi Cuaca')
# Urutan hue berdasarkan jumlah cnt
hue_order = dw_df.groupby('weathersit')['cnt'].sum().sort_values(ascending=False).index

# Buat plot menggunakan seaborn dengan palet warna yang lebih kontras
sns.set(style="whitegrid")
g = sns.FacetGrid(dw_df, col="season", hue="weathersit", col_wrap=4, height=6, palette="Dark2", hue_order=hue_order)
g.map_dataframe(sns.histplot, x="cnt", bins=10, kde=True)
g.add_legend()

# Atur judul
plt.subplots_adjust(top=0.9)
plt.suptitle('Histogram Jumlah Sepeda yang Disewa per Musim dengan Variasi Kondisi Cuaca', fontweight='bold')
plt.show()

# Tampilkan plot pada Streamlit
plt1 = plt.gcf()
st.pyplot(plt1)

with st.expander("Summary"):
    st.markdown(
    '''
    Berdasarkan analisis grafik yang diberikan, beberapa insight penting yang dapat diambil adalah:

    1. Cuaca cerah memiliki tren penyewaan sepeda tertinggi di setiap musim, terutama pada musim gugur dan semi. Ini mengindikasikan bahwa kondisi cuaca cerah mendorong minat masyarakat untuk menyewa sepeda. Oleh karena itu, perusahaan penyewaan sepeda perlu mempersiapkan stok sepeda yang memadai pada musim-musim tersebut.

    2. Pada musim dingin, cuaca cerah dan berkabut memiliki tren penyewaan sepeda yang cukup tinggi, meskipun lebih rendah daripada musim lainnya. Ini menunjukkan bahwa masyarakat masih memiliki minat untuk menyewa sepeda pada musim dingin, terutama pada cuaca cerah dan berkabut. Perusahaan penyewaan sepeda dapat mempertimbangkan untuk menyediakan layanan khusus atau promosi pada musim dingin untuk meningkatkan penyewaan.

    3. Cuaca salju ringan memiliki tren penyewaan sepeda yang sangat rendah di setiap musim. Ini mengindikasikan bahwa masyarakat cenderung tidak menyewa sepeda pada saat cuaca salju ringan. Perusahaan penyewaan sepeda dapat mempertimbangkan untuk mengurangi jumlah sepeda yang tersedia atau bahkan menghentikan operasi sementara pada saat cuaca salju ringan untuk menghemat biaya operasional.

    4. Tren penyewaan sepeda pada musim gugur dan panas cenderung lebih tinggi daripada musim lainnya, terutama pada cuaca cerah. Ini menunjukkan bahwa masyarakat lebih tertarik untuk menyewa sepeda pada musim-musim tersebut. Perusahaan penyewaan sepeda perlu mempersiapkan strategi pemasaran dan operasional yang sesuai untuk memenuhi permintaan yang tinggi pada musim-musim tersebut.

    5. Secara umum, kondisi cuaca cerah dan musim yang sejuk (semi dan gugur) menjadi faktor pendorong utama dalam tren penyewaan sepeda. Perusahaan penyewaan sepeda perlu memperhatikan pola ini dan mengoptimalkan layanan serta sumber daya mereka sesuai dengan kondisi lingkungan dan musim.

    Insight-insight ini dapat membantu perusahaan penyewaan sepeda dalam menganalisis pengaruh kondisi lingkungan dan musim terhadap tren penyewaan sepeda, serta mengembangkan strategi yang tepat untuk meningkatkan efisiensi operasional dan memenuhi permintaan pelanggan secara optimal.
    '''
    )
st.markdown("---")


# Pie Chart
st.subheader('Sepeda yang Disewa pada Hari Libur dan Hari Kerja')
col1, col2= st.columns(2)
with col1:
    st.markdown("**Banyaknya Hari kerja dan Hari libur**")
    
    # Streamlit cloud ada masalha dalam operasi bool
    # Encoding bool jadi 0 1 dan jadikan float
    dw_df['holiday_encoded'] = dw_df['holiday'].replace({'Libur': 1, '-': 0}).astype(float)
    dw_df['workingday_encoded'] = dw_df['workingday'].replace({'WeekEnd': 1, 'WeekDay': 0}).astype(float)

    # Menghitung jumlah hari libur & weekend
    holiday_weekend_count = dw_df[(dw_df['holiday_encoded'] == 1) & (dw_df['workingday_encoded'] == 1)].shape[0]
    
    # Menghitung jumlah hari kerja/weekday
    weekday_count = dw_df[(dw_df['holiday_encoded'] == 0) & (dw_df['workingday_encoded'] == 0)].shape[0]

    # Membuat Pie Chart
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plotting untuk hari libur & weekend dan hari kerja/weekday
    labels = ['Hari Libur & Weekend', 'Hari Kerja/Weekday']
    sizes = [holiday_weekend_count, weekday_count]
    colors = ['#dddddd', '#1380A1']

    # Pengecekan nilai sizes
    if sum(sizes) == 0:
        st.warning("Tidak ada data untuk ditampilkan.")
    else:
        # Menampilkan pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

    # Menambahkan frekuensi di sebelah label
    for i, label in enumerate(labels):
        texts[i].set_text(label + f'\n({sizes[i]} hari)')

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    plt1 = plt.gcf()
    st.pyplot(plt1)

with col2:
    st.markdown("**Banyaknya sepeda yang disewa per hari kerja/libur**")
    # Dummy grouped_data (digunakan untuk demo)
    grouped_data = dw_df.groupby(['holiday', 'workingday'])['cnt'].sum()

    # Menghitung jumlah hari libur & weekend
    holiday_weekend_count = dw_df[(dw_df['holiday'] == 'Libur') & (dw_df['workingday'] == 'WeekEnd')].shape[0] + dw_df[(dw_df['holiday'] == '-') & (dw_df['workingday'] == 'WeekEnd')].shape[0]

    # Menghitung jumlah hari kerja/weekday
    weekday_count = dw_df[(dw_df['holiday'] == '-') & (dw_df['workingday'] == 'WeekDay')].shape[0] + dw_df[(dw_df['holiday'] == 'Libur') & (dw_df['workingday'] == 'WeekDay')].shape[0]

    # Menghitung total penyewaan sepeda pada hari libur/weekend dan hari kerja/weekday
    holiday_weekend = grouped_data.loc[('Libur', 'WeekEnd')] + grouped_data.loc[('-', 'WeekEnd')]
    weekday_weekend = grouped_data.loc[('-', 'WeekDay')] + grouped_data.loc[('Libur', 'WeekDay')]

    # Membuat Pie Chart
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plotting untuk hari libur/weekend dan hari kerja/weekday
    labels = ['Hari Libur & Weekend', 'Hari Kerja/Weekday']
    sizes = [holiday_weekend / holiday_weekend_count, weekday_weekend / weekday_count]
    colors = ['#dddddd', '#1380A1']

    # Pengecekan nilai sizes
    if any(size < 0 for size in sizes):
        st.warning("Nilai negatif tidak valid untuk membuat pie chart.")
    else:
        # Menampilkan pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

    # Menambahkan frekuensi di sebelah label
    for i, label in enumerate(labels):
        texts[i].set_text(label + f'\n({sizes[i]:.2f} sepeda/hari)')

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    plt1 = plt.gcf()
    st.pyplot(plt1)

st.caption(
    """
    **Notes:** Hari libur disini merupakan gabungan hari libur nasional dan hari Weekend. 
    Sedangkan hari kerja diisini merupakan hari Weekday yang bukan hari libur nasional.

    Perbedaan antara jumlah sepeda yang disewa pada hari libur dan kerja per hari ternyata tidak
    berbeda terlalu jauh. Walau begitu, frekuensi penyewaan sepeda lebih banyak pada hari kerja. 
    """
)


st.markdown("---")
# Time Series
st.write("\n\n")
st.subheader('Data Deret Waktu')

# Konversi kolom 'dteday' menjadi tipe data datetime
dw_df['dteday'] = day_df['dteday'] 
dw_df['dteday'] = pd.to_datetime(dw_df['dteday'])

import matplotlib.pyplot as plt
import pandas as pd

# Konversi kolom 'dteday' menjadi tipe data datetime
dw_df['dteday'] = pd.to_datetime(dw_df['dteday'])

# Plot the time series
plt.figure(figsize=(35, 8), dpi=300)
plt.plot(dw_df['dteday'], dw_df['cnt'], linestyle='-', color='black', alpha=0.7, linewidth=2.5)
plt.scatter(dw_df[dw_df['holiday'] != '-']['dteday'], dw_df[dw_df['holiday'] != '-']['cnt'], marker='x', color='red', label='Hari Libur', s=100)
plt.scatter(dw_df[dw_df['workingday'] != 'WeekDay']['dteday'], dw_df[dw_df['workingday'] != 'WeekDay']['cnt'], marker='o', color='red', label='Week End', s=10)
plt.scatter(dw_df[dw_df['workingday'] != 'WeekEnd']['dteday'], dw_df[dw_df['workingday'] != 'WeekEnd']['cnt'], marker='o', color='green', label='Week Day', s=50)
plt.title('Data Deret Waktu Dari Sistem berbagi Sepeda', fontsize=20)
plt.xlabel('Date')
plt.ylabel('Banyaknya sepeda')
plt.grid(True)

# Menyesuaikan format tanggal pada sumbu x
plt.gcf().autofmt_xdate()

# Warna untuk setiap musim
colors = ['#feb813', '#e9324c', '#973a06', '#005e72']

# Daftar untuk menyimpan legenda unik
unique_legends = []

# Highlight each season's time range
for season, color in zip(dw_df['season'].unique(), colors):
    season_data = dw_df[dw_df['season'] == season]
    sorted_dates = season_data['dteday'].sort_values()
    
    start_range = None
    first_iteration = True
    for i in range(len(sorted_dates)):
        current_date = sorted_dates.iloc[i]
        if start_range is None:
            start_range = current_date
        elif (current_date - sorted_dates.iloc[i - 1]).days > 1 or i == len(sorted_dates) - 1:
            end_range = sorted_dates.iloc[i - 1] if i != len(sorted_dates) - 1 else current_date
            
            # Tambahkan legenda unik jika belum ada
            if season not in unique_legends:
                unique_legends.append(season)
                plt.axvspan(start_range, end_range, color=color, alpha=0.3, label=season)
            else:
                plt.axvspan(start_range, end_range, color=color, alpha=0.3)
            
            start_range = None
            first_iteration = False

# Menambahkan legenda
plt.legend()

plt.show()
plt1 = plt.gcf()
st.pyplot(plt1)

# Interpretasi
with st.expander("Insight pola penyewaan sepeda"):
    st.write(
        """
        **1. Tren Musiman:**

        Terlihat bahwa tren penyewaan sepeda cenderung mengikuti pola musiman, dengan peningkatan pada musim semi dan musim panas, sedangkan pada musim gugur dan musim dingin cenderung stabil atau menurun. Hal ini mengindikasikan adanya pola permintaan yang terkait dengan musim dan cuaca.

        **2. Pengaruh Hari dalam Seminggu:**

        Hari-hari weekend memiliki tingkat penyewaan yang lebih tinggi dibandingkan dengan hari weekday. Namun, saat permintaan meningkat, perbedaan antara hari weekend dan weekday menjadi tidak terlalu signifikan. Ini menunjukkan bahwa permintaan sepeda cenderung bergantung pada faktor-faktor tertentu seperti cuaca atau acara khusus, bukan hanya hari dalam seminggu.

        **3. Pengaruh Hari Libur:**

        Meskipun hari libur nasional cenderung memiliki tingkat penyewaan yang lebih rendah dibandingkan dengan hari biasa, ada beberapa hari libur yang memiliki tingkat penyewaan yang tinggi. Ini menunjukkan bahwa ada faktor lain selain hari libur yang memengaruhi permintaan, seperti perayaan lokal atau acara khusus.

        **4. Pola Turun Drastis pada Awal 2013:**

        Terdapat penurunan drastis dalam jumlah penyewaan sepeda pada awal tahun 2013, terutama pada musim dingin. Hal ini mungkin disebabkan oleh perubahan faktor eksternal seperti kebijakan baru, perubahan tren, atau kondisi ekonomi.

        **5. Potensi Pengembangan Layanan:**

        Tren peningkatan jumlah total penyewaan sepeda dari tahun 2011 hingga 2012 menunjukkan adanya permintaan yang meningkat terhadap layanan penyewaan sepeda. Hal ini dapat menjadi peluang bagi penyedia layanan untuk mengembangkan atau meningkatkan layanan mereka, seperti menambah jumlah sepeda, meningkatkan promosi, atau menyesuaikan harga dengan pola permintaan yang berubah-ubah.
        """
    )

# Matriks Korelasi 
st.write("\n\n")
st.subheader('Matriks Korelasi')
df = dw_df.iloc[:, 10:16]

# Plot heatmap
def corrfunc(x, y, **kws):
  r, p = stats.pearsonr(x, y)
  p_stars = ''
  if p <= 0.05:
    p_stars = '*'
  if p <= 0.01:
    p_stars = '**'
  if p <= 0.001:
    p_stars = '***'
  ax = plt.gca()
  ax.annotate('r = {:.2f} '.format(r) + p_stars,
              xy=(0.05, 0.9), xycoords=ax.transAxes)

def annotate_colname(x, **kws):
  ax = plt.gca()
  ax.annotate(x.name, xy=(0.05, 0.9), xycoords=ax.transAxes,
              fontweight='bold')

def cor_matrix(df):
  g = sns.PairGrid(df, palette=['red'], diag_sharey=False)
  # Use normal regplot as `lowess=True` doesn't provide CIs.
  # Upper
  g.map_upper(sns.regplot, scatter_kws={'s': 20, 'color': 'DarkCyan'}, line_kws={'color': '#472a7a'}) 
  # Diag
  g.map_diag(sns.histplot, kde=True, kde_kws=dict(cut=3), alpha=.7, color='teal', edgecolor='black')
  g.map_diag(annotate_colname)
  # Lower
  g.map_lower(sns.kdeplot, cmap='viridis')
  g.map_lower(corrfunc)
  # Remove axis labels, as they're in the diagonals.
  for ax in g.axes.flatten():
    ax.set_ylabel('')
    ax.set_xlabel('')
  return g

st.pyplot(cor_matrix(df))

# Interpretasi
with st.expander("Interpretasi"):
    st.write(
       """
        * *Keterkaitan antara Variabel Registered dan Total Sepeda Disewakan:* 
            Insight dari matriks korelasi menunjukkan bahwa variabel registered memiliki korelasi positif yang paling kuat dengan variabel respons cnt. Ini menunjukkan bahwa jumlah sepeda yang disewakan yang didaftarkan memiliki keterkaitan yang erat dengan total jumlah sepeda yang disewakan secara keseluruhan. Hal ini mengindikasikan bahwa pengguna terdaftar memiliki pengaruh signifikan terhadap total penggunaan layanan sewa sepeda.
        * *Pengaruh Kelembapan Terhadap Jumlah Sepeda Disewakan:* 
            Korelasi negatif yang lemah antara variabel kelembapan udara (hum) dan total jumlah sepeda yang disewakan (cnt) menunjukkan bahwa kelembapan udara memiliki dampak yang relatif kecil terhadap permintaan layanan sewa sepeda. Hal ini menunjukkan bahwa faktor cuaca seperti kelembapan mungkin tidak menjadi faktor utama dalam menentukan jumlah sepeda yang disewakan, dan faktor-faktor lain seperti musim atau kondisi cuaca lainnya mungkin memiliki pengaruh yang lebih signifikan.
       """
    )
