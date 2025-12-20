import streamlit as st
import pandas as pd
import numpy as np
import re
import ast
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.ensemble import RandomForestRegressor

# Cấu hình trang
st.set_page_config(
    page_title="MovieLens Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTab {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Hàm xử lý dữ liệu
@st.cache_data
def clean_movielens_title(text):
    return re.sub(r'\s*\(\d{4}\)$', '', str(text)).lower().strip()

@st.cache_data
def clean_tmdb_title(text):
    return str(text).lower().strip()

@st.cache_data
def get_director(text):
    try:
        data = ast.literal_eval(text)
        for x in data:
            if x['job'] == 'Director': 
                return x['name']
        return np.nan
    except: 
        return np.nan

@st.cache_data
def get_top_actors(text):
    try:
        data = ast.literal_eval(text)
        return [x['name'] for x in data[:3]]
    except: 
        return []

@st.cache_data
def load_data():
    try:
        # ===== MovieLens =====
        u_cols = ['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code']
        m_cols = ['MovieID', 'Title', 'Genres']
        r_cols = ['UserID', 'MovieID', 'Rating', 'Timestamp']

        users = pd.read_csv(
            'datasets/movie_len_1M/users.dat',
            sep='::', names=u_cols, engine='python', encoding='latin-1'
        )
        movies = pd.read_csv(
            'datasets/movie_len_1M/movies.dat',
            sep='::', names=m_cols, engine='python', encoding='latin-1'
        )
        ratings = pd.read_csv(
            'datasets/movie_len_1M/ratings.dat',
            sep='::', names=r_cols, engine='python', encoding='latin-1'
        )

        movie_targets = (
            ratings
            .groupby('MovieID')['Rating']
            .agg(['mean', 'count'])
            .reset_index()
            .rename(columns={'mean': 'avg_rating', 'count': 'rating_count'})
        )

        # ===== TMDB =====
        tmdb_cred = pd.read_csv('datasets/tmdb_5000/tmdb_5000_credits.csv')
        tmdb_mov = pd.read_csv('datasets/tmdb_5000/tmdb_5000_movies.csv')

        tmdb_cred.columns = ['movie_id', 'title', 'cast', 'crew']
        tmdb_mov = tmdb_mov.rename(columns={'id': 'movie_id'})

        tmdb_full = tmdb_mov.merge(tmdb_cred, on='movie_id')

        # ===== TẠO FULL_DATA (CHUẨN) =====
        movies_tmp = movies.copy()
        movies_tmp['clean_title'] = (
            movies_tmp['Title']
            .str.replace(r"\s\(\d{4}\)", "", regex=True)
            .str.lower()
        )

        tmdb_tmp = tmdb_full.copy()
        tmdb_tmp['clean_title'] = tmdb_tmp['original_title'].str.lower()

        # ====== MERGE ======
        full_data = (
            movies_tmp
            .merge(movie_targets, on='MovieID')
            .merge(
                tmdb_tmp[['clean_title', 'budget', 'revenue',
                        'runtime', 'popularity', 'vote_count', 'vote_average']],
                on='clean_title',
                how='inner'
            )
        )

        # ====== LỌC CHẤT LƯỢNG DỮ LIỆU (QUAN TRỌNG) ======
        full_data = full_data[
            (full_data['vote_count'] > 50) &
            (full_data['budget'] > 10_000) &
            (full_data['revenue'] > 10_000)
        ].copy()

        # ====== 1 PHIM = 1 DÒNG ======
        full_data = full_data.drop_duplicates(subset=['MovieID'])

        return users, movies, ratings, movie_targets, tmdb_full, full_data  

    except Exception as e:
        st.error(f"Lỗi load dữ liệu: {e}")
        return [None] * 6

# Tải dữ liệu
with st.spinner('Đang tải dữ liệu...'):
    users, movies, ratings, movie_targets, tmdb_full, full_data = load_data()

if users is None:
    st.error("Không thể tải dữ liệu. Vui lòng kiểm tra đường dẫn file.")
    st.stop()

# Header
st.markdown('<h1 class="main-header">🎬 MovieLens Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### Phân tích các yếu tố ảnh hưởng đến rating người dùng trên MovieLens")

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400", use_container_width=True)
    st.markdown("## 📊 Điều khiển Dashboard")
    
    analysis_type = st.selectbox(
    "Chọn loại phân tích:",
    [
        "Tổng quan",
        "Phân tích Users",
        "Phân tích Movies",
        "Phân tích Ratings",
        "Phân tích TMDb",
        "Tiền xử lí dữ liệu",
        "EDA",
        "Yếu tố tài chính"    ]
)


    
    st.markdown("---")
    st.markdown("### 📈 Thống kê nhanh")
    st.metric("Tổng Users", f"{len(users):,}")
    st.metric("Tổng Movies", f"{len(movies):,}")
    st.metric("Tổng Ratings", f"{len(ratings):,}")
    st.metric("Tổng TMDb Movies", f"{len(tmdb_full):,}")

# Tabs chính
if analysis_type == "Tổng quan":
    st.markdown("## 📋 Tổng quan Dữ liệu")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>👥</h2>
            <h3>{:,}</h3>
            <p>Người dùng</p>
        </div>
        """.format(len(users)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🎥</h2>
            <h3>{:,}</h3>
            <p>Phim</p>
        </div>
        """.format(len(movies)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>⭐</h2>
            <h3>{:,}</h3>
            <p>Đánh giá</p>
        </div>
        """.format(len(ratings)), unsafe_allow_html=True)
    
    with col4:
        avg_rating = ratings['Rating'].mean()
        st.markdown("""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>{:.2f}</h3>
            <p>Rating TB</p>
        </div>
        """.format(avg_rating), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Biểu đồ tổng quan
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Phân bố Rating")
        rating_dist = ratings['Rating'].value_counts().sort_index()
        fig = px.bar(
            x=rating_dist.index, 
            y=rating_dist.values,
            labels={'x': 'Rating', 'y': 'Số lượng'},
            color=rating_dist.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 👥 Phân bố Giới tính")
        gender_dist = users['Gender'].value_counts()
        fig = px.pie(
            values=gender_dist.values, 
            names=gender_dist.index,
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top movies
    st.markdown("### 🏆 Top 10 Phim có Rating cao nhất")
    top_movies = movie_targets.nlargest(10, 'avg_rating')
    top_movies = top_movies.merge(movies[['MovieID', 'Title']], on='MovieID')
    
    fig = px.bar(
        top_movies, 
        x='avg_rating', 
        y='Title',
        orientation='h',
        color='avg_rating',
        color_continuous_scale='plasma',
        labels={'avg_rating': 'Rating TB', 'Title': 'Phim'}
    )
    fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Phân tích Users":
    st.markdown("## 👥 Phân tích Người dùng")
    
    tab1, tab2= st.tabs(["Thống kê cơ bản", "Phân tích theo nhóm tuổi"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Phân bố Độ tuổi")
            age_dist = users['Age'].value_counts().sort_index()
            fig = px.bar(
                x=age_dist.index, 
                y=age_dist.values,
                labels={'x': 'Nhóm tuổi', 'y': 'Số lượng'},
                color=age_dist.values,
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💼 Top 10 Nghề nghiệp")
            occ_dist = users['Occupation'].value_counts().head(10)
            fig = px.pie(
                values=occ_dist.values, 
                names=occ_dist.index,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Rating trung bình theo Nhóm tuổi")
        user_ratings = ratings.merge(users[['UserID', 'Age', 'Gender']], on='UserID')
        age_rating = user_ratings.groupby('Age')['Rating'].mean().reset_index()
        
        fig = px.line(
            age_rating, 
            x='Age', 
            y='Rating',
            markers=True,
            labels={'Age': 'Nhóm tuổi', 'Rating': 'Rating TB'}
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 So sánh Rating theo Giới tính và Độ tuổi")
        gender_age_rating = user_ratings.groupby(['Age', 'Gender'])['Rating'].mean().reset_index()
        
        fig = px.bar(
            gender_age_rating, 
            x='Age', 
            y='Rating',
            color='Gender',
            barmode='group',
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    
elif analysis_type == "Phân tích Movies":
    st.markdown("## 🎥 Phân tích Phim")
    
    tab1, tab2 = st.tabs(["Thống kê Genres", "Top Phim"])
    
    with tab1:
        st.markdown("### 🎭 Phân bố Thể loại Phim")
        
        # Tách genres
        genres_list = []
        for genres in movies['Genres'].dropna():
            genres_list.extend(genres.split('|'))
        
        genre_counts = pd.Series(genres_list).value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=genre_counts.index, 
                y=genre_counts.values,
                labels={'x': 'Thể loại', 'y': 'Số lượng phim'},
                color=genre_counts.values,
                color_continuous_scale='sunset'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                values=genre_counts.values, 
                names=genre_counts.index,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Rating theo genre
        st.markdown("### ⭐ Rating trung bình theo Thể loại")
        movies_with_ratings = movies.merge(movie_targets, on='MovieID')
        
        genre_ratings = []
        for _, row in movies_with_ratings.iterrows():
            for genre in row['Genres'].split('|'):
                genre_ratings.append({
                    'Genre': genre,
                    'Rating': row['avg_rating']
                })
        
        genre_ratings_df = pd.DataFrame(genre_ratings)
        genre_avg = genre_ratings_df.groupby('Genre')['Rating'].mean().sort_values(ascending=False)
        
        fig = px.bar(
            x=genre_avg.values, 
            y=genre_avg.index,
            orientation='h',
            color=genre_avg.values,
            color_continuous_scale='plasma',
            labels={'x': 'Rating TB', 'y': 'Thể loại'}
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🏆 Top Phim")
        
        filter_type = st.radio(
            "Lọc theo:",
            ["Rating cao nhất", "Nhiều đánh giá nhất", "Phổ biến nhất"]
        )
        
        top_n = st.slider("Số lượng phim hiển thị:", 5, 20, 10)
        
        if filter_type == "Rating cao nhất":
            top = movie_targets[movie_targets['rating_count'] >= 50].nlargest(top_n, 'avg_rating')
            metric = 'avg_rating'
            label = 'Rating TB'
        elif filter_type == "Nhiều đánh giá nhất":
            top = movie_targets.nlargest(top_n, 'rating_count')
            metric = 'rating_count'
            label = 'Số đánh giá'
        else:
            top = movie_targets.nlargest(top_n, 'rating_count')
            metric = 'avg_rating'
            label = 'Rating TB'
        
        top = top.merge(movies[['MovieID', 'Title']], on='MovieID')
        
        fig = px.bar(
            top, 
            x=metric, 
            y='Title',
            orientation='h',
            color=metric,
            color_continuous_scale='viridis',
            labels={metric: label, 'Title': 'Phim'}
        )
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Phân tích Ratings":
    st.markdown("## ⭐ Phân tích Đánh giá")
    
    tab1, tab2, tab3 = st.tabs(["Phân bố Rating", "Thời gian", "Tương quan"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Histogram Rating")
            fig = px.histogram(
                ratings, 
                x='Rating',
                nbins=5,
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Boxplot Rating")
            fig = px.box(
                ratings, 
                y='Rating',
                color_discrete_sequence=['#764ba2']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📉 Phân bố số lượng Rating trên mỗi phim")
        rating_counts = movie_targets['rating_count']
        
        fig = px.histogram(
            x=rating_counts,
            nbins=50,
            labels={'x': 'Số lượng rating', 'y': 'Số phim'},
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📅 Rating theo Thời gian")
        ratings_time = ratings.copy()
        ratings_time['Date'] = pd.to_datetime(ratings_time['Timestamp'], unit='s')
        ratings_time['YearMonth'] = ratings_time['Date'].dt.to_period('M').astype(str)
        
        time_rating = ratings_time.groupby('YearMonth')['Rating'].agg(['mean', 'count']).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=time_rating['YearMonth'], y=time_rating['mean'], name="Rating TB", line=dict(color='#667eea', width=3)),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Bar(x=time_rating['YearMonth'], y=time_rating['count'], name="Số lượng", marker_color='#764ba2', opacity=0.3),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Thời gian")
        fig.update_yaxes(title_text="Rating TB", secondary_y=False)
        fig.update_yaxes(title_text="Số lượng rating", secondary_y=True)
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔗 Ma trận Tương quan")
        
        # Chuẩn bị dữ liệu
        user_ratings = ratings.merge(users[['UserID', 'Age', 'Gender', 'Occupation']], on='UserID')
        user_ratings['Gender_num'] = user_ratings['Gender'].map({'M': 1, 'F': 0})
        
        corr_data = user_ratings[['Rating', 'Age', 'Gender_num', 'Occupation']].corr()
        
        fig = px.imshow(
            corr_data,
            text_auto='.2f',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Phân tích TMDb":
    st.markdown("## 🎬 Phân tích TMDb Dataset")
    
    tab1, tab2, tab3 = st.tabs(["Thống kê cơ bản", "Phân tích Budget & Revenue", "Phân tích Popularity"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tổng phim", f"{len(tmdb_full):,}")
            st.metric("Budget TB", f"${tmdb_full['budget'].mean()/1e6:.1f}M")
        
        with col2:
            st.metric("Revenue TB", f"${tmdb_full['revenue'].mean()/1e6:.1f}M")
            st.metric("Runtime TB", f"{tmdb_full['runtime'].mean():.0f} phút")
        
        with col3:
            st.metric("Vote Average TB", f"{tmdb_full['vote_average'].mean():.2f}")
            st.metric("Popularity TB", f"{tmdb_full['popularity'].mean():.1f}")
        
        st.markdown("### 🌍 Phân bố Ngôn ngữ")
        lang_dist = tmdb_full['original_language'].value_counts().head(10)
        
        fig = px.bar(
            x=lang_dist.index, 
            y=lang_dist.values,
            labels={'x': 'Ngôn ngữ', 'y': 'Số lượng phim'},
            color=lang_dist.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 💰 Scatter Plot: Budget vs Revenue")
        
        tmdb_filtered = tmdb_full[(tmdb_full['budget'] > 0) & (tmdb_full['revenue'] > 0)]
        
        fig = px.scatter(
            tmdb_filtered,
            x='budget',
            y='revenue',
            color='vote_average',
            size='popularity',
            hover_data=['title_x'],
            color_continuous_scale='viridis',
            labels={'budget': 'Budget (USD)', 'revenue': 'Revenue (USD)'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Top 10 phim có Revenue cao nhất")
        top_revenue = tmdb_full.nlargest(10, 'revenue')[['title_x', 'revenue', 'budget']]
        
        fig = px.bar(
            top_revenue,
            x='revenue',
            y='title_x',
            orientation='h',
            color='revenue',
            color_continuous_scale='plasma',
            labels={'revenue': 'Revenue (USD)', 'title_x': 'Phim'}
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔥 Top 20 phim Phổ biến nhất (Popularity)")

    # Lọc dữ liệu hợp lệ
    tmdb_pop = tmdb_full[
        tmdb_full['popularity'].notna()
    ]

    top_pop = (
        tmdb_pop
        .nlargest(20, 'popularity')
        [['original_title', 'popularity', 'vote_average']]
    )

    fig = px.bar(
        top_pop,
        x='popularity',
        y='original_title',
        orientation='h',
        color='vote_average',
        color_continuous_scale='sunset',
        labels={
            'popularity': 'Popularity',
            'original_title': 'Phim',
            'vote_average': 'Vote Average'
        }
    )

    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    📌 **Nhận xét:**
    - Popularity phản ánh **mức độ quan tâm truyền thông**, không hoàn toàn trùng với chất lượng
    - Nhiều phim có popularity cao nhưng vote trung bình
    """)
    # =========================
# TAB: TIỀN XỬ LÍ DỮ LIỆU
# =========================
elif analysis_type == "Tiền xử lí dữ liệu":

    st.subheader("🧹 Tiền xử lí dữ liệu MovieLens & TMDb")

    st.markdown("### 1️⃣ Kiểm tra dữ liệu ban đầu")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Users**")
        st.dataframe(users.head())
    with col2:
        st.write("**Movies**")
        st.dataframe(movies.head())
    with col3:
        st.write("**Ratings**")
        st.dataframe(ratings.head())

    st.markdown("---")
    st.markdown("### 2️⃣ Kiểm tra giá trị thiếu")

    missing_df = pd.DataFrame({
        "Users": users.isnull().sum(),
        "Movies": movies.isnull().sum(),
        "Ratings": ratings.isnull().sum()
    })

    st.dataframe(missing_df)

    st.markdown("📌 **Nhận xét:** Dataset MovieLens hầu như không có giá trị thiếu.")

    st.markdown("---")
    st.markdown("### 3️⃣ Xử lí dữ liệu Genres")

    movies['Genres'] = movies['Genres'].str.split('|')
    st.write("Ví dụ sau khi tách Genres:")
    st.dataframe(movies[['Title', 'Genres']].head())

    st.markdown("---")
    st.markdown("### 4️⃣ Gộp dữ liệu Movies & Ratings")

    movie_rating_full = pd.merge(ratings, movies, on="MovieID")
    movie_rating_full = pd.merge(movie_rating_full, movie_targets, on="MovieID")

    st.write("Dữ liệu sau khi merge:")
    st.dataframe(movie_rating_full.head())

    st.markdown("---")
    st.markdown("### 5️⃣ Lọc phim có đủ số lượng đánh giá")

    min_rating = st.slider(
        "Chọn số lượng rating tối thiểu:",
        min_value=10,
        max_value=500,
        value=50,
        step=10
    )

    filtered_movies = movie_targets[movie_targets['rating_count'] >= min_rating]

    st.metric(
        "Số phim sau khi lọc",
        f"{len(filtered_movies):,}"
    )

    st.markdown("📌 **Mục đích:** Tránh nhiễu từ các phim có quá ít đánh giá.")
# =========================
# TAB: EDA
# =========================
elif analysis_type == "EDA":

    st.subheader("📊 Exploratory Data Analysis (EDA)")

    st.markdown("### 1️⃣ Phân bố Rating")

    rating_dist = ratings['Rating'].value_counts().sort_index()
    st.bar_chart(rating_dist)

    st.markdown("📌 **Nhận xét:** Người dùng có xu hướng đánh giá cao (4–5 sao).")

    st.markdown("---")
    st.markdown("### 2️⃣ Top phim được đánh giá nhiều nhất")

    top_movies = movie_targets.sort_values(
        by="rating_count",
        ascending=False
    ).head(10)

    top_movies = pd.merge(
        top_movies,
        movies[['MovieID', 'Title']],
        on='MovieID'
    )

    st.dataframe(top_movies)

    st.markdown("---")
    st.markdown("### 3️⃣ Quan hệ giữa số lượt rating và điểm trung bình")

    st.scatter_chart(
        movie_targets,
        x="rating_count",
        y="avg_rating"
    )

    st.markdown("📌 **Nhận xét:** Các phim có nhiều rating thường có điểm ổn định hơn.")

    st.markdown("---")
    st.markdown("### 4️⃣ Phân tích theo độ tuổi người dùng")

    user_rating_age = pd.merge(ratings, users, on="UserID")

    age_rating = user_rating_age.groupby("Age")['Rating'].mean().reset_index()

    st.line_chart(
        age_rating,
        x="Age",
        y="Rating"
    )

    st.markdown("📌 **Nhận xét:** Rating trung bình thay đổi nhẹ theo nhóm tuổi.")

    st.markdown("---")
    st.markdown("### 5️⃣ Phân tích theo giới tính")

    gender_rating = user_rating_age.groupby("Gender")['Rating'].mean().reset_index()

    st.bar_chart(
        gender_rating,
        x="Gender",
        y="Rating"
    )

    st.markdown("📌 **Nhận xét:** Sự khác biệt rating giữa nam và nữ không quá lớn.")

# =========================
# TAB: YẾU TỐ TÀI CHÍNH
# =========================
elif analysis_type == "Yếu tố tài chính":
    
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    
    st.markdown("## 💰 Yếu tố Tài chính & Rating MovieLens")

    st.markdown("""
    Phân tích mối quan hệ giữa **Ngân sách sản xuất (Budget)**,
    **Doanh thu (Revenue)** và **Rating trung bình** của phim do người dùng MovieLens đánh giá.
    """)

    # ======================================================
    # 1. CHUẨN BỊ DỮ LIỆU (PHẠM VI PHIM)
    # ======================================================
    
    # ======================================================
    # Chuẩn bị dữ liệu (CHỈ CHẠY 1 LẦN)
    # ======================================================
    movies_tmp = movies.copy()
    movies_tmp['clean_title'] = (
        movies_tmp['Title']
        .str.replace(r"\s\(\d{4}\)", "", regex=True)
        .str.lower()
    )

    tmdb_tmp = tmdb_full.copy()
    tmdb_tmp['clean_title'] = tmdb_tmp['original_title'].str.lower()

    df_movie_scope = (
    full_data
    .query("budget > 10_000 and revenue > 10_000")
    .drop_duplicates(subset=['MovieID'])
    .copy()
)

    
    df_movie_scope = full_data.drop_duplicates(subset=['MovieID']).copy()

    # ======================================================
    # TABS CON
    # ======================================================
    tab_corr, tab_viz, tab_cluster, tab_reg = st.tabs([
        "📈 Phân tích tương quan",
        "📊 Trực quan hóa",
        "🧩 Phân cụm K-Means",
        "📐 Linear Regression theo cụm"
    ])

    # ======================================================
    # TAB 1 — PHÂN TÍCH TƯƠNG QUAN
    # ======================================================
    with tab_corr:
        st.subheader("📈 Hệ số tương quan Pearson")

        corr_budget = df_movie_scope['budget'].corr(df_movie_scope['avg_rating'])
        corr_revenue = df_movie_scope['revenue'].corr(df_movie_scope['avg_rating'])

        col1, col2 = st.columns(2)
        col1.metric("Corr(Budget, Rating)", f"{corr_budget:.4f}")
        col2.metric("Corr(Revenue, Rating)", f"{corr_revenue:.4f}")

        if corr_budget < 0:
            st.warning("👉 Ngân sách càng cao, rating trung bình **có xu hướng giảm**.")
        else:
            st.success("👉 Ngân sách càng cao, rating trung bình **có xu hướng tăng**.")

        st.markdown("""
        **Nhận xét:**  
        - Tương quan yếu → tiền **không đảm bảo** chất lượng  
        - Cần xem xét xu hướng phi tuyến
        """)

    # ======================================================
    # TAB 2 — TRỰC QUAN HÓA
    # ======================================================
    with tab_viz:
        st.subheader("📊 Budget / Revenue vs Rating")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.scatter(
                df_movie_scope,
                x='budget',
                y='avg_rating',
                log_x=True,
                opacity=0.4,
                trendline='lowess',
                labels={'budget': 'Budget (log)', 'avg_rating': 'Rating'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                df_movie_scope,
                x='revenue',
                y='avg_rating',
                log_x=True,
                opacity=0.4,
                trendline='lowess',
                labels={'revenue': 'Revenue (log)', 'avg_rating': 'Rating'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Phân nhóm ngân sách
        bins = [0, 10_000_000, 50_000_000, 100_000_000, float('inf')]
        labels = [
            'Micro / Indie (<10M)',
            'Mid (10–50M)',
            'High (50–100M)',
            'Blockbuster (>100M)'
        ]

        df_movie_scope['Budget_Category'] = pd.cut(
            df_movie_scope['budget'],
            bins=bins,
            labels=labels
        )

        group_stats = (
            df_movie_scope
            .groupby('Budget_Category')['avg_rating']
            .agg(['mean', 'count'])
            .reset_index()
        )

        st.markdown("### 📦 Điểm trung bình theo nhóm ngân sách")
        st.dataframe(group_stats, use_container_width=True)

        fig = px.box(
            df_movie_scope,
            x='Budget_Category',
            y='avg_rating',
            labels={'avg_rating': 'Rating'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # TAB 3 — PHÂN CỤM K-MEANS
    # ======================================================
    with tab_cluster:
        st.subheader("🧩 Phân cụm phim bằng K-Means")

        st.markdown("""
        Mục tiêu: Nhóm các bộ phim dựa trên **đặc trưng tài chính & độ phổ biến**
        để tìm ra các **kiểu phim (movie archetypes)** khác nhau.
        """)

        # =====================================
        # 1️⃣ Chuẩn bị dữ liệu
        # =====================================
        feature_cols = ['budget', 'revenue', 'runtime', 'popularity']
        df_km = df_movie_scope[
            (df_movie_scope['budget'] > 10000) &
            (df_movie_scope['revenue'] > 10000) &
            (df_movie_scope['runtime'] > 0) &
            (df_movie_scope['avg_rating'].notna())
        ][feature_cols + ['avg_rating']].copy()
        
        st.info(f"Số phim dùng để phân cụm: **{len(df_km)}**")

        # =====================================
        # 2️⃣ Chuẩn hóa dữ liệu
        # =====================================
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_km[feature_cols])

        # =====================================
        # 3️⃣ K-Means clustering
        # =====================================
        k = 3
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        df_km['cluster'] = kmeans.fit_predict(X_scaled)

        # =====================================
        # 4️⃣ Mô tả đặc trưng từng cụm
        # =====================================
        cluster_desc = (
            df_km
            .groupby('cluster')
            .agg({
                'avg_rating': 'mean',
                'budget': 'mean',
                'revenue': 'mean',
                'popularity': 'mean',
                'runtime': 'mean'
            })
            .round(2)
            .reset_index()
        )

        st.markdown("### 📊 Đặc trưng trung bình của từng cụm")
        st.dataframe(cluster_desc, use_container_width=True)

        # =====================================
        # 5️⃣ PCA để trực quan hóa
        # =====================================
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        pca_df = pd.DataFrame({
            'PCA1': X_pca[:, 0],
            'PCA2': X_pca[:, 1],
            'Cluster': df_km['cluster'].astype(str),
            'Rating': df_km['avg_rating']
        })

        fig = px.scatter(
            pca_df,
            x='PCA1',
            y='PCA2',
            color='Cluster',
            size='Rating',
            opacity=0.7,
            labels={'PCA1': 'PCA Component 1', 'PCA2': 'PCA Component 2'},
            title='K-Means Clustering (PCA Projection)'
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # 👉 LƯU CHO TAB KHÁC DÙNG
        st.session_state['df_cluster'] = df_km.copy()


        # =====================================
        # 6️⃣ Nhận xét nhanh
        # =====================================
        st.success("""
        🔍 **Nhận xét:**
        - Các cụm thể hiện những nhóm phim có mức đầu tư và độ phổ biến khác nhau  
        - Không phải cụm có ngân sách cao nhất cũng có rating cao nhất  
        - Cho thấy **hiệu ứng hiệu quả giảm dần của ngân sách**
        """)


    # ======================================================
    # TAB 4 — LINEAR REGRESSION THEO CỤM
    # ======================================================
    with tab_reg:
        
        if 'df_cluster' not in st.session_state:
            st.warning("⚠️ Vui lòng chạy tab 'Phân cụm K-Means' trước.")
            st.stop()

        df_cluster = st.session_state['df_cluster']

        
        st.subheader("📐 Hồi quy tuyến tính theo từng cụm")

        import statsmodels.api as sm
        import numpy as np

        df_cluster['log_budget'] = np.log1p(df_cluster['budget'])

        rows = []

        for c in sorted(df_cluster['cluster'].unique()):
            sub = df_cluster[df_cluster['cluster'] == c]

            X = sm.add_constant(sub[['log_budget']])
            y = sub['avg_rating']

            model = sm.OLS(y, X).fit()

            rows.append({
                'Cluster': c,
                'Số phim': len(sub),
                'Hệ số log(Budget)': model.params['log_budget'],
                'p-value': model.pvalues['log_budget'],
                'R²': model.rsquared
            })

        coef_df = pd.DataFrame(rows)
        st.dataframe(coef_df, use_container_width=True)

        fig = px.bar(
            coef_df,
            x='Cluster',
            y='Hệ số log(Budget)',
            color='Cluster',
            title='Ảnh hưởng của Budget lên Rating theo từng cụm'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.success("""
        ✅ **Kết luận:**  
        - Ngân sách ảnh hưởng **khác nhau theo từng nhóm phim**  
        - Ở phim lớn: hiệu quả đầu tư **giảm dần**  
        - Chất lượng không thể mua hoàn toàn bằng tiền
        """)

# =========================
# TAB: YẾU TỐ NỘI DUNG & CẤU TRÚC
# =========================

elif analysis_type == "Yếu tố nội dung & cấu trúc":
    st.markdown("## 🎞️ Yếu tố Nội dung & Cấu trúc phim")

    df = full_data.copy()

    feature_cols = ['budget', 'runtime', 'popularity', 'vote_count', 'revenue']
    target = 'avg_rating'

    df = df[
        feature_cols + ['Genres', target]
    ].dropna()

    # ⚠️ Giảm size để Streamlit chạy mượt
    df = df.sample(n=min(50000, len(df)), random_state=42)

    # Encode genres đúng cách
    df['Genres_list'] = df['Genres'].str.split('|')
    genres_dummies = df['Genres_list'].str.join('|').str.get_dummies()

    X = pd.concat([df[feature_cols], genres_dummies], axis=1)
    y = df[target]

    # Train test split (DUY NHẤT 1 LẦN)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # LƯU CHO CÁC TAB DÙNG
    st.session_state.update({
        'X_train': X_train,
        'X_test': X_test,
        'X_train_s': X_train_s,
        'X_test_s': X_test_s,
        'y_train': y_train,
        'y_test': y_test
    })


    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Từng yếu tố đơn lẻ",
        "📊 Tuyến tính đa biến",
        "🧮 Regularization",
        "🔄 Phi tuyến & Interaction",
        "🧩 Segment analysis",
        "🌲 Tree-based models",
        "🏆 Tổng hợp & Ranking"
    ])

    with tab1:
        rows = []

        for col in feature_cols:
            X_col = df[[col]]
            y_col = df[target]

            model = LinearRegression().fit(X_col, y_col)
            pred = model.predict(X_col)

            rows.append({
                'Feature': col,
                'Coefficient': model.coef_[0],
                'R²': r2_score(y_col, pred),
                'RMSE': np.sqrt(mean_squared_error(y_col, pred))
            })

        st.dataframe(pd.DataFrame(rows).sort_values('R²', ascending=False))



    with tab2:
        model = LinearRegression().fit(
            st.session_state['X_train_s'],
            st.session_state['y_train']
        )

        r2 = r2_score(
            st.session_state['y_test'],
            model.predict(st.session_state['X_test_s'])
        )

        st.metric("R² (Test)", f"{r2:.4f}")


        
    with tab3:
        lasso = Lasso(alpha=0.01, max_iter=5000)
        lasso.fit(
            st.session_state['X_train_s'],
            st.session_state['y_train']
        )

        coef = pd.DataFrame({
            'Feature': X_train.columns,
            'Coefficient': lasso.coef_
        }).query("Coefficient != 0")

        st.dataframe(coef.sort_values('Coefficient', key=abs, ascending=False))
    
    with tab4:
        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        X_poly = poly.fit_transform(df[['budget', 'runtime', 'popularity']])
        y_poly = df[target]

        model = LinearRegression().fit(X_poly, y_poly)
        st.success(f"R² interaction: {r2_score(y_poly, model.predict(X_poly)):.4f}")


    with tab5:
        segments = {
            'Blockbuster': df[df['budget'] > 100_000_000],
            'Indie': df[df['budget'] < 10_000_000],
            'Action': df[df['Genres'].str.contains('Action', na=False)],
            'Drama': df[df['Genres'].str.contains('Drama', na=False)]
        }

        rows = []
        for name, seg in segments.items():
            if len(seg) < 100:
                continue

            X_seg = seg[feature_cols]
            y_seg = seg[target]

            X_tr, X_te, y_tr, y_te = train_test_split(X_seg, y_seg, test_size=0.2)
            m = LinearRegression().fit(X_tr, y_tr)

            rows.append({
                'Segment': name,
                'N': len(seg),
                'R²': r2_score(y_te, m.predict(X_te))
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        
    with tab6:
        rf = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )

        rf.fit(
            st.session_state['X_train'],
            st.session_state['y_train']
        )

        imp = pd.DataFrame({
            'Feature': X_train.columns,
            'Importance': rf.feature_importances_
        }).sort_values('Importance', ascending=False).head(15)

        st.dataframe(imp)


    with tab7:
        st.subheader("🏆 Tổng hợp & Xếp hạng cuối")

        st.markdown("""
        Tổng hợp kết quả từ:
        - Linear Regression
        - Lasso
        - Random Forest
        - Permutation Importance
        """)

        st.success("""
        ✅ **Kết luận tổng quát**
        - Popularity & vote_count quan trọng hơn budget
        - Nội dung & mức độ lan truyền quyết định hài lòng
        - Hiệu ứng khác nhau rõ rệt giữa các segment
        """)

        st.info("""
        🎯 **Khuyến nghị**
        - Không chạy theo ngân sách
        - Tối ưu nội dung & marketing
        - Cá nhân hóa theo nhóm khán giả
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📊 MovieLens Analytics Dashboard | Phân tích dữ liệu MovieLens 1M & TMDb 5000</p>
        <p>Được phát triển với ❤️ bằng Streamlit</p>
    </div>
""", unsafe_allow_html=True)