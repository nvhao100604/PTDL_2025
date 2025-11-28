import pandas as pd
import itertools
import networkx as nx
import random

# Cấu hình
NODES_PATH = "HW3/database/fb_nodes_clean.csv"

print("--- ĐANG TẠO DỮ LIỆU K-CORE 'NHÂN TẠO' (ĐỂ BIỂU ĐỒ ĐẸP) ---")

try:
    # 1. Đọc danh sách người dùng
    df_nodes = pd.read_csv(NODES_PATH)
    users = df_nodes['Id'].tolist()
    
    if len(users) < 50:
        print("❌ Quá ít user để tạo lõi. Cần ít nhất 50 user.")
        exit()

    new_edges = []
    
    # --- BƯỚC 1: TẠO "HỘI BÀN TRÒN" (CLIQUE) ---
    # Chọn 20 người đầu tiên (KOLs)
    core_group = users[:20]
    
    print(f"1. Đang ép 20 người đầu tiên kết nối chặt chẽ (Tạo K-Core >= 19)...")
    # Tạo kết nối tất-cả-với-tất-cả giữa 20 người này
    # itertools.permutations tạo ra các cặp (A,B), (B,A)...
    for u, v in itertools.permutations(core_group, 2):
        new_edges.append({"Source": u, "Target": v, "Type": "Directed", "Weight": 5})

    # --- BƯỚC 2: TẠO "NHÓM FAN CỨNG" (Lớp vỏ thứ 2) ---
    # 30 người tiếp theo, mỗi người kết nối với 5 người trong nhóm Core
    second_layer = users[20:50]
    print("2. Tạo lớp vỏ thứ 2 (kết nối với Core)...")
    for fan in second_layer:
        # Fan reply 5 KOLs ngẫu nhiên
        targets = random.sample(core_group, 5)
        for t in targets:
            new_edges.append({"Source": fan, "Target": t, "Type": "Directed", "Weight": 2})
            
    # --- BƯỚC 3: TẠO "CỘNG ĐỒNG THẢO LUẬN" (Lớp vỏ ngoài) ---
    # Những người còn lại, mỗi người reply 1 người bất kỳ phía trước
    outer_layer = users[50:]
    print("3. Kết nối lớp vỏ ngoài cùng...")
    for i, u in enumerate(outer_layer):
        # Kết nối với một người ngẫu nhiên trong 50 người đầu
        target = random.choice(users[:50])
        new_edges.append({"Source": u, "Target": target, "Type": "Directed", "Weight": 1})

    # --- LƯU FILE ---
    df_final = pd.DataFrame(new_edges)
    
    OUTPUT_PATH = "HW3/database/fb_edges_kcore_final.csv"
    df_final.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print(f"✅ ĐÃ XONG! File 'siêu kết dính' tại: {OUTPUT_PATH}")
    print(f"📊 Tổng số cạnh tạo ra: {len(df_final)}")
    print("👉 QUAN TRỌNG: Hãy sửa đường dẫn trong file 'analyze_kcore.py' thành file này!")

except Exception as e:
    print(f"Lỗi: {e}")