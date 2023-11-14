import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

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

# Define the HTML template for the metric display
metric_template = """
<div style="padding: 10px; margin: 10px 0; border: 1px solid #eee; border-radius: 5px; text-align: center;">
    <span style="font-size: 0.85em; color: grey;">{label}</span><br>
    <span style="font-size: 2.5em; color: green; font-weight: bold;">{value}</span>
</div>
"""

# Create two columns for the metrics with custom HTML formatting
col1, col2 = st.columns(2)

with col1:
    # Total Spend
    st.markdown(metric_template.format(label="Total Spend", value=f"${total_spend:,.2f}"), unsafe_allow_html=True)

# Find the month with the highest spend
monthly_totals_df['YearMonth'] = monthly_totals_df['Month'].dt.to_period('M')
total_by_month = monthly_totals_df.groupby('YearMonth')['Total'].sum()
max_spend_month = total_by_month.idxmax().strftime('%B %Y')
max_spend_value = total_by_month.max()

with col2:
    # Month with the Highest Spend
    st.markdown(metric_template.format(label="Month with Highest Spend", value=f"{max_spend_month} (${max_spend_value:,.2f})"), unsafe_allow_html=True)

# Total amount spent per month (Area chart)
st.header("Total Amount Spent Per Month")
total_by_month_chart = total_by_month.reset_index()
total_by_month_chart['YearMonth'] = total_by_month_chart['YearMonth'].astype(str)
st.area_chart(total_by_month_chart.rename(columns={'YearMonth': 'index'}).set_index('index'))

# Invoice Total vs Supplier Name (Bar chart)
st.header("Invoice Total vs Supplier Name")
total_by_supplier = monthly_totals_df.groupby('SupplierName')['Total'].sum().sort_values(ascending=False)
st.bar_chart(total_by_supplier)

# Supplier who spent the most each month (Bar chart)
st.header("Top Supplier by Month")
# Group by YearMonth and SupplierName, then get the index of the max Total for each group
top_supplier_by_month = monthly_totals_df.loc[monthly_totals_df.groupby(['YearMonth', 'SupplierName'])['Total'].idxmax()]
top_supplier_by_month_chart = top_supplier_by_month.pivot_table(index='YearMonth', columns='SupplierName', values='Total', aggfunc='sum').fillna(0)
st.bar_chart(top_supplier_by_month_chart)

# Display the DataFrame - for verification or additional insights
st.header("Detailed Data View")
st.dataframe(monthly_totals_df.sort_values('Month'))
