import pandas as pd
import numpy as np

# --- 1. ĐỌC BỘ DỮ LIỆU MOVIELENS 1M ---

# Định nghĩa tên cột cho các file .dat (theo tài liệu README của MovieLens)
u_cols = ['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code']
m_cols = ['MovieID', 'Title', 'Genres']
r_cols = ['UserID', 'MovieID', 'Rating', 'Timestamp']

# Đọc file users.dat
# engine='python' là bắt buộc khi dùng separator nhiều ký tự (::)
users = pd.read_csv('MovieLens/datasets/movie_len_1M/users.dat', sep='::', names=u_cols, encoding='latin-1', engine='python')

# Đọc file movies.dat
movies = pd.read_csv('MovieLens/datasets/movie_len_1M/movies.dat', sep='::', names=m_cols, encoding='latin-1', engine='python')

# Đọc file ratings.dat
ratings = pd.read_csv('MovieLens/datasets/movie_len_1M/ratings.dat', sep='::', names=r_cols, encoding='latin-1', engine='python')

print("--- Đã tải xong MovieLens 1M ---")
print(f"Users shape: {users.shape}")
print(f"Movies shape: {movies.shape}")
print(f"Ratings shape: {ratings.shape}")
print("-" * 30)

# --- 2. ĐỌC BỘ DỮ LIỆU TMDB 5000 ---

# Đọc file tmdb_5000_credits.csv (File này dùng dấu phẩy ',' chuẩn nên đọc bình thường)
tmdb_credits = pd.read_csv('MovieLens/datasets/tmdb_5000_credits.csv', encoding='latin-1')

print("--- Đã tải xong TMDB 5000 Credits ---")
print(f"TMDB Credits shape: {tmdb_credits.shape}")

# --- 3. HIỂN THỊ DỮ LIỆU MẪU ĐỂ KIỂM TRA ---

print("\n--- Sample Users ---")
users.head(3)

print("\n--- Sample Movies ---")
movies.head(3)

print("\n--- Sample Ratings ---")
ratings.head(3)

print("\n--- Sample TMDB Credits ---")
tmdb_credits.head(3)
