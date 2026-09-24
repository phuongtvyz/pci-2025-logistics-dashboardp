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
    "Phân tích môi trường kinh doanh cấp địa phương "
    "theo PCI 2025"
)

st.markdown(
    """
    Dashboard hỗ trợ phân tích mức độ thuận lợi của môi trường
    kinh doanh tại 34 địa phương dựa trên 9 thành phần PCI 2025.

    **Lưu ý:** Điểm tổng hợp được sử dụng cho mục đích đánh giá
    và sàng lọc tương đối, không phải mô hình tối ưu hóa vị trí
    kho hoặc trung tâm hoàn tất đơn hàng.
    """
)


# ============================================================
# 3. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "pci_2025_dashboard.csv",
        encoding="utf-8-sig"
    )

    return df


df = load_data()


# ============================================================
# 4. DEFINE PCI COLUMNS
# ============================================================

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
# 5. SIDEBAR
# ============================================================

st.sidebar.header("Bộ lọc")

selected_province = st.sidebar.selectbox(
    "Chọn địa phương",
    ["Tất cả"] + sorted(
        df["Tỉnh/Thành phố"].tolist()
    )
)


# ============================================================
# 6. FILTER
# ============================================================

if selected_province == "Tất cả":

    df_display = df.copy()

else:

    df_display = df[
        df["Tỉnh/Thành phố"] == selected_province
    ].copy()


# ============================================================
# 7. KPI
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Số địa phương",
    df["Tỉnh/Thành phố"].nunique()
)

col2.metric(
    "Điểm cao nhất",
    f"{df[score_col].max():.2f}"
)

col3.metric(
    "Điểm thấp nhất",
    f"{df[score_col].min():.2f}"
)

col4.metric(
    "Số nhóm Ward",
    df[cluster_col].nunique()
)


# ============================================================
# 8. TABS
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

    st.subheader(
        "Xếp hạng môi trường kinh doanh"
    )

    st.caption(
        "Xếp hạng được tính từ điểm môi trường kinh doanh tổng hợp "
        "trên 9 thành phần PCI 2025, với trọng số bằng nhau."
    )

# --------------------------------------------------------
# 1. Chuẩn bị dữ liệu xếp hạng
# --------------------------------------------------------

ranking_df = (
    df[
        [
            "Tỉnh/Thành phố",
            score_col,
            rank_col,
            cluster_col
        ]
    ]
    .sort_values(
        by=score_col,
        ascending=False
    )
    .copy()
)

# Đảo thứ tự để điểm cao nhất nằm trên cùng
ranking_plot_df = ranking_df.iloc[::-1].copy()

# --------------------------------------------------------
# 2. Biểu đồ xếp hạng
# --------------------------------------------------------

fig = px.bar(
    ranking_plot_df,
    x=score_col,
    y="Tỉnh/Thành phố",
    orientation="h",
    text=score_col,
    title="Điểm môi trường kinh doanh tổng hợp"
)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    xaxis_title="Điểm môi trường kinh doanh",
    yaxis_title="",

    xaxis=dict(
        range=[0, 10],
        dtick=1
    ),

    height=1200,

    margin=dict(
        l=20,
        r=80,
        t=70,
        b=50
    ),

    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

    # --------------------------------------------------------
    # 3. Cấu hình trục và giao diện biểu đồ
    # --------------------------------------------------------

    fig.update_layout(
        xaxis_title="Điểm môi trường kinh doanh",
        yaxis_title="",
        xaxis=dict(
            range=[
                0,
                max(10, ranking_df[score_col].max() + 1)
            ],
            dtick=1
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=ranking_df[
                "Tỉnh/Thành phố"
            ].tolist()
        ),
        height=900,
        margin=dict(
            l=20,
            r=80,
            t=70,
            b=50
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # 4. Bảng xếp hạng
    # --------------------------------------------------------

    st.subheader("Bảng xếp hạng")

    ranking_table = (
        df[
            [
                "Tỉnh/Thành phố",
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

    ranking_table.columns = [
        "Tỉnh/Thành phố",
        "Điểm tổng hợp",
        "Xếp hạng",
        "Ward Cluster"
    ]

    st.dataframe(
        ranking_table,
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# TAB 2 — CLUSTERING
# ============================================================

with tab2:

    st.subheader(
        "Phân nhóm địa phương bằng Ward Clustering"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Số cụm",
        df[cluster_col].nunique()
    )

    col2.metric(
        "Cluster 0",
        len(df[df[cluster_col] == 0])
    )

    col3.metric(
        "Cluster 1",
        len(df[df[cluster_col] == 1])
    )

    st.info(
        """
        K = 2 được lựa chọn trong số các giá trị K = 2–5
        được kiểm định, với silhouette trung bình = 0.2905.
        Kết quả Ward được kiểm chứng bằng K-Means với
        ARI = 1.0000.
        """
    )

    cluster_mean = (
        df.groupby(cluster_col)[pci_cols]
        .mean()
        .reset_index()
    )

    st.dataframe(
        cluster_mean,
        use_container_width=True,
        hide_index=True
    )

    selected_cluster = st.selectbox(
        "Chọn nhóm để xem địa phương",
        sorted(df[cluster_col].unique())
    )

    cluster_members = df[
        df[cluster_col] == selected_cluster
    ].sort_values(
        by=score_col,
        ascending=False
    )

    st.dataframe(
        cluster_members[
            [
                "Tỉnh/Thành phố",
                score_col,
                rank_col,
                silhouette_col
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 3 — PCI ANALYSIS
# ============================================================

with tab3:

    st.subheader(
        "Phân tích 9 thành phần PCI"
    )

    selected_pci = st.selectbox(
        "Chọn thành phần PCI",
        pci_cols
    )

    pci_df = df[
        [
            "Tỉnh/Thành phố",
            selected_pci
        ]
    ].sort_values(
        by=selected_pci,
        ascending=False
    )

    fig = px.bar(
        pci_df,
        x=selected_pci,
        y="Tỉnh/Thành phố",
        orientation="h",
        title=selected_pci
    )

    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 4 — DATA
# ============================================================

with tab4:

    st.subheader(
        "Dataset phân tích"
    )

    st.write(
        f"Dữ liệu gồm {len(df)} địa phương "
        f"và {len(pci_cols)} thành phần PCI."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
