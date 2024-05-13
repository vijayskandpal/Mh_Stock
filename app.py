"""Module providing a function printing python version."""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Define the scopes for Google Sheets API
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Load service account key from Streamlit secrets
skey = st.secrets["gcp_service_account"]

# Create credentials object from the service account key
credentials = Credentials.from_service_account_info(skey, scopes=scopes)

# Authorize the client using the credentials
client = gspread.authorize(credentials)

sheet_id = "1uG-cGTqzzofZCNTLh1sb3tE4GaaofQK-JA2EtucVsEo"
workbook = client.open_by_key(sheet_id)

# Cache data loading functions


@st.cache_data
def load_data_from_worksheet(worksheet_name, expected_headers):
    worksheet = workbook.worksheet(worksheet_name)
    data = pd.DataFrame(worksheet.get_all_records(
        expected_headers=expected_headers))
    return data


# Load data from DATA worksheet
dataFrame = load_data_from_worksheet("DATA", ["IN/OUT", "ITEM_CODE", "IN/OUT QTY", "BILL_INVNO_FAULTY_SAMPLE",
                                              "BILL_DATE", "MTRL_INOUT_DATE", "NAME_CLIENT", "REMARKS",
                                              "CLOSING_STOCK", "ITEM_NAME"])

# Load data from Item_List worksheet
dataItem_List = load_data_from_worksheet("Item_List", ["Net", "Item_Code", "Model No", "Particulars",
                                                       "BRAND", "Category", "Box Location", "Physical Date",
                                                       "MIN QTY", "MAX QTY"])
dataItem_List = dataItem_List.loc[:, ["Net", "Item_Code", "Model No", "Particulars",
                                      "BRAND", "Category", "MIN QTY", "MAX QTY"]]

# Streamlit tab option active
tab1, tab2 = st.tabs(["Closing Stock", "Item_List"])

# Closing Stock
with tab1:
    cl = dataFrame.iloc[:, [1, 9, 8]]
    cl = cl[cl['CLOSING_STOCK'] > 0]
    cl_val = cl.sort_values(by='ITEM_CODE', ascending=True)
    closing_stock = cl_val.drop_duplicates().reset_index(drop=True)
    closing_stock_Total = closing_stock['CLOSING_STOCK'].sum()
    # Create a new DataFrame row for the total
    grand_total_row = pd.DataFrame({'ITEM_CODE': 'Grand Total', 'ITEM_NAME': '',
                                    'CLOSING_STOCK': closing_stock_Total}, index=[0])
    # Append the grand total row to the closing stock DataFrame
    closing_stock = pd.concat(
        [closing_stock, grand_total_row], ignore_index=True)
    st.metric(label="Closing Stock", value=closing_stock_Total)
    st.table(closing_stock)

with tab2:
    st.write('Items with Closing Stock > Max Quantity')
    filtered_data = dataItem_List[(dataItem_List['Net'] > dataItem_List['MAX QTY']) & (
        dataItem_List['MAX QTY'] != 0)].reset_index(drop=True)
    st.dataframe(filtered_data)



