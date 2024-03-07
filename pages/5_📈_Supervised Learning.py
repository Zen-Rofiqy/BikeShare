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
import statsmodels.api as sm

# Setting
st.set_page_config(
    page_title="BikeShare",
    page_icon="🚲",
)

st.markdown("<h1 style='text-align: center; color: white;'>📈 Supervised Learning</h1>", unsafe_allow_html=True)
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

# Memisahkan variabel independen (X) dan variabel dependen (y)
X = dw_dummy.drop(columns=['cnt'])  # Peubah independen, kecuali cnt
y = dw_dummy['cnt']  # Peubah dependen

# Menambahkan kolom konstan untuk model
X = sm.add_constant(X)

# Membuat model regresi
model = sm.OLS(y, X)

# Melatih model menggunakan data
results = model.fit()

# Regresi
st.markdown(
    """
    > **Syntax**
    ```python
    # Memisahkan variabel independen (X) dan variabel dependen (y)
    X = dw_dummy.drop(columns=['cnt'])  # Peubah independen, kecuali cnt
    y = dw_dummy['cnt']  # Peubah dependen

    # Menambahkan kolom konstan untuk model
    X = sm.add_constant(X)

    # Membuat model regresi
    model = sm.OLS(y, X)

    # Melatih model menggunakan data
    results = model.fit()

    # Menampilkan ringkasan hasil regresi
    print(results.summary())
    ```
    > **Output**
    """
)
st.text(
    """
                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:                    cnt   R-squared:                       1.000
    Model:                            OLS   Adj. R-squared:                  1.000
    Method:                 Least Squares   F-statistic:                 2.155e+31
    Date:                Fri, 08 Mar 2024   Prob (F-statistic):               0.00
    Time:                        00:57:21   Log-Likelihood:                 18649.
    No. Observations:                 731   AIC:                        -3.724e+04
    Df Residuals:                     700   BIC:                        -3.709e+04
    Df Model:                          30                                         
    Covariance Type:            nonrobust                                         
    ===========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -------------------------------------------------------------------------------------------
    const                     4.32e-12   9.57e-13      4.514      0.000    2.44e-12     6.2e-12
    temp                     5.969e-13   3.76e-12      0.159      0.874   -6.78e-12    7.98e-12
    atemp                    3.979e-13   3.92e-12      0.102      0.919    -7.3e-12    8.09e-12
    hum                      2.345e-13   7.98e-13      0.294      0.769   -1.33e-12     1.8e-12
    windspeed                6.608e-13   1.15e-12      0.576      0.565   -1.59e-12    2.91e-12
    casual                      1.0000   2.25e-16   4.44e+15      0.000       1.000       1.000
    registered                  1.0000   1.31e-16   7.63e+15      0.000       1.000       1.000
    season_M Gugur           -1.99e-13   5.22e-13     -0.381      0.703   -1.22e-12    8.26e-13
    season_M Panas          -1.279e-12   5.82e-13     -2.197      0.028   -2.42e-12   -1.36e-13
    season_M Semi            1.137e-13   5.23e-13      0.217      0.828   -9.14e-13    1.14e-12
    yr_2012                  5.471e-13   2.71e-13      2.018      0.044    1.49e-14    1.08e-12
    ...
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The smallest eigenvalue is 1.03e-22. This might indicate that there are
    strong multicollinearity problems or that the design matrix is singular.
    """
)



st.caption(
    """
    Hasil dari regresi model awal adalah seperti yang ditampilkan di atas.

    Mohon maaf, memang hasilnya agak gak makesense, pasti ada yang salah. 
    Namun saya rasa saya memang perlu belajar lebih untuk supervised dan unsupervised learning di python.
    Agaknya cukup berbeda jauh dengan yang ada dalam bahasa R 🙏🙏.
    """
)