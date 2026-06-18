"""
Food Distribution Streamlit Dashboard
CSV Version — works on Streamlit Cloud
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Distribution Dashboard",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F0F4F8; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%);
    }
    [data-testid="stSidebar"] * { color: #D8F3DC !important; }
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #1B4332 !important;
        font-weight: 700;
    }
    .section-header {
        background: white;
        border-left: 4px solid #2D6A4F;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin: 20px 0 12px 0;
        font-size: 16px;
        font-weight: 700;
        color: #1B4332;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data from CSV ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    food      = pd.read_csv("food_listings_data.csv")
    claims    = pd.read_csv("claims_data.csv")
    providers = pd.read_csv("providers_data.csv")
    receivers = pd.read_csv("receivers_data.csv")
    return food, claims, providers, receivers

food, claims, providers, receivers = load_data()

# ── Merge Tables ──────────────────────────────────────────────────────────────
food_prov   = food.merge(providers[["Provider_ID","City","Name","Contact","Type"]],
                         on="Provider_ID", how="left")
food_claims = food.merge(claims, on="Food_ID", how="left")
claims_full = claims.merge(receivers[["Receiver_ID","Type"]], on="Receiver_ID", how="left") \
                    .merge(food[["Food_ID","Quantity","Provider_Type"]], on="Food_ID", how="left")

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🍱 Food Distribution")
st.sidebar.markdown("### Filters")

all_cities     = ["All"] + sorted(providers["City"].dropna().unique().tolist())
all_providers  = ["All"] + sorted(providers["Type"].dropna().unique().tolist())
all_meal_types = ["All"] + sorted(food["Meal_Type"].dropna().unique().tolist())
all_food_types = ["All"] + sorted(food["Food_Type"].dropna().unique().tolist())

sel_city      = st.sidebar.selectbox("🏙️ City",          all_cities)
sel_provider  = st.sidebar.selectbox("🏪 Provider Type",  all_providers)
sel_meal      = st.sidebar.selectbox("🍽️ Meal Type",      all_meal_types)
sel_food      = st.sidebar.selectbox("🥗 Food Type",      all_food_types)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Food distribution analytics dashboard.")

# ── Apply Filters ─────────────────────────────────────────────────────────────
fp = food_prov.copy()
if sel_city     != "All": fp = fp[fp["City"]          == sel_city]
if sel_provider != "All": fp = fp[fp["Provider_Type"] == sel_provider]
if sel_meal     != "All": fp = fp[fp["Meal_Type"]     == sel_meal]
if sel_food     != "All": fp = fp[fp["Food_Type"]     == sel_food]

filtered_food_ids = fp["Food_ID"].tolist()
fc = food_claims[food_claims["Food_ID"].isin(filtered_food_ids)]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:32px;font-weight:800;color:#1B4332">🍱 Food Distribution Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:14px;color:#64748B;margin-bottom:24px">Real-time analytics across providers, food listings, and claims</div>', unsafe_allow_html=True)

# ── KPI METRICS ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Listings",   f"{len(fp):,}")
k2.metric("Total Quantity",   f"{fp['Quantity'].sum():,.0f}")
k3.metric("Avg Quantity",     f"{fp['Quantity'].mean():.1f}")
k4.metric("Total Claims",     f"{len(fc):,}")
completed = fc[fc["Status"]=="Completed"] if "Status" in fc.columns else pd.DataFrame()
k5.metric("Completed Claims", f"{len(completed):,}")
k6.metric("Providers",        f"{fp['Provider_ID'].nunique():,}")

# ── PALETTE ───────────────────────────────────────────────────────────────────
PALETTE = ["#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7","#D8F3DC"]

# ── UNIVARIATE ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Univariate Analysis</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("**Provider Type Distribution**")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_alpha(0)
    counts = fp["Provider_Type"].value_counts()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
           colors=PALETTE[:len(counts)],
           wedgeprops={"edgecolor":"white","linewidth":2})
    st.pyplot(fig, use_container_width=True)
    plt.close()

with c2:
    st.markdown("**Receiver Type Distribution**")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_alpha(0)
    counts = receivers["Type"].value_counts()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
           colors=PALETTE[:len(counts)],
           wedgeprops={"edgecolor":"white","linewidth":2})
    st.pyplot(fig, use_container_width=True)
    plt.close()

with c3:
    st.markdown("**Food Type Distribution**")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_alpha(0)
    counts = fp["Food_Type"].value_counts()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
           colors=["#2D6A4F","#52B788","#95D5B2"],
           wedgeprops={"edgecolor":"white","linewidth":2})
    st.pyplot(fig, use_container_width=True)
    plt.close()

with c4:
    st.markdown("**Meal Type Distribution**")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_alpha(0)
    counts = fp["Meal_Type"].value_counts()
    ax.barh(counts.index, counts.values,
            color=PALETTE[:len(counts)], edgecolor="white")
    for i, v in enumerate(counts.values):
        ax.text(v+1, i, str(v), va="center", fontsize=8)
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── BIVARIATE ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📉 Bivariate Analysis</div>', unsafe_allow_html=True)
b1, b2 = st.columns(2)

with b1:
    st.markdown("**Top 10 Cities by Food Listings**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    city_counts = fp["City"].value_counts().head(10)
    ax.barh(city_counts.index[::-1], city_counts.values[::-1],
            color="#2D6A4F", edgecolor="white")
    ax.set_xlabel("Listings")
    for i, v in enumerate(city_counts.values[::-1]):
        ax.text(v+0.3, i, str(v), va="center", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with b2:
    st.markdown("**Provider Type vs Avg Quantity**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    prov_qty = fp.groupby("Provider_Type")["Quantity"].mean().sort_values(ascending=False)
    bars = ax.bar(prov_qty.index, prov_qty.values,
                  color=PALETTE[:len(prov_qty)], edgecolor="white")
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f"{bar.get_height():.1f}", ha="center", fontsize=9)
    ax.set_ylabel("Avg Quantity")
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

b3, b4 = st.columns(2)

with b3:
    st.markdown("**Food Type vs Avg Quantity**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    food_qty = fp.groupby("Food_Type")["Quantity"].mean().sort_values(ascending=False)
    bars = ax.bar(food_qty.index, food_qty.values,
                  color=["#2D6A4F","#52B788","#95D5B2"], edgecolor="white")
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f"{bar.get_height():.1f}", ha="center", fontsize=9)
    ax.set_ylabel("Avg Quantity")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with b4:
    st.markdown("**Meal Type vs Avg Quantity**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    meal_qty = fp.groupby("Meal_Type")["Quantity"].mean().sort_values(ascending=False)
    bars = ax.bar(meal_qty.index, meal_qty.values,
                  color=PALETTE[:len(meal_qty)], edgecolor="white")
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f"{bar.get_height():.1f}", ha="center", fontsize=9)
    ax.set_ylabel("Avg Quantity")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── MULTIVARIATE ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Multivariate Analysis</div>', unsafe_allow_html=True)
m1, m2 = st.columns(2)

with m1:
    st.markdown("**Food Type × Meal Type Heatmap**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    heat = fp.groupby(["Food_Type","Meal_Type"])["Quantity"].mean().unstack(fill_value=0)
    sns.heatmap(heat, ax=ax, annot=True, fmt=".1f",
                cmap="Greens", linewidths=0.5)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with m2:
    st.markdown("**Provider Type: Avg Qty vs Claims**")
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0)
    prov_c = claims_full.groupby("Provider_Type").agg(
        total_claims=("Claim_ID","count"),
        avg_qty=("Quantity","mean")
    ).reset_index()
    bars = ax.bar(prov_c["Provider_Type"], prov_c["avg_qty"],
                  color=PALETTE[:4], edgecolor="white")
    ax2 = ax.twinx()
    ax2.plot(prov_c["Provider_Type"], prov_c["total_claims"],
             "D--", color="#D62828", linewidth=2, markersize=8)
    ax.set_ylabel("Avg Quantity")
    ax2.set_ylabel("Total Claims", color="#D62828")
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── CLAIM ANALYSIS ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Claim Analysis</div>', unsafe_allow_html=True)
cl1, cl2, cl3 = st.columns(3)

with cl1:
    st.markdown("**Claim Status Distribution**")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_alpha(0)
    sc = claims["Status"].value_counts()
    colors_map = {"Completed":"#2D6A4F","Pending":"#F4A261","Cancelled":"#E76F51"}
    wc = [colors_map.get(s,"#ADB5BD") for s in sc.index]
    ax.pie(sc, labels=sc.index, autopct="%1.1f%%",
           colors=wc, wedgeprops={"edgecolor":"white","linewidth":2})
    st.pyplot(fig, use_container_width=True)
    plt.close()

with cl2:
    st.markdown("**Top 10 Receivers by Claims**")
    top_recv = claims["Receiver_ID"].value_counts().head(10).reset_index()
    top_recv.columns = ["Receiver_ID","Claims"]
    top_recv = top_recv.merge(receivers[["Receiver_ID","Name","Type"]], on="Receiver_ID", how="left")
    fig, ax = plt.subplots(figsize=(5,4))
    fig.patch.set_alpha(0)
    ax.barh(top_recv["Name"].str.split().str[0]+" ("+top_recv["Type"]+")",
            top_recv["Claims"], color="#2D6A4F", edgecolor="white")
    ax.invert_yaxis()
    ax.set_xlabel("Claims")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with cl3:
    st.markdown("**Top 10 Providers: Listings vs Claims**")
    tp = food["Provider_ID"].value_counts().head(10).reset_index()
    tp.columns = ["Provider_ID","listings"]
    cpp = food_claims.groupby("Provider_ID")["Claim_ID"].count().reset_index()
    cpp.columns = ["Provider_ID","claims"]
    tp = tp.merge(cpp, on="Provider_ID", how="left").fillna(0)
    tp["label"] = "P-" + tp["Provider_ID"].astype(str)
    fig, ax = plt.subplots(figsize=(5,4))
    fig.patch.set_alpha(0)
    x = np.arange(len(tp)); w = 0.35
    ax.bar(x-w/2, tp["listings"], w, label="Listings", color="#2D6A4F", edgecolor="white")
    ax.bar(x+w/2, tp["claims"],   w, label="Claims",   color="#74C69D", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(tp["label"], rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── SQL QUERY RESULTS (using Pandas) ─────────────────────────────────────────
st.markdown('<div class="section-header">🗄️ Query Results</div>', unsafe_allow_html=True)

query_options = {
    "1. Providers by City":
        lambda: providers.groupby("City").size().reset_index(name="Total_Providers").sort_values("Total_Providers", ascending=False).head(10),
    "2. Receivers by City":
        lambda: receivers.groupby("City").size().reset_index(name="Total_Receivers").sort_values("Total_Receivers", ascending=False).head(10),
    "3. Most Contributing Provider":
        lambda: food.merge(providers[["Provider_ID","Name","City","Type"]], on="Provider_ID") \
                    .groupby(["Provider_ID","Name","City","Type"]).size() \
                    .reset_index(name="Total_Listings").sort_values("Total_Listings", ascending=False).head(10),
    "4. Most Claimed Food":
        lambda: food.merge(claims, on="Food_ID") \
                    .groupby("Food_Name").size() \
                    .reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False).head(10),
    "5. Total Food Quantity":
        lambda: pd.DataFrame({"Total_Quantity":[food["Quantity"].sum()],
                              "Avg_Quantity":[round(food["Quantity"].mean(),2)],
                              "Max_Quantity":[food["Quantity"].max()],
                              "Min_Quantity":[food["Quantity"].min()]}),
    "6. Top City by Food Listing":
        lambda: food.merge(providers[["Provider_ID","City"]], on="Provider_ID") \
                    .groupby("City").size() \
                    .reset_index(name="Total_Listings").sort_values("Total_Listings", ascending=False).head(10),
    "7. Most Common Food Type":
        lambda: food.groupby("Food_Type").size().reset_index(name="Count").sort_values("Count", ascending=False),
    "8. Claims per Food Item":
        lambda: food.merge(claims, on="Food_ID", how="left") \
                    .groupby(["Food_Name","Food_Type","Meal_Type"]).size() \
                    .reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False).head(10),
    "9. Provider with Most Successful Claims":
        lambda: claims[claims["Status"]=="Completed"].merge(food[["Food_ID","Provider_ID"]], on="Food_ID") \
                    .merge(providers[["Provider_ID","Name","City"]], on="Provider_ID") \
                    .groupby(["Provider_ID","Name","City"]).size() \
                    .reset_index(name="Successful_Claims").sort_values("Successful_Claims", ascending=False).head(10),
    "10. Claim Status %":
        lambda: claims.groupby("Status").size().reset_index(name="Total") \
                    .assign(Percentage=lambda x: round(x["Total"]*100/x["Total"].sum(), 2)) \
                    .sort_values("Total", ascending=False),
    "11. Average Quantity Claimed":
        lambda: pd.DataFrame({"Avg_Quantity_Per_Claim": [
                    round(claims[claims["Status"]=="Completed"].merge(food[["Food_ID","Quantity"]], on="Food_ID")["Quantity"].mean(), 2)]}),
    "12. Most Claimed Meal Type":
        lambda: food.merge(claims, on="Food_ID") \
                    .groupby("Meal_Type").size() \
                    .reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False),
    "13. Total Donated Quantity by Provider":
        lambda: food.merge(providers[["Provider_ID","Name","Type","City"]], on="Provider_ID") \
                    .groupby(["Provider_ID","Name","Type","City"])["Quantity"].sum() \
                    .reset_index(name="Total_Donated").sort_values("Total_Donated", ascending=False).head(10),
    "14. Receiver Type with Most Claims":
        lambda: claims.merge(receivers[["Receiver_ID","Type"]], on="Receiver_ID") \
                    .groupby("Type").size() \
                    .reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False),
    "15. Monthly Claim Trend":
        lambda: claims.assign(Month=claims["Timestamp"].str[:7]) \
                    .groupby("Month").agg(
                        Total_Claims=("Claim_ID","count"),
                        Completed=("Status", lambda x: (x=="Completed").sum()),
                        Pending=("Status",   lambda x: (x=="Pending").sum()),
                        Cancelled=("Status", lambda x: (x=="Cancelled").sum())
                    ).reset_index().sort_values("Month"),
}

selected_query = st.selectbox("Select a Query to View:", list(query_options.keys()))
if selected_query:
    result = query_options[selected_query]()
    st.dataframe(result.reset_index(drop=True), use_container_width=True)

# ── PROVIDER CONTACT INFO ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📞 Provider Contact Information</div>', unsafe_allow_html=True)

search = st.text_input("🔍 Search Provider by Name or City")
prov_display = providers.copy()
if search:
    prov_display = prov_display[
        prov_display["Name"].str.contains(search, case=False, na=False) |
        prov_display["City"].str.contains(search, case=False, na=False)
    ]
if sel_city     != "All": prov_display = prov_display[prov_display["City"] == sel_city]
if sel_provider != "All": prov_display = prov_display[prov_display["Type"] == sel_provider]

st.dataframe(
    prov_display[["Provider_ID","Name","Type","City","Address","Contact"]].reset_index(drop=True),
    use_container_width=True,
    height=300
)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94A3B8;font-size:13px'>"
    "🍱 Food Distribution Dashboard • Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
