import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("DASHBOARD")
# Set the directory where your Excel files are stored
directory = 'Excel'

# Load the data
@st.cache_data
def load_data():
    monthly_totals_path = os.path.join(directory, 'monthly_totals_final.csv')
    monthly_totals_df = pd.read_csv(monthly_totals_path)
    monthly_totals_df['Month'] = pd.to_datetime(monthly_totals_df['Month'], errors='coerce')
    return monthly_totals_df

monthly_totals_df = load_data()

# Drop any NaT values that resulted from conversion errors
monthly_totals_df.dropna(subset=['Month'], inplace=True)

# Calculate the total money spent entirely
total_spend = monthly_totals_df['Total'].sum()

# Load the combined_final.csv data
@st.cache_data
def load_combined_final():
    combined_final_path = os.path.join(directory, 'combine_final.csv')
    combined_final_df = pd.read_csv(combined_final_path)
    combined_final_df['InvoiceDate'] = pd.to_datetime(combined_final_df['InvoiceDate'], errors='coerce')
    combined_final_df['Month'] = combined_final_df['InvoiceDate'].dt.strftime('%b')  # Use month abbreviation for display
    return combined_final_df

combined_final_df = load_combined_final()

# Drop any NaT values that resulted from conversion errors
monthly_totals_df.dropna(subset=['Month'], inplace=True)
combined_final_df.dropna(subset=['InvoiceDate'], inplace=True)

# Calculate the total money spent entirely
total_spend = monthly_totals_df['Total'].sum()

# Calculate the total number of products ordered
total_products_ordered = len(combined_final_df)
# Define the HTML template for the metric display
metric_template = """
<div style="padding: 10px; margin: 10px 0; border: 1px solid transparent; border-radius: 5px; text-align: center;">
    <span style="font-size: 0.8em; color: green;float:left">{label}</span><br>
    <span style="font-size: 2em; color: darkgreen; font-weight: bold;float:left">{value}</span>
</div>
"""

# Create two columns for the metrics with custom HTML formatting
col1, col2,col3 = st.columns(3)

with col1:
    # Total Spend
    st.markdown(metric_template.format(label="Total Spend", value=f"${total_spend:,.2f}"), unsafe_allow_html=True)

# Find the month with the highest spend
monthly_totals_df['YearMonth'] = monthly_totals_df['Month'].dt.to_period('M')
total_by_month = monthly_totals_df.groupby('YearMonth')['Total'].sum()
max_spend_month = total_by_month.idxmax().strftime('%B')
max_spend_value = total_by_month.max()

with col2:
    # Month with the Highest Spend
    st.markdown(metric_template.format(label="Month with Highest Spend", value=f"{max_spend_month} (${max_spend_value:,.2f})"), unsafe_allow_html=True)

with col3:
    # Total Products Ordered
    st.markdown(metric_template.format(label="Total Products Ordered", value=f"{total_products_ordered}"), unsafe_allow_html=True)
st.divider()


# Total amount spent per month (Area chart)
st.markdown("**Total Amount Spent Per Month**")
total_by_month_chart = total_by_month.reset_index()
total_by_month_chart['YearMonth'] = total_by_month_chart['YearMonth'].astype(str)
st.area_chart(total_by_month_chart.rename(columns={'YearMonth': 'index'}).set_index('index'),color="#8fadff")

# Invoice Total vs Supplier Name (Bar chart)

total_by_supplier = monthly_totals_df.groupby('SupplierName')['Total'].sum().sort_values(ascending=False)
top_supplier_by_month = monthly_totals_df.loc[monthly_totals_df.groupby(['YearMonth', 'SupplierName'])['Total'].idxmax()]
top_supplier_by_month_chart = top_supplier_by_month.pivot_table(index='YearMonth', columns='SupplierName', values='Total', aggfunc='sum').fillna(0)


top_supplier_by_month['Month'] = pd.to_datetime(top_supplier_by_month['Month']).dt.strftime('%b')

# Now create the pivot table for the bar chart
top_supplier_by_month_chart = top_supplier_by_month.pivot_table(index='Month', columns='SupplierName', values='Total', aggfunc='sum').fillna(0)

col1,col2 = st.columns(2)

with col1:
    st.markdown("**Invoice Total vs Supplier Name**")
    st.bar_chart(total_by_supplier)
with col2:
    st.markdown("**Top Supplier by Month**")
    st.bar_chart(top_supplier_by_month_chart)


# Total products ordered each month for any supplier (Graph)
st.markdown("**Total Products Ordered Each Month**")
products_per_month = combined_final_df.groupby('Month').size()
st.line_chart(products_per_month,color="#667aff")

# Detailed DataFrame view with a filter option by month
st.markdown("**Detailed Products Ordered by Month**")
selected_month = st.selectbox("Filter by month", options=combined_final_df['Month'].unique(), index=0)
filtered_data = combined_final_df[combined_final_df['Month'] == selected_month]
st.dataframe(filtered_data)