import io
import json
import streamlit as st
import pandas as pd
from googleapiclient.http import  MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit_authenticator as stauth
import yaml
import time
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
    master_data_id = "1ry614-7R4-s0uQcv0zrNeS4O0KAbhVEC67rl5_VllGI"  # Replace with your file's ID
    article_data_id = "1b7eyqlN3lTapBRYcO1VrXGsj_gBVSxQLIyLCPu3UcG8"
    district_data_id = "1lwJL-_KQaOY3VSd2cOeOdiR5QOn8yvX3zp6xNfQJo9U"


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

        alert1 = st.success(f"File updated: {updated_file.get('id')}")
        time.sleep(1)
        alert1.empty()



    # Load Data
    article = read_file(article_data_id)
    district = read_file(district_data_id)


    # Sidebar Navigation
    selected_tab = st.sidebar.radio("Select Tab", ["Entry"])

    if selected_tab == "Entry":
        # Radio buttons to select type
        type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions","Others"], horizontal=True)

        if type_choice == "District":

            # Input fields
            name = st.selectbox("District Name", district["District Name"].unique().tolist())
            pname = district[district["District Name"]==name]["President Name"].values.tolist()[0]
            pno = str(district[district["District Name"]==name]["Mobile Number"].values.tolist()[0])
            st.write(f"President Name: {pname}, Mobile Number: {pno}")

            article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist() + ["Add New"])
            #new article
            if article_name == "Add New":
                new_article =  st.text_input("Enter Article Name")
                if new_article:
                    new_cpu = st.number_input("Enter Cost Per Unit", min_value=0)
                    new_item_type = st.radio("Select Type", ["Article", "Aid", "Project"], horizontal=True)
                    if st.button("Save Article"):
                        new_article_entry = {
                            "Articles": new_article,
                            "Cost per unit": new_cpu,
                            "Item Type": new_item_type,
                        }
                        new_article_data = pd.concat([article, pd.DataFrame([new_article_entry])], ignore_index=True).reset_index(drop=True)
                        new_article_data.drop_duplicates(subset=["Articles"], inplace=True)
                        update_file(article_data_id, new_article_data)

            else:

                cpu = st.number_input("Cost Per Unit",value = article[article["Articles"] == article_name]["Cost per unit"].tolist()[0],disabled=True)
                quantity = st.number_input("Quantity", min_value=0, step=1)  # Allow 0 to delete the record

                # Calculate and display total value if quantity > 0
                if quantity > 0:
                    total_value = quantity * cpu
                    st.text_input("Total Value", f"₹ {total_value:,}")
                else:
                    total_value = 0  # No value if quantity is 0

                comment = st.text_area("Enter Comment")

                # Read the saved data from Google Drive
                saved_data = read_file(master_data_id)

                # Dynamic Remaining Funds Display
                if name:  # Ensure district is selected
                    alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
                    # Calculate remaining funds dynamically based on current inputs (without saving)
                    current_total_cost = saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
                    dynamic_remaining_fund = alloted_fund - (current_total_cost + total_value)

                    # Display dynamically
                    st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_fund:,}</span></h5>",
                                unsafe_allow_html=True)
                    if dynamic_remaining_fund > 0:
                        fund_color = "green"
                    else:
                        fund_color = "red"
                    st.markdown(
                        f"<h5>Remaining Fund (Projected): ₹ <span style='color:{fund_color};'>{dynamic_remaining_fund:,}</span></h5>",
                        unsafe_allow_html=True, )

                # Save button
                if st.button("Submit"):
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
                            alert2 = st.success(f"Record for {name} and {article_name} deleted successfully!")
                            time.sleep(1)
                            alert2.empty()

                        else:
                            # Check for duplicates and replace if necessary
                            duplicate_condition = (
                                (saved_data["NAME OF THE DISTRICT"] == name) &
                                (saved_data["REQUESTED ARTICLE"] == article_name)
                            )
                            if duplicate_condition.any():
                                saved_data.loc[duplicate_condition, ["QUANTITY", "TOTAL COST"]] = [quantity, total_value]
                                alert3 = st.info("Duplicate entry found. Existing record updated.")
                                time.sleep(1)
                                alert3.empty()

                            else:
                                new_entry = {
                                    "NAME OF THE DISTRICT": name,
                                    "REQUESTED ARTICLE": article_name,
                                    "QUANTITY": quantity,
                                    "TOTAL COST": total_value,
                                    "COST PER UNIT": cpu,
                                    "COMMENTS":comment,
                                    "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],
                                }

                                saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True).sort_values(by=["NAME OF THE DISTRICT","REQUESTED ARTICLE"],ascending=True).reset_index(drop=True)

                        alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
                        remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
                        try:
                            last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[-1]
                            first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[0]

                            # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
                            saved_data.loc[saved_data["NAME OF THE DISTRICT"] == name, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
                            saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_fund
                            saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
                        except IndexError:
                            pass

                        saved_data = saved_data.reset_index(drop=True)
                        alert4 = st.success("Data saved successfully!")
                        time.sleep(1)
                        alert4.empty()

                        # Save to CSV
                        update_file(master_data_id, saved_data)


                # Display the table below
                st.subheader("Summary")
                st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == name])
                remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
                if remaining_fund > 0:
                    color = "green"
                else:
                    color = "red"
                st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)



                st.download_button(
                    label="Download Records",
                    data=saved_data.to_csv(index=False).encode('utf-8'),
                    file_name="District Beneficiaries Records.csv",
                    mime="text/csv")




        elif type_choice == "Public":


            public_data_id = "1sO08BfwN1gzNs_N7XDq1RnqMgJDDKMdq_nsaNhmjKhs"
            public = read_file(public_data_id)
            public_master_id = "1EdEySmYe6ZJUW16f65_q30nkqfbvDADjcmEkAEJrrL4"
            public_master = read_file(public_master_id)

            # Initialize session state for checked Aadhaar numbers
            p_choice = st.radio("", ["Validation", "Entry"], horizontal=True)

            if p_choice == "Validation":
                if "checked_aadhar" not in st.session_state:
                    st.session_state["checked_aadhar"] = set()
                # Input for Aadhaar Number
                aadhar_no = st.text_input("Enter Aadhaar Number", key="aadhar_input")
                if aadhar_no:
                    # Check if the Aadhaar number has already been checked
                    if aadhar_no in st.session_state["checked_aadhar"]:
                        st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
                    else:
                        # Add the Aadhaar number to the checked list
                        st.session_state["checked_aadhar"].add(aadhar_no)
                    # Check if the Aadhaar number exists in the database
                    if aadhar_no in public["AADHAR No.1"].astype(str).values:
                        Name_b = public[public["AADHAR No.1"] == aadhar_no]["NAME"].values.tolist()[0]
                        Art_n = public[public["AADHAR No.1"] == aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
                        year_p = public[public["AADHAR No.1"] == aadhar_no]["YEAR"].values.tolist()[0]
                        st.error(
                            f"Aadhaar Number {aadhar_no} is present in the database. Beneficiary: {Name_b}, Item: {Art_n}, Year: {year_p}.")
                    else:
                        st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")

            if p_choice == "Entry":
                # Input fields for Public data
                app_no = st.text_input("Application Number (e.g., P 001)", key="app_no_input")
                aadhar = st.text_input("Aadhaar Number", key="aadhar_entry")
                name = st.text_input("Name", key="name_input")
                handicapped = st.radio("Handicapped", options=["Yes", "No"], horizontal=True,
                                       key="handicapped_input")
                address = st.text_area("Address", key="address_input")
                mobile = st.text_input("Mobile Number", key="mobile_input")
                article_name = st.selectbox("Select Article Name", article["Articles"].unique().tolist(),
                                            key="article_selectbox")
                quantity = st.number_input("Quantity", min_value=0, step=1,
                                           key="quantity_input")  # Allow 0 to delete the record
                comment = st.text_area("Comments", key="comments_input")

                # Select Record to modify or delete
                selected_record = st.selectbox("Select Application to Modify/Delete",
                                               public_master["App. No."].unique(), key="select_record")

                # Get the selected record's details for modifying
                if selected_record:
                    selected_row = public_master[public_master["App. No."] == selected_record]
                    app_no = selected_row["App. No."].values[0]
                    aadhar = selected_row["Aadhar (Without Space)"].values[0]
                    name = selected_row["Name"].values[0]
                    handicapped = selected_row["Handicapped (Yes / No)"].values[0]
                    address = selected_row["Address"].values[0]
                    mobile = selected_row["Mobile"].values[0]
                    article_name = selected_row["Article Name"].values[0]
                    quantity = selected_row["QTY"].values[0]
                    comment = selected_row["Comments"].values[0]

                # Buttons to Modify or Delete
                if st.button("Delete", key="delete_button"):
                    if selected_record:
                        public_master = public_master[
                            public_master["App. No."] != selected_record]  # Remove the record
                        update_file(public_master_id, public_master)
                        st.success(f"Record for {selected_record} deleted successfully!")
                    else:
                        st.error("Please select a record to delete.")

                if st.button("Modify", key="modify_button"):
                    # Modify the existing record with new values
                    if selected_record:
                        modified_entry = {
                            "App. No.": app_no,
                            "Aadhar (Without Space)": aadhar,
                            "Name": name,
                            "Handicapped (Yes / No)": handicapped,
                            "Address": address,
                            "Mobile": mobile,
                            "Article Name": article_name,
                            "QTY": quantity,
                            "Comments": comment
                        }

                        # Update the record
                        public_master.loc[
                            public_master["App. No."] == selected_record, list(modified_entry.keys())] = list(
                            modified_entry.values())
                        update_file(public_master_id, public_master)
                        st.success(f"Record for {selected_record} modified successfully!")

                # Submit button to add a new record
                if st.button("Add", key="submit_button"):
                    try:
                        # Ensure the columns are of string type for comparison
                        public_master["App. No."] = public_master["App. No."].astype(str)
                        public_master["Aadhar (Without Space)"] = public_master["Aadhar (Without Space)"].astype(
                            str)
                        # Validate application number and Aadhaar
                        if not app_no:
                            st.warning("Application Number cannot be empty.")
                        elif app_no in public_master["App. No."].astype(str).values:
                            st.error("Application Number already exists in the database.")
                        elif not aadhar:
                            st.warning("Aadhaar Number cannot be empty.")
                        elif aadhar in public["AADHAR No.1"].astype(str).values:
                            st.error("Aadhaar number is already present in the database.")
                        elif aadhar in public_master["Aadhar (Without Space)"].values:
                            st.error("Aadhaar Number is already added to an application.")
                        else:
                            # Create a new entry
                            new_entry = {
                                "App. No.": app_no,
                                "Aadhar (Without Space)": aadhar,
                                "Name": name,
                                "Handicapped (Yes / No)": handicapped,
                                "Address": address,
                                "Mobile": mobile,
                                "Article Name": article_name,
                                "QTY": quantity,
                                "Comments": comment
                            }

                            # Append the new entry to the DataFrame
                            public_master = pd.concat(
                                [public_master, pd.DataFrame([new_entry])],
                                ignore_index=True
                            ).sort_values(by=["App. No."], ascending=True).reset_index(drop=True)

                            # Save the updated data back to the file
                            update_file(public_master_id, public_master)

                            # Success message and updated DataFrame display
                            st.success(f"Application {app_no} added successfully!")
                            st.data_editor(public_master)

                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")




elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    alert5 = st.warning('Please enter your username and password')
    time.sleep(1)
    alert5.empty()