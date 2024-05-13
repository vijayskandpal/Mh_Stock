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

# Fetch data from DATA worksheet
dfSheetData = workbook.worksheet("DATA")

dataFrame = pd.DataFrame(dfSheetData.get_all_records(
    expected_headers=["IN/OUT", "ITEM_CODE",
                      "IN/OUT QTY", "BILL_INVNO_FAULTY_SAMPLE", "BILL_DATE",
                      "MTRL_INOUT_DATE", "NAME_CLIENT", "REMARKS",
                      "CLOSING_STOCK", "ITEM_NAME"]))


# Fetch data from Item_List worksheet
dfSheetItem_List = workbook.worksheet("Item_List")
dataItem_List = pd.DataFrame(dfSheetItem_List.get_all_records(
    expected_headers=["Net", "Item_Code", "Model No", "Particulars",
                      "BRAND", "Category", "Box Location", "Physical Date",
                      "MIN QTY", "MAX QTY"]))
dataItem_List = dataItem_List.loc[:, ["Net", "Item_Code", "Model No", "Particulars",
                                      "BRAND", "Category", "MIN QTY", "MAX QTY"]]


# stremlit tab option active
tab1, tab2 = st.tabs(["Closing Stock", "Item_List"])


dataFrame = dataFrame.iloc[:, range(0, 10)]
# Assuming df is your DataFrame containing the data
dataFrame['BILL_DATE'] = pd.to_datetime(
    dataFrame['BILL_DATE'], format='%d-%b-%y')
dataFrame['MTRL_INOUT_DATE'] = pd.to_datetime(
    dataFrame['MTRL_INOUT_DATE'], format='%d-%b-%y')


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
    st.write('hello')

