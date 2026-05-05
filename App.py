import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Nassau Confections · Sales Dashboard",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0f0f1a; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a0a2e,#16213e); border-right:1px solid #2d1b4e; }
[data-testid="stSidebar"] * { color:#c8b8e8 !important; }
.kpi { background:linear-gradient(135deg,#1e1040,#2d1b69); border:1px solid #4a2f8a;
       border-radius:16px; padding:18px; text-align:center; margin-bottom:8px; }
.kpi-label { font-size:12px; color:#9b8fc0; letter-spacing:1px; text-transform:uppercase; }
.kpi-value { font-size:28px; font-weight:800; color:#d4b8ff; }
h1,h2,h3 { color:#b89ce0 !important; }
footer, #MainMenu { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

BG   = "rgba(0,0,0,0)"
GRID = "#2d1b4e"
FONT = dict(color="#c8b8e8", family="Inter,sans-serif", size=12)
BASE = dict(paper_bgcolor=BG, plot_bgcolor=BG, font=FONT,
            margin=dict(l=40,r=20,t=40,b=40),
            legend=dict(bgcolor=BG),
            xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
            yaxis=dict(gridcolor=GRID, zerolinecolor=GRID))
COL  = ["#a855f7","#6366f1","#ec4899","#06b6d4","#10b981","#f59e0b","#f87171"]

@st.cache_data
def load():
    df = pd.read_csv("cleaned_nassau_data.csv", parse_dates=["order_date","ship_date"])
    df["month"]   = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["year"]    = df["order_date"].dt.year.astype(int).astype(str)
    df["quarter"] = df["order_date"].dt.to_period("Q").astype(str)
    df["margin"]  = (df["gross_profit"] / df["sales"] * 100).round(1)
    return df

df_raw = load()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 Nassau Confections")
    st.markdown("---")
    years   = sorted(df_raw["year"].unique())
    divs    = sorted(df_raw["division"].unique())
    regions = sorted(df_raw["region"].unique())
    ships   = sorted(df_raw["ship_mode"].unique())

    sel_y = st.multiselect("📅 Year",      years,   default=years)
    sel_d = st.multiselect("🏭 Division",  divs,    default=divs)
    sel_r = st.multiselect("🌍 Region",    regions, default=regions)
    sel_s = st.multiselect("🚚 Ship Mode", ships,   default=ships)
    st.markdown("---")
    st.caption("10,194 orders · 2024–2025")

df = df_raw[
    df_raw["year"].isin(sel_y) &
    df_raw["division"].isin(sel_d) &
    df_raw["region"].isin(sel_r) &
    df_raw["ship_mode"].isin(sel_s)
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🍫 Nassau Confections — Sales Dashboard")
st.caption(f"{len(df):,} transactions · {df['order_date'].min().date()} → {df['order_date'].max().date()}")

# ── KPIs ─────────────────────────────────────────────────────────────────────
sales  = df["sales"].sum()
profit = df["gross_profit"].sum()
units  = df["units"].sum()
orders = df["order_id"].nunique()
margin = (profit / sales * 100) if sales else 0
cost   = df["cost"].sum()

c1,c2,c3,c4,c5,c6 = st.columns(6)
for col, label, val in zip(
    [c1,c2,c3,c4,c5,c6],
    ["💰 Total Sales","📈 Gross Profit","📦 Units","🧾 Orders","📊 Avg Margin","💸 Total Cost"],
    [f"${sales:,.0f}", f"${profit:,.0f}", f"{units:,.0f}", f"{orders:,}", f"{margin:.1f}%", f"${cost:,.0f}"]
):
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>',
                 unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(["📈 Sales Trends","🍫 Products & Divisions","🌍 Regional","📋 Data"])

# ─── TAB 1 ───────────────────────────────────────────────────────────────────
with t1:
    monthly = df.groupby("month").agg(
        sales=("sales","sum"), profit=("gross_profit","sum"), units=("units","sum")
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["month"], y=monthly["sales"],
                         name="Sales", marker_color="#7c3aed", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["profit"],
                             name="Gross Profit", line=dict(color="#a855f7",width=3),
                             mode="lines+markers"), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["units"],
                             name="Units", line=dict(color="#06b6d4",width=2,dash="dot"),
                             mode="lines"), secondary_y=True)
    fig.update_layout(title="Monthly Sales, Profit & Units", **BASE)
    fig.update_yaxes(title_text="$ Value", secondary_y=False, gridcolor=GRID)
    fig.update_yaxes(title_text="Units",   secondary_y=True,  gridcolor=GRID)
    st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        qdf = df.groupby("quarter").agg(sales=("sales","sum")).reset_index()
        fig2 = px.bar(qdf, x="quarter", y="sales", title="Quarterly Revenue",
                      color="sales", color_continuous_scale="Purples",
                      labels={"sales":"Sales ($)","quarter":"Quarter"})
        fig2.update_layout(**BASE)
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with cb:
        yoy = df.groupby(["year","month"]).agg(sales=("sales","sum")).reset_index()
        yoy["mon"] = yoy["month"].dt.strftime("%b")
        order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig3 = px.line(yoy, x="mon", y="sales", color="year", title="Year-over-Year Sales",
                       color_discrete_sequence=COL, labels={"sales":"Sales ($)","mon":"Month"},
                       category_orders={"mon": order})
        fig3.update_layout(**BASE)
        st.plotly_chart(fig3, use_container_width=True)

    sm = df.groupby(["month","ship_mode"]).agg(sales=("sales","sum")).reset_index()
    fig4 = px.area(sm, x="month", y="sales", color="ship_mode",
                   title="Sales by Ship Mode Over Time", color_discrete_sequence=COL,
                   labels={"sales":"Sales ($)","month":"Month","ship_mode":"Ship Mode"})
    fig4.update_layout(**BASE)
    st.plotly_chart(fig4, use_container_width=True)

# ─── TAB 2 ───────────────────────────────────────────────────────────────────
with t2:
    da, db = st.columns(2)
    divdf = df.groupby("division").agg(sales=("sales","sum"), profit=("gross_profit","sum")).reset_index()
    divdf["margin"] = (divdf["profit"] / divdf["sales"] * 100).round(1)

    with da:
        fig5 = px.pie(divdf, names="division", values="sales", title="Sales by Division",
                      color_discrete_sequence=COL, hole=0.45)
        fig5.update_layout(**BASE)
        fig5.update_traces(textinfo="percent+label", textfont_color="#e8e0f0")
        st.plotly_chart(fig5, use_container_width=True)

    with db:
        fig6 = px.bar(divdf, x="division", y="margin", title="Profit Margin by Division (%)",
                      color="margin", color_continuous_scale="Purples",
                      labels={"margin":"Margin (%)","division":"Division"}, text="margin")
        fig6.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig6.update_layout(**BASE)
        fig6.update_coloraxes(showscale=False)
        st.plotly_chart(fig6, use_container_width=True)

    top = (df.groupby("product_name")
             .agg(sales=("sales","sum"), profit=("gross_profit","sum"), units=("units","sum"))
             .sort_values("sales", ascending=False).head(15).reset_index())
    top["margin"] = (top["profit"] / top["sales"] * 100).round(1)
    fig7 = px.bar(top, x="sales", y="product_name", orientation="h",
                  color="margin", color_continuous_scale="Purples",
                  title="Top 15 Products by Revenue",
                  labels={"sales":"Sales ($)","product_name":"Product","margin":"Margin %"})
    layout7 = {**BASE, "yaxis": dict(autorange="reversed", gridcolor=GRID)}
    fig7.update_layout(**layout7)
    fig7.update_coloraxes(showscale=False)
    st.plotly_chart(fig7, use_container_width=True)

    scat = (df.groupby("product_name")
              .agg(sales=("sales","sum"), profit=("gross_profit","sum"),
                   units=("units","sum"), division=("division","first"))
              .reset_index().nlargest(30,"sales"))
    fig8 = px.scatter(scat, x="sales", y="profit", size="units", color="division",
                      hover_name="product_name", color_discrete_sequence=COL,
                      title="Sales vs Profit — Top 30 Products (bubble = units)",
                      labels={"sales":"Sales ($)","profit":"Gross Profit ($)"})
    fig8.update_layout(**BASE)
    st.plotly_chart(fig8, use_container_width=True)

# ─── TAB 3 ───────────────────────────────────────────────────────────────────
with t3:
    ra, rb = st.columns(2)
    regdf = df.groupby("region").agg(sales=("sales","sum"), profit=("gross_profit","sum")).reset_index()
    regdf["margin"] = (regdf["profit"] / regdf["sales"] * 100).round(1)

    with ra:
        fig9 = px.bar(regdf, x="region", y="sales", color="margin",
                      color_continuous_scale="Purples", title="Sales by Region",
                      labels={"sales":"Sales ($)","region":"Region"}, text_auto=".2s")
        fig9.update_layout(**BASE)
        fig9.update_coloraxes(showscale=False)
        st.plotly_chart(fig9, use_container_width=True)

    with rb:
        sundf = df.groupby(["region","division"]).agg(sales=("sales","sum")).reset_index()
        fig10 = px.sunburst(sundf, path=["region","division"], values="sales",
                            title="Region → Division Breakdown",
                            color="sales", color_continuous_scale="Purples")
        fig10.update_layout(**BASE)
        fig10.update_coloraxes(showscale=False)
        st.plotly_chart(fig10, use_container_width=True)

    citydf = (df.groupby(["city","state_province","region"])
                .agg(sales=("sales","sum"), profit=("gross_profit","sum"))
                .reset_index().nlargest(20,"sales"))
    citydf["margin"] = (citydf["profit"] / citydf["sales"] * 100).round(1)
    fig11 = px.bar(citydf, x="sales", y="city", orientation="h", color="region",
                   title="Top 20 Cities by Revenue", color_discrete_sequence=COL,
                   labels={"sales":"Sales ($)","city":"City"}, hover_data=["state_province","margin"])
    layout11 = {**BASE, "yaxis": dict(autorange="reversed", gridcolor=GRID)}
    fig11.update_layout(**layout11)
    st.plotly_chart(fig11, use_container_width=True)

    heat = df.groupby(["region","ship_mode"]).agg(sales=("sales","sum")).reset_index()
    pivot = heat.pivot(index="region", columns="ship_mode", values="sales").fillna(0)
    fig12 = px.imshow(pivot, color_continuous_scale="Purples", text_auto=".2s",
                      title="Heatmap: Region × Ship Mode", labels={"color":"Sales ($)"})
    fig12.update_layout(**BASE)
    st.plotly_chart(fig12, use_container_width=True)

# ─── TAB 4 ───────────────────────────────────────────────────────────────────
with t4:
    st.markdown("### 🔍 Data Explorer")
    search = st.text_input("Search product name", "")
    show = df if not search else df[df["product_name"].str.contains(search, case=False, na=False)]
    cols = ["order_date","order_id","product_name","division","region","city",
            "ship_mode","sales","units","gross_profit","cost","margin"]
    st.dataframe(
        show[cols].sort_values("order_date", ascending=False).reset_index(drop=True),
        use_container_width=True, height=460,
        column_config={
            "sales":       st.column_config.NumberColumn("Sales ($)",       format="$%.2f"),
            "gross_profit":st.column_config.NumberColumn("Gross Profit ($)", format="$%.2f"),
            "cost":        st.column_config.NumberColumn("Cost ($)",        format="$%.2f"),
            "margin":      st.column_config.NumberColumn("Margin %",        format="%.1f%%"),
            "units":       st.column_config.NumberColumn("Units",           format="%.0f"),
        }
    )
    st.caption(f"{len(show):,} rows")
    st.download_button("⬇️ Download CSV", show[cols].to_csv(index=False).encode(), "nassau_filtered.csv", "text/csv")
