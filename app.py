import streamlit as st
import pandas as pd
import os
st.set_page_config(layout="wide")
# Set the directory where your Excel files are stored
directory = 'Excel'

# Initialize the list of suppliers
suppliers = ['Deme', 'GroundService', 'Gunsight', 'Knight', 'Onyx', 'Overture', 'Raymow']

# Sidebar - Supplier selection
selected_supplier = st.sidebar.selectbox('Select a Supplier', suppliers)


# Main panel
st.title(selected_supplier)

# Function to load data
def load_data(supplier_name):
    monthly_totals_path = os.path.join(directory, supplier_name, 'monthly_totals.csv')
    combined_data_path = os.path.join(directory, supplier_name, 'combined_data.csv')

    monthly_totals_df = pd.read_csv(monthly_totals_path)
    combined_data_df = pd.read_csv(combined_data_path)
    
    # Ensure the 'Month' column exists and is in datetime format
    if 'Month' in monthly_totals_df.columns:
        monthly_totals_df['Month'] = pd.to_datetime(monthly_totals_df['Month'])
        monthly_totals_df['Month'] = monthly_totals_df['Month'].dt.strftime('%b') # Convert to month abbreviation
    if 'Month' in combined_data_df.columns:
        combined_data_df['Month'] = pd.to_datetime(combined_data_df['Month'])
        combined_data_df['Month'] = combined_data_df['Month'].dt.strftime('%b')

    return monthly_totals_df, combined_data_df

# Load the data for selected supplier
monthly_totals_df, combined_data_df = load_data(selected_supplier)

if monthly_totals_df is not None and combined_data_df is not None:
    # Display total spend
    total_spend = monthly_totals_df['Total'].sum()
    st.markdown(f"**Total Spend: ${total_spend:,.0f}**")

    # Plot the line graph for monthly spend
    st.markdown("### Monthly Spend Over Time")
    monthly_totals_df = monthly_totals_df.set_index('Month')
    st.line_chart(monthly_totals_df['Total'], use_container_width=True)  # Streamlit will auto-size the graph

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
