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
from sklearn.cluster import KMeans
from scipy import stats
import sys
import io
from babel.numbers import format_currency
import matplotlib.dates as mdates
from PIL import Image, ImageOps, ImageDraw
import requests
from io import BytesIO
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

# Setting
st.set_page_config(
    page_title="BikeShare",
    page_icon="🚲",
)

st.markdown("<h1 style='text-align: center; color: white;'>📱 Unsupervised Learning</h1>", unsafe_allow_html=True)
st.markdown("---")

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

# Data
st.write(
    """
    Data yang akan digunakan ialah data tanpa kolom `instant` dan `dteday`, serperti tabel berikut.
    """
)

st.dataframe(dw_df.drop(['dteday', 'instant'], axis=1))
st.caption(
    """
    Terlihat bahwa ada beberapa data yang kategorik, jadi Data akan dibuat dummy variable dulu
    sebelum dilakukan *clustering*.
    """
)

#Dummy
dw_dummy = pd.get_dummies(dw_df.drop(['dteday', 'instant'], axis=1), drop_first=True).astype(float)

with st.expander("Hasil Dummy Variable"):
    st.dataframe(dw_dummy)  


# Clustering
# K-Means
st.subheader('K-Means Clustering')
st.write(
    """
    > **Penentuan Jumlah *Cluster***

    Ada beberapa metode yang biasa digunakan untuk menentukan jumlah *Cluster*, salah satunya adalah metode **Elbow**.
    Pertama-tama data di *scaling* dahulu untuk setiap peubah (kolom) dengan mean 0, dan stan deviasi 1. 
    """
)
#create scaled DataFrame where each variable has mean of 0 and standard dev of 1
scaled_df = StandardScaler().fit_transform(dw_dummy)

# Elbow
#initialize kmeans parameters
kmeans_kwargs = {
"init": "random",
"n_init": 10,
"random_state": 1,
}

#create list to hold SSE values for each k
sse = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(scaled_df)
    sse.append(kmeans.inertia_)

#visualize results
plt.plot(range(1, 11), sse)
plt.xticks(range(1, 11))
plt.xlabel("Number of Clusters")
plt.ylabel("SSE")
plt.show()
plt1 = plt.gcf()
st.pyplot(plt1)

st.caption(
    """
    Metode Elbow menetukan *cluster* dengan melihat siku mana yang paling runcing. 
    Terlihat bahwa siku yang paling runcing berada di nomor 2. 
    Sehingga jumlah cluster yang optimal menurut metode elbow adalah 2.
    """
)
st.markdown("---")

#kmeans
#instantiate the k-means class, using optimal number of clusters
kmeans = KMeans(init="random", n_clusters=2, n_init=10, random_state=1)

#fit k-means algorithm to data
kmeans.fit(scaled_df)

#append cluster assingments to original DataFrame
km_data = dw_df
km_data['cluster'] = kmeans.labels_

col = km_data.pop('cluster')
km_data.insert(1, col.name, col)

st.subheader("Hasil K-Means Clustering")

# Hasil cluster
st.write("> **Tabel Data**")
st.dataframe(km_data)
st.caption(
    """
    Keanggotaan cluster bisa dilihat pada kolom cluster yakni kolom kedua. 
    Angka nol tersebut menandakan bahwa baris tersebut merupakan anggota dari
    cluster 0. 
    """
)
st.markdown("---")

st.write("> **Perbandingan jumlah antar cluster**")
st.dataframe(km_data["cluster"].value_counts())
st.caption(
    """
    Perbandingan jumlah antara cluster 0 dengan cluster 1 tidak berbeda jauh. 
    Hanya memiliki selisih 75 anggota saja.
    """
)

st.markdown("---")
# Cluster Profiling
st.write("> **Cluster Profiling**")

# Memisahkan kolom numerik dan non-numerik
numeric_cols = km_data.select_dtypes(include=['number']).columns
non_numeric_cols = km_data.select_dtypes(exclude=['number']).columns

# Membuat list kategori numerik
categories = numeric_cols[2:]  # Menggunakan semua kolom numerik (termasuk 'temp')

# Daftar warna kalem untuk setiap cluster
colors = ['rgba(153, 204, 255, 0.5)', 'rgba(204, 255, 204, 0.5)', 'rgba(255, 204, 204, 0.5)', 
          'rgba(204, 204, 255, 0.5)', 'rgba(255, 204, 153, 0.5)', 'rgba(204, 153, 255, 0.5)']

# Membuat figure
fig = go.Figure()

# Menambahkan trace untuk setiap cluster
for i, cluster in enumerate(km_data['cluster'].unique()):
    cluster_data = km_data[km_data['cluster'] == cluster][categories]
    fig.add_trace(go.Scatterpolar(
        r=cluster_data.mean().values,
        theta=categories,
        fill='toself',  # Fill area dengan warna
        fillcolor=colors[i % len(colors)],  # Warna fill sesuai cluster
        mode='lines',  # Menampilkan garis dan area fill
        name=f'Cluster {cluster}',
        line=dict(color='white')  # Mengatur warna garis menjadi putih
    ))

# Mengatur layout
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, color='white'),  # Mengatur warna radial axis menjadi putih
        angularaxis=dict(color='white'),  # Mengatur warna angular axis menjadi putih
        bgcolor='black'  # Mengatur warna latar belakang menjadi hitam
    ),
    showlegend=True,
    plot_bgcolor='black'  # Mengatur warna latar belakang menjadi hitam
)

# Menampilkan plot di Streamlit
st.plotly_chart(fig)

with st.expander("Penjelasan Radar Chart"):
    st.write(
        """
        #### Karakteristik Kluster:

        **Miripnya Karakteristik:** Semua klaster memiliki nilai yang rendah atau bahkan tidak ada pada variabel 'windspeed', 'hum', 'atemp', dan 'temp'. Hal ini menunjukkan bahwa variabel-variabel ini mungkin tidak memiliki pengaruh yang signifikan dalam membentuk klaster.

        **Perbedaan dalam Jumlah Peminjaman:** Meskipun karakteristik dasar dari klaster cenderung mirip, terdapat perbedaan yang signifikan dalam jumlah peminjaman sepeda ('cnt'), baik secara total maupun terbagi antara peminjaman terdaftar ('registered') dan peminjaman tidak terdaftar ('casual').

        #### Insight:

        **Pengaruh Variabel Cuaca:** Karakteristik yang mirip pada variabel cuaca ('windspeed', 'hum', 'atemp', dan 'temp') menunjukkan bahwa faktor-faktor ini mungkin tidak memiliki peran yang dominan dalam pembentukan klaster. Hal ini bisa disebabkan oleh variasi yang rendah dari variabel cuaca di seluruh dataset.
        
        **Perbedaan dalam Jumlah Peminjaman:** Perbedaan yang signifikan dalam jumlah peminjaman antara klaster menunjukkan bahwa ada faktor-faktor lain di luar variabel cuaca yang mempengaruhi perilaku peminjaman sepeda. Hal ini bisa jadi disebabkan oleh faktor-faktor seperti lokasi, waktu, promosi, atau kebijakan penyewaan yang berbeda.
        """
    )
st.markdown("---")

# Kesimpulan
st.markdown("### Kesimpulan")
st.markdown(
    """
    <p style="text-align:justify; text-indent: 40px;">
    Berdasarkan analisis radar chart dan perbandingan nilai variabel pada setiap klaster, 
    dapat disimpulkan bahwa karakteristik cuaca, seperti kecepatan angin ('windspeed'), 
    kelembaban udara ('hum'), suhu aktual ('atemp'), dan suhu ('temp'), cenderung memiliki pengaruh yang serupa 
    di semua klaster. Hal ini menunjukkan bahwa faktor-faktor cuaca tersebut mungkin tidak menjadi faktor utama 
    yang memengaruhi pola peminjaman sepeda. Namun, terdapat perbedaan signifikan dalam jumlah peminjaman sepeda
    antara klaster. Klaster dengan jumlah peminjaman yang lebih tinggi, baik secara total maupun terbagi 
    antara peminjaman terdaftar dan tidak terdaftar, menunjukkan bahwa ada faktor-faktor lain di luar cuaca 
    yang memengaruhi perilaku peminjaman sepeda. Kemungkinan faktor-faktor seperti lokasi, waktu, promosi, 
    atau kebijakan penyewaan yang berbeda dapat menjadi penjelasan atas perbedaan ini. Oleh karena itu, 
    studi ini menunjukkan bahwa aspek-aspek lain selain cuaca dapat memiliki dampak yang signifikan terhadap 
    tren peminjaman sepeda, dan analisis lebih lanjut diperlukan untuk memahami faktor-faktor tersebut dan 
    bagaimana kontribusinya terhadap jumlah peminjaman sepeda.
    </p>
    """, unsafe_allow_html=True
)