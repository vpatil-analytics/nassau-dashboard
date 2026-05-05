import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_nassau_data.csv")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert date columns
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce')

    return df

df = load_data()

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("🔍 Filters")

region = st.sidebar.multiselect(
    "Select Region",
    options=df['region'].dropna().unique(),
    default=df['region'].dropna().unique()
)

division = st.sidebar.multiselect(
    "Select Division",
    options=df['division'].dropna().unique(),
    default=df['division'].dropna().unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['order_date'].min(), df['order_date'].max()]
)

# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered_df = df[
    (df['region'].isin(region)) &
    (df['division'].isin(division)) &
    (df['order_date'] >= pd.to_datetime(date_range[0])) &
    (df['order_date'] <= pd.to_datetime(date_range[1]))
]

# ----------------------------
# TITLE
# ----------------------------
st.title("📊 E-Commerce Sales Dashboard")
st.markdown("### Business Performance Overview")

# ----------------------------
# KPI CARDS
# ----------------------------
total_sales = filtered_df['sales'].sum()
total_orders = filtered_df['order_id'].nunique()
total_units = filtered_df['units'].sum()

# NEW KPIs
avg_order_value = total_sales / total_orders if total_orders != 0 else 0

avg_shipping_days = (
    (filtered_df['ship_date'] - filtered_df['order_date'])
    .dt.days
    .dropna()
    .mean()
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📦 Total Orders", total_orders)
col3.metric("🛒 Units Sold", int(total_units))
col4.metric("📈 Avg Order Value", f"${avg_order_value:,.2f}")
col5.metric("🚚 Avg Shipping Days", f"{avg_shipping_days:.1f} Days" if pd.notnull(avg_shipping_days) else "N/A")

# ----------------------------
# SALES TREND
# ----------------------------
st.subheader("📈 Sales Trend")

sales_trend = (
    filtered_df.groupby('order_date')['sales']
    .sum()
    .reset_index()
)

fig1 = px.line(
    sales_trend,
    x='order_date',
    y='sales',
    title="Sales Over Time"
)

st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# SALES BY DIVISION
# ----------------------------
st.subheader("📊 Sales by Division")

div_sales = (
    filtered_df.groupby('division')['sales']
    .sum()
    .reset_index()
)

fig2 = px.bar(
    div_sales,
    x='division',
    y='sales',
    text_auto=True,
    title="Division-wise Sales"
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# SALES BY REGION
# ----------------------------
st.subheader("🌍 Sales by Region")

region_sales = (
    filtered_df.groupby('region')['sales']
    .sum()
    .reset_index()
)

fig3 = px.pie(
    region_sales,
    names='region',
    values='sales',
    title="Region Contribution"
)

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# TOP PRODUCTS
# ----------------------------
st.subheader("🏆 Top 10 Products")

top_products = (
    filtered_df.groupby('product_name')['sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x='sales',
    y='product_name',
    orientation='h',
    title="Top Products"
)

st.plotly_chart(fig4, use_container_width=True)

# ----------------------------
# DATA TABLE
# ----------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered_df.head(100), use_container_width=True)
