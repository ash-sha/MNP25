## Without delete module

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

##-----------------------------------------------------------------------------------------------
### Delete Button
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

###_------------------------------------------------------------------------------------------------
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

###_____Multiselect Articles__________________________________________________________________________

import streamlit as st
import pandas as pd
import os
# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive
# from googleapiclient.http import MediaFileUpload
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

def upload_data(saved_data_file):
    creds = service_account.Credentials.from_service_account_file('mnpdatabase-4c0143764944.json',
        scopes=['https://www.googleapis.com/auth/drive'])

    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': saved_data_file,
        'parents': ['1ritUg2jlAaf2GsiKWndw93_i9Y6yy0ll']  # ID of the folder where you want to upload
    }

    file_path = 'articles.csv'

    media = MediaFileUpload(file_path, mimetype='text/csv')

    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()


# Load Data
article = pd.read_csv("articles.csv")
district = pd.read_csv("District_beneficiary.csv")
public = pd.read_excel("DISTRICT AND PUBLIC DATA BASE 24122024.xlsx",sheet_name="DO NOT TOUCH_2021 to 24 data")


# Initialize App
st.set_page_config(page_title="மக்கள் நல பணி", layout="wide")
st.title("மக்கள் நல பணி")

# Sidebar Navigation
selected_tab = st.sidebar.radio("Select Tab", ["Input"])

if selected_tab == "Input":
    # Radio buttons to select type
    type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)

    if type_choice == "District":

        # Input fields
        name = st.selectbox("District Name", district["District Name"].unique().tolist())
        article_name = st.multiselect("Enter Article Name", article["Articles"].unique().tolist())
        quantity = st.number_input("Quantity", min_value=0, step=1)  # Allow 0 to delete the record

        # Calculate and display total value if quantity > 0
        if quantity > 0:
            total_value = quantity * article[article["Articles"] == article_name]["Cost per unit"].tolist()[0]
            st.subheader(f"₹ {total_value:,}")
        else:
            total_value = 0  # No value if quantity is 0

        # Load saved data
        saved_data_file = "saved_data.csv"
        if os.path.exists(saved_data_file):
            saved_data = pd.read_csv(saved_data_file)
        else:
            saved_data = pd.DataFrame(columns=["District Name", "Article Name", "Quantity", "Total Value"])

        # Save button
        if st.button("Save"):
            if not name or not article_name:
                st.warning("Please fill all fields before saving.")
            else:
                # Check if quantity is 0 (delete the record)
                if quantity == 0:
                    # Find and remove the selected row from the DataFrame
                    delete_condition = (
                        (saved_data["District Name"] == name) &
                        (saved_data["Article Name"] == article_name)
                    )
                    saved_data = saved_data[~delete_condition]  # Remove the record
                    st.success(f"Record for {name} and {article_name} deleted successfully!")
                else:
                    # Check for duplicates and replace if necessary
                    duplicate_condition = (
                        (saved_data["District Name"] == name) &
                        (saved_data["Article Name"] == article_name)
                    )
                    if duplicate_condition.any():
                        saved_data.loc[duplicate_condition, ["Quantity", "Total Value"]] = [quantity, total_value]
                        st.info("Duplicate entry found. Existing record updated.")
                    else:
                        new_entry = {
                            "District Name": name,
                            "Article Name": article_name,
                            "Quantity": quantity,
                            "Total Value": total_value,
                        }
                        saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True)
                        st.success("Data saved successfully!")

                # Save to CSV
                saved_data.to_csv(saved_data_file, index=False)


        # Display the table below
        alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
        remaining_fund = alloted_fund - saved_data[saved_data["District Name"] == name]["Total Value"].sum()
        st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:blue;'>{alloted_fund:,}</span></h5>", unsafe_allow_html=True)
        if remaining_fund > 0:
            color = "green"
        else:
            color = "red"
        st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)
        st.subheader("Summary")
        st.dataframe(saved_data[saved_data["District Name"] == name])


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
