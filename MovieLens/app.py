# =========================
# IMPORT
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Movie Satisfaction Analysis",
    layout="wide"
)

st.title("🎬 Phân tích các yếu tố ảnh hưởng đến mức độ hài lòng của khán giả")
st.markdown("**Dữ liệu: MovieLens & TMDB**")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("data/merged_data.csv")
    return df

df = load_data()

# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio(
    "📌 Chọn nội dung",
    [
        "Giới thiệu",
        "Tiền xử lý dữ liệu",
        "Phân tích mô tả",
        "Phân tích đa biến",
        "Xây dựng mô hình",
        "Feature Importance",
        "Dự đoán"
    ]
)

# =========================
# GIỚI THIỆU (Markdown cell)
# =========================
if menu == "Giới thiệu":
    st.header("📘 Giới thiệu đề tài")
    st.markdown("""
    Nghiên cứu này nhằm phân tích các yếu tố ảnh hưởng đến mức độ hài lòng của khán giả
    đối với phim điện ảnh dựa trên hai bộ dữ liệu MovieLens và TMDB.
    """)

    st.subheader("📊 Dữ liệu mẫu")
    st.dataframe(df.head())

# =========================
# TIỀN XỬ LÝ (Code cells)
# =========================
elif menu == "Tiền xử lý dữ liệu":
    st.header("⚙️ Tiền xử lý dữ liệu")

    st.write("Kiểm tra missing values:")
    st.write(df.isnull().sum())

    st.write("Loại bỏ các dòng thiếu dữ liệu quan trọng")
    df_clean = df.dropna(subset=[
        'rating', 'runtime', 'budget', 'popularity', 'vote_average'
    ])

    st.success(f"Dữ liệu sau xử lý: {df_clean.shape[0]} dòng")
    st.dataframe(df_clean.head())

# =========================
# PHÂN TÍCH MÔ TẢ
# =========================
elif menu == "Phân tích mô tả":
    st.header("📈 Phân tích mô tả")

    feature = st.selectbox(
        "Chọn biến",
        ['rating', 'runtime', 'budget', 'popularity', 'vote_average']
    )

    fig, ax = plt.subplots()
    sns.histplot(df[feature].dropna(), kde=True, ax=ax)
    ax.set_title(f"Phân phối {feature}")
    st.pyplot(fig)

# =========================
# PHÂN TÍCH ĐA BIẾN
# =========================
elif menu == "Phân tích đa biến":
    st.header("🔍 Phân tích đa biến")

    x_var = st.selectbox("Biến X", ['runtime', 'budget', 'popularity'])
    y_var = st.selectbox("Biến Y", ['rating', 'vote_average'])

    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x_var, y=y_var, alpha=0.5, ax=ax)
    ax.set_title(f"{y_var} theo {x_var}")
    st.pyplot(fig)

# =========================
# XÂY DỰNG MÔ HÌNH
# =========================
elif menu == "Xây dựng mô hình":
    st.header("🤖 Xây dựng mô hình")

    features = ['runtime', 'budget', 'popularity', 'vote_average']
    X = df[features]
    y = df['rating']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model_type = st.selectbox(
        "Chọn mô hình",
        ["Linear Regression", "Random Forest"]
    )

    if model_type == "Linear Regression":
        model = LinearRegression()
    else:
        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42
        )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    st.write("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
    st.write("R² Score:", r2_score(y_test, y_pred))

# =========================
# FEATURE IMPORTANCE
# =========================
elif menu == "Feature Importance":
    st.header("📌 Feature Importance")

    features = ['runtime', 'budget', 'popularity', 'vote_average']
    X = df[features]
    y = df['rating']

    rf_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )
    rf_model.fit(X, y)

    perm_importance = permutation_importance(
        rf_model, X, y,
        n_repeats=10,
        random_state=42,
        n_jobs=-1
    )

    imp_df = pd.DataFrame({
        'Feature': features,
        'Importance': perm_importance.importances_mean
    }).sort_values(by='Importance', ascending=False)

    st.dataframe(imp_df)

    fig, ax = plt.subplots()
    sns.barplot(data=imp_df, x='Importance', y='Feature', ax=ax)
    st.pyplot(fig)

# =========================
# DỰ ĐOÁN
# =========================
elif menu == "Dự đoán":
    st.header("🎯 Dự đoán rating phim")

    runtime = st.slider("Runtime", 60, 240, 120)
    budget = st.number_input("Budget", 0, 300_000_000, 50_000_000)
    popularity = st.slider("Popularity", 0.0, 100.0, 20.0)
    vote_average = st.slider("Vote Average", 0.0, 10.0, 6.5)

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    X = df[['runtime', 'budget', 'popularity', 'vote_average']]
    y = df['rating']
    model.fit(X, y)

    if st.button("Dự đoán"):
        X_input = np.array([[runtime, budget, popularity, vote_average]])
        pred = model.predict(X_input)
        st.success(f"⭐ Rating dự đoán: {pred[0]:.2f}")
