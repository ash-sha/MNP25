###_____Multiselect Articles__________________________________________________________________________
import io
import json
import streamlit as st
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize App
st.set_page_config(page_title="மக்கள் நலப்பணி 2025", layout="wide")
st.title("மக்கள் நலப்பணி 2025")


# Pass the required configurations to the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state['authentication_status']:
    authenticator.logout("Logout","sidebar")


    # File ID of the existing file on Google Drive
    file_id = "1ry614-7R4-s0uQcv0zrNeS4O0KAbhVEC67rl5_VllGI"  # Replace with your file's ID

    ## Access API from local json
    # creds = service_account.Credentials.from_service_account_file('mnpdatabase-ca1a93fefdd6.json',
    #         scopes=['https://www.googleapis.com/auth/drive'])

    ## Access via streamlit secrets
    credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
    creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)


    def read_file(file_id):
        try:
            # Specify the desired MIME type for export (e.g., text/csv for Sheets)
            request = drive_service.files().export_media(
                fileId=file_id,
                mimeType='text/csv'  # Change this based on the file type
            )
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%")

            file_stream.seek(0)  # Reset the stream position
            df = pd.read_csv(file_stream)
            return df

        except Exception as e:
            st.error(f"Failed to read file: {e}")

    def update_file(file_id, updated_df):
        updated_stream = io.BytesIO()
        updated_df.to_csv(updated_stream, index=False)
        updated_stream.seek(0)

        media = MediaIoBaseUpload(updated_stream, mimetype="text/csv")
        updated_file = drive_service.files().update(
            fileId=file_id,
            media_body=media).execute()

        st.success(f"File updated: {updated_file.get('id')}")



    # Load Data
    article = pd.read_csv("articles.csv")
    district = pd.read_csv("District_beneficiary.csv")
    public = pd.read_excel("Public_Beneficiary_21_24.xlsx")



    # Sidebar Navigation
    selected_tab = st.sidebar.radio("Select Tab", ["Entry"])

    if selected_tab == "Entry":
        # Radio buttons to select type
        type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)

        if type_choice == "District":

            # Input fields
            name = st.selectbox("District Name", district["District Name"].unique().tolist())
            article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
            quantity = st.number_input("Quantity", min_value=0, step=1)  # Allow 0 to delete the record
            cpu = article[article["Articles"] == article_name]["Cost per unit"].tolist()[0]

            # Calculate and display total value if quantity > 0
            if quantity > 0:
                total_value = quantity * cpu
                st.subheader(f"₹ {total_value:,}")
            else:
                total_value = 0  # No value if quantity is 0


            # Read the saved data from Google Drive
            saved_data = read_file(file_id)


            # Save button
            if st.button("Save"):
                if not name or not article_name:
                    st.warning("Please fill all fields before saving.")
                else:
                    # Check if quantity is 0 (delete the record)
                    if quantity == 0:
                        # Find and remove the selected row from the DataFrame
                        delete_condition = (
                            (saved_data["NAME OF THE DISTRICT"] == name) &
                            (saved_data["REQUESTED ARTICLE"] == article_name)
                        )
                        saved_data = saved_data[~delete_condition]  # Remove the record
                        st.success(f"Record for {name} and {article_name} deleted successfully!")
                    else:
                        # Check for duplicates and replace if necessary
                        duplicate_condition = (
                            (saved_data["NAME OF THE DISTRICT"] == name) &
                            (saved_data["REQUESTED ARTICLE"] == article_name)
                        )
                        if duplicate_condition.any():
                            saved_data.loc[duplicate_condition, ["QUANTITY", "TOTAL COST"]] = [quantity, total_value]
                            st.info("Duplicate entry found. Existing record updated.")
                        else:
                            new_entry = {
                                "NAME OF THE DISTRICT": name,
                                "REQUESTED ARTICLE": article_name,
                                "QUANTITY": quantity,
                                "TOTAL COST": total_value,
                                "COST PER UNIT": cpu,
                            }
                            saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True)
                            saved_data = saved_data.sort_values(by=["NAME OF THE DISTRICT","REQUESTED ARTICLE"],ascending=True).reset_index(drop=True)
                            st.success("Data saved successfully!")

                    # Save to CSV
                    update_file(file_id, saved_data)



            # Display the table below
            alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
            remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
            st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_fund:,}</span></h5>", unsafe_allow_html=True)
            if remaining_fund > 0:
                color = "green"
            else:
                color = "red"
            st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)
            st.subheader("Summary")
            st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == name])


            st.download_button(
                label="Download Records",
                data=saved_data.to_csv(index=False).encode('utf-8'),
                file_name="District Beneficiaries Records.csv",
                mime="text/csv"
            )

        elif type_choice == "Public":
            aadhar_no = st.text_input("Enter aadhar Number")

            if aadhar_no in public["AADHAR No.1"].astype(str).values:
                Name_b = public[public["AADHAR No.1"]== aadhar_no]["NAME"].values.tolist()[0]
                Art_n = public[public["AADHAR No.1"]== aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
                year_p = public[public["AADHAR No.1"]== aadhar_no]["YEAR"].values.tolist()[0]
                st.error(f"Aadhaar Number {aadhar_no} is present in the database.Beneficiary {Name_b} of {Art_n} at {year_p}")
            else:
                st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")



elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')