import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# Set the directory where your Excel files are stored
directory = 'Excel'

# Initialize the list of suppliers
suppliers = ['Deme Construction LLC', 'Ground Service Technology', 'Gunsight Construction Companies', 'Knight Trenching and Excavating', 'Onyx Corporation', 'Overture Promotions', 'Raymow Construction']

# Sidebar - Supplier selection
selected_supplier = st.sidebar.selectbox('Select a Supplier', suppliers)

# Main panel
st.title(selected_supplier)
st.divider()

# Define the HTML template for the metric display
metric_template = """
<div style="padding: 10px; margin: 10px 0; border: 1px solid #eee; border-radius: 5px; text-align: center;">
    <span style="font-size: 0.85em; color: grey;">{label}</span><br>
    <span style="font-size: 4.5em; color: green; font-weight: bold;">{value}</span>
</div>
"""

# Function to load data
def load_data(supplier_name):
    monthly_totals_path = os.path.join(directory, supplier_name, 'monthly_totals.csv')
    combined_data_path = os.path.join(directory, supplier_name, 'combined_data.csv')

    monthly_totals_df = pd.read_csv(monthly_totals_path)
    combined_data_df = pd.read_csv(combined_data_path)
    
    # Ensure the 'Month' column exists and is in datetime format
    if 'Month' in monthly_totals_df.columns:
        monthly_totals_df['Month'] = pd.to_datetime(monthly_totals_df['Month']).dt.strftime('%b') # Convert to month abbreviation
    if 'Month' in combined_data_df.columns:
        combined_data_df['Month'] = pd.to_datetime(combined_data_df['Month']).dt.strftime('%b')

    return monthly_totals_df, combined_data_df

# Load the data for selected supplier
monthly_totals_df, combined_data_df = load_data(selected_supplier)

if not monthly_totals_df.empty and not combined_data_df.empty:
    # Calculate total spend and month count
    total_spend = monthly_totals_df['Total'].sum()
    total_month_count = monthly_totals_df['Month'].nunique()

    # Create two columns for the metrics with custom HTML formatting
    col1, col2 = st.columns(2)

    with col1:
        # Total Spend
        st.markdown(metric_template.format(label="Total Spend", value=f"${total_spend:,.0f}"), unsafe_allow_html=True)
    with col2:
        # Total Month Count
        st.markdown(metric_template.format(label="Total Month Count", value=f"{total_month_count}"), unsafe_allow_html=True)

    # Plot the line graph for monthly spend
    st.markdown("### Monthly Spend Over Time")
    monthly_totals_df = monthly_totals_df.set_index('Month')
    st.line_chart(monthly_totals_df['Total'], use_container_width=True)

    # Option to select a month and display the DataFrame
    st.markdown("### Detailed Spend by Month")
    months = monthly_totals_df.index.unique()
    selected_month = st.selectbox('Select a Month', months)

    # Ensure the 'Month' column exists before filtering
    if 'Month' in combined_data_df.columns:
        monthly_data = combined_data_df[combined_data_df['Month'] == selected_month]
        st.dataframe(monthly_data)
    else:
        st.error("The 'Month' column is not present in the combined data.")
else:
    st.error('Data not available for the selected supplier.')
