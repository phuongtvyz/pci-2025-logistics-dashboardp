import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PCI 2025 – Môi trường kinh doanh",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. BASIC UI
# ============================================================

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
    }

    .method-note {
        padding: 12px 16px;
        border-left: 4px solid #1f77b4;
        background-color: #f7f9fc;
        margin: 10px 0;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. DATA LOADING
# ============================================================

DATA_FILE = "pci_2025_dashboard.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig"
    )
    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        f"Không tìm thấy file `{DATA_FILE}`. "
        "Hãy kiểm tra file CSV có nằm cùng thư mục với app.py hay không."
    )
    st.stop()

except Exception as e:
    st.error(f"Không thể đọc dữ liệu: {e}")
    st.stop()


# ============================================================
# 4. COLUMN DEFINITIONS
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


required_cols = [
    province_col,
    *pci_cols,
    score_col,
    rank_col,
    cluster_col,
    silhouette_col
]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if missing_cols:
    st.error(
        "Dataset thiếu các cột bắt buộc:\n\n"
        + "\n".join(f"- {c}" for c in missing_cols)
    )
    st.stop()


# ============================================================
# 5. DATA VALIDATION
# ============================================================

# Ép kiểu số cho các cột phân tích
for col in pci_cols + [
    score_col,
    rank_col,
    cluster_col,
    silhouette_col
]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Kiểm tra dữ liệu
data_quality = {
    "Số dòng": len(df),
    "Số địa phương": df[province_col].nunique(),
    "Missing values": int(df[required_cols].isna().sum().sum()),
    "Duplicate địa phương": int(
        df[province_col].duplicated().sum()
    ),
    "Số cluster": df[cluster_col].nunique()
}


# ============================================================
# 6. SIDEBAR
# ============================================================

st.sidebar.header("🔎 Bộ lọc")

selected_province = st.sidebar.selectbox(
    "Chọn địa phương",
    ["Tất cả"] + sorted(
        df[province_col].dropna().unique().tolist()
    )
)

st.sidebar.markdown("---")

st.sidebar.subheader("📌 Thông tin dữ liệu")

st.sidebar.write(
    f"**Số địa phương:** {data_quality['Số địa phương']}"
)

st.sidebar.write(
    f"**Số thành phần PCI:** {len(pci_cols)}"
)

st.sidebar.write(
    f"**Số cluster:** {data_quality['Số cluster']}"
)

st.sidebar.write(
    f"**Missing values:** {data_quality['Missing values']}"
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    **Phạm vi phân tích**

    Dashboard sử dụng 9 thành phần PCI 2025
    để đánh giá và so sánh tương đối môi trường
    kinh doanh giữa các địa phương.

    Kết quả không phải là mô hình tối ưu hóa
    vị trí kho hoặc trung tâm hoàn tất đơn hàng.
    """
)


# ============================================================
# 7. HEADER
# ============================================================

st.title(
    "📊 Phân tích môi trường kinh doanh cấp địa phương theo PCI 2025"
)

st.caption(
    "Dashboard hỗ trợ đánh giá, so sánh và phân tích khám phá "
    "34 địa phương dựa trên 9 thành phần PCI 2025."
)


# ============================================================
# 8. KPI
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Số địa phương",
        f"{df[province_col].nunique()}"
    )

with kpi2:
    st.metric(
        "Điểm cao nhất",
        f"{df[score_col].max():.2f}"
    )

with kpi3:
    st.metric(
        "Điểm thấp nhất",
        f"{df[score_col].min():.2f}"
    )

with kpi4:
    st.metric(
        "Số nhóm Ward",
        f"{df[cluster_col].nunique()}"
    )


# ============================================================
# 9. TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏆 Xếp hạng",
        "🧩 Phân nhóm",
        "📈 Phân tích PCI",
        "⚙️ Kịch bản",
        "💾 Dữ liệu"
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
        "Điểm tổng hợp được tính từ 9 thành phần PCI "
        "sau chuẩn hóa về thang 0–10, với trọng số bằng nhau."
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

    # --------------------------------------------------------
    # TOP 10
    # --------------------------------------------------------

    st.subheader(
        "Top 10 địa phương theo điểm tổng hợp"
    )

    top10 = (
        ranking_df
        .sort_values(
            by=score_col,
            ascending=False
        )
        .head(10)
        .sort_values(
            by=score_col,
            ascending=True
        )
    )

    fig_top10 = px.bar(
        top10,
        x=score_col,
        y=province_col,
        orientation="h",
        text=score_col,
        title="Top 10 địa phương"
    )

    fig_top10.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_top10.update_layout(
        xaxis_title="Điểm môi trường kinh doanh",
        yaxis_title="",
        xaxis=dict(
            range=[0, 10],
            dtick=1
        ),
        height=600,
        margin=dict(
            l=20,
            r=80,
            t=70,
            b=50
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig_top10,
        use_container_width=True
    )

    # --------------------------------------------------------
    # FULL RANKING TABLE
    # --------------------------------------------------------

    st.subheader(
        "Bảng xếp hạng đầy đủ 34 địa phương"
    )

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
        height=650
    )

    st.info(
        """
        **Lưu ý phương pháp**

        Điểm tổng hợp được xây dựng từ 9 thành phần PCI
        sau khi chuẩn hóa về thang 0–10 và sử dụng
        trọng số bằng nhau.

        Điểm cao hơn phản ánh mức độ thuận lợi tương đối
        cao hơn trong phạm vi các khía cạnh môi trường
        kinh doanh được đại diện bởi 9 thành phần PCI.

        Kết quả không phải là mô hình tối ưu hóa vị trí
        kho hoặc trung tâm hoàn tất đơn hàng.
        """
    )


# ============================================================
# TAB 2 — CLUSTERING
# ============================================================

with tab2:

    st.subheader(
        "🧩 Phân nhóm địa phương"
    )

    # --------------------------------------------------------
    # CLUSTER METRICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Số cụm",
            "2"
        )

    with c2:
        st.metric(
            "Silhouette",
            "0.2905"
        )

    with c3:
        st.metric(
            "ARI Ward – K-Means",
            "1.0000"
        )

    st.info(
        """
        K=2 được lựa chọn vì đạt Silhouette cao nhất
        trong phạm vi K=2 đến K=5 được kiểm định.

        ARI = 1.0000 cho thấy Ward và K-Means tạo ra
        cùng một phân hoạch dữ liệu sau khi loại bỏ
        ảnh hưởng của việc gán nhãn cụm.

        Tuy nhiên, Silhouette = 0.2905 cho thấy mức độ
        phân tách giữa các cụm còn tương đối hạn chế.
        Vì vậy, kết quả được sử dụng cho mục đích
        khám phá cấu trúc dữ liệu.
        """
    )

    # --------------------------------------------------------
    # CLUSTER PROFILE
    # --------------------------------------------------------

    cluster_profile = (
        df
        .groupby(cluster_col)[pci_cols]
        .mean()
        .round(2)
    )

    st.subheader(
        "Hồ sơ trung bình của các cụm"
    )

    profile_display = cluster_profile.T.copy()

    profile_display.columns = [
        f"Cluster {c}"
        for c in profile_display.columns
    ]

    profile_display.index = [
        c.split(":")[0]
        for c in profile_display.index
    ]

    st.dataframe(
        profile_display,
        use_container_width=True
    )

    # --------------------------------------------------------
    # HEATMAP
    # --------------------------------------------------------

    heatmap_df = cluster_profile.copy()

    heatmap_df.columns = [
        f"Cluster {c}"
        for c in heatmap_df.columns
    ]

    heatmap_df.index = [
        c.split(":")[0]
        for c in heatmap_df.index
    ]

    fig_heatmap = px.imshow(
        heatmap_df.T,
        text_auto=".2f",
        aspect="auto",
        title="Hồ sơ PCI trung bình theo Cluster",
        labels={
            "x": "Thành phần PCI",
            "y": "Cluster",
            "color": "Điểm"
        }
    )

    fig_heatmap.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CLUSTER SIZE
    # --------------------------------------------------------

    st.subheader(
        "Quy mô các cụm"
    )

    cluster_size = (
        df[cluster_col]
        .value_counts()
        .sort_index()
        .rename_axis("Cluster")
        .reset_index(name="Số địa phương")
    )

    fig_cluster_size = px.bar(
        cluster_size,
        x="Cluster",
        y="Số địa phương",
        text="Số địa phương",
        title="Số lượng địa phương theo Cluster"
    )

    fig_cluster_size.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_cluster_size,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CLUSTER MEMBER
    # --------------------------------------------------------

    st.subheader(
        "Danh sách địa phương theo Cluster"
    )

    selected_cluster = st.selectbox(
        "Chọn Cluster",
        sorted(
            df[cluster_col]
            .dropna()
            .unique()
            .tolist()
        )
    )

    cluster_members = (
        df[
            df[cluster_col] == selected_cluster
        ][
            [
                province_col,
                score_col,
                rank_col,
                silhouette_col
            ]
        ]
        .sort_values(
            by=silhouette_col,
            ascending=True
        )
        .copy()
    )

    cluster_members.columns = [
        "Tỉnh/Thành phố",
        "Điểm tổng hợp",
        "Xếp hạng",
        "Silhouette"
    ]

    st.dataframe(
        cluster_members,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # VĨNH LONG WARNING
    # --------------------------------------------------------

    if (
        selected_cluster == 1
        and "Vĩnh Long" in cluster_members[
            "Tỉnh/Thành phố"
        ].values
    ):
        st.warning(
            """
            **Lưu ý về Vĩnh Long:**

            Vĩnh Long có Silhouette = 0.0195,
            rất gần 0, cho thấy quan sát này nằm gần
            ranh giới giữa các cụm.

            Do đó không nên diễn giải kết quả phân nhóm
            như một phân loại tuyệt đối.
            """
        )


# ============================================================
# TAB 3 — INTERACTIVE PCI ANALYTICS
# ============================================================

with tab3:

    st.subheader(
        "📈 Phân tích tương tác 9 thành phần PCI"
    )

    # ========================================================
    # 3.1 RADAR CHART
    # ========================================================

    st.markdown(
        "### ⚔️ So sánh hồ sơ PCI giữa hai địa phương"
    )

    col_prov1, col_prov2 = st.columns(2)

    province_options = sorted(
        df[province_col]
        .dropna()
        .unique()
        .tolist()
    )

    with col_prov1:
        prov1 = st.selectbox(
            "Địa phương 1",
            province_options,
            index=(
                province_options.index("Đà Nẵng")
                if "Đà Nẵng" in province_options
                else 0
            )
        )

    with col_prov2:
        default_index_2 = (
            province_options.index("TP. Hồ Chí Minh")
            if "TP. Hồ Chí Minh" in province_options
            else min(1, len(province_options) - 1)
        )

        prov2 = st.selectbox(
            "Địa phương 2",
            province_options,
            index=default_index_2
        )

    v1 = (
        df[
            df[province_col] == prov1
        ][pci_cols]
        .iloc[0]
        .values
    )

    v2 = (
        df[
            df[province_col] == prov2
        ][pci_cols]
        .iloc[0]
        .values
    )

    categories = [
        c.split(":")[0]
        for c in pci_cols
    ]

    categories_closed = categories + [categories[0]]

    v1_closed = list(v1) + [v1[0]]
    v2_closed = list(v2) + [v2[0]]

    fig_radar = go.Figure()

    fig_radar.add_trace(
        go.Scatterpolar(
            r=v1_closed,
            theta=categories_closed,
            fill="toself",
            name=prov1
        )
    )

    fig_radar.add_trace(
        go.Scatterpolar(
            r=v2_closed,
            theta=categories_closed,
            fill="toself",
            name=prov2
        )
    )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                dtick=2
            )
        ),
        showlegend=True,
        title=f"So sánh hồ sơ PCI: {prov1} vs {prov2}",
        height=650
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

    st.caption(
        "Radar chart dùng để so sánh tương đối hồ sơ 9 thành phần "
        "PCI giữa hai địa phương; không dùng để xác định quan hệ nhân quả."
    )

    st.markdown("---")

    # ========================================================
    # 3.2 SCATTER PLOT
    # ========================================================

    st.markdown(
        "### 📌 Mối quan hệ giữa hai thành phần PCI"
    )

    col_x, col_y = st.columns(2)

    with col_x:
        x_axis = st.selectbox(
            "Trục X",
            pci_cols,
            index=4
        )

    with col_y:
        y_axis = st.selectbox(
            "Trục Y",
            pci_cols,
            index=8
        )

    fig_scatter = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color=cluster_col,
        hover_name=province_col,
        hover_data={
            score_col: ":.2f",
            rank_col: True,
            silhouette_col: ":.4f"
        },
        title=(
            f"Mối quan hệ giữa "
            f"{x_axis.split(':')[0]} và "
            f"{y_axis.split(':')[0]}"
        )
    )

    fig_scatter.update_layout(
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        height=600
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    st.caption(
        "Scatter plot mô tả sự phân bố và mối liên hệ tuyến tính "
        "giữa hai thành phần PCI được lựa chọn. "
        "Tương quan không được diễn giải là quan hệ nhân quả."
    )

    st.markdown("---")

    # ========================================================
    # 3.3 CORRELATION MATRIX
    # ========================================================

    st.markdown(
        "### 🔗 Ma trận tương quan Pearson"
    )

    corr = df[pci_cols].corr()

    corr_display = corr.copy()

    corr_display.index = [
        c.split(":")[0]
        for c in corr_display.index
    ]

    corr_display.columns = [
        c.split(":")[0]
        for c in corr_display.columns
    ]

    fig_corr = px.imshow(
        corr_display,
        text_auto=".2f",
        aspect="auto",
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        title="Tương quan Pearson giữa 9 thành phần PCI"
    )

    fig_corr.update_layout(
        height=650
    )

    st.plotly_chart(
        fig_corr,
        use_container_width=True
    )

    st.info(
        """
        Ma trận Pearson phản ánh mức độ liên hệ tuyến tính
        giữa các thành phần PCI trong mẫu 34 địa phương.

        Đây là phân tích mô tả/khám phá và không cho phép
        suy luận quan hệ nhân quả.
        """
    )

    # ========================================================
    # 3.4 DESCRIPTIVE STATISTICS
    # ========================================================

    st.markdown(
        "### 📊 Thống kê mô tả"
    )

    descriptive = (
        df[pci_cols]
        .describe()
        .T[
            [
                "mean",
                "std",
                "min",
                "max"
            ]
        ]
        .round(2)
    )

    descriptive.index = [
        c.split(":")[0]
        for c in descriptive.index
    ]

    descriptive.columns = [
        "Mean",
        "Std",
        "Min",
        "Max"
    ]

    st.dataframe(
        descriptive,
        use_container_width=True
    )


# ============================================================
# TAB 4 — WHAT-IF WEIGHTING
# ============================================================

with tab4:

    st.subheader(
        "⚙️ Phân tích kịch bản trọng số What-if"
    )

    st.info(
        """
        **Mục đích:** mô phỏng độ nhạy của điểm tổng hợp
        và thứ hạng khi thay đổi trọng số của 9 thành phần PCI.

        Trọng số mặc định bằng nhau và không được xem là
        trọng số tối ưu. Các kịch bản do người dùng thiết lập
        chỉ mang tính phân tích độ nhạy.
        """
    )

    st.markdown(
        "### 1. Thiết lập trọng số"
    )

    weights = {}

    slider_cols = st.columns(3)

    for idx, col_name in enumerate(pci_cols):

        short_name = col_name.split(":")[0]

        with slider_cols[idx % 3]:

            weights[col_name] = st.slider(
                short_name,
                min_value=0.0,
                max_value=3.0,
                value=1.0,
                step=0.1,
                key=f"weight_{idx}"
            )

    total_weight = sum(weights.values())

    if total_weight == 0:

        st.error(
            "Tổng trọng số phải lớn hơn 0."
        )

        st.stop()

    # --------------------------------------------------------
    # CUSTOM SCORE
    # --------------------------------------------------------

    weighted_score = sum(
        df[col] * weights[col]
        for col in pci_cols
    ) / total_weight

    df_custom = df.copy()

    df_custom["Điểm kịch bản"] = (
        weighted_score.round(2)
    )

    df_custom["Xếp hạng kịch bản"] = (
        df_custom["Điểm kịch bản"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    # --------------------------------------------------------
    # SCORE COMPARISON
    # --------------------------------------------------------

    st.markdown(
        "### 2. Kết quả kịch bản"
    )

    scenario_min = df_custom[
        "Điểm kịch bản"
    ].min()

    scenario_max = df_custom[
        "Điểm kịch bản"
    ].max()

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Tổng trọng số",
            f"{total_weight:.1f}"
        )

    with s2:
        st.metric(
            "Điểm cao nhất",
            f"{scenario_max:.2f}"
        )

    with s3:
        st.metric(
            "Điểm thấp nhất",
            f"{scenario_min:.2f}"
        )

    scenario_table = (
        df_custom[
            [
                province_col,
                "Điểm kịch bản",
                "Xếp hạng kịch bản",
                score_col,
                rank_col,
                cluster_col
            ]
        ]
        .sort_values(
            by=[
                "Xếp hạng kịch bản",
                "Điểm kịch bản"
            ],
            ascending=[
                True,
                False
            ]
        )
    )

    st.dataframe(
        scenario_table,
        use_container_width=True,
        hide_index=True,
        height=650
    )

    # --------------------------------------------------------
    # RANK CHANGE
    # --------------------------------------------------------

    st.markdown(
        "### 3. Thay đổi thứ hạng so với kịch bản cơ sở"
    )

    df_change = df_custom[
        [
            province_col,
            rank_col,
            "Xếp hạng kịch bản",
            score_col,
            "Điểm kịch bản"
        ]
    ].copy()

    df_change["Thay đổi thứ hạng"] = (
        df_change[rank_col]
        - df_change["Xếp hạng kịch bản"]
    )

    df_change = df_change.sort_values(
        by="Thay đổi thứ hạng",
        ascending=False
    )

    df_change.columns = [
        "Tỉnh/Thành phố",
        "Hạng cơ sở",
        "Hạng kịch bản",
        "Điểm cơ sở",
        "Điểm kịch bản",
        "Thay đổi thứ hạng"
    ]

    st.dataframe(
        df_change,
        use_container_width=True,
        hide_index=True,
        height=550
    )

    st.caption(
        """
        Giá trị dương trong “Thay đổi thứ hạng” cho biết
        địa phương cải thiện vị trí trong kịch bản;
        giá trị âm cho biết thứ hạng giảm.

        Đây là phân tích độ nhạy theo giả định trọng số,
        không phải kết quả của một mô hình tối ưu hóa.
        """
    )


# ============================================================
# TAB 5 — DATA & EXPORT
# ============================================================

with tab5:

    st.subheader(
        "💾 Dữ liệu và kiểm tra chất lượng"
    )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    st.markdown(
        "### Kiểm tra dữ liệu"
    )

    quality_table = pd.DataFrame(
        {
            "Tiêu chí": [
                "Số dòng",
                "Số địa phương duy nhất",
                "Missing values",
                "Địa phương trùng lặp",
                "Số thành phần PCI",
                "Số Cluster"
            ],
            "Kết quả": [
                len(df),
                df[province_col].nunique(),
                int(
                    df[required_cols]
                    .isna()
                    .sum()
                    .sum()
                ),
                int(
                    df[province_col]
                    .duplicated()
                    .sum()
                ),
                len(pci_cols),
                df[cluster_col].nunique()
            ]
        }
    )

    st.dataframe(
        quality_table,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    st.markdown(
        "### Dataset"
    )

    display_df = df.copy()

    if selected_province != "Tất cả":

        display_df = display_df[
            display_df[province_col]
            == selected_province
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

    # --------------------------------------------------------
    # DOWNLOAD FULL DATASET
    # --------------------------------------------------------

    st.markdown(
        "### 📥 Tải dữ liệu"
    )

    csv_full = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 Tải toàn bộ Dataset PCI 2025",
        data=csv_full,
        file_name="pci_2025_analyzed_data.csv",
        mime="text/csv"
    )

    # --------------------------------------------------------
    # DOWNLOAD FILTERED DATASET
    # --------------------------------------------------------

    if selected_province != "Tất cả":

        csv_filtered = display_df.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            label=(
                f"📥 Tải dữ liệu của {selected_province}"
            ),
            data=csv_filtered,
            file_name=(
                f"pci_2025_{selected_province}.csv"
            ),
            mime="text/csv"
        )


# ============================================================
# 10. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    """
    PCI 2025 – Interactive Analytical Dashboard |
    34 địa phương | 9 thành phần PCI |
    Ward Hierarchical Clustering + K-Means validation |
    """
)

