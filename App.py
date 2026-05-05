import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Confections · Sales Dashboard",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0f0f1a; color: #e8e0f0; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0a2e 0%, #16213e 100%);
        border-right: 1px solid #2d1b4e;
    }
    section[data-testid="stSidebar"] * { color: #c8b8e8 !important; }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e1040 0%, #2d1b69 100%);
        border: 1px solid #4a2f8a;
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(100,50,200,0.25);
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 13px; color: #9b8fc0; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { font-size: 32px; font-weight: 800; color: #d4b8ff; }
    .kpi-delta { font-size: 13px; margin-top: 4px; }
    .kpi-delta.up   { color: #6ee7b7; }
    .kpi-delta.down { color: #f87171; }

    /* Section headers */
    .section-header {
        font-size: 18px; font-weight: 700; color: #b89ce0;
        border-left: 4px solid #7c3aed;
        padding-left: 12px; margin: 28px 0 12px 0;
    }

    /* Chart container */
    .chart-card {
        background: #1a1035;
        border: 1px solid #2d1b4e;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    /* Plotly chart background override */
    .js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme defaults ─────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c8b8e8", family="Inter, sans-serif", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#2d1b4e", zerolinecolor="#2d1b4e"),
    yaxis=dict(gridcolor="#2d1b4e", zerolinecolor="#2d1b4e"),
)
PALETTE = px.colors.sequential.Purples[3:]
QUALITATIVE = ["#a855f7","#6366f1","#ec4899","#06b6d4","#10b981","#f59e0b","#f87171"]

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_nassau_data.csv", parse_dates=["order_date", "ship_date"])
    df["month"]      = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["year"]       = df["order_date"].dt.year
    df["quarter"]    = df["order_date"].dt.to_period("Q").astype(str)
    df["margin_pct"] = (df["gross_profit"] / df["sales"] * 100).round(1)
    return df

df_raw = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 Nassau Confections")
    st.markdown("---")

    years = sorted(df_raw["year"].unique())
    sel_years = st.multiselect("📅 Year", years, default=years)

    divisions = sorted(df_raw["division"].unique())
    sel_divs = st.multiselect("🏭 Division", divisions, default=divisions)

    regions = sorted(df_raw["region"].unique())
    sel_regions = st.multiselect("🌍 Region", regions, default=regions)

    ship_modes = sorted(df_raw["ship_mode"].unique())
    sel_ships = st.multiselect("🚚 Ship Mode", ship_modes, default=ship_modes)

    st.markdown("---")
    st.caption("Data: 2024 – 2025 | 10,194 orders")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["year"].isin(sel_years) &
    df_raw["division"].isin(sel_divs) &
    df_raw["region"].isin(sel_regions) &
    df_raw["ship_mode"].isin(sel_ships)
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🍫 Nassau Confections — Sales Dashboard")
st.caption(f"Showing **{len(df):,}** transactions after filters · Dates {df['order_date'].min().date()} → {df['order_date'].max().date()}")

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_sales   = df["sales"].sum()
total_profit  = df["gross_profit"].sum()
total_cost    = df["cost"].sum()
total_units   = df["units"].sum()
avg_margin    = (total_profit / total_sales * 100) if total_sales else 0
num_orders    = df["order_id"].nunique()

kpi_cols = st.columns(6)
kpi_data = [
    ("💰 Total Sales",    f"${total_sales:,.0f}",    None),
    ("📈 Gross Profit",   f"${total_profit:,.0f}",   None),
    ("📦 Total Units",    f"{total_units:,.0f}",     None),
    ("🧾 Orders",         f"{num_orders:,}",         None),
    ("📊 Avg Margin",     f"{avg_margin:.1f}%",      None),
    ("💸 Total Cost",     f"${total_cost:,.0f}",     None),
]
for col, (label, value, delta) in zip(kpi_cols, kpi_data):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>""", unsafe_allow_html=True)

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Trends", "🍫 Products & Divisions", "🌍 Regional", "📋 Data Table"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SALES TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Monthly sales + profit combo
    monthly = (
        df.groupby("month")
          .agg(sales=("sales","sum"), profit=("gross_profit","sum"), units=("units","sum"))
          .reset_index()
    )
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(go.Bar(
        x=monthly["month"], y=monthly["sales"],
        name="Sales", marker_color="#7c3aed", opacity=0.85,
    ), secondary_y=False)
    fig_combo.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["profit"],
        name="Gross Profit", line=dict(color="#a855f7", width=3),
        mode="lines+markers", marker=dict(size=6),
    ), secondary_y=False)
    fig_combo.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["units"],
        name="Units Sold", line=dict(color="#06b6d4", width=2, dash="dot"),
        mode="lines",
    ), secondary_y=True)
    fig_combo.update_layout(title="Monthly Sales, Profit & Units", **PLOTLY_LAYOUT)
    fig_combo.update_yaxes(title_text="$ Value", secondary_y=False, gridcolor="#2d1b4e")
    fig_combo.update_yaxes(title_text="Units", secondary_y=True, gridcolor="#2d1b4e")
    st.plotly_chart(fig_combo, use_container_width=True)

    c1, c2 = st.columns(2)

    # Quarterly revenue
    with c1:
        quarterly = df.groupby("quarter").agg(sales=("sales","sum")).reset_index()
        fig_q = px.bar(quarterly, x="quarter", y="sales", title="Quarterly Revenue",
                       color="sales", color_continuous_scale="Purples",
                       labels={"sales":"Sales ($)","quarter":"Quarter"})
        fig_q.update_layout(**PLOTLY_LAYOUT)
        fig_q.update_coloraxes(showscale=False)
        st.plotly_chart(fig_q, use_container_width=True)

    # YoY comparison
    with c2:
        yoy = df.groupby(["year","month"]).agg(sales=("sales","sum")).reset_index()
        yoy["month_label"] = yoy["month"].dt.strftime("%b")
        fig_yoy = px.line(yoy, x="month_label", y="sales", color="year",
                          title="Year-over-Year Monthly Sales",
                          color_discrete_sequence=QUALITATIVE,
                          labels={"sales":"Sales ($)","month_label":"Month","year":"Year"},
                          category_orders={"month_label":["Jan","Feb","Mar","Apr","May","Jun",
                                                           "Jul","Aug","Sep","Oct","Nov","Dec"]})
        fig_yoy.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_yoy, use_container_width=True)

    # Ship mode breakdown over time
    ship_monthly = df.groupby(["month","ship_mode"]).agg(sales=("sales","sum")).reset_index()
    fig_ship = px.area(ship_monthly, x="month", y="sales", color="ship_mode",
                       title="Sales by Ship Mode Over Time",
                       color_discrete_sequence=QUALITATIVE,
                       labels={"sales":"Sales ($)","month":"Month","ship_mode":"Ship Mode"})
    fig_ship.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig_ship, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS & DIVISIONS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    # Division pie
    with c1:
        div_sales = df.groupby("division").agg(sales=("sales","sum"), profit=("gross_profit","sum")).reset_index()
        fig_div = px.pie(div_sales, names="division", values="sales",
                         title="Sales Share by Division",
                         color_discrete_sequence=QUALITATIVE, hole=0.45)
        fig_div.update_layout(**PLOTLY_LAYOUT)
        fig_div.update_traces(textfont_color="#e8e0f0", textinfo="percent+label")
        st.plotly_chart(fig_div, use_container_width=True)

    # Division margin bar
    with c2:
        div_sales["margin"] = (div_sales["profit"] / div_sales["sales"] * 100).round(1)
        fig_dm = px.bar(div_sales, x="division", y="margin",
                        title="Profit Margin by Division (%)",
                        color="margin", color_continuous_scale="Purples",
                        labels={"margin":"Margin (%)","division":"Division"},
                        text="margin")
        fig_dm.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_dm.update_layout(**PLOTLY_LAYOUT)
        fig_dm.update_coloraxes(showscale=False)
        st.plotly_chart(fig_dm, use_container_width=True)

    # Top 15 products by sales
    top_prods = (
        df.groupby("product_name")
          .agg(sales=("sales","sum"), profit=("gross_profit","sum"), units=("units","sum"))
          .sort_values("sales", ascending=False).head(15).reset_index()
    )
    top_prods["margin"] = (top_prods["profit"] / top_prods["sales"] * 100).round(1)
    fig_prod = px.bar(top_prods, x="sales", y="product_name", orientation="h",
                      color="margin", color_continuous_scale="Purples",
                      title="Top 15 Products by Revenue",
                      labels={"sales":"Sales ($)","product_name":"Product","margin":"Margin %"})
    fig_prod.update_layout(**{**PLOTLY_LAYOUT, "yaxis": dict(autorange="reversed", gridcolor="#2d1b4e")})
    st.plotly_chart(fig_prod, use_container_width=True)

    # Sales vs Profit scatter by product (top 30)
    scatter_df = (
        df.groupby("product_name")
          .agg(sales=("sales","sum"), profit=("gross_profit","sum"),
               units=("units","sum"), division=("division","first"))
          .reset_index().nlargest(30, "sales")
    )
    fig_scatter = px.scatter(
        scatter_df, x="sales", y="profit", size="units",
        color="division", hover_name="product_name",
        title="Sales vs Profit (top 30 products, bubble = units)",
        color_discrete_sequence=QUALITATIVE,
        labels={"sales":"Sales ($)","profit":"Gross Profit ($)"},
    )
    fig_scatter.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — REGIONAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    # Region sales bar
    with c1:
        reg = df.groupby("region").agg(sales=("sales","sum"), profit=("gross_profit","sum")).reset_index()
        reg["margin"] = (reg["profit"] / reg["sales"] * 100).round(1)
        fig_reg = px.bar(reg, x="region", y="sales", color="margin",
                         color_continuous_scale="Purples",
                         title="Sales by Region",
                         labels={"sales":"Sales ($)","region":"Region","margin":"Margin %"},
                         text_auto=".2s")
        fig_reg.update_layout(**PLOTLY_LAYOUT)
        fig_reg.update_coloraxes(showscale=False)
        st.plotly_chart(fig_reg, use_container_width=True)

    # Region margin sunburst
    with c2:
        sun_df = df.groupby(["region","division"]).agg(sales=("sales","sum")).reset_index()
        fig_sun = px.sunburst(sun_df, path=["region","division"], values="sales",
                              title="Sales Breakdown: Region → Division",
                              color="sales", color_continuous_scale="Purples")
        fig_sun.update_layout(**PLOTLY_LAYOUT)
        fig_sun.update_coloraxes(showscale=False)
        st.plotly_chart(fig_sun, use_container_width=True)

    # Top cities
    city_df = (
        df.groupby(["city","state_province","region"])
          .agg(sales=("sales","sum"), profit=("gross_profit","sum"))
          .reset_index().nlargest(20, "sales")
    )
    city_df["margin"] = (city_df["profit"] / city_df["sales"] * 100).round(1)
    fig_city = px.bar(city_df, x="sales", y="city", orientation="h",
                      color="region", title="Top 20 Cities by Revenue",
                      color_discrete_sequence=QUALITATIVE,
                      labels={"sales":"Sales ($)","city":"City","region":"Region"},
                      hover_data=["state_province","margin"])
    fig_city.update_layout(**{**PLOTLY_LAYOUT, "yaxis": dict(autorange="reversed", gridcolor="#2d1b4e")})
    st.plotly_chart(fig_city, use_container_width=True)

    # Region × Ship Mode heatmap
    heat = df.groupby(["region","ship_mode"]).agg(sales=("sales","sum")).reset_index()
    heat_pivot = heat.pivot(index="region", columns="ship_mode", values="sales").fillna(0)
    fig_heat = px.imshow(heat_pivot, color_continuous_scale="Purples",
                         title="Sales Heatmap: Region × Ship Mode",
                         labels={"color":"Sales ($)"}, text_auto=".2s",
                         aspect="auto")
    fig_heat.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔍 Filtered Data Explorer")
    search = st.text_input("Search product name", "")
    show_df = df if not search else df[df["product_name"].str.contains(search, case=False, na=False)]

    cols = ["order_date","order_id","product_name","division","region","city",
            "ship_mode","sales","units","gross_profit","cost","margin_pct"]
    st.dataframe(
        show_df[cols].sort_values("order_date", ascending=False).reset_index(drop=True),
        use_container_width=True, height=460,
        column_config={
            "sales":       st.column_config.NumberColumn("Sales ($)", format="$%.2f"),
            "gross_profit":st.column_config.NumberColumn("Gross Profit ($)", format="$%.2f"),
            "cost":        st.column_config.NumberColumn("Cost ($)", format="$%.2f"),
            "margin_pct":  st.column_config.NumberColumn("Margin %", format="%.1f%%"),
            "units":       st.column_config.NumberColumn("Units", format="%.0f"),
        }
    )
    st.caption(f"{len(show_df):,} rows shown")

    csv_out = show_df[cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered CSV", csv_out, "nassau_filtered.csv", "text/csv")
