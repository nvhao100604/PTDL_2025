# =====================================
# STREAMLIT APP - CONVERTED FROM NOTEBOOK
# Source: TONGQUAN.ipynb
# =====================================

import streamlit as st
import pandas as pd
import numpy as np
import re
import json
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import warnings

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="Movie Data Analysis",
    layout="wide"
)

st.title("🎬 PHÂN TÍCH DỮ LIỆU PHIM")
st.markdown("Chuyển đổi trực tiếp từ Jupyter Notebook sang Streamlit")

# =====================================
# SIDEBAR
# =====================================
menu = st.sidebar.radio(
    "📌 Nội dung",
    [
        "Tổng quan",
        "Tiền xử lí dữ liệu",
        "Khám phá dữ liệu",
        "Khám phá chuyên sâu"
    ]
)

# =====================================
# CELL 1–2: LOAD DATA
# =====================================
@st.cache_data
def load_data():
    movies = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")
    return movies, ratings

movies, ratings = load_data()

# =====================================
# 1️⃣ TỔNG QUAN
# =====================================
if menu == "Tổng quan":
    st.header("📊 Tổng quan dữ liệu")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Số phim", movies.shape[0])
    with col2:
        st.metric("Số đánh giá", ratings.shape[0])
    with col3:
        st.metric("Số người dùng", ratings["UserID"].nunique())

    st.subheader("📋 Movies dataset")
    st.dataframe(movies.head())

    st.subheader("📋 Ratings dataset")
    st.dataframe(ratings.head())

# =====================================
# 2️⃣ TIỀN XỬ LÍ DỮ LIỆU
# =====================================
elif menu == "Tiền xử lí dữ liệu":
    st.header("🧹 Tiền xử lí dữ liệu")

    st.subheader("🔍 Kiểm tra dữ liệu thiếu")
    st.write(movies.isnull().sum())

    # CELL: XỬ LÝ GENRES
    movies['Genres'] = movies['Genres'].apply(
        lambda x: x.split('|') if isinstance(x, str) else []
    )

    st.subheader("🎭 Sample genres đã xử lí")
    st.write(movies[['Title', 'Genres']].head())

    # CELL: ENCODE GENRES
    mlb = MultiLabelBinarizer()
    genres_encoded = mlb.fit_transform(movies['Genres'])
    genres_df = pd.DataFrame(
        genres_encoded,
        columns=mlb.classes_,
        index=movies.index
    )

    movies_encoded = pd.concat([movies, genres_df], axis=1)

    st.success("✅ Hoàn tất tiền xử lí dữ liệu")
    st.dataframe(movies_encoded.head())

# =====================================
# 3️⃣ KHÁM PHÁ DỮ LIỆU
# =====================================
elif menu == "Khám phá dữ liệu":
    st.header("📈 Khám phá dữ liệu")

    st.subheader("⭐ Phân phối rating")

    fig, ax = plt.subplots()
    sns.histplot(ratings["Rating"], bins=20, kde=True, ax=ax)
    ax.set_title("Distribution of Ratings")
    st.pyplot(fig)

    st.subheader("📊 Rating trung bình theo phim")

    movie_avg = ratings.groupby("MovieID")["Rating"].mean()
    fig, ax = plt.subplots()
    sns.histplot(movie_avg, bins=30, kde=True, ax=ax)
    ax.set_title("Average Rating per Movie")
    st.pyplot(fig)

# =====================================
# 4️⃣ KHÁM PHÁ CHUYÊN SÂU
# =====================================
elif menu == "Khám phá chuyên sâu":
    st.header("🧠 Khám phá chuyên sâu")

    st.subheader("📌 Tính điểm trung bình cho từng phim")

    movie_targets = ratings.groupby('MovieID')['Rating'].mean().reset_index()
    movie_targets.columns = ['MovieID', 'avg_rating']

    st.dataframe(movie_targets.head())

    st.subheader("📉 Phân cụm phim theo rating")

    X = movie_targets[['avg_rating']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42)
    movie_targets['cluster'] = kmeans.fit_predict(X_scaled)

    fig = px.scatter(
        movie_targets,
        x='MovieID',
        y='avg_rating',
        color='cluster',
        title="Clustering Movies by Average Rating"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Insight chính:**
    - Phim có thể chia thành nhiều nhóm rating khác nhau  
    - Không phải phim nổi tiếng nào cũng được đánh giá cao  
    - Phân cụm giúp hỗ trợ recommendation system
    """)

    st.success("🎯 Hoàn tất phân tích chuyên sâu")
