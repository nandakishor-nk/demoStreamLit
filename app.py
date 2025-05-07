import streamlit as st
import pandas as pd
import os
from azure.storage.blob import BlobServiceClient # type: ignore
from datetime import datetime
from io import BytesIO
 
# Azure Blob Configs
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=demohcp;AccountKey=HJzqp4ZJ4UCtlll1RESBLKlnDOigGrDxCiOUwnlqyH5roPtEhAsK6FlCjaG2A8Ziu2qEdty4tuMg+AStduVJpA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "excel-files"
 
# Init blob service
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
 
# Ensure container exists
try:
    container_client.create_container()
except Exception:
    pass
 
def upload_to_blob(file_name, data):
    blob_client = container_client.get_blob_client(file_name)
    blob_client.upload_blob(data, overwrite=True)
 
def list_output_files():
    return [blob.name for blob in container_client.list_blobs() if blob.name.startswith("output_")]

def download_blob(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client.download_blob().readall()
 
def process_files(file1, file2):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    return df1
    # # Sample processing: merge by first common column
    # key = list(set(df1.columns).intersection(set(df2.columns)))[0]
    # result_df = pd.merge(df1, df2, on=key, how='inner')
    # return result_df
 
st.set_page_config(page_title="Excel Processor", layout="wide")
 
pages = ["Main", "History"]
page = st.sidebar.selectbox("Select a page", pages)
 
if page == "Main":
    st.title("Excel File Processor")
 
    file1 = st.file_uploader("Upload first Excel file", type=["xlsx"])
    file2 = st.file_uploader("Upload second Excel file", type=["xlsx"])
 
    if file1 and file2:
        if st.button("Process Files"):
            result_df = process_files(file1, file2)
            output = BytesIO()
            result_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
 
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"output_{timestamp}.xlsx"
            upload_to_blob(output_filename, output)
 
            st.success("Files processed and uploaded!")
            st.download_button("Download Result", data=output, file_name=output_filename, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
 
elif page == "History":
    st.title("Processed Files History")
 
    files = list_output_files()
    if not files:
        st.info("No output files found.")
    else:
        for f in files:
            file_data = download_blob(f)
            st.download_button(f"Download {f}", data=file_data, file_name=f)