"""
Food Distribution Streamlit Dashboard
======================================
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sqlalchemy import create_engine
from urllib.parse import quote_plus
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
    /* Main background */
    .stApp { background-color: #F0F4F8; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%);
    }
    [data-testid="stSidebar"] * { color: #D8F3DC !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #B7E4C7 !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #64748B !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #1B4332 !important;
        font-weight: 700;
    }

    /* Section headers */
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

    /* Tables */
    .dataframe { font-size: 13px !important; }
    thead tr th {
        background-color: #1B4332 !important;
        color: white !important;
    }

    /* Title */
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #1B4332;
        margin-bottom: 4px;
    }
    .main-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ── DB Connection ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    password = quote_plus("Dharsini@01")   # ← your MySQL password
    return create_engine(
        f"mysql+pymysql://root:{password}@127.0.0.1:3306/food_distribution"
    )

@st.cache_data
def load_data():
    engine = get_engine()
    food      = pd.read_sql("SELECT * FROM food_listings", engine)
    claims    = pd.read_sql("SELECT * FROM claims", engine)
    providers = pd.read_sql("SELECT * FROM providers", engine)
    receivers = pd.read_sql("SELECT * FROM receivers", engine)
    return food, claims, providers, receivers

# ── Load Data ─────────────────────────────────────────────────────────────────
try:
    food, claims, providers, receivers = load_data()
    engine = get_engine()
    connected = True
except Exception as e:
    st.error(f"❌ Cannot connect to MySQL: {e}")
    st.info("Make sure MySQL is running and password is correct in the script.")
    connected = False
    st.stop()

# ── Merge ─────────────────────────────────────────────────────────────────────
food_prov   = food.merge(providers[["Provider_ID","City","Name","Contact","Type"]],
                         on="Provider_ID", how="left",
                         suffixes=("","_prov"))
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
st.sidebar.markdown("Food distribution analytics dashboard connecting providers, receivers, and claims data.")

# ── Apply Filters ─────────────────────────────────────────────────────────────
fp = food_prov.copy()
if sel_city     != "All": fp = fp[fp["City"]          == sel_city]
if sel_provider != "All": fp = fp[fp["Provider_Type"] == sel_provider]
if sel_meal     != "All": fp = fp[fp["Meal_Type"]     == sel_meal]
if sel_food     != "All": fp = fp[fp["Food_Type"]     == sel_food]

filtered_food_ids = fp["Food_ID"].tolist()
fc = food_claims[food_claims["Food_ID"].isin(filtered_food_ids)]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🍱 Food Distribution Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Real-time analytics across providers, food listings, and claims</div>', unsafe_allow_html=True)

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

# ── CHARTS ROW 1 ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Univariate Analysis</div>', unsafe_allow_html=True)

PALETTE = ["#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7","#D8F3DC"]

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
    ax.set_xlabel("Count", fontsize=9)
    for i, v in enumerate(counts.values):
        ax.text(v+1, i, str(v), va="center", fontsize=8)
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── CHARTS ROW 2 ─────────────────────────────────────────────────────────────
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

# ── CHARTS ROW 3 ─────────────────────────────────────────────────────────────
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
    sc = fc["Status"].value_counts() if "Status" in fc.columns else claims["Status"].value_counts()
    colors_map = {"Completed":"#2D6A4F","Pending":"#F4A261","Cancelled":"#E76F51","Unknown":"#ADB5BD"}
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
    import numpy as np
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

# ── SQL QUERY OUTPUTS ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗄️ SQL Query Results</div>', unsafe_allow_html=True)

query_map = {
    "1. Providers by City":             "SELECT City, COUNT(*) AS Total_Providers FROM providers GROUP BY City ORDER BY Total_Providers DESC LIMIT 10",
    "2. Receivers by City":             "SELECT City, COUNT(*) AS Total_Receivers FROM receivers GROUP BY City ORDER BY Total_Receivers DESC LIMIT 10",
    "3. Most Contributing Provider":    "SELECT p.Name, p.City, p.Type, COUNT(f.Food_ID) AS Total_Listings FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID,p.Name,p.City,p.Type ORDER BY Total_Listings DESC LIMIT 10",
    "4. Most Claimed Food":             "SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_Name ORDER BY Total_Claims DESC LIMIT 10",
    "5. Total Food Quantity":           "SELECT SUM(Quantity) AS Total_Quantity, ROUND(AVG(Quantity),2) AS Avg_Quantity, MAX(Quantity) AS Max_Quantity, MIN(Quantity) AS Min_Quantity FROM food_listings",
    "6. Top City by Food Listing":      "SELECT p.City, COUNT(f.Food_ID) AS Total_Listings FROM food_listings f JOIN providers p ON f.Provider_ID=p.Provider_ID GROUP BY p.City ORDER BY Total_Listings DESC LIMIT 10",
    "7. Most Common Food Type":         "SELECT Food_Type, COUNT(*) AS Count FROM food_listings GROUP BY Food_Type ORDER BY Count DESC",
    "8. Claims per Food Item":          "SELECT f.Food_Name, f.Food_Type, f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_ID,f.Food_Name,f.Food_Type,f.Meal_Type ORDER BY Total_Claims DESC LIMIT 10",
    "9. Provider with Most Successful Claims": "SELECT p.Name, p.City, COUNT(c.Claim_ID) AS Successful_Claims FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID JOIN claims c ON f.Food_ID=c.Food_ID WHERE c.Status='Completed' GROUP BY p.Provider_ID,p.Name,p.City ORDER BY Successful_Claims DESC LIMIT 10",
    "10. Claim Status %":               "SELECT Status, COUNT(*) AS Total, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),2) AS Percentage FROM claims GROUP BY Status ORDER BY Total DESC",
    "11. Average Quantity Claimed":     "SELECT ROUND(AVG(f.Quantity),2) AS Avg_Quantity_Per_Claim FROM claims c JOIN food_listings f ON c.Food_ID=f.Food_ID WHERE c.Status='Completed'",
    "12. Most Claimed Meal Type":       "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY Total_Claims DESC",
    "13. Total Donated Quantity":       "SELECT p.Name, p.Type, p.City, SUM(f.Quantity) AS Total_Donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID,p.Name,p.Type,p.City ORDER BY Total_Donated DESC LIMIT 10",
    "14. Receiver Type with Most Claims": "SELECT r.Type AS Receiver_Type, COUNT(c.Claim_ID) AS Total_Claims FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Type ORDER BY Total_Claims DESC",
    "15. Monthly Claim Trend":          "SELECT LEFT(Timestamp,7) AS Month, COUNT(*) AS Total_Claims, SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS Completed, SUM(CASE WHEN Status='Pending' THEN 1 ELSE 0 END) AS Pending, SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled FROM claims GROUP BY LEFT(Timestamp,7) ORDER BY Month",
}

selected_query = st.selectbox("Select a Query to View:", list(query_map.keys()))
if selected_query:
    result = pd.read_sql(query_map[selected_query], engine)
    st.dataframe(result, use_container_width=True)

# ── PROVIDER CONTACT INFO ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📞 Provider Contact Information</div>', unsafe_allow_html=True)

search = st.text_input("🔍 Search Provider by Name or City")
prov_display = providers.copy()
if search:
    prov_display = prov_display[
        prov_display["Name"].str.contains(search, case=False, na=False) |
        prov_display["City"].str.contains(search, case=False, na=False)
    ]
if sel_city != "All":
    prov_display = prov_display[prov_display["City"] == sel_city]
if sel_provider != "All":
    prov_display = prov_display[prov_display["Type"] == sel_provider]

st.dataframe(
    prov_display[["Provider_ID","Name","Type","City","Address","Contact"]].reset_index(drop=True),
    use_container_width=True,
    height=300
)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:13px;'>"
    "🍱 Food Distribution Dashboard • Built with Streamlit + MySQL"
    "</div>",
    unsafe_allow_html=True
)
