import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Nassau Confections", page_icon="🍫", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f0f1a; }
[data-testid="stSidebar"] { background: #1a1035; border-right: 1px solid #2d1b4e; }
[data-testid="stSidebar"] * { color: #c8b8e8 !important; }
.kpi { background: #1e1040; border: 1px solid #4a2f8a; border-radius: 12px;
       padding: 16px; text-align: center; margin-bottom: 8px; }
.kpi-label { font-size: 11px; color: #9b8fc0; text-transform: uppercase; letter-spacing: 1px; }
.kpi-value { font-size: 26px; font-weight: 800; color: #d4b8ff; }
footer, #MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

BG   = "rgba(0,0,0,0)"
GRID = "#2d1b4e"
BASE = dict(paper_bgcolor=BG, plot_bgcolor=BG,
            font=dict(color="#c8b8e8", size=12),
            margin=dict(l=30, r=20, t=40, b=30),
            xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID),
            legend=dict(bgcolor=BG))
COLORS = ["#9333ea","#6366f1","#f472b6","#22d3ee","#34d399","#fbbf24"]

@st.cache_data
def load():
    df = pd.read_csv("cleaned_nassau_data.csv", parse_dates=["order_date"])
    df["year"]    = df["order_date"].dt.year.astype(int).astype(str)
    df["month"]   = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["quarter"] = df["order_date"].dt.to_period("Q").astype(str)
    df["margin"]  = (df["gross_profit"] / df["sales"] * 100).round(1)
    return df

df_all = load()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 Nassau Confections")
    st.markdown("---")
    sel_year   = st.multiselect("📅 Year",      sorted(df_all["year"].unique()),     default=sorted(df_all["year"].unique()))
    sel_div    = st.multiselect("🏭 Division",  sorted(df_all["division"].unique()), default=sorted(df_all["division"].unique()))
    sel_region = st.multiselect("🌍 Region",    sorted(df_all["region"].unique()),   default=sorted(df_all["region"].unique()))
    sel_ship   = st.multiselect("🚚 Ship Mode", sorted(df_all["ship_mode"].unique()),default=sorted(df_all["ship_mode"].unique()))

df = df_all[
    df_all["year"].isin(sel_year) &
    df_all["division"].isin(sel_div) &
    df_all["region"].isin(sel_region) &
    df_all["ship_mode"].isin(sel_ship)
]

if df.empty:
    st.warning("No data for selected filters.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🍫 Nassau Confections — Sales Dashboard")
st.caption(f"{len(df):,} transactions · {df['order_date'].min().date()} → {df['order_date'].max().date()}")
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
sales  = df["sales"].sum()
profit = df["gross_profit"].sum()
units  = df["units"].sum()
orders = df["order_id"].nunique()
margin = profit / sales * 100
cost   = df["cost"].sum()

for col, lbl, val in zip(
    st.columns(6),
    ["💰 Revenue", "📈 Gross Profit", "📦 Units", "🧾 Orders", "📊 Margin", "💸 Cost"],
    [f"${sales:,.0f}", f"${profit:,.0f}", f"{units:,.0f}", f"{orders:,}", f"{margin:.1f}%", f"${cost:,.0f}"]
):
    col.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div></div>',
                 unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(["📈 Trends", "🍫 Products", "🌍 Regional", "📋 Data"])

# ── TAB 1: Trends ─────────────────────────────────────────────────────────────
with t1:
    # Monthly revenue bar + profit line
    monthly = df.groupby("month").agg(Sales=("sales","sum"), Profit=("gross_profit","sum")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly["month"], y=monthly["Sales"],
                         name="Revenue", marker_color="#7c3aed", opacity=0.85))
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["Profit"],
                             name="Profit", line=dict(color="#f472b6", width=3),
                             mode="lines+markers", marker=dict(size=6)))
    fig.update_layout(title="Monthly Revenue & Profit", **BASE)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        # Quarterly
        qdf = df.groupby("quarter").agg(Sales=("sales","sum"), Profit=("gross_profit","sum")).reset_index()
        fig2 = px.bar(qdf, x="quarter", y=["Sales","Profit"], barmode="group",
                      title="Quarterly Sales vs Profit",
                      color_discrete_sequence=["#7c3aed","#f472b6"],
                      labels={"value":"Amount ($)","quarter":"Quarter","variable":"Metric"})
        fig2.update_layout(**BASE)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        # Ship mode over time
        sm = df.groupby(["month","ship_mode"]).agg(Sales=("sales","sum")).reset_index()
        fig3 = px.area(sm, x="month", y="Sales", color="ship_mode",
                       title="Revenue by Ship Mode",
                       color_discrete_sequence=COLORS,
                       labels={"Sales":"Revenue ($)","month":"Month","ship_mode":"Ship Mode"})
        fig3.update_layout(**BASE)
        fig3.update_traces(opacity=0.75)
        st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: Products ───────────────────────────────────────────────────────────
with t2:
    c1, c2 = st.columns([3, 2])

    with c1:
        prod = df.groupby("product_name").agg(
            Sales=("sales","sum"), Profit=("gross_profit","sum"), Units=("units","sum")
        ).reset_index().sort_values("Sales")
        prod["Margin"] = (prod["Profit"] / prod["Sales"] * 100).round(1)
        fig4 = px.bar(prod, x="Sales", y="product_name", orientation="h",
                      color="Margin", color_continuous_scale="Purples",
                      title="Products by Revenue",
                      labels={"Sales":"Revenue ($)","product_name":"Product","Margin":"Margin %"})
        fig4.update_layout(**{**BASE, "yaxis": dict(gridcolor=GRID)},
                           coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    with c2:
        # Division donut
        div = df.groupby("division").agg(Sales=("sales","sum")).reset_index()
        fig5 = px.pie(div, names="division", values="Sales", hole=0.5,
                      title="Revenue by Division",
                      color_discrete_sequence=COLORS)
        fig5.update_layout(**BASE)
        fig5.update_traces(textinfo="percent+label", textfont_color="#e8e0f0")
        st.plotly_chart(fig5, use_container_width=True)

        # Division margin bars
        div2 = df.groupby("division").agg(
            Sales=("sales","sum"), Profit=("gross_profit","sum")
        ).reset_index()
        div2["Margin"] = (div2["Profit"] / div2["Sales"] * 100).round(1)
        fig6 = px.bar(div2, x="division", y="Margin",
                      title="Margin % by Division",
                      color="Margin", color_continuous_scale="Purples",
                      labels={"Margin":"Margin (%)","division":"Division"},
                      text="Margin")
        fig6.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig6.update_layout(**BASE, coloraxis_showscale=False)
        st.plotly_chart(fig6, use_container_width=True)

# ── TAB 3: Regional ───────────────────────────────────────────────────────────
with t3:
    c1, c2 = st.columns(2)

    with c1:
        reg = df.groupby("region").agg(Sales=("sales","sum"), Profit=("gross_profit","sum")).reset_index()
        reg["Margin"] = (reg["Profit"] / reg["Sales"] * 100).round(1)
        fig7 = px.bar(reg, x="region", y="Sales", color="Margin",
                      color_continuous_scale="Purples", title="Revenue by Region",
                      labels={"Sales":"Revenue ($)","region":"Region"}, text_auto=".2s")
        fig7.update_layout(**BASE, coloraxis_showscale=False)
        st.plotly_chart(fig7, use_container_width=True)

    with c2:
        sun = df.groupby(["region","division"]).agg(Sales=("sales","sum")).reset_index()
        fig8 = px.sunburst(sun, path=["region","division"], values="Sales",
                           title="Region → Division Breakdown",
                           color="Sales", color_continuous_scale="Purples")
        fig8.update_layout(**BASE, coloraxis_showscale=False)
        st.plotly_chart(fig8, use_container_width=True)

    # Top 10 cities
    cities = df.groupby(["city","region"]).agg(Sales=("sales","sum")).reset_index()
    cities = cities.nlargest(10,"Sales")
    fig9 = px.bar(cities, x="Sales", y="city", orientation="h", color="region",
                  title="Top 10 Cities by Revenue", color_discrete_sequence=COLORS,
                  labels={"Sales":"Revenue ($)","city":"City"})
    fig9.update_layout(**{**BASE, "yaxis": dict(gridcolor=GRID, autorange="reversed")})
    st.plotly_chart(fig9, use_container_width=True)

# ── TAB 4: Data ───────────────────────────────────────────────────────────────
with t4:
    search = st.text_input("🔍 Search product", "")
    cols   = ["order_date","product_name","division","region","city","ship_mode",
              "sales","units","gross_profit","cost","margin"]
    show   = df[cols] if not search else df[df["product_name"].str.contains(search, case=False, na=False)][cols]
    st.dataframe(
        show.sort_values("order_date", ascending=False).reset_index(drop=True),
        use_container_width=True, height=420,
        column_config={
            "sales":       st.column_config.NumberColumn("Sales ($)",  format="$%.2f"),
            "gross_profit":st.column_config.NumberColumn("Profit ($)", format="$%.2f"),
            "cost":        st.column_config.NumberColumn("Cost ($)",   format="$%.2f"),
            "margin":      st.column_config.NumberColumn("Margin %",   format="%.1f%%"),
            "units":       st.column_config.NumberColumn("Units",      format="%.0f"),
        }
    )
    st.caption(f"{len(show):,} rows")
    st.download_button("⬇️ Download CSV",
                       show.to_csv(index=False).encode(),
                       "nassau_filtered.csv", "text/csv")
