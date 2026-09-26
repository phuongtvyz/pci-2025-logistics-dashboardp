# -*- coding: utf-8 -*-

"""
PCI 2025 - Local Business Environment Dashboard

Nguồn dữ liệu:
    pci_2025_dashboard.csv

Dataset cuối cùng:
    34 địa phương
    9 thành phần PCI đã chuẩn hóa về thang 0-10
    Điểm môi trường kinh doanh tổng hợp
    Xếp hạng
    Ward Cluster
    Silhouette

Mục đích:
    Phân tích và sàng lọc tương đối mức độ thuận lợi
    của môi trường kinh doanh cấp địa phương.

Lưu ý:
    Dashboard KHÔNG phải mô hình tối ưu hóa vị trí kho,
    trung tâm phân phối hoặc fulfillment center.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PCI 2025 - Môi trường kinh doanh",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# 2. TITLE
# ============================================================

st.title(
    "📊 Phân tích môi trường kinh doanh cấp địa phương "
    "theo PCI 2025"
)

st.markdown(
    """
Dashboard hỗ trợ phân tích mức độ thuận lợi của môi trường
kinh doanh tại **34 địa phương** dựa trên **9 thành phần PCI 2025**.

Điểm tổng hợp được sử dụng cho mục đích **đánh giá và sàng lọc tương đối**
giữa các địa phương, không phải mô hình tối ưu hóa vị trí kho,
trung tâm phân phối hoặc trung tâm hoàn tất đơn hàng.
"""
)


# ============================================================
# 3. LOAD DATA (ĐÃ SỬA ĐƯỜNG DẪN TỰ ĐỘNG THEO THƯ MỤC CỦA SCRIPT)
# ============================================================

@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "pci_2025_dashboard.csv")
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    return df


try:
    df = load_data()
except Exception as e:
    st.error("Không thể đọc file `pci_2025_dashboard.csv`.")
    st.code(str(e))
    st.stop()


# ============================================================
# 4. DEFINE COLUMNS
# ============================================================

province_col = "Tỉnh/Thành phố"

pci_cols = [
    "PCI_1: Gia nhập thị trường",
    "PCI_2: Tiếp cận đất đai",
    "PCI_3: Tính minh bạch",
    "PCI_4: Chi phí tuân thủ hành chính",
    "PCI_5: Chi phí không chính thức",
    "PCI_6: Cạnh tranh bình đẳng",
    "PCI_7: Hỗ trợ doanh nghiệp",
    "PCI_8: Thiết chế pháp lý",
    "PCI_9: Chính quyền kiến tạo"
]

score_col = "Điểm môi trường kinh doanh tổng hợp"
rank_col = "Xếp hạng"
cluster_col = "Ward_Cluster"
silhouette_col = "Silhouette"


# ============================================================
# 5. DATA VALIDATION
# ============================================================

required_cols = [
    province_col,
    *pci_cols,
    score_col,
    rank_col,
    cluster_col,
    silhouette_col
]

missing_cols = [
    col for col in required_cols if col not in df.columns
]

if missing_cols:
    st.error("Dataset thiếu các cột bắt buộc:")
    st.write(missing_cols)
    st.write("Các cột hiện có trong dataset:")
    st.write(df.columns.tolist())
    st.stop()


# ============================================================
# 6. BASIC DATA CLEANING
# ============================================================

df = df.copy()

df[province_col] = df[province_col].astype(str).str.strip()
df = df[df[province_col].notna()]
df = df[df[province_col] != ""]
df = df.drop_duplicates(subset=[province_col])

for col in pci_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
df[rank_col] = pd.to_numeric(df[rank_col], errors="coerce")
df[cluster_col] = pd.to_numeric(df[cluster_col], errors="coerce")
df[silhouette_col] = pd.to_numeric(df[silhouette_col], errors="coerce")


# ============================================================
# 7. SIDEBAR
# ============================================================

st.sidebar.header("🔎 Bộ lọc")

province_options = ["Tất cả"] + sorted(df[province_col].unique().tolist())

selected_province = st.sidebar.selectbox(
    "Chọn địa phương",
    province_options
)


# ============================================================
# 8. FILTERED DATA
# ============================================================

if selected_province == "Tất cả":
    df_selected = df.copy()
else:
    df_selected = df[df[province_col] == selected_province].copy()


# ============================================================
# 9. KPI
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Số địa phương", df[province_col].nunique())

with col2:
    st.metric("Điểm cao nhất", f"{df[score_col].max():.2f}")

with col3:
    st.metric("Điểm thấp nhất", f"{df[score_col].min():.2f}")

with col4:
    st.metric("Số nhóm Ward", df[cluster_col].nunique())


# ============================================================
# 10. TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 Xếp hạng",
        "🔎 Phân nhóm",
        "📊 Phân tích PCI",
        "📋 Dữ liệu"
    ]
)

# ============================================================
# TAB 1 — RANKING
# ============================================================

with tab1:
    st.subheader("Xếp hạng môi trường kinh doanh")
    st.caption(
        "Xếp hạng được tính từ điểm môi trường kinh doanh "
        "tổng hợp trên 9 thành phần PCI 2025, "
        "với trọng số bằng nhau."
    )

    ranking_df = (
        df[
            [
                province_col,
                score_col,
                rank_col,
                cluster_col
            ]
        ]
        .sort_values(
            by=[rank_col, score_col],
            ascending=[True, False]
        )
        .copy()
    )

    st.subheader("Top 10 địa phương theo điểm tổng hợp")

    top10 = (
        ranking_df
        .sort_values(by=score_col, ascending=False)
        .head(10)
        .sort_values(by=score_col, ascending=True)
    )

    fig = px.bar(
        top10,
        x=score_col,
        y=province_col,
        orientation="h",
        text=score_col,
        title="Top 10 địa phương"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Điểm môi trường kinh doanh",
        yaxis_title="",
        xaxis=dict(range=[0, 10], dtick=1),
        height=600,
        margin=dict(l=20, r=80, t=70, b=50),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bảng xếp hạng đầy đủ 34 địa phương")

    ranking_table = ranking_df.copy()
    ranking_table.columns = [
        "Tỉnh/Thành phố",
        "Điểm tổng hợp",
        "Xếp hạng",
        "Ward Cluster"
    ]

    st.dataframe(
        ranking_table,
        use_container_width=True,
        hide_index=True,
        height=700
    )

    st.info(
        """
Điểm tổng hợp được xây dựng từ 9 thành phần PCI sau khi
chuẩn hóa về thang 0–10 và sử dụng trọng số bằng nhau.

Điểm cao hơn phản ánh mức độ thuận lợi tương đối cao hơn
trong phạm vi các thành phần PCI được đưa vào mô hình.

Kết quả không phải là mô hình tối ưu hóa vị trí kho hoặc
trung tâm hoàn tất đơn hàng.
"""
    )

# ============================================================
# TAB 2 — CLUSTERING
# ============================================================

with tab2:
    st.subheader("🔎 Phân nhóm địa phương bằng Ward Clustering")

    st.markdown(
        """
Phân cụm được thực hiện trên **9 thành phần PCI đã chuẩn hóa**,
không sử dụng trực tiếp điểm tổng hợp hoặc thứ hạng để tạo cụm.
"""
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Số cụm", int(df[cluster_col].nunique()))

    with c2:
        cluster0_size = int((df[cluster_col] == 0).sum())
        st.metric("Cluster 0", cluster0_size)

    with c3:
        cluster1_size = int((df[cluster_col] == 1).sum())
        st.metric("Cluster 1", cluster1_size)

    with c4:
        st.metric("Silhouette", "0.2905")

    st.info(
        """
**K = 2** được lựa chọn trong phạm vi K = 2–5 được kiểm định,
với hệ số silhouette trung bình = **0.2905**.

Kết quả Ward được kiểm chứng bằng K-Means với
**Adjusted Rand Index (ARI) = 1.0000**.

Silhouette ở mức vừa phải nên kết quả phân cụm được sử dụng
theo hướng **khám phá cấu trúc dữ liệu**, không xem là phân loại
tuyệt đối của các địa phương.
"""
    )

    st.subheader("Hồ sơ trung bình của các cụm")

    cluster_profile = (
        df
        .groupby(cluster_col)[pci_cols]
        .mean()
        .round(2)
    )

    cluster_profile_display = (
        cluster_profile
        .T
        .reset_index()
    )

    cluster_profile_display.columns = [
        "Thành phần PCI",
        "Cluster 0",
        "Cluster 1"
    ]

    st.dataframe(
        cluster_profile_display,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # Heatmap (ĐÃ SỬA LỖI CRASH INDEX INT VÀ SẮP XẾP HÀNG/CỘT)
    # --------------------------------------------------------

    heatmap_df = cluster_profile.T.copy()
    heatmap_df.columns = [f"Cluster {c}" for c in heatmap_df.columns]
    heatmap_df.index = [str(col).replace("PCI_", "") for col in heatmap_df.index]

    fig_heatmap = px.imshow(
        heatmap_df,
        text_auto=".2f",
        aspect="auto",
        title="Hồ sơ 9 thành phần PCI theo cụm",
        labels={
            "x": "Cụm",
            "y": "Thành phần PCI",
            "color": "Điểm"
        }
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("Diễn giải cấu trúc cụm")

    st.markdown(
        """
**Cluster 0** gồm 30 địa phương. Hồ sơ của nhóm này tương đối
cao hơn mức trung bình toàn mẫu ở một số thành phần như
PCI_3, PCI_5, PCI_7 và PCI_9, nhưng vẫn có sự khác biệt giữa
các địa phương trong cùng cụm.

**Cluster 1** gồm 4 địa phương. Nhóm này có một hồ sơ khá khác
biệt: PCI_8 có giá trị trung bình cao, trong khi PCI_3, PCI_5,
PCI_7 và PCI_9 thấp hơn đáng kể so với Cluster 0.

Do Cluster 1 chỉ gồm 4 địa phương và một số quan sát có
Silhouette thấp, kết quả nên được xem là một **cấu trúc phân nhóm
mang tính khám phá**, thay vì kết luận rằng một nhóm tốt hoặc xấu
hơn tuyệt đối.
"""
    )

    selected_cluster = st.selectbox(
        "Chọn cụm để xem các địa phương",
        sorted(df[cluster_col].dropna().unique())
    )

    cluster_members = (
        df[df[cluster_col] == selected_cluster]
        [[
            province_col,
            score_col,
            rank_col,
            silhouette_col
        ]]
        .sort_values(by=score_col, ascending=False)
        .copy()
    )

    st.subheader(f"Địa phương thuộc Cluster {selected_cluster}")

    st.dataframe(
        cluster_members,
        use_container_width=True,
        hide_index=True
    )

    if selected_cluster == 1:
        st.warning(
            """
Trong Cluster 1, **Vĩnh Long có Silhouette = 0.0195**,
cho thấy quan sát này nằm rất gần ranh giới giữa các cụm.
Do đó cần thận trọng khi diễn giải cấu trúc Cluster 1.
"""
        )

# ============================================================
# TAB 3 — PCI ANALYSIS
# ============================================================

with tab3:
    st.subheader("📊 Phân tích 9 thành phần PCI")

    st.markdown(
        """
Các biến PCI trong dataset đã được chuẩn hóa về thang điểm
**0–10** bằng MinMaxScaler trong bước xử lý dữ liệu.
"""
    )

    selected_pci = st.selectbox("Chọn thành phần PCI", pci_cols)

    pci_df = (
        df[[province_col, selected_pci]]
        .sort_values(by=selected_pci, ascending=True)
        .copy()
    )

    fig_pci = px.bar(
        pci_df,
        x=selected_pci,
        y=province_col,
        orientation="h",
        text=selected_pci,
        title=selected_pci
    )

    fig_pci.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_pci.update_layout(
        xaxis_title="Điểm chuẩn hóa (0–10)",
        yaxis_title="",
        xaxis=dict(range=[0, 10], dtick=1),
        height=1000,
        margin=dict(l=20, r=80, t=70, b=50),
        showlegend=False
    )

    st.plotly_chart(fig_pci, use_container_width=True)

    st.subheader("Thống kê mô tả")

    stats_df = df[pci_cols].describe().T.round(2).reset_index()
    stats_df = stats_df.rename(columns={"index": "Thành phần PCI"})

    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Ma trận tương quan giữa 9 thành phần PCI")

    corr_matrix = df[pci_cols].corr().round(2)

    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Tương quan Pearson giữa các thành phần PCI",
        labels={"color": "Hệ số tương quan"}
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    st.caption(
        """
Tương quan Pearson mô tả mức độ liên hệ tuyến tính giữa các
thành phần PCI trong mẫu 34 địa phương; không nên diễn giải
thành quan hệ nhân quả.
"""
    )

# ============================================================
# TAB 4 — DATA
# ============================================================

with tab4:
    st.subheader("📋 Dataset phân tích")

    st.write(
        f"""
Dataset hiện tại gồm **{len(df)} địa phương**,
**{len(pci_cols)} thành phần PCI** và các biến kết quả
gồm điểm tổng hợp, xếp hạng, Ward Cluster và Silhouette.
"""
    )

    search_text = st.text_input(
        "Tìm kiếm địa phương",
        placeholder="Nhập tên địa phương..."
    )

    if search_text:
        data_display = df[
            df[province_col].str.contains(search_text, case=False, na=False)
        ].copy()
    else:
        data_display = df.copy()

    st.dataframe(
        data_display,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Kiểm tra chất lượng dữ liệu")

    validation_col1, validation_col2, validation_col3 = st.columns(3)

    with validation_col1:
        st.metric("Số dòng", len(df))

    with validation_col2:
        st.metric("Địa phương duy nhất", df[province_col].nunique())

    with validation_col3:
        missing_values = int(df[required_cols].isna().sum().sum())
        st.metric("Missing values", missing_values)

# ============================================================
# 11. FOOTER
# ============================================================

st.divider()

st.caption(
    """
PCI 2025 Local Business Environment Dashboard |
Phân tích dữ liệu bằng Python / PySpark và trực quan hóa bằng Streamlit.
"""
)

# Thêm Biểu đồ Radar so sánh 2 địa phương trong Tab Phân tích
import plotly.graph_objects as go

st.subheader("⚔️ So sánh hồ sơ 9 thành phần PCI giữa hai địa phương (Radar Chart)")
col_prov1, col_prov2 = st.columns(2)
with col_prov1:
    prov1 = st.selectbox("Chọn địa phương 1", df[province_col].unique(), index=0)
with col_prov2:
    prov2 = st.selectbox("Chọn địa phương 2", df[province_col].unique(), index=1)

v1 = df[df[province_col] == prov1][pci_cols].values.flatten()
v2 = df[df[province_col] == prov2][pci_cols].values.flatten()
categories = [c.replace("PCI_", "") for c in pci_cols]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(r=v1, theta=categories, fill='toself', name=prov1))
fig_radar.add_trace(go.Scatterpolar(r=v2, theta=categories, fill='toself', name=prov2))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
    showlegend=True,
    title=f"So sánh năng lực PCI: {prov1} vs {prov2}"
)
st.plotly_chart(fig_radar, use_container_width=True)

