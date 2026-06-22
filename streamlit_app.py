"""
Local Food Wastage Management System
Multi-page Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Wastage Management",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F8FAF8; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%);
        min-width: 260px;
    }
    [data-testid="stSidebar"] * { color: #D8F3DC !important; }

    .metric-card {
        background: white;
        border: 1.5px solid #D8F3DC;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 13px;
        color: #52B788;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        color: #1B4332;
        font-weight: 800;
    }
    .section-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .section-title {
        font-size: 15px;
        font-weight: 700;
        color: #1B4332;
        border-left: 4px solid #52B788;
        padding-left: 10px;
        margin-bottom: 14px;
    }
    .page-title {
        font-size: 34px;
        font-weight: 800;
        color: #1B4332;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #74C69D;
        font-style: italic;
        margin-bottom: 24px;
    }
    .stButton > button {
        background-color: #2D6A4F;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 20px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #1B4332;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    food      = pd.read_csv("food_listings_data.csv")
    claims    = pd.read_csv("claims_data.csv")
    providers = pd.read_csv("providers_data.csv")
    receivers = pd.read_csv("receivers_data.csv")
    return food, claims, providers, receivers

food, claims, providers, receivers = load_data()

food_prov   = food.merge(providers[["Provider_ID","City","Name","Contact","Type","Address"]],
                         on="Provider_ID", how="left")
food_claims = food.merge(claims, on="Food_ID", how="left")
claims_full = claims.merge(receivers[["Receiver_ID","Type"]], on="Receiver_ID", how="left") \
                    .merge(food[["Food_ID","Quantity","Provider_Type","Food_Type","Meal_Type"]],
                           on="Food_ID", how="left")

PALETTE = ["#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7"]

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🥗 Food Wastage")
st.sidebar.markdown("### Management System")
st.sidebar.markdown("---")

pages = {
    "🏠 Dashboard":        "dashboard",
    "🔍 SQL Queries (15)": "sql",
    "📊 EDA & Charts":     "eda",
    "🔎 Filter & Search":  "filter",
    "✏️ CRUD Operations":  "crud",
    "📋 Data Tables":      "tables",
}

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

for label, key in pages.items():
    if st.sidebar.button(label, key=f"nav_{key}",
                         use_container_width=True):
        st.session_state.page = key

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:12px;color:#95D5B2;text-align:center'>"
    "Python · SQL · Streamlit · Plotly"
    "</div>", unsafe_allow_html=True
)

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown('<div class="page-title">🥗 Local Food Wastage Management System</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Connecting surplus food providers with those in need</div>', unsafe_allow_html=True)

    # KPI Cards
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpis = [
        ("🏪 Providers",  len(providers)),
        ("🤝 Receivers",  len(receivers)),
        ("🍱 Listings",   len(food)),
        ("📋 Claims",     len(claims)),
        ("📦 Total Qty",  f"{food['Quantity'].sum():,}"),
        ("✅ Completed",  len(claims[claims["Status"]=="Completed"])),
    ]
    for col, (label, val) in zip([c1,c2,c3,c4,c5,c6], kpis):
        display_val = f"{val:,}" if isinstance(val, int) else str(val)
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{display_val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown('<div class="section-title">Claim Status Breakdown</div>', unsafe_allow_html=True)
        sc = claims["Status"].value_counts()
        fig = go.Figure(go.Pie(
            labels=sc.index, values=sc.values,
            hole=0.5,
            marker_colors=["#2D6A4F","#E76F51","#F4A261"],
        ))
        fig.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10),
                          showlegend=True, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.markdown('<div class="section-title">Provider Type Distribution</div>', unsafe_allow_html=True)
        pt = food["Provider_Type"].value_counts()
        fig = px.bar(x=pt.index, y=pt.values,
                     color=pt.index,
                     color_discrete_sequence=["#2D6A4F","#40916C","#52B788","#74C69D"],
                     labels={"x":"Provider Type","y":"Count"})
        fig.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10),
                          showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown('<div class="section-title">Food Type Distribution</div>', unsafe_allow_html=True)
        ft = food["Food_Type"].value_counts()
        fig = px.pie(values=ft.values, names=ft.index,
                     color_discrete_sequence=["#2D6A4F","#52B788","#95D5B2"])
        fig.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        st.markdown('<div class="section-title">Meal Type Distribution</div>', unsafe_allow_html=True)
        mt = food["Meal_Type"].value_counts()
        fig = px.bar(x=mt.values, y=mt.index, orientation="h",
                     color=mt.index,
                     color_discrete_sequence=PALETTE)
        fig.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10),
                          showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "sql":
    st.markdown('<div class="page-title">🔍 SQL Query Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">15 analytical queries using Pandas</div>', unsafe_allow_html=True)

    query_options = {
        "1. Providers by City":
            lambda: providers.groupby("City").size().reset_index(name="Total_Providers").sort_values("Total_Providers",ascending=False).head(10),
        "2. Receivers by City":
            lambda: receivers.groupby("City").size().reset_index(name="Total_Receivers").sort_values("Total_Receivers",ascending=False).head(10),
        "3. Most Contributing Provider":
            lambda: food.merge(providers[["Provider_ID","Name","City","Type"]],on="Provider_ID") \
                        .groupby(["Name","City","Type"]).size().reset_index(name="Total_Listings") \
                        .sort_values("Total_Listings",ascending=False).head(10),
        "4. Most Claimed Food":
            lambda: food.merge(claims,on="Food_ID").groupby("Food_Name").size() \
                        .reset_index(name="Total_Claims").sort_values("Total_Claims",ascending=False).head(10),
        "5. Total Food Quantity":
            lambda: pd.DataFrame({"Total_Quantity":[food["Quantity"].sum()],
                                  "Avg_Quantity":[round(food["Quantity"].mean(),2)],
                                  "Max_Quantity":[food["Quantity"].max()],
                                  "Min_Quantity":[food["Quantity"].min()]}),
        "6. Top City by Food Listing":
            lambda: food.merge(providers[["Provider_ID","City"]],on="Provider_ID") \
                        .groupby("City").size().reset_index(name="Total_Listings") \
                        .sort_values("Total_Listings",ascending=False).head(10),
        "7. Most Common Food Type":
            lambda: food.groupby("Food_Type").size().reset_index(name="Count").sort_values("Count",ascending=False),
        "8. Claims per Food Item":
            lambda: food.merge(claims,on="Food_ID",how="left") \
                        .groupby(["Food_Name","Food_Type","Meal_Type"]).size() \
                        .reset_index(name="Total_Claims").sort_values("Total_Claims",ascending=False).head(10),
        "9. Provider with Most Successful Claims":
            lambda: claims[claims["Status"]=="Completed"].merge(food[["Food_ID","Provider_ID"]],on="Food_ID") \
                        .merge(providers[["Provider_ID","Name","City"]],on="Provider_ID") \
                        .groupby(["Name","City"]).size().reset_index(name="Successful_Claims") \
                        .sort_values("Successful_Claims",ascending=False).head(10),
        "10. Claim Status %":
            lambda: claims.groupby("Status").size().reset_index(name="Total") \
                        .assign(Percentage=lambda x: round(x["Total"]*100/x["Total"].sum(),2)) \
                        .sort_values("Total",ascending=False),
        "11. Average Quantity Claimed":
            lambda: pd.DataFrame({"Avg_Quantity_Per_Claim":[
                        round(claims[claims["Status"]=="Completed"] \
                              .merge(food[["Food_ID","Quantity"]],on="Food_ID")["Quantity"].mean(),2)]}),
        "12. Most Claimed Meal Type":
            lambda: food.merge(claims,on="Food_ID").groupby("Meal_Type").size() \
                        .reset_index(name="Total_Claims").sort_values("Total_Claims",ascending=False),
        "13. Total Donated Quantity by Provider":
            lambda: food.merge(providers[["Provider_ID","Name","Type","City"]],on="Provider_ID") \
                        .groupby(["Name","Type","City"])["Quantity"].sum() \
                        .reset_index(name="Total_Donated").sort_values("Total_Donated",ascending=False).head(10),
        "14. Receiver Type with Most Claims":
            lambda: claims.merge(receivers[["Receiver_ID","Type"]],on="Receiver_ID") \
                        .groupby("Type").size().reset_index(name="Total_Claims") \
                        .sort_values("Total_Claims",ascending=False),
        "15. Monthly Claim Trend":
            lambda: claims.assign(Month=claims["Timestamp"].str[:7]) \
                        .groupby("Month").agg(
                            Total_Claims=("Claim_ID","count"),
                            Completed=("Status",lambda x:(x=="Completed").sum()),
                            Pending=("Status",lambda x:(x=="Pending").sum()),
                            Cancelled=("Status",lambda x:(x=="Cancelled").sum())
                        ).reset_index().sort_values("Month"),
    }

    selected = st.selectbox("Select Query:", list(query_options.keys()))
    result = query_options[selected]()
    st.dataframe(result.reset_index(drop=True), use_container_width=True, height=350)

    # Chart for result
    if len(result) > 1 and result.shape[1] >= 2:
        num_cols = result.select_dtypes(include=np.number).columns.tolist()
        cat_cols = result.select_dtypes(exclude=np.number).columns.tolist()
        if cat_cols and num_cols:
            fig = px.bar(result.head(10), x=cat_cols[0], y=num_cols[0],
                         color_discrete_sequence=["#2D6A4F"])
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — EDA & CHARTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "eda":
    st.markdown('<div class="page-title">📊 EDA & Charts</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Exploratory Data Analysis with Visualizations</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Univariate", "📈 Bivariate", "🔥 Multivariate"])

    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">Provider Type Distribution</div>', unsafe_allow_html=True)
            pt = food["Provider_Type"].value_counts()
            fig = px.pie(values=pt.values, names=pt.index,
                         color_discrete_sequence=PALETTE)
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">Receiver Type Distribution</div>', unsafe_allow_html=True)
            rt = receivers["Type"].value_counts()
            fig = px.pie(values=rt.values, names=rt.index,
                         color_discrete_sequence=PALETTE)
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-title">Food Type Distribution</div>', unsafe_allow_html=True)
            ft = food["Food_Type"].value_counts()
            fig = px.pie(values=ft.values, names=ft.index,
                         color_discrete_sequence=["#2D6A4F","#52B788","#95D5B2"])
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            st.markdown('<div class="section-title">Meal Type Distribution</div>', unsafe_allow_html=True)
            mt = food["Meal_Type"].value_counts()
            fig = px.bar(x=mt.index, y=mt.values,
                         color=mt.index, color_discrete_sequence=PALETTE)
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">Top 15 Cities by Food Listings</div>', unsafe_allow_html=True)
            city = food_prov["City"].value_counts().head(15)
            fig = px.bar(x=city.values, y=city.index, orientation="h",
                         color_discrete_sequence=["#2D6A4F"])
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">Provider Type vs Avg Quantity</div>', unsafe_allow_html=True)
            pq = food.groupby("Provider_Type")["Quantity"].mean().reset_index()
            fig = px.bar(pq, x="Provider_Type", y="Quantity",
                         color="Provider_Type", color_discrete_sequence=PALETTE)
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-title">Food Type vs Avg Quantity</div>', unsafe_allow_html=True)
            fq = food.groupby("Food_Type")["Quantity"].mean().reset_index()
            fig = px.bar(fq, x="Food_Type", y="Quantity",
                         color="Food_Type",
                         color_discrete_sequence=["#2D6A4F","#52B788","#95D5B2"])
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            st.markdown('<div class="section-title">Meal Type vs Avg Quantity</div>', unsafe_allow_html=True)
            mq = food.groupby("Meal_Type")["Quantity"].mean().reset_index()
            fig = px.bar(mq, x="Meal_Type", y="Quantity",
                         color="Meal_Type", color_discrete_sequence=PALETTE)
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">Food Type × Meal Type Heatmap</div>', unsafe_allow_html=True)
            heat = food.groupby(["Food_Type","Meal_Type"])["Quantity"].mean().unstack(fill_value=0)
            fig = px.imshow(heat, color_continuous_scale="Greens",
                            text_auto=".1f", aspect="auto")
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">Provider Type: Claims vs Avg Quantity</div>', unsafe_allow_html=True)
            pc = claims_full.groupby("Provider_Type").agg(
                total_claims=("Claim_ID","count"),
                avg_qty=("Quantity","mean")
            ).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=pc["Provider_Type"], y=pc["avg_qty"],
                                 name="Avg Qty", marker_color="#2D6A4F"))
            fig.add_trace(go.Scatter(x=pc["Provider_Type"], y=pc["total_claims"],
                                     name="Claims", mode="lines+markers",
                                     marker_color="#E76F51", yaxis="y2"))
            fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                              yaxis2=dict(overlaying="y", side="right"))
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — FILTER & SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "filter":
    st.markdown('<div class="page-title">🔎 Filter & Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Filter food listings by multiple criteria</div>', unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns(4)
    cities     = ["All"] + sorted(providers["City"].dropna().unique().tolist())
    prov_types = ["All"] + sorted(food["Provider_Type"].dropna().unique().tolist())
    meal_types = ["All"] + sorted(food["Meal_Type"].dropna().unique().tolist())
    food_types = ["All"] + sorted(food["Food_Type"].dropna().unique().tolist())

    sel_city  = f1.selectbox("🏙️ City",          cities)
    sel_prov  = f2.selectbox("🏪 Provider Type",  prov_types)
    sel_meal  = f3.selectbox("🍽️ Meal Type",      meal_types)
    sel_food  = f4.selectbox("🥗 Food Type",      food_types)

    fp = food_prov.copy()
    if sel_city != "All": fp = fp[fp["City"]          == sel_city]
    if sel_prov != "All": fp = fp[fp["Provider_Type"] == sel_prov]
    if sel_meal != "All": fp = fp[fp["Meal_Type"]     == sel_meal]
    if sel_food != "All": fp = fp[fp["Food_Type"]     == sel_food]

    st.markdown(f"**{len(fp):,} listings found**")
    st.dataframe(fp[["Food_ID","Food_Name","Quantity","Food_Type","Meal_Type",
                      "Provider_Type","City","Expiry_Date"]].reset_index(drop=True),
                 use_container_width=True, height=400)

    if len(fp) > 0:
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Listings",  f"{len(fp):,}")
        m2.metric("Total Quantity",  f"{fp['Quantity'].sum():,}")
        m3.metric("Avg Quantity",    f"{fp['Quantity'].mean():.1f}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — CRUD OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "crud":
    st.markdown('<div class="page-title">✏️ CRUD Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">View, Add, Update, Delete records</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👁️ View", "➕ Add Record", "🔍 Search by ID"])

    with tab1:
        table = st.selectbox("Select Table:", ["Food Listings","Providers","Receivers","Claims"])
        table_map = {"Food Listings": food, "Providers": providers,
                     "Receivers": receivers, "Claims": claims}
        df = table_map[table]
        st.dataframe(df.head(50), use_container_width=True, height=400)
        st.caption(f"Showing 50 of {len(df):,} records")

    with tab2:
        st.markdown("### Add New Food Listing")
        col1, col2 = st.columns(2)
        with col1:
            food_name  = st.text_input("Food Name")
            quantity   = st.number_input("Quantity", min_value=1, value=10)
            food_type  = st.selectbox("Food Type", ["Vegetarian","Vegan","Non-Vegetarian"])
        with col2:
            meal_type  = st.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])
            prov_type  = st.selectbox("Provider Type", ["Restaurant","Supermarket","Grocery Store","Catering Service"])
            expiry     = st.date_input("Expiry Date")

        if st.button("➕ Add Record"):
            if food_name:
                st.success(f"✅ Record '{food_name}' added successfully! (Demo mode — not saved to file)")
            else:
                st.warning("Please enter a Food Name")

    with tab3:
        st.markdown("### Search by ID")
        search_table = st.selectbox("Table:", ["Food Listings","Providers","Receivers","Claims"], key="search_t")
        id_col_map = {"Food Listings":"Food_ID","Providers":"Provider_ID",
                      "Receivers":"Receiver_ID","Claims":"Claim_ID"}
        id_col = id_col_map[search_table]
        search_id = st.number_input(f"Enter {id_col}:", min_value=1, value=1)
        df_s = table_map[search_table]
        result = df_s[df_s[id_col] == search_id]
        if len(result) > 0:
            st.dataframe(result, use_container_width=True)
        else:
            st.warning(f"No record found with {id_col} = {search_id}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — DATA TABLES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "tables":
    st.markdown('<div class="page-title">📋 Data Tables</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse all raw data tables</div>', unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["🍱 Food Listings","🏪 Providers","🤝 Receivers","📋 Claims"])

    with tab1:
        st.markdown(f"**{len(food):,} records**")
        st.dataframe(food, use_container_width=True, height=450)

    with tab2:
        st.markdown(f"**{len(providers):,} records**")
        st.dataframe(providers, use_container_width=True, height=450)

    with tab3:
        st.markdown(f"**{len(receivers):,} records**")
        st.dataframe(receivers, use_container_width=True, height=450)

    with tab4:
        st.markdown(f"**{len(claims):,} records**")
        st.dataframe(claims, use_container_width=True, height=450)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;margin-top:8px;padding:12px;"
    "background:#1B4332;border-radius:8px;'>"
    "<span style='color:#D8F3DC;font-size:14px;font-weight:600;'>"
    "👩‍💻 Created by Priyadharsini S"
    "</span>"
    "</div>",
    unsafe_allow_html=True
)