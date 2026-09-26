# -*- coding: utf-8 -*-

"""
PCI 2025 - Local Business Environment Dashboard

Nguồn dữ liệu:
    pci_2025_dashboard.csv

Dataset cuối cùng:
    34 địa phương
    9 thành phần PCI đã chuẩn hóa về thang 0-10
    Điểm môi trường kinh doanh tổng hợp
    Xếp hạng (Dense Rank)
    Ward Cluster (K=2)
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
import plotly.graph_objects as go


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PCI 2025 - Môi trường kinh doanh",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# 2. TITLE & INTRODUCTION
# ============================================================

st.title("📊 Phân tích môi trường kinh doanh cấp địa phương theo PCI 2025")

st.markdown(
    """
Dashboard hỗ trợ phân tích mức độ thuận lợi của môi trường kinh doanh tại **34 địa phương** dựa trên **9 thành phần PCI 2025**.

Điểm tổng hợp được sử dụng cho mục đích **đánh giá và sàng lọc tương đối** giữa các địa phương, không phải mô hình tối ưu hóa vị trí kho bãi hay trung tâm logistics.
"""
)


# ============================================================
# 3. LOAD DATA
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
# 5. DATA VALIDATION & CLEANING
# ============================================================

required_cols = [province_col, *pci_cols, score_col, rank_col, cluster_col, silhouette_col]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Dataset thiếu các cột bắt buộc: {missing_cols}")
    st.stop()

df = df.copy()
df[province_col] = df[province_col].astype(str).str.strip()
df = df[df[province_col].notna() & (df[province_col] != "")].drop_duplicates(subset=[province_col])

for col in pci_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
df[rank_col] = pd.to_numeric(df[rank_col], errors="coerce")
df[cluster_col] = pd.to_numeric(df[cluster_col], errors="coerce")
df[silhouette_col] = pd.to_numeric(df[silhouette_col], errors="coerce")


# ============================================================
# 6. SIDEBAR
# ============================================================

st.sidebar.header("🔎 Bộ lọc địa phương")
province_options = ["Tất cả"] + sorted(df[province_col].unique().tolist())
selected_province = st.sidebar.selectbox("Chọn địa phương", province_options)

if selected_province == "Tất cả":
    df_selected = df.copy()
else:
    df_selected = df[df[province_col] == selected_province].copy()


# ============================================================
# 7. SUMMARY KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Số địa phương", df[province_col].nunique())
with col2:
    st.metric("Điểm cao nhất", f"{df[score_col].max():.2f}")
with col3:
    st.metric("Điểm thấp nhất", f"{df[score_col].min():.2f}")
with col4:
    st.metric("Số cụm Ward", df[cluster_col].nunique())


# ============================================================
# 8. TABS STRUCTURE (5 TABS)
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏆 Xếp hạng",
        "🔎 Phân nhóm",
        "📊 Phân tích PCI",
        "⚖️ Kịch bản trọng số",
        "📋 Dữ liệu & Export"
    ]
)

# ------------------------------------------------------------
# TAB 1 — RANKING
# ------------------------------------------------------------
with tab1:
    st.subheader("Xếp hạng môi trường kinh doanh gốc")
    st.caption(
        "Xếp hạng được tính từ điểm môi trường kinh doanh tổng hợp trên 9 thành phần PCI 2025 "
        "với trọng số bằng nhau (1/9) và áp dụng phương pháp Dense Ranking."
    )

    ranking_df = (
        df[[province_col, score_col, rank_col, cluster_col]]
        .sort_values(by=[rank_col, score_col], ascending=[True, False])
        .copy()
    )

    st.subheader("Top 10 địa phương theo điểm tổng hợp")
    top10 = (
        ranking_df.sort_values(by=score_col, ascending=False)
        .head(10)
        .sort_values(by=score_col, ascending=True)
    )

    fig = px.bar(
        top10, x=score_col, y=province_col, orientation="h",
        text=score_col, title="Top 10 địa phương dẫn đầu"
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Điểm môi trường kinh doanh", yaxis_title="",
        xaxis=dict(range=[0, 10], dtick=1), height=500,
        margin=dict(l=20, r=80, t=50, b=50), showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bảng xếp hạng đầy đủ 34 địa phương")
    ranking_table = ranking_df.copy()
    ranking_table.columns = ["Tỉnh/Thành phố", "Điểm tổng hợp", "Xếp hạng (Dense)", "Ward Cluster"]
    st.dataframe(ranking_table, use_container_width=True, hide_index=True, height=600)

    st.info(
        "Lưu ý: Mẫu nghiên cứu sử dụng trọng số bằng nhau làm kịch bản cơ sở nhằm hạn chế việc "
        "áp đặt chủ quan khi không có dữ liệu thực nghiệm độc lập về trọng số ngành."
    )


# ------------------------------------------------------------
# TAB 2 — CLUSTERING
# ------------------------------------------------------------
with tab2:
    st.subheader("🔎 Phân nhóm địa phương bằng Ward Clustering")
    st.markdown("Phân cụm được thực hiện trên **9 thành phần PCI đã chuẩn hóa**, không sử dụng điểm tổng hợp hay thứ hạng.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Số cụm (K)", int(df[cluster_col].nunique()))
    with c2:
        st.metric("Cluster 0", int((df[cluster_col] == 0).sum()))
    with c3:
        st.metric("Cluster 1", int((df[cluster_col] == 1).sum()))
    with c4:
        st.metric("Silhouette Trung bình", "0.2905")

    st.info(
        "K = 2 được lựa chọn với hệ số Silhouette = 0.2905. Kết quả Ward được kiểm chứng bằng K-Means "
        "với Adjusted Rand Index (ARI) = 1.0000. Phân cụm mang tính chất khám phá cấu trúc dữ liệu."
    )

    st.subheader("Hồ sơ trung bình của các cụm")
    cluster_profile = df.groupby(cluster_col)[pci_cols].mean().round(2)
    cluster_profile_display = cluster_profile.T.reset_index()
    cluster_profile_display.columns = ["Thành phần PCI", "Cluster 0", "Cluster 1"]
    st.dataframe(cluster_profile_display, use_container_width=True, hide_index=True)

    # Heatmap
    heatmap_df = cluster_profile.T.copy()
    heatmap_df.columns = [f"Cluster {c}" for c in heatmap_df.columns]
    heatmap_df.index = [str(col).replace("PCI_", "") for col in heatmap_df.index]

    fig_heatmap = px.imshow(
        heatmap_df, text_auto=".2f", aspect="auto",
        title="Hồ sơ 9 thành phần PCI theo cụm",
        labels={"x": "Cụm", "y": "Thành phần PCI", "color": "Điểm"}
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    selected_cluster = st.selectbox("Chọn cụm để xem các địa phương", sorted(df[cluster_col].dropna().unique()))
    cluster_members = df[df[cluster_col] == selected_cluster][[province_col, score_col, rank_col, silhouette_col]].sort_values(by=score_col, ascending=False)
    
    st.subheader(f"Địa phương thuộc Cluster {selected_cluster}")
    st.dataframe(cluster_members, use_container_width=True, hide_index=True)

    if selected_cluster == 1:
        st.warning("Trong Cluster 1, Vĩnh Long có Silhouette = 0.0195, nằm rất gần ranh giới giữa các cụm.")


# ------------------------------------------------------------
# TAB 3 — PCI ANALYSIS (RADAR + SCATTER + CORRELATION)
# ------------------------------------------------------------
with tab3:
    st.subheader("📊 Phân tích khám phá 9 thành phần PCI")

    # --- UPGRADE 1: RADAR CHART ---
    st.markdown("### 1. So sánh hồ sơ 9 thành phần PCI giữa hai địa phương")
    province_list = sorted(df[province_col].dropna().unique().tolist())
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        province_a = st.selectbox("Địa phương 1", province_list, index=0, key="radar_a")
    with col_r2:
        default_b = 18 if len(province_list) > 18 else 1  # Mặc định TP.HCM hoặc vị trí khác
        province_b = st.selectbox("Địa phương 2", province_list, index=default_b, key="radar_b")

    radar_a = df[df[province_col] == province_a].iloc[0]
    radar_b = df[df[province_col] == province_b].iloc[0]

    # Khép kín đường đa giác radar
    categories = [c.replace("PCI_", "PCI ") for c in pci_cols]
    categories_closed = categories + [categories[0]]
    val_a = [radar_a[c] for c in pci_cols] + [radar_a[pci_cols[0]]]
    val_b = [radar_b[c] for c in pci_cols] + [radar_b[pci_cols[0]]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=val_a, theta=categories_closed, fill="toself", name=province_a))
    fig_radar.add_trace(go.Scatterpolar(r=val_b, theta=categories_closed, fill="toself", name=province_b))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title=f"So sánh hồ sơ PCI: {province_a} vs {province_b}",
        height=550
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.caption("Radar Chart trực quan hóa sự khác biệt hồ sơ giữa 2 địa phương trên thang điểm chuẩn hóa 0–10.")

    st.divider()

    # --- UPGRADE 3: SCATTER PLOT ---
    st.markdown("### 2. Quan hệ giữa hai thành phần PCI và phân bố cụm")
    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        x_var = st.selectbox("Biến trục X", pci_cols, index=4, key="sc_x") # PCI_5
    with sc_col2:
        y_var = st.selectbox("Biến trục Y", pci_cols, index=8, key="sc_y") # PCI_9

    scatter_df = df.copy()
    scatter_df["Ward Cluster"] = scatter_df[cluster_col].astype(str).map(lambda x: f"Cluster {x}")

    fig_scatter = px.scatter(
        scatter_df, x=x_var, y=y_var, color="Ward Cluster",
        hover_name=province_col, hover_data=[score_col, rank_col, silhouette_col],
        title=f"Mối quan hệ giữa {x_var.split(':')[0]} và {y_var.split(':')[0]}"
    )
    fig_scatter.update_layout(xaxis_title=x_var, yaxis_title=y_var, height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

    pair_corr = scatter_df[[x_var, y_var]].corr().iloc[0, 1]
    st.metric("Hệ số tương quan Pearson (2 biến chọn)", f"{pair_corr:.3f}")
    st.caption("Scatter plot mô tả liên hệ tuyến tính 2D và cách phân bố cụm; không thay thế cho thuật toán phân cụm 9D.")

    st.divider()

    # --- CORRELATION MATRIX & STATS ---
    st.markdown("### 3. Ma trận tương quan toàn bộ 9 thành phần PCI")
    corr_matrix = df[pci_cols].corr().round(2)
    fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Tương quan Pearson toàn bộ 9 thành phần PCI")
    st.plotly_chart(fig_corr, use_container_width=True)


# ------------------------------------------------------------
# TAB 4 — WHAT-IF WEIGHTING (UPGRADE 2)
# ------------------------------------------------------------
with tab4:
    st.subheader("⚖️ Phân tích kịch bản trọng số (What-If / Sensitivity Analysis)")
    st.markdown(
        "Thay đổi trọng số của 9 thành phần PCI để quan sát mức độ thay đổi của điểm tổng hợp và thứ hạng địa phương. "
        "Đây là **phân tích kịch bản / độ nhạy**, không phải mô hình tìm trọng số tối ưu."
    )

    st.markdown("### Thiết lập trọng số thử nghiệm")
    weight_values = {}
    weight_columns = st.columns(3)
    for i, pci_col in enumerate(pci_cols):
        with weight_columns[i % 3]:
            weight_values[pci_col] = st.slider(
                pci_col.split(":")[0], min_value=0.0, max_value=3.0, value=1.0, step=0.1, key=f"w_{i}"
            )

    total_weight = sum(weight_values.values())

    if total_weight == 0:
        st.error("Tổng trọng số phải lớn hơn 0. Vui lòng chọn ít nhất một thành phần PCI có trọng số > 0.")
    else:
        normalized_weights = {c: weight_values[c] / total_weight for c in pci_cols}

        scenario_df = df.copy()
        scenario_df["Điểm kịch bản"] = sum(scenario_df[c] * normalized_weights[c] for c in pci_cols)
        
        # Dense Rank đồng bộ với pipeline chính
        scenario_df["Xếp hạng kịch bản"] = scenario_df["Điểm kịch bản"].rank(method="dense", ascending=False).astype(int)
        
        # Thay đổi thứ hạng (Số dương = Thăng hạng/Cải thiện thứ hạng)
        scenario_df["Thay đổi thứ hạng"] = scenario_df[rank_col] - scenario_df["Xếp hạng kịch bản"]

        st.subheader("Bảng so sánh kết quả kịch bản")
        scenario_table = scenario_df[
            [province_col, score_col, rank_col, "Điểm kịch bản", "Xếp hạng kịch bản", "Thay đổi thứ hạng", cluster_col]
        ].sort_values(by="Xếp hạng kịch bản", ascending=True).copy()

        scenario_table.columns = [
            "Tỉnh/Thành phố", "Điểm gốc", "Hạng gốc", "Điểm kịch bản", "Hạng kịch bản", "Thay đổi vị trí", "Ward Cluster"
        ]

        st.dataframe(scenario_table, use_container_width=True, hide_index=True, height=500)
        st.caption("Chú thích 'Thay đổi vị trí': Số dương (+) thể hiện địa phương tăng hạng (ví dụ từ hạng 18 lên hạng 10 là +8).")

        st.subheader("Top 10 địa phương theo kịch bản mới")
        top10_scenario = scenario_df.sort_values(by="Điểm kịch bản", ascending=False).head(10).sort_values(by="Điểm kịch bản", ascending=True)
        
        fig_scenario = px.bar(top10_scenario, x="Điểm kịch bản", y=province_col, orientation="h", text="Điểm kịch bản", title="Top 10 kịch bản mới")
        fig_scenario.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_scenario.update_layout(xaxis_title="Điểm kịch bản", yaxis_title="", xaxis=dict(range=[0, 10], dtick=1), height=450)
        st.plotly_chart(fig_scenario, use_container_width=True)


# ------------------------------------------------------------
# TAB 5 — DATA & EXPORT (UPGRADE 4)
# ------------------------------------------------------------
with tab5:
    st.subheader("📋 Dataset phân tích & Xuất dữ liệu")

    st.write(f"Dataset hiện tại gồm **{len(df)} địa phương** và **9 thành phần PCI**.")

    search_text = st.text_input("Tìm kiếm địa phương", placeholder="Nhập tên địa phương...")
    if search_text:
        data_display = df[df[province_col].str.contains(search_text, case=False, na=False)].copy()
    else:
        data_display = df.copy()

    st.dataframe(data_display, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("⬇️ Xuất dữ liệu (Export Options)")
    ex_col1, ex_col2 = st.columns(2)

    with ex_col1:
        csv_full = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Tải toàn bộ Dataset 34 địa phương (CSV)",
            data=csv_full,
            file_name="pci_2025_full_dataset.csv",
            mime="text/csv"
        )

    with ex_col2:
        csv_display = data_display.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Tải dữ liệu đang hiển thị / lọc (CSV)",
            data=csv_display,
            file_name="pci_2025_filtered_dataset.csv",
            mime="text/csv"
        )


# ============================================================
# 9. FOOTER
# ============================================================

st.divider()
st.caption("PCI 2025 Local Business Environment Dashboard | Xử lý dữ liệu bằng Python & Trực quan hóa bằng Streamlit.")
