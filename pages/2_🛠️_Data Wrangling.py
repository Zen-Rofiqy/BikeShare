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

# Setting
st.set_page_config(
    page_title="BikeShare",
    page_icon="🚲",
)

st.markdown("<h1 style='text-align: center; color: white;'>🛠️ Data Wrangling</h1>", unsafe_allow_html=True)
st.markdown("---")

data = st.session_state["data"]
day_df = st.session_state["day_df"]

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

# Data Wrangling
st.subheader("Assessing Data")
st.caption(
    """
    Sebagai permulaan, kita memeriksa tipe data data dari tiap kolom yang terdapat dalam `day_df`. 
    Proses ini dapat dilakukan menggunakan method `day_df.info()`.
    Berikut merupakan tampilan dari data awal.
    """
)

st.dataframe(day_df)
st.caption(
    """
    **Notes:** memang berbeda dengan data pada **Main Page**, 
    karena pada **Main Page** merupakan data yang sudah di sesuaikan enak dilihat.
    Jadi beginilah tampilan dari data asli yang disimpan pada variabel `day_df`.
    """
)

with st.expander("**Syntax & Output**"):
    st.markdown(
        """
        ```python
        print(day_df.info())
        ```
        """
    )
    st.text(
        """
        <class 'pandas.core.frame.DataFrame'>
        RangeIndex: 731 entries, 0 to 730
        Data columns (total 16 columns):
        #   Column      Non-Null Count  Dtype  
        ---  ------      --------------  -----  
        0   instant     731 non-null    int64  
        1   dteday      731 non-null    object 
        2   season      731 non-null    int64  
        3   yr          731 non-null    int64  
        4   mnth        731 non-null    int64  
        5   holiday     731 non-null    int64  
        6   weekday     731 non-null    int64  
        7   workingday  731 non-null    int64  
        8   weathersit  731 non-null    int64  
        9   temp        731 non-null    float64
        10  atemp       731 non-null    float64
        11  hum         731 non-null    float64
        12  windspeed   731 non-null    float64
        13  casual      731 non-null    int64  
        14  registered  731 non-null    int64  
        15  cnt         731 non-null    int64  
        dtypes: float64(4), int64(11), object(1)
        memory usage: 91.5+ KB
        """
    )
st.caption(
    """
    Jika diperhatikan, jumlah baris data semuanya itu sama yakni 731. Ini menandakan tiadak adanya *missing data*.
    Namun tipe data masih belum sesuai, contohnya `season` seharusnya bertipe `category`.
    """
)

dw_df = pd.DataFrame(day_df)

dw_df['season'] = dw_df['season'].replace({1: 'M Semi', 2: 'M Panas', 3:"M Gugur", 4:"M Dingin"})
dw_df['yr'] = dw_df['yr'].replace({0: '2011', 1: '2012'})
dw_df['mnth']= dw_df['mnth'].astype('category')
dw_df['holiday'] = dw_df['holiday'].replace({0: '-', 1: 'Libur'}).astype('category')
dw_df['workingday'] = dw_df['workingday'].replace({0: 'WeekEnd', 1: 'WeekDay'}).astype('category')
dw_df['workingday']= dw_df['workingday'].astype('category')
dw_df['weekday'] = dw_df['weekday'].replace({0: 'Senin', 1: 'Selasa', 2:'Rabu', 3:'Kamis', 4:"Jum'at", 5:"Sabtu", 6:"Minggu"})
dw_df['weathersit'] = dw_df['weathersit'].replace({1: 'Cerah', 2: 'Berkabut', 3:'Salju Ringan', 4:'Hujan Lebat'})
dw_df['season']= dw_df['season'].astype('category')
dw_df['yr']= dw_df['yr'].astype('category')
dw_df['weekday']= dw_df['weekday'].astype('category')
dw_df['weathersit'] = dw_df['weathersit'].astype('category')

st.session_state["dw_df"] = dw_df 

with st.expander("**Syntax & Output**"):
    st.markdown(
        """
        > **Syntax**
        ```python
        dw_df = pd.DataFrame(day_df)

        dw_df['season'] = dw_df['season'].replace({1: 'M Semi', 2: 'M Panas', 3:"M Gugur", 4:"M Dingin"})
        dw_df['yr'] = dw_df['yr'].replace({0: '2011', 1: '2012'})
        dw_df['mnth']= dw_df['mnth'].astype('category')
        dw_df['holiday'] = dw_df['holiday'].replace({0: '-', 1: 'Libur'}).astype('category')
        dw_df['workingday'] = dw_df['workingday'].replace({0: 'WeekEnd', 1: 'WeekDay'}).astype('category')
        dw_df['workingday']= dw_df['workingday'].astype('category')
        dw_df['weekday'] = dw_df['weekday'].replace({0: 'Senin', 1: 'Selasa', 2:'Rabu', 3:'Kamis', 4:"Jum'at", 5:"Sabtu", 6:"Minggu"})
        dw_df['weathersit'] = dw_df['weathersit'].replace({1: 'Cerah', 2: 'Berkabut', 3:'Salju Ringan', 4:'Hujan Lebat'})
        dw_df['season']= dw_df['season'].astype('category')
        dw_df['yr']= dw_df['yr'].astype('category')
        dw_df['weekday']= dw_df['weekday'].astype('category')
        dw_df['weathersit'] = dw_df['weathersit'].astype('category')

        dw_df.info()
        ```
        """
    )
    st.caption(
        """
        **Notes:** `temp`, `hum`, dan `windspeed`tidak diubah seperti pada **Main Page**
        karena data dw_df ini yang akan kita analisis, sehingga perlu dalam keadaan semula 
        (setelah dibagi dengan angkanya masing-masing).
        """
    )
    st.markdown("> **Output**")
    st.text(
        """
        <class 'pandas.core.frame.DataFrame'>
        RangeIndex: 731 entries, 0 to 730
        Data columns (total 16 columns):
        #   Column      Non-Null Count  Dtype         
        ---  ------      --------------  -----         
        0   instant     731 non-null    int64         
        1   dteday      731 non-null    datetime64[ns]
        2   season      731 non-null    category      
        3   yr          731 non-null    category      
        4   mnth        731 non-null    category      
        5   holiday     731 non-null    category      
        6   weekday     731 non-null    category      
        7   workingday  731 non-null    category      
        8   weathersit  731 non-null    category      
        9   temp        731 non-null    float64       
        10  atemp       731 non-null    float64       
        11  hum         731 non-null    float64       
        12  windspeed   731 non-null    float64       
        13  casual      731 non-null    int64         
        14  registered  731 non-null    int64         
        15  cnt         731 non-null    int64         
        dtypes: category(7), datetime64[ns](1), float64(4), int64(4)
        memory usage: 57.9 KB
        """
    )
st.caption(
    """
    Terlihat bahwa semua tipe data kini sudah sesuai.
    """
)
st.markdown(
    """
    ---
    > Hasil Data setelah disesuaikan
    """
)


col1, col2= st.columns(2)
with col1 : 
    st.markdown(""" Tipe Data """)  
    st.dataframe(dw_df.dtypes)
    st.caption("Terdapat 4 tipe data beruba, yakni kategorik, numerik (rasio dan interval), dan date.")
with col2 :
    st.markdown(""" Data NA""")
    st.dataframe(dw_df.isnull().sum())
    st.caption("Memang terbukti bahwa tidak ada missing value pada `data`.")
st.write("Jumlah data duplikat: " + str(dw_df.duplicated().sum()))
st.caption("Tidak ada Data yang Duplikat")
st.markdown("---")

st. subheader("Tabel Data")
st.markdown(""" Data setelah di cleaning""")
st.dataframe(dw_df)
st.caption("Notes: `mnth` tidak diubah menjadi nama bulan karena lebih mudah jika dalam bentuk angka.")