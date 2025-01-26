# ## Without delete module
# import io
#
# import streamlit as st
# import pandas as pd
# import os
#
# # Check if the data file exists
# article = "articles.csv"
# saved_data_file = "saved_data.csv"
#
# # if not os.path.exists(data_file):
# #     st.error(f"The file '{data_file}' was not found.")
# #     st.stop()
#
# # Load data
# article = pd.read_csv(article)
# district = pd.read_csv("District_beneficiary.csv")
#
# # Initialize app
# st.set_page_config(page_title="மக்கள் நல பணி", layout="wide")
# st.title("மக்கள் நல பணி")
#
# # Sidebar navigation
# selected_tab = st.sidebar.radio("Select Tab", ["Input"])
#
# if selected_tab == "Input":
#     # Radio buttons to select type
#     type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)
#
#     if type_choice == "District":
#         # Input fields
#         name = st.selectbox("District Name", district["District Name"].unique().tolist())
#         article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
#         quantity = st.number_input("Quantity", min_value=1, step=1)
#
#         # Calculate and display total value
#         total_value = quantity * article[article["Articles"]==article_name]["Cost per unit"].tolist()[0]
#         st.subheader(f"₹ {total_value:,}")
#
#         # Load saved data
#         if os.path.exists(saved_data_file):
#             saved_data = pd.read_csv(saved_data_file)
#         else:
#             saved_data = pd.DataFrame(columns=["District Name", "Article Name", "Quantity", "Total Value"])
#
#         # Save button
#         if st.button("Save"):
#             if not name or not article_name:
#                 st.warning("Please fill all fields before saving.")
#             else:
#                 # Check for duplicates and replace if necessary
#                 duplicate_condition = (
#                         (saved_data["District Name"] == name) &
#                         (saved_data["Article Name"] == article_name)
#                 )
#                 if duplicate_condition.any():
#                     saved_data.loc[duplicate_condition, ["Quantity", "Total Value"]] = [quantity, total_value]
#                     st.info("Duplicate entry found. Existing record updated.")
#                 else:
#                     new_entry = {
#                         "District Name": name,
#                         "Article Name": article_name,
#                         "Quantity": quantity,
#                         "Total Value": total_value,
#                     }
#                     saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True)
#                     st.success("Data saved successfully!")
#
#                 # Save to CSV
#                 saved_data.to_csv(saved_data_file, index=False)
#
#         # Display the table below
#         st.subheader("Saved Data")
#         st.dataframe(saved_data[saved_data["District Name"] == name])
#
#         st.download_button(
#             label="Download Records",
#             data=saved_data.to_csv(index=False).encode('utf-8'),
#             file_name="District Beneficiaries Records.csv",
#             mime = "text/csv"
#         )
#
# ##-----------------------------------------------------------------------------------------------
# ### Delete Button
# import streamlit as st
# import pandas as pd
# import os
#
# # Data Files
# article = "articles.csv"
# saved_data_file = "saved_data.csv"
#
# # Load Data
# article = pd.read_csv(article)
# district = pd.read_csv("District_beneficiary.csv")
#
# # Initialize App
# st.set_page_config(page_title="மக்கள் நல பணி", layout="wide")
# st.title("மக்கள் நல பணி")
#
# # Sidebar Navigation
# selected_tab = st.sidebar.radio("Select Tab", ["Input"])
#
# if selected_tab == "Input":
#     # Radio buttons to select type
#     type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)
#
#     if type_choice == "District":
#         # Input fields
#         name = st.selectbox("District Name", district["District Name"].unique().tolist())
#         article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
#         quantity = st.number_input("Quantity", min_value=0, step=1)
#
#         # Calculate and display total value
#         total_value = quantity * article[article["Articles"] == article_name]["Cost per unit"].tolist()[0]
#         st.subheader(f"₹ {total_value:,}")
#
#         # Load saved data
#         if os.path.exists(saved_data_file):
#             saved_data = pd.read_csv(saved_data_file)
#         else:
#             saved_data = pd.DataFrame(columns=["District Name", "Article Name", "Quantity", "Total Value"])
#
#         # Columns layout for Save and Delete buttons side by side
#         col1, col2 = st.columns([1, 1])  # Creates two equal-width columns
#
#         # Save button
#         with col1:
#             if st.button("Save"):
#                 if not name or not article_name:
#                     st.warning("Please fill all fields before saving.")
#                 else:
#                     # Check for duplicates and replace if necessary
#                     duplicate_condition = (
#                             (saved_data["District Name"] == name) &
#                             (saved_data["Article Name"] == article_name)
#                     )
#                     if duplicate_condition.any():
#                         saved_data.loc[duplicate_condition, ["Quantity", "Total Value"]] = [quantity, total_value]
#                         st.info("Duplicate entry found. Existing record updated.")
#                     else:
#                         new_entry = {
#                             "District Name": name,
#                             "Article Name": article_name,
#                             "Quantity": quantity,
#                             "Total Value": total_value,
#                         }
#                         saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True)
#                         st.success("Data saved successfully!")
#
#                     # Save to CSV
#                     saved_data.to_csv(saved_data_file, index=False)
#
#         # Delete button (works with the table shown below)
#         with col2:
#             delete_condition = (
#                     (saved_data["District Name"] == name) &
#                     (saved_data["Article Name"] == article_name)
#             )
#             if st.button("Delete") and delete_condition.any():
#                 # Remove the selected row from the DataFrame
#                 saved_data = saved_data[~delete_condition]
#                 saved_data.to_csv(saved_data_file, index=False)
#                 st.success(f"Record for {name} and {article_name} deleted successfully!")
#
#         # Display the table below
#         st.subheader("Saved Data")
#         st.dataframe(saved_data[saved_data["District Name"] == name])
#
#         st.download_button(
#             label="Download Records",
#             data=saved_data.to_csv(index=False).encode('utf-8'),
#             file_name="District Beneficiaries Records.csv",
#             mime="text/csv"
#         )
#
# ##_------------------------------------------------------------------------------------------------
# #### with Quantity as delete feature
#
# import streamlit as st
# import pandas as pd
# import os
#
# # Data Files
# article = "articles.csv"
# saved_data_file = "saved_data.csv"
#
# # Load Data
# article = pd.read_csv(article)
# district = pd.read_csv("District_beneficiary.csv")
#
# # Initialize App
# st.set_page_config(page_title="மக்கள் நல பணி", layout="wide")
# st.title("மக்கள் நல பணி")
#
# # Sidebar Navigation
# selected_tab = st.sidebar.radio("Select Tab", ["Input"])
#
# if selected_tab == "Input":
#     # Radio buttons to select type
#     type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)
#
#     if type_choice == "District":
#         # Input fields
#         name = st.selectbox("District Name", district["District Name"].unique().tolist())
#         article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
#         quantity = st.number_input("Quantity", min_value=0, step=1)  # Allow 0 to delete the record
#
#         # Calculate and display total value if quantity > 0
#         if quantity > 0:
#             total_value = quantity * article[article["Articles"] == article_name]["Cost per unit"].tolist()[0]
#             st.subheader(f"₹ {total_value:,}")
#         else:
#             total_value = 0  # No value if quantity is 0
#
#         # Load saved data
#         if os.path.exists(saved_data_file):
#             saved_data = pd.read_csv(saved_data_file)
#         else:
#             saved_data = pd.DataFrame(columns=["District Name", "Article Name", "Quantity", "Total Value"])
#
#         # Save button
#         if st.button("Save"):
#             if not name or not article_name:
#                 st.warning("Please fill all fields before saving.")
#             else:
#                 # Check if quantity is 0 (delete the record)
#                 if quantity == 0:
#                     # Find and remove the selected row from the DataFrame
#                     delete_condition = (
#                         (saved_data["District Name"] == name) &
#                         (saved_data["Article Name"] == article_name)
#                     )
#                     saved_data = saved_data[~delete_condition]  # Remove the record
#                     st.success(f"Record for {name} and {article_name} deleted successfully!")
#                 else:
#                     # Check for duplicates and replace if necessary
#                     duplicate_condition = (
#                         (saved_data["District Name"] == name) &
#                         (saved_data["Article Name"] == article_name)
#                     )
#                     if duplicate_condition.any():
#                         saved_data.loc[duplicate_condition, ["Quantity", "Total Value"]] = [quantity, total_value]
#                         st.info("Duplicate entry found. Existing record updated.")
#                     else:
#                         new_entry = {
#                             "District Name": name,
#                             "Article Name": article_name,
#                             "Quantity": quantity,
#                             "Total Value": total_value,
#                         }
#                         saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True)
#                         st.success("Data saved successfully!")
#
#                 # Save to CSV
#                 saved_data.to_csv(saved_data_file, index=False)
#
#         # Display the table below
#         alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#         remaining_fund = alloted_fund - saved_data[saved_data["District Name"] == name]["Total Value"].sum()
#         st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:blue;'>{alloted_fund:,}</span></h5>", unsafe_allow_html=True)
#         if remaining_fund > 0:
#             color = "green"
#         else:
#             color = "red"
#         st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)
#         st.subheader("Summary")
#         st.dataframe(saved_data[saved_data["District Name"] == name])
#
#
#         st.download_button(
#             label="Download Records",
#             data=saved_data.to_csv(index=False).encode('utf-8'),
#             file_name="District Beneficiaries Records.csv",
#             mime="text/csv"
#         )


#### - Accepted 1
### ------------------------------------------------------------------------------------
###_____Single select Articles__________________________________________________________________________
# import io
# import json
# import streamlit as st
# import pandas as pd
# import os
# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive
# from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
# from googleapiclient.discovery import build
# from google.oauth2 import service_account
# import streamlit_authenticator as stauth
# import yaml
# import time
# from yaml.loader import SafeLoader
#
# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)
#
# # Initialize App
# st.set_page_config(page_title="மக்கள் நலப்பணி 2025", layout="wide")
# st.title("மக்கள் நலப்பணி 2025")
#
#
# # Pass the required configurations to the authenticator
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days']
# )
#
# authenticator.login()
#
# if st.session_state['authentication_status']:
#     authenticator.logout("Logout","sidebar")
#
#
#     # File ID of the existing file on Google Drive
#     file_id = "1ry614-7R4-s0uQcv0zrNeS4O0KAbhVEC67rl5_VllGI"  # Replace with your file's ID
#
#     ## Access API from local json
#     # creds = service_account.Credentials.from_service_account_file('mnpdatabase-ca1a93fefdd6.json',
#     #         scopes=['https://www.googleapis.com/auth/drive'])
#
#     ## Access via streamlit secrets
#     credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
#     creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=['https://www.googleapis.com/auth/drive'])
#     drive_service = build('drive', 'v3', credentials=creds)
#
#
#     def read_file(file_id):
#         try:
#             # Specify the desired MIME type for export (e.g., text/csv for Sheets)
#             request = drive_service.files().export_media(
#                 fileId=file_id,
#                 mimeType='text/csv'  # Change this based on the file type
#             )
#             file_stream = io.BytesIO()
#             downloader = MediaIoBaseDownload(file_stream, request)
#
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 print(f"Download progress: {int(status.progress() * 100)}%")
#
#             file_stream.seek(0)  # Reset the stream position
#             df = pd.read_csv(file_stream)
#             return df
#
#         except Exception as e:
#             st.error(f"Failed to read file: {e}")
#
#     def update_file(file_id, updated_df):
#         updated_stream = io.BytesIO()
#         updated_df.to_csv(updated_stream, index=False)
#         updated_stream.seek(0)
#
#         media = MediaIoBaseUpload(updated_stream, mimetype="text/csv")
#         updated_file = drive_service.files().update(
#             fileId=file_id,
#             media_body=media).execute()
#
#         alert1 = st.success(f"File updated: {updated_file.get('id')}")
#         time.sleep(3)
#         alert1.empty()
#
#
#
#     # Load Data
#     article = pd.read_csv("articles.csv")
#     district = pd.read_csv("District_beneficiary.csv")
#     public = pd.read_excel("Public_Beneficiary_21_24.xlsx")
#
#
#
#     # Sidebar Navigation
#     selected_tab = st.sidebar.radio("Select Tab", ["Entry"])
#
#     if selected_tab == "Entry":
#         # Radio buttons to select type
#         type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)
#
#         if type_choice == "District":
#
#             # Input fields
#             name = st.selectbox("District Name", district["District Name"].unique().tolist())
#             article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
#             quantity = st.number_input("Quantity", min_value=0, step=1)  # Allow 0 to delete the record
#             cpu = article[article["Articles"] == article_name]["Cost per unit"].tolist()[0]
#             item_type = st.selectbox("Item Type", ["Article","Aid","Project"])
#             comment = st.text_area("Enter Comment")
#
#             # Calculate and display total value if quantity > 0
#             if quantity > 0:
#                 total_value = quantity * cpu
#                 st.text_input("Total Value", f"₹ {total_value:,}")
#             else:
#                 total_value = 0  # No value if quantity is 0
#
#
#             # Read the saved data from Google Drive
#             saved_data = read_file(file_id)
#
#             # Dynamic Remaining Funds Display
#             if name:  # Ensure district is selected
#                 alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#                 # Calculate remaining funds dynamically based on current inputs (without saving)
#                 current_total_cost = saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#                 dynamic_remaining_fund = alloted_fund - (current_total_cost + total_value)
#
#                 # Display dynamically
#                 st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_fund:,}</span></h5>",
#                             unsafe_allow_html=True)
#                 if dynamic_remaining_fund > 0:
#                     fund_color = "green"
#                 else:
#                     fund_color = "red"
#                 st.markdown(
#                     f"<h5>Remaining Fund (Projected): ₹ <span style='color:{fund_color};'>{dynamic_remaining_fund:,}</span></h5>",
#                     unsafe_allow_html=True, )
#
#             # Save button
#             if st.button("Save"):
#                 if not name or not article_name:
#                     st.warning("Please fill all fields before saving.")
#                 else:
#                     # Check if quantity is 0 (delete the record)
#                     if quantity == 0:
#                         # Find and remove the selected row from the DataFrame
#                         delete_condition = (
#                             (saved_data["NAME OF THE DISTRICT"] == name) &
#                             (saved_data["REQUESTED ARTICLE"] == article_name)
#                         )
#                         saved_data = saved_data[~delete_condition]  # Remove the record
#                         alert2 = st.success(f"Record for {name} and {article_name} deleted successfully!")
#                         time.sleep(3)
#                         alert2.empty()
#
#                     else:
#                         # Check for duplicates and replace if necessary
#                         duplicate_condition = (
#                             (saved_data["NAME OF THE DISTRICT"] == name) &
#                             (saved_data["REQUESTED ARTICLE"] == article_name)
#                         )
#                         if duplicate_condition.any():
#                             saved_data.loc[duplicate_condition, ["QUANTITY", "TOTAL COST"]] = [quantity, total_value]
#                             alert3 = st.info("Duplicate entry found. Existing record updated.")
#                             time.sleep(3)
#                             alert3.empty()
#
#                         else:
#                             new_entry = {
#                                 "NAME OF THE DISTRICT": name,
#                                 "REQUESTED ARTICLE": article_name,
#                                 "QUANTITY": quantity,
#                                 "TOTAL COST": total_value,
#                                 "COST PER UNIT": cpu,
#                                 "COMMENTS":comment,
#                                 "ARTICLE TYPE": item_type,
#                             }
#
#                             saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True).sort_values(by=["NAME OF THE DISTRICT","REQUESTED ARTICLE"],ascending=True).reset_index(drop=True)
#
#                     alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#                     remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#
#                     last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[-1]
#                     first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[0]
#
#                     # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
#                     saved_data.loc[saved_data["NAME OF THE DISTRICT"] == name, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
#                     saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_fund
#                     saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
#                     saved_data = saved_data.reset_index(drop=True)
#                     alert4 = st.success("Data saved successfully!")
#                     time.sleep(3)
#                     alert4.empty()
#
#                     # Save to CSV
#                     update_file(file_id, saved_data)
#
#
#             # Display the table below
#             st.subheader("Summary")
#             st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == name])
#             remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#             if remaining_fund > 0:
#                 color = "green"
#             else:
#                 color = "red"
#             st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)
#
#
#
#             st.download_button(
#                 label="Download Records",
#                 data=saved_data.to_csv(index=False).encode('utf-8'),
#                 file_name="District Beneficiaries Records.csv",
#                 mime="text/csv")
#
#
#
#         elif type_choice == "Public":
#
#             # Initialize session state for checked Aadhaar numbers
#             if "checked_aadhar" not in st.session_state:
#                 st.session_state["checked_aadhar"] = set()
#             # Input for Aadhaar Number
#             aadhar_no = st.text_input("Enter Aadhaar Number")
#             if aadhar_no:
#                 # Check if the Aadhaar number has already been checked
#                 if aadhar_no in st.session_state["checked_aadhar"]:
#                     st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
#
#                 else:
#                     # Add the Aadhaar number to the checked list
#                     st.session_state["checked_aadhar"].add(aadhar_no)
#                 # Check if the Aadhaar number exists in the database
#                 if aadhar_no in public["AADHAR No.1"].astype(str).values:
#                     Name_b = public[public["AADHAR No.1"] == aadhar_no]["NAME"].values.tolist()[0]
#                     Art_n = public[public["AADHAR No.1"] == aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
#                     year_p = public[public["AADHAR No.1"] == aadhar_no]["YEAR"].values.tolist()[0]
#                     st.error(
#                         f"Aadhaar Number {aadhar_no} is present in the database. Beneficiary: {Name_b}, Item: {Art_n}, Year: {year_p}.")
#                 else:
#                     st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")
#
#
# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state['authentication_status'] is None:
#     alert5 = st.warning('Please enter your username and password')
#     time.sleep(3)
#     alert5.empty()