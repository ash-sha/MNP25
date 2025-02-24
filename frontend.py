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


# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# Initialize App
st.set_page_config(page_title="மக்கள் நலப்பணி 2025", layout="wide")
st.title("மக்கள் நலப்பணி 2025")
st.logo("amma.png",size="large")

# # Pass the required configurations to the authenticator
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'])

# authenticator.login()
#
# if st.session_state['authentication_status']:
#     authenticator.logout("Logout","sidebar")


# File ID of the existing file on Google Drive
master_data_id = "1ry614-7R4-s0uQcv0zrNeS4O0KAbhVEC67rl5_VllGI"  # Replace with your file's ID
article_data_id = "1b7eyqlN3lTapBRYcO1VrXGsj_gBVSxQLIyLCPu3UcG8"
district_data_id = "1lwJL-_KQaOY3VSd2cOeOdiR5QOn8yvX3zp6xNfQJo9U"
public_data_id = "1sO08BfwN1gzNs_N7XDq1RnqMgJDDKMdq_nsaNhmjKhs"
public_master_id = "1EdEySmYe6ZJUW16f65_q30nkqfbvDADjcmEkAEJrrL4"
inst_data_id = "1dOMubywUqJId2gXHwNWp185L3QmadUnwxyFf0DC9M1s"
ord_req_id = "1ou21kOkXQpL-hoaJ-11av2m7Kwk5hsif65jVOiFaU2Y"


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
selected_tab = st.sidebar.radio("Select Tab", ["Article Entry","Manage Articles", "Inventory", "District Records","All Records"])

if selected_tab == "Article Entry":
    # Radio buttons to select type
    type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions & Others"], horizontal=True)

    if type_choice == "District":

        # Streamlit UI
        st.header("District Requests")
        saved_data = read_file(master_data_id)


        # Function to reset form fields
        def reset_form():
            st.session_state.clear()
            st.session_state["district_name"] = ""
            st.session_state["selected_articles"] = []
            st.session_state["article_comments"] = {}


        # Initialize session state for form fields if not already set
        if "district_name" not in st.session_state:
            reset_form()

        # User action selection
        action = st.radio("Select Action", ["Add", "Edit", "Delete"], horizontal=True)

        if action == "Add":

            # District Name
            st.session_state["district_name"] = st.selectbox("District Name*",district["District Name"].tolist(),
                index=0 if not st.session_state["district_name"] else district["District Name"].tolist().index(
                    st.session_state["district_name"]))
            dm = st.session_state["district_name"]
            pname = district[district["District Name"] == st.session_state["district_name"]]["President Name"].values.tolist()[0]
            pno = str(district[district["District Name"] == st.session_state["district_name"]]["Mobile Number"].values.tolist()[0])

            st.markdown(f"<h4>President: <b>{pname}</b>, Mobile: <b>{pno}</b></h4>", unsafe_allow_html=True, )

            # Article Selection
            st.session_state["selected_articles"] = st.multiselect("Select Articles*",article["Articles"].tolist(),
                default=st.session_state["selected_articles"])

            # Article Details
            article_entries = []
            article_comments = {}

            for article_name in st.session_state["selected_articles"]:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Use a unique key by combining article name and district name
                    quantity = st.number_input(f"Quantity of {article_name}*",min_value=1,step=1,key=f"qty_{article_name}_{st.session_state['district_name']}")

                cost_per_unit = article.loc[article["Articles"] == article_name, "Cost per unit"].values[0]

                with col2:
                    st.write(f"Cost per Unit: ₹{cost_per_unit}")

                with col3:
                    if cost_per_unit == 0:
                        total_value = st.number_input(
                            f"Total Value for {article_name}*",min_value=0,step=1,key=f"total_value_{article_name}_{st.session_state['district_name']}")
                    else:
                        total_value = quantity * cost_per_unit
                        st.write(f"Total: ₹{total_value}")

                with col4:
                    comment = st.text_area(f"Comment for {article_name}",
                                           key=f"comment_{article_name}_{st.session_state['district_name']}",
                                           value="No", height=68)

                    article_comments[article_name] = comment

                article_entries.append({
                    "NAME OF THE DISTRICT": st.session_state["district_name"],
                    "REQUESTED ARTICLE": article_name,
                    "QUANTITY": quantity,
                    "COST PER UNIT": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
                    "TOTAL COST": total_value,
                    "COMMENTS": article_comments[article_name],
                    "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],
                    "Beneficiary Type": "District", })

            # Submit Button for new requests
            if st.button("Add"):
                if not st.session_state["district_name"] or not st.session_state["selected_articles"]:
                    st.error("Please fill all required fields (*) before submitting.")
                else:
                    # Check for duplicate entries (same District Name, Article Name, and Comments)
                    duplicate_entries = []

                    for entry in article_entries:
                        duplicate = saved_data[
                            (saved_data["NAME OF THE DISTRICT"] == entry["NAME OF THE DISTRICT"]) &
                            (saved_data["REQUESTED ARTICLE"] == entry["REQUESTED ARTICLE"]) &
                            (saved_data["COMMENTS"] == entry["COMMENTS"])]
                        if not duplicate.empty:
                            duplicate_entries.append(entry["REQUESTED ARTICLE"])

                    if duplicate_entries:
                        st.error(
                            f"Duplicate entries found: {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")
                    else:
                        # Flatten the article entries into individual rows
                        flattened_articles = []

                        for entry in article_entries:
                            flattened_articles.append({
                                "NAME OF THE DISTRICT": entry["NAME OF THE DISTRICT"],
                                "REQUESTED ARTICLE": entry["REQUESTED ARTICLE"],
                                "QUANTITY": entry["QUANTITY"],
                                "COST PER UNIT": entry["COST PER UNIT"],
                                "TOTAL COST": entry["TOTAL COST"],
                                "COMMENTS": entry["COMMENTS"],
                                "ITEM TYPE": entry["ITEM TYPE"],
                                "Beneficiary Type": entry["Beneficiary Type"],
                            })

                        # Convert the flattened articles into a DataFrame
                        flattened_df = pd.DataFrame(flattened_articles)

                        # Append the new flattened data to the existing data
                        saved_data = pd.concat([saved_data, flattened_df], ignore_index=True).sort_values(
                            by=["NAME OF THE DISTRICT", "REQUESTED ARTICLE"], ascending=True).reset_index(drop=True)

                        alloted_funds = district[district["District Name"] == dm]["Alloted Budget"].values.tolist()[0]
                        remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == dm]["TOTAL COST"].sum()

                        # to resolve mismatched cells
                        saved_data = saved_data.reset_index(drop=True)

                        try:
                            last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == dm].index[-1]
                            first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == dm].index[0]

                            # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
                            saved_data.loc[saved_data["NAME OF THE DISTRICT"] == dm, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
                            saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_funds
                            saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
                        except IndexError:
                            pass

                        # Save the updated data back to storage
                        update_file(master_data_id, saved_data)

                        # Clear form fields after successful submission
                        reset_form()

                        # Success message
                        st.success("Request submitted successfully!")
                        st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == dm])


            alloted_funds = district[district["District Name"] == dm]["Alloted Budget"].values.tolist()[0]
            remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == dm]["TOTAL COST"].sum()
            st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_funds:,}</span></h5>",
                        unsafe_allow_html=True)
            if remaining_fund > 0:
                fund_color = "green"
            else:
                fund_color = "red"
            st.markdown(
                f"<h5>Remaining Fund: ₹ <span style='color:{fund_color};'>{remaining_fund:,}</span></h5>",
                unsafe_allow_html=True, )


        elif action == "Edit":

            if not saved_data.empty:
                district_names = saved_data["NAME OF THE DISTRICT"].unique()
                selected_district_name = st.selectbox("Select District Name to Edit", district_names)
                # Filter only the relevant data
                selected_entries = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]
                st.write("Edit the selected entries:")

                article_entries = []
                modified_indices = []  # Track which entries are modified

                for index, row in selected_entries.iterrows():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        quantity = st.number_input(f"Quantity of {row['REQUESTED ARTICLE']}*", min_value=1, step=1,
                            value=int(row["QUANTITY"]),key=f"qty_{row['REQUESTED ARTICLE']}_{selected_district_name}_{index}")


                    cost_per_unit = article.loc[article["Articles"] == row["REQUESTED ARTICLE"], "Cost per unit"].values[0]

                    with col2:
                        st.write(f"Cost per Unit: ₹{cost_per_unit}")

                    with col3:
                        if cost_per_unit == 0:

                            total_value = st.number_input(f"Total Value for {row['REQUESTED ARTICLE']}*", min_value=0.0, step=1.0,
                                value=float(row["TOTAL COST"]),key=f"total_value_{row['REQUESTED ARTICLE']}_{selected_district_name}_{index}")

                        else:
                            total_value = quantity * cost_per_unit
                            st.write(f"Total: ₹{total_value}")

                    with col4:
                        comment = st.text_area(f"Comment for {row['REQUESTED ARTICLE']}",key=f"comment_{row['REQUESTED ARTICLE']}_{selected_district_name}_{index}",
                            value=row["COMMENTS"], height=68)

                    # Track modifications
                    if (quantity != row["QUANTITY"] or total_value != row["TOTAL COST"] or comment != row["COMMENTS"]):
                        modified_indices.append(index)  # Store modified index

                    article_entries.append({
                        "INDEX": index,  # Store index to track which ones to update
                        "NAME OF THE DISTRICT": selected_district_name,
                        "REQUESTED ARTICLE": row["REQUESTED ARTICLE"],
                        "QUANTITY": quantity,
                        "COST PER UNIT": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
                        "TOTAL COST": total_value,
                        "COMMENTS": comment,
                        "ITEM TYPE": article[article["Articles"] == row["REQUESTED ARTICLE"]]["Item Type"].tolist()[0],
                        "Beneficiary Type": "District",
                    })

                if st.button("Update"):

                    for entry in article_entries:
                        if entry["INDEX"] in modified_indices:
                            saved_data.loc[entry["INDEX"], "QUANTITY"] = entry["QUANTITY"]
                            saved_data.loc[entry["INDEX"], "TOTAL COST"] = entry["TOTAL COST"]
                            saved_data.loc[entry["INDEX"], "COMMENTS"] = entry["COMMENTS"]
                            saved_data.loc[entry["INDEX"], "COST PER UNIT"] = entry["COST PER UNIT"]


                    alloted_funds = district[district["District Name"] == selected_district_name]["Alloted Budget"].values.tolist()[0]
                    remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]["TOTAL COST"].sum()
                    # to resolve mismatched cells
                    saved_data = saved_data.reset_index(drop=True)
                    try:
                        last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name].index[-1]
                        first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name].index[0]

                        # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
                        saved_data.loc[saved_data["NAME OF THE DISTRICT"] == selected_district_name, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
                        saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_funds
                        saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
                    except IndexError:
                        pass

                    #Save changes to storage
                    update_file(master_data_id, saved_data)
                    st.success("Request updated successfully!")
                    st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name])

                alloted_funds = district[district["District Name"] == selected_district_name]["Alloted Budget"].values.tolist()[0]
                remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]["TOTAL COST"].sum()
                st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_funds:,}</span></h5>",unsafe_allow_html=True)
                if remaining_fund > 0:
                    fund_color = "green"
                else:
                    fund_color = "red"
                st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{fund_color};'>{remaining_fund:,}</span></h5>",unsafe_allow_html=True, )

            else:
                st.write("No entries available to edit.")


        elif action == "Delete":
            # Select an entry to delete
            if not saved_data.empty:
                district_names = saved_data["NAME OF THE DISTRICT"].unique()
                selected_district_name = st.selectbox("Select District Name to Delete", district_names)

                # Filter the data for the selected district name
                selected_entries = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]

                # Add a checkbox for each record to allow selection
                st.write("Select records to delete:")

                delete_indices = []
                for index, row in selected_entries.iterrows():
                    if st.checkbox(
                            f"Delete {row['REQUESTED ARTICLE']} (Qty: {row['QUANTITY']}, Total: ₹{row['TOTAL COST']}, Comments: {row['COMMENTS']})",
                            key=f"delete_{index}"):
                        delete_indices.append(index)

                # Delete Button
                if st.button("Delete Selection"):
                    if not delete_indices:
                        st.error("Please select at least one record to delete.")
                    else:
                        # Remove the selected records
                        saved_data = saved_data.drop(delete_indices).sort_values(by="NAME OF THE DISTRICT", ascending=True).reset_index(drop=True)

                        alloted_funds = district[district["District Name"] == selected_district_name]["Alloted Budget"].values.tolist()[0]
                        remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]["TOTAL COST"].sum()

                        # to resolve mismatched cells
                        saved_data = saved_data.reset_index(drop=True)

                        try:
                            last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name].index[-1]
                            first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name].index[0]

                            # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
                            saved_data.loc[saved_data["NAME OF THE DISTRICT"] == selected_district_name, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
                            saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_funds
                            saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
                        except IndexError:
                            pass

                        # Save the updated data back to storage
                        update_file(master_data_id, saved_data)

                        # Success message
                        st.success("Selected records deleted successfully!")
                        st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name])

                alloted_funds = district[district["District Name"] == selected_district_name]["Alloted Budget"].values.tolist()[0]
                remaining_fund = alloted_funds - saved_data[saved_data["NAME OF THE DISTRICT"] == selected_district_name]["TOTAL COST"].sum()
                st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_funds:,}</span></h5>",unsafe_allow_html=True)
                if remaining_fund > 0:
                    fund_color = "green"
                else:
                    fund_color = "red"
                st.markdown(
                    f"<h5>Remaining Fund: ₹ <span style='color:{fund_color};'>{remaining_fund:,}</span></h5>",
                    unsafe_allow_html=True, )
            else:
                st.write("No entries available to delete.")


        # Download Functionality
        st.download_button(
            label="Download Records",
            data=saved_data.to_csv(index=False).encode('utf-8'),
            file_name="District_Records.csv",
            mime="text/csv"
        )

    elif type_choice == "Public":

        public = read_file(public_data_id)
        public_master = read_file(public_master_id)
        public_master["Aadhar (Without Space)"] = public_master["Aadhar (Without Space)"].astype(str)
        checked_id = "1X12wSEFnt7mivh5dysPSnH4nVZZPfPJgWBUk3e_oO7c"
        check_file = read_file(checked_id)

        # Initialize session state for checked Aadhaar numbers
        p_choice = st.radio("", ["Validation", "Entry"], horizontal=True)

        if p_choice == "Validation":
            # Validation logic remains the same
            aadhar_no = st.text_input("Enter Aadhaar Number")
            if aadhar_no:
                if aadhar_no in check_file["checked_aadhar_no"].astype(str).values:
                    st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
                else:
                    check_file = pd.concat([check_file, pd.DataFrame([{"checked_aadhar_no": str(aadhar_no)}])],
                                           ignore_index=True)
                    update_file(checked_id, check_file)

                if aadhar_no in public["AADHAR No.1"].astype(str).values:
                    Name_b = public[public["AADHAR No.1"] == aadhar_no]["NAME"].values.tolist()[0]
                    Art_n = public[public["AADHAR No.1"] == aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
                    year_p = public[public["AADHAR No.1"] == aadhar_no]["YEAR"].values.tolist()[0]
                    st.error(
                        f"Aadhaar Number {aadhar_no} is present in the database. Beneficiary: {Name_b}, Item: {Art_n}, Year: {year_p}.")
                else:
                    st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")

        if p_choice == "Entry":

            st.header("Public Request")
            action = st.radio("Action", options=["Add", "Edit", "Delete"], horizontal=True)
            # Initialize session state for form fields
            if "form_data" not in st.session_state:
                st.session_state["form_data"] = {
                    "app_no": "",
                    "aadhar": "",
                    "name": "",
                    "handicapped": "No",
                    "address": "",
                    "mobile": "",
                    "article_name": "",
                    "quantity": 1,
                    "comment": "No"
                }

            # Input common fields
            app_no = st.text_input("Application Number (e.g., P 001)",value=st.session_state["form_data"]["app_no"])

            st.session_state["form_data"]["app_no"] = app_no

            if action == "Add":
                aadhar = st.text_input("Aadhaar Number", value=st.session_state["form_data"]["aadhar"])
                name = st.text_input("Name", value=st.session_state["form_data"]["name"])
                handicapped = st.radio("Handicapped", options=["Yes", "No"], horizontal=True,
                                       index=["Yes", "No"].index(st.session_state["form_data"]["handicapped"]))
                address = st.text_area("Address", value=st.session_state["form_data"]["address"])
                mobile = st.text_input("Mobile Number", value=st.session_state["form_data"]["mobile"])
                # Ensure article_name is not defaulted to the first element
                article_options = article["Articles"].unique().tolist()
                article_name = st.selectbox(
                    "Select Article Name",
                    options=article_options,
                    index=article_options.index(st.session_state["form_data"]["article_name"]) if
                    st.session_state["form_data"]["article_name"] in article_options else 0)

                cpu = st.number_input("Cost Per Unit",
                                      value=article[article["Articles"] == article_name]["Cost per unit"].tolist()[
                                          0], disabled=True)
                quantity = st.number_input("Quantity*", min_value=1, step=1,
                                           value=st.session_state["form_data"]["quantity"])
                default_total_value = quantity * cpu

                total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
                                              disabled=(cpu != 0))

                comment = st.text_area("Comments", height=68, value=st.session_state["form_data"]["comment"])

                # Update session state with current values
                st.session_state["form_data"].update({
                    "aadhar": aadhar,
                    "name": name,
                    "handicapped": handicapped,
                    "address": address,
                    "mobile": mobile,
                    "article_name": article_name,
                    "quantity": quantity,
                    "comment": comment
                })

                if st.button("Submit"):

                    try:
                        if not app_no:
                            st.warning("Application Number cannot be empty.")
                        elif app_no in public_master["App. No."].values:
                            st.error("Application Number already added to the Application.")
                        elif not aadhar:
                            st.warning("Aadhaar Number cannot be empty.")
                        elif aadhar in public["AADHAR No.1"].astype(str).values:
                            st.error("Aadhaar number is already present in the database.")
                        elif aadhar in public_master["Aadhar (Without Space)"].values:
                            st.error("Aadhaar Number is already added to an application.")
                        else:
                            new_entry = {
                                "App. No.": str(app_no),
                                "Aadhar (Without Space)": str(aadhar),
                                "Name": str(name),
                                "Handicapped (Yes / No)": handicapped,
                                "Address": address,
                                "Mobile": str(mobile),
                                "Article Name": article_name,
                                "Comments": comment,
                                "Cost Per Unit": int(total_value / quantity if cpu == 0 else cpu),
                                "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],
                                "Total Value": int(total_value),
                                "Quantity": int(quantity),
                                "Beneficiary Type": "Public"
                            }

                            public_master = pd.concat([public_master, pd.DataFrame([new_entry])],ignore_index=True).sort_values(by=["App. No."],
                                                                                     ascending=True).reset_index(drop=True)

                            update_file(public_master_id, public_master)

                            st.success(f"Application {app_no} added successfully!")

                            st.dataframe(public_master)

                            # Reset form fields

                            st.session_state["form_data"] = {
                                "app_no": "",
                                "aadhar": "",
                                "name": "",
                                "handicapped": "No",
                                "address": "",
                                "mobile": "",
                                "article_name": "",  # Reset to empty
                                "quantity": 1,
                                "comment": "No"
                            }

                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")


            elif action == "Edit":

                if st.button("Search", key="search_button"):
                    # Search for the record by Application Number
                    record = public_master[public_master["App. No."] == app_no.strip()]

                    if not record.empty:
                        # Store record in session state for persistence
                        st.session_state["edit_record"] = record.iloc[0].to_dict()
                    else:
                        st.error("Application not found.")

                if "edit_record" in st.session_state:

                    # Retrieve the stored record from session state
                    record = st.session_state["edit_record"]

                    # Display fields for editing
                    aadhar = st.text_input("Aadhaar Number", value=record["Aadhar (Without Space)"])
                    name = st.text_input("Name", value=record["Name"])
                    handicapped = st.radio("Handicapped",options=["Yes", "No"],horizontal=True,
                        index=["Yes", "No"].index(record["Handicapped (Yes / No)"]))
                    address = st.text_area("Address", value=record["Address"])
                    mobile = st.text_input("Mobile Number", value=record["Mobile"])
                    article_name = st.selectbox("Select Article Name",
                        article["Articles"].unique().tolist(),
                        index=article["Articles"].tolist().index(record["Article Name"]))
                    cpu = st.number_input("Cost Per Unit",value= record["Cost Per Unit"],disabled=True)
                    quantity = st.number_input("Quantity*", min_value=1, step=1,value=record["Quantity"])

                    default_total_value = quantity * cpu
                    total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
                                                  disabled=(cpu != 0))
                    comment = st.text_area("Comments", value=record["Comments"],height=68)

                    if st.button("Update", key="update_button"):
                        try:
                            # Update the record in the DataFrame
                            public_master.loc[public_master["App. No."] == app_no, "Aadhar (Without Space)"] = aadhar
                            public_master.loc[public_master["App. No."] == app_no, "Name"] = name
                            public_master.loc[public_master["App. No."] == app_no, "Handicapped (Yes / No)"] = handicapped
                            public_master.loc[public_master["App. No."] == app_no, "Address"] = address
                            public_master.loc[public_master["App. No."] == app_no, "Mobile"] = str(mobile)
                            public_master.loc[public_master["App. No."] == app_no, "Article Name"] = article_name
                            public_master.loc[public_master["App. No."] == app_no, "Comments"] = comment
                            public_master.loc[public_master["App. No."] == app_no, "Cost Per Unit"] = int(total_value/quantity if cpu == 0 else cpu)
                            public_master.loc[public_master["App. No."] == app_no, "Quantity"] = int(quantity)
                            public_master.loc[public_master["App. No."] == app_no, "Total Value"] = int(total_value)
                            public_master.loc[public_master["App. No."] == app_no, "Beneficiary Type"] = "Public"
                            public_master.loc[public_master["App. No."] == app_no, "ITEM TYPE"] = article[article["Articles"] == article_name]["Item Type"].tolist()[0],

                            # Save the updated data back to the file
                            update_file(public_master_id, public_master)
                            st.success(f"Application {app_no} updated successfully!")
                            st.session_state.pop("edit_record")  # Clear session state after update
                            st.dataframe(public_master)
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")

            elif action == "Delete":
                if st.button("Delete"):
                    # Check if the record exists
                    if app_no in public_master["App. No."].values:
                        # Delete the record
                        public_master = public_master[public_master["App. No."] != app_no]

                        # Save the updated data back to the file
                        update_file(public_master_id, public_master)

                        st.success(f"Application {app_no} deleted successfully!")
                    else:
                        st.error("Application not found.")
                st.dataframe(public_master)

            pub_fund = public_master['Total Value'].sum()
            # color
            st.markdown(f"<h5>Total Accrued: ₹ <span style='color:{'Green' if pub_fund >= 0 else 'Red'};'>{pub_fund:,.0f}</span></h5>",
                        unsafe_allow_html=True)
            st.download_button(
                label="Download Records",
                data=public_master.to_csv(index=False).encode('utf-8'),
                file_name="Public Beneficiaries Records.csv",
                mime="text/csv")

    elif type_choice == "Institutions & Others":

        # Streamlit UI
        st.header("Institution & Other Requests")

        # Load institution data (replace with your actual file reading)
        inst_data = read_file(inst_data_id)


        # Function to reset form fields
        def reset_form():
            st.session_state.clear()
            st.session_state["app_number"] = ""
            st.session_state["institution_name"] = ""
            st.session_state["institution_type"] = "Institution"  # Default to "Institution"
            st.session_state["address"] = ""
            st.session_state["mobile"] = ""
            st.session_state["selected_articles"] = []
            st.session_state["article_comments"] = {}


        # Initialize session state for form fields if not already set
        if "app_number" not in st.session_state:
            reset_form()

        # User action selection
        action = st.radio("Select Action", ["Add", "Edit", "Delete"], horizontal=True)

        if action == "Add":

            # Application Number
            st.session_state["app_number"] = st.text_input("Application No.*(Eg. 'I 001', 'O 001')",
                                                           value=st.session_state["app_number"])

            # Institution Details
            st.session_state["institution_name"] = st.text_input("Institution Name*",
                                                                 value=st.session_state["institution_name"])
            st.session_state["institution_type"] = st.radio("Institution Type*",
                ["Institution", "Others"],
                index=0 if st.session_state.get("institution_type", "Institution") == "Institution" else 1,
                horizontal=True)

            st.session_state["address"] = st.text_area("Address*", value=st.session_state["address"])
            st.session_state["mobile"] = st.text_input("Mobile*", value=st.session_state["mobile"])

            # Article Selection
            st.session_state["selected_articles"] = st.multiselect("Select Articles*", article["Articles"].tolist(),
                                                                   default=st.session_state["selected_articles"])

            # Article Details

            article_entries = []
            article_comments = {}

            for article_name in st.session_state["selected_articles"]:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Use a unique key by combining article name and application number
                    quantity = st.number_input(
                        f"Quantity of {article_name}*",
                        min_value=1,
                        step=1,
                        key=f"qty_{article_name}_{st.session_state['app_number']}"  # Unique key
                    )
                cost_per_unit = article.loc[article["Articles"] == article_name, "Cost per unit"].values[0]

                with col2:
                    st.write(f"Cost per Unit: ₹{cost_per_unit}")

                with col3:
                    if cost_per_unit == 0:
                        total_value = st.number_input(
                            f"Total Value for {article_name}*",
                            min_value=0.0,
                            step=1.0,
                            key=f"total_value_{article_name}_{st.session_state['app_number']}")

                    else:
                        total_value = quantity * cost_per_unit
                        st.write(f"Total: ₹{total_value}")

                with col4:
                    comment = st.text_area(
                        f"Comment for {article_name}",
                        key=f"comment_{article_name}_{st.session_state['app_number']}",  # Unique key
                        value="No", height=68
                    )
                    article_comments[article_name] = comment

                article_entries.append({
                    "Article Name": article_name,
                    "Quantity": quantity,
                    "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
                    "Total Value": total_value,
                    "Comments": article_comments[article_name],
                    "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],

                })

            # Submit Button for new requests
            if st.button("Add"):
                if not st.session_state["app_number"] or not st.session_state["institution_name"] or not \
                st.session_state["address"] or not st.session_state["mobile"] or not st.session_state[
                    "selected_articles"]:
                    st.error("Please fill all required fields (*) before submitting.")

                else:
                    # Check for duplicate entries (same App. No., Article Name, and Comments)
                    duplicate_entries = []

                    for entry in article_entries:
                        duplicate = inst_data[
                            (inst_data["App. No."] == st.session_state["app_number"]) &
                            (inst_data["Article Name"] == entry["Article Name"]) &
                            (inst_data["Comments"] == entry["Comments"])
                            ]
                        if not duplicate.empty:
                            duplicate_entries.append(entry["Article Name"])

                    if duplicate_entries:
                        st.error(
                            f"Duplicate entries found for the following articles with the same comments: {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")

                    else:
                        # Flatten the article entries into individual rows
                        flattened_articles = []

                        for entry in article_entries:
                            flattened_articles.append({
                                "App. No.": st.session_state["app_number"],
                                "Institution Name": st.session_state["institution_name"],
                                "Beneficiary Type": st.session_state["institution_type"],
                                "Address": st.session_state["address"],
                                "Mobile": str(st.session_state["mobile"]),
                                "Article Name": entry["Article Name"],
                                "Quantity": entry["Quantity"],
                                "Cost Per Unit": entry["Cost Per Unit"],
                                "Total Value": entry["Total Value"],
                                "Comments": entry["Comments"],
                                "ITEM TYPE": entry["ITEM TYPE"],
                            })

                        # Convert the flattened articles into a DataFrame
                        flattened_df = pd.DataFrame(flattened_articles)

                        # Append the new flattened data to the existing institution data
                        inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
                            by="App. No.", ascending=True).reset_index(drop=True)

                        # Save the updated data back to storage
                        update_file(inst_data_id, inst_data)

                        # Clear form fields after successful submission
                        reset_form()

                        # Success message
                        st.success("Request submitted successfully!")
                        st.dataframe(inst_data)


        elif action == "Edit":

            # Select an entry to edit
            if not inst_data.empty:
                app_numbers = inst_data["App. No."].unique()
                selected_app_number = st.selectbox("Select Application Number to Edit", app_numbers)

                # Filter the data for the selected application number
                selected_entries = inst_data[inst_data["App. No."] == selected_app_number]

                # Display the selected entries for editing
                st.write("Edit the selected entries:")

                # Institution Details
                institution_name = st.text_input("Institution Name*",
                                                 value=selected_entries["Institution Name"].values[0])
                institution_type = st.radio("Institution Type*", ["Institution", "Others"], horizontal=True,
                                            index=0 if st.session_state.get("institution_type",
                                                                            "Institution") == "Institution" else 1)
                address = st.text_area("Address*", value=selected_entries["Address"].values[0])
                mobile = st.text_input("Mobile*", value=selected_entries["Mobile"].values[0])

                # Article Details

                article_entries = []

                for index, row in selected_entries.iterrows():

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        # Use a unique key by combining article name, application number, and index
                        quantity = st.number_input(
                            f"Quantity of {row['Article Name']}*",min_value=1,step=1,
                            value=int(row["Quantity"]),
                            key=f"qty_{row['Article Name']}_{selected_app_number}_{index}"  # Unique key
                        )

                    cost_per_unit = article.loc[article["Articles"] == row["Article Name"], "Cost per unit"].values[0]

                    with col2:
                        st.write(f"Cost per Unit: ₹{cost_per_unit}")

                    with col3:
                        if cost_per_unit == 0:
                            total_value = st.number_input(
                                f"Total Value for {row['Article Name']}*",
                                min_value=0.0,
                                step=1.0,
                                value=float(row["Total Value"]),
                                key=f"total_value_{row['Article Name']}_{selected_app_number}_{index}"
                            )
                        else:
                            total_value = quantity * cost_per_unit
                            st.write(f"Total: ₹{total_value}")

                    with col4:
                        comment = st.text_area(f"Comment for {row['Article Name']}",
                            key=f"comment_{row['Article Name']}_{selected_app_number}_{index}",  # Unique key
                            value=row["Comments"], height=68)

                    article_entries.append({
                        "Article Name": row["Article Name"],
                        "Quantity": quantity,
                        "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
                        "Total Value": total_value,
                        "Comments": comment,
                        "ITEM TYPE": article[article["Articles"] == row["Article Name"]]["Item Type"].tolist()[0],

                    })

                # Update Button for editing
                if st.button("Update"):
                    if not institution_name or not address or not mobile or not article_entries:
                        st.error("Please fill all required fields (*) before updating.")

                    else:
                        # Check for duplicate entries (same App. No., Article Name, and Comments)
                        duplicate_entries = []

                        for entry in article_entries:
                            duplicate = inst_data[
                                (inst_data["App. No."] == selected_app_number) &
                                (inst_data["Article Name"] == entry["Article Name"]) &
                                (inst_data["Comments"] == entry["Comments"]) &
                                (inst_data.index != index)  # Exclude the current entry being edited
                                ]
                            if not duplicate.empty:
                                duplicate_entries.append(entry["Article Name"])

                        if duplicate_entries:
                            st.error(
                                f"Duplicate entries found : {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")

                        else:
                            # Remove the old entries
                            inst_data = inst_data[inst_data["App. No."] != selected_app_number]

                            # Flatten the article entries into individual rows
                            flattened_articles = []

                            for entry in article_entries:
                                flattened_articles.append({
                                    "App. No.": selected_app_number,
                                    "Institution Name": institution_name,
                                    "Beneficiary Type": institution_type,
                                    "Address": address,
                                    "Mobile": str(mobile),
                                    "Article Name": entry["Article Name"],
                                    "Quantity": entry["Quantity"],
                                    "Cost Per Unit": entry["Cost Per Unit"],
                                    "Total Value": entry["Total Value"],
                                    "Comments": entry["Comments"],
                                    "ITEM TYPE": entry["ITEM TYPE"],
                                })

                            # Convert the flattened articles into a DataFrame
                            flattened_df = pd.DataFrame(flattened_articles)

                            # Append the updated data to the existing institution data
                            inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
                                by="App. No.", ascending=True).reset_index(drop=True)

                            # Save the updated data back to storage
                            update_file(inst_data_id, inst_data)
                            # Success message
                            st.success("Request updated successfully!")
                            st.dataframe(inst_data)

            else:
                st.write("No entries available to edit.")


        elif action == "Delete":

            # Select an entry to delete
            if not inst_data.empty:
                app_numbers = inst_data["App. No."].unique()
                selected_app_number = st.selectbox("Select Application Number to Delete", app_numbers)
                # Filter the data for the selected application number
                selected_entries = inst_data[inst_data["App. No."] == selected_app_number]
                # Add a checkbox for each record to allow selection
                st.write("Select records to delete:")

                delete_indices = []
                for index, row in selected_entries.iterrows():
                    if st.checkbox(
                            f"Delete {row['Article Name']} (Qty: {row['Quantity']}, Total: ₹{row['Total Value']}, Comments: {row['Comments']})",
                            key=f"delete_{index}"):
                        delete_indices.append(index)

                # Delete Button
                if st.button("Delete Selection"):

                    if not delete_indices:
                        st.error("Please select at least one record to delete.")

                    else:
                        # Remove the selected records
                        inst_data = inst_data.drop(delete_indices).sort_values(by="App. No.",
                                                                               ascending=True).reset_index(drop=True)
                        # Save the updated data back to storage
                        update_file(inst_data_id, inst_data)
                        # Success message
                        st.success("Selected records deleted successfully!")
                        st.dataframe(inst_data)
            else:
                st.write("No entries available to delete.")

        inst_fund = inst_data[inst_data["Beneficiary Type"]=="Institution"]['Total Value'].sum()
        oth_fund = inst_data[inst_data["Beneficiary Type"]=="Others"]['Total Value'].sum()
        # color = ?
        st.markdown(f"<h5>Total Accrued (Instn): ₹ <span style='color:{'Green' if inst_fund >= 0 else 'Red'};'>{inst_fund:,.0f}</span></h5>",
            unsafe_allow_html=True)
        st.markdown(
            f"<h5>Total Accrued (Others): ₹ <span style='color:{'Green' if oth_fund >= 0 else 'Red'};'>{oth_fund:,.0f}</span></h5>",
            unsafe_allow_html=True)

        st.download_button(
            label="Download Records",
            data=inst_data.to_csv(index=False).encode('utf-8'),
            file_name="Instn_Oth_Records.csv",
            mime="text/csv"

        )


if selected_tab == "Manage Articles":
    st.header("Manage Articles")

    article_options = ["Add New"] + list(article["Articles"].unique())
    article_name = st.selectbox("Select Article", article_options)

    if article_name == "Add New":
        # Adding a new article
        new_article = st.text_input("Enter New Article Name*")
        new_cpu = st.number_input("Enter Cost Per Unit*", min_value=0)
        new_item_type = st.radio("Select Type", ["Article", "Aid", "Project"], horizontal=True)

        if st.button("Save Article"):
            if new_article:
                new_article_entry = {
                    "Articles": new_article,
                    "Cost per unit": new_cpu,
                    "Item Type": new_item_type,
                }

                # Append new article and remove duplicates
                article = pd.concat([article, pd.DataFrame([new_article_entry])], ignore_index=True).sort_values(by="Articles",ascending=True).reset_index(drop=True)
                article.drop_duplicates(subset=["Articles","Cost per unit"], inplace=True)

                # Save updated article data
                update_file(article_data_id,article)

                st.success(f"Article '{new_article}' added successfully!")
                st.dataframe(article)
            else:
                st.error("Please enter a valid article name.")

    else:
        # Editing an existing article with a checkbox to enable editing
        existing_article = article[article["Articles"] == article_name].iloc[0]

        edit_enabled = st.checkbox("Edit", key=f"edit_{article_name}")

        edit_cpu = st.number_input(
            "Cost Per Unit*",
            min_value=0,
            value=int(existing_article["Cost per unit"]),
            disabled=not edit_enabled
        )

        edit_item_type = st.radio(
            "Item Type",
            ["Article", "Aid", "Project"],
            horizontal=True,
            index=["Article", "Aid", "Project"].index(existing_article["Item Type"]),
            disabled=not edit_enabled
        )

        if edit_enabled and st.button("Update Article"):
            article.loc[article["Articles"] == article_name, "Cost per unit"] = edit_cpu
            article.loc[article["Articles"] == article_name, "Item Type"] = edit_item_type

            # Save updated article data
            update_file(article_data_id,article)

            st.success(f"Article '{article_name}' updated successfully!")
            st.dataframe(article)

        # Delete functionality
        if st.button("Delete Article"):
            article = article[article["Articles"] != article_name]
            update_file(article_data_id,article)
            st.success(f"Article '{article_name}' deleted successfully!")
            st.dataframe(article)

    # Download Functionality
    st.download_button(
        label="Download Article List",
        data=article.to_csv(index=False).encode('utf-8'),
        file_name="Article_list.csv",
        mime="text/csv"
    )


if selected_tab == "District Records":
    st.header("Districts Records")
    rc_data = read_file(master_data_id)
    dname = st.selectbox("Select District",rc_data["NAME OF THE DISTRICT"].unique())
    st.dataframe(rc_data[rc_data["NAME OF THE DISTRICT"] == dname])


if selected_tab == "Inventory":
    st.header("Inventory Management")
    # Read and process data FOR INVENTORY

    district_df = read_file(master_data_id)[["REQUESTED ARTICLE", "QUANTITY", "Beneficiary Type"]]
    public_df = \
    read_file(public_master_id).rename(columns={"Article Name": "REQUESTED ARTICLE", "Quantity": "QUANTITY"})[
        ["REQUESTED ARTICLE", "QUANTITY", "Beneficiary Type"]]
    inst_df = read_file(inst_data_id).rename(columns={"Article Name": "REQUESTED ARTICLE", "Quantity": "QUANTITY"})[
        ["REQUESTED ARTICLE", "QUANTITY", "Beneficiary Type"]]
    final = pd.concat([district_df, public_df, inst_df]).reset_index(drop=True).groupby(
        ["REQUESTED ARTICLE", "Beneficiary Type"], as_index=False).sum()

    inv_opt = list(final["REQUESTED ARTICLE"].unique()) + ["Sewing Motor"]
    selected_inventory = st.selectbox("Select Inventory", inv_opt)

    if selected_inventory == "Sewing Motor":
        st.warning("Tracking Motor separately for inventory purposes.")

        # Read order data and ensure required columns exist
        existing_data = read_file(ord_req_id)
        if "Ordered Quantity" not in existing_data:
            existing_data["Ordered Quantity"] = 0
        if "Remaining Quantity" not in existing_data:
            existing_data["Remaining Quantity"] = existing_data.get("Total", 0)

        # Check if "Motor" row exists, otherwise add it
        if "Sewing Motor" not in existing_data["REQUESTED ARTICLE"].values:
            new_motor_row = pd.DataFrame({"REQUESTED ARTICLE": ["Sewing Motor"],
                                          "District":[int(existing_data[existing_data["REQUESTED ARTICLE"]=="Sewing Machine ORD / Motor"]["District"].values[0])],
                                          "Institution": [int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Institution"].values[0])],
                                          "Others": [int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Others"].values[0])],
                                          "Public": [int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Public"].values[0])],
                                          "Total": [int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Total"].values[0])],
                                          "Ordered Quantity": [0], "Remaining Quantity": [0]})
            existing_data = pd.concat([existing_data, new_motor_row], ignore_index=True)

        # Get existing ordered quantity for "Sewing Motor"
        motor_ordered_qty = int(existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Ordered Quantity"].values[0])

        # Input for ordered quantity of motors
        ordered_motor_quantity = st.number_input("Enter Ordered Quantity for Motor", min_value=0,
                                                 value=motor_ordered_qty)
        remaining_motor_quantity = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Total"].values[0]) - ordered_motor_quantity  # No total quantity tracking, so it equals ordered

        st.markdown(f"<h5>Ordered: <span style='color:black;'>{motor_ordered_qty}</span></h5>", unsafe_allow_html=True)
        st.markdown(f"<h5>Remaining: <span style='color:black;'>{remaining_motor_quantity}</span></h5>",unsafe_allow_html=True)

        # Update motor order tracking
        if st.button("Update Motor"):
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "District"] = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["District"].values[0])
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Public"] = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Public"].values[0])
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Others"] = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Others"].values[0])
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Institution"] = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Institution"].values[0])
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Total"] = int(existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Machine ORD / Motor"]["Total"].values[0])
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Ordered Quantity"] = int(ordered_motor_quantity)
            existing_data.loc[existing_data["REQUESTED ARTICLE"] == "Sewing Motor", "Remaining Quantity"] = int(remaining_motor_quantity)
            existing_data = existing_data.sort_values("REQUESTED ARTICLE",ascending=True).reset_index(drop=True)
            update_file(ord_req_id, existing_data)
            st.success("Motor ordered quantity updated successfully!")
        st.write("Select other articles to see Download Button")

    else:

        filtered_final = final[final["REQUESTED ARTICLE"] == selected_inventory]
        total = int(filtered_final["QUANTITY"].sum())

        # Check if data is available
        if filtered_final.empty:
            st.markdown("**No data available for this inventory item.**")
        else:
            # Create four columns
            col1, col2, col3, col4 = st.columns(4)

            # Define a mapping of beneficiary types to columns
            column_map = {"District": col1, "Public": col2, "Institution": col3, "Others": col4}

            # Initialize each column to 0 if the corresponding beneficiary type is missing
            for beneficiary in column_map.keys():
                filtered_beneficiary = filtered_final[filtered_final["Beneficiary Type"] == beneficiary]
                quantity = filtered_beneficiary["QUANTITY"].sum() if not filtered_beneficiary.empty else 0
                column_map[beneficiary].markdown(
                    f"<h2>{beneficiary}: <span style='color:Green;'>{quantity}</span></h2>", unsafe_allow_html=True)
            st.markdown(f"<h2>Total : <span style='color:Blue;'>{total}</span></h2>", unsafe_allow_html=True)

        # Pivot the DataFrame to create columns for each Beneficiary Type and total
        pivot_df = final.pivot_table(index="REQUESTED ARTICLE", columns="Beneficiary Type", values="QUANTITY",aggfunc="sum", fill_value=0)

        # Reset index and add missing columns for Beneficiary Types
        pivot_df = pivot_df.reset_index()
        pivot_df["District"] = pivot_df.get("District", 0)
        pivot_df["Public"] = pivot_df.get("Public", 0)
        pivot_df["Institution"] = pivot_df.get("Institution", 0)
        pivot_df["Others"] = pivot_df.get("Others", 0)

        # Calculate Total Quantity
        pivot_df["Total"] = pivot_df[["District", "Public", "Institution", "Others"]].sum(axis=1)

        # Add input fields for ordered quantity and calculate remaining quantity
        existing_data = read_file(ord_req_id)

        # Ensure required columns exist in the existing data
        if "Ordered Quantity" not in existing_data:
            existing_data["Ordered Quantity"] = 0
        if "Remaining Quantity" not in existing_data:
            existing_data["Remaining Quantity"] = existing_data.get("Total", 0)

        # 🔥 Preserve "Sewing Motor" before merging
        motor_row = existing_data[existing_data["REQUESTED ARTICLE"] == "Sewing Motor"]

        # Merge pivot_df with existing data to include all articles
        updated_df = pivot_df.merge(
            existing_data[["REQUESTED ARTICLE", "Ordered Quantity", "Remaining Quantity"]],
            on="REQUESTED ARTICLE",
            how="left",
            suffixes=("", "_old")
        )

        # Fill NaN values for Ordered Quantity and Remaining Quantity
        updated_df["Ordered Quantity"] = updated_df["Ordered Quantity"].fillna(0)
        updated_df["Remaining Quantity"] = updated_df["Remaining Quantity"].fillna(updated_df["Total"])

        # 🔥 Ensure "Sewing Motor" is added back to the file
        if not motor_row.empty:
            updated_df = pd.concat([updated_df, motor_row], ignore_index=True)

        # Get the existing ordered quantity for the selected inventory
        ex_or_qty = int(
            updated_df.loc[updated_df["REQUESTED ARTICLE"] == selected_inventory, "Ordered Quantity"].values[0])

        # Input for ordered quantity
        ordered_quantity = st.number_input("Enter Ordered Quantity", min_value=0, value=ex_or_qty)
        remaining_quantity = total - ordered_quantity

        # Display existing and remaining quantities
        st.markdown(f"<h5>Ordered: <span style='color:black;'>{ex_or_qty}</span></h5>", unsafe_allow_html=True)
        st.markdown(f"<h5>Remaining: <span style='color:black;'>{remaining_quantity}</span></h5>",
                    unsafe_allow_html=True)

        # Update the ordered and remaining quantities for the selected inventory
        if st.button("Update Order"):
            updated_df.loc[updated_df["REQUESTED ARTICLE"] == selected_inventory, "Ordered Quantity"] = int(ordered_quantity)
            updated_df.loc[updated_df["REQUESTED ARTICLE"] == selected_inventory, "Remaining Quantity"] = int(remaining_quantity)
            updated_df["Remaining Quantity"] = updated_df["Total"] - updated_df["Ordered Quantity"]
            updated_df = updated_df.sort_values("REQUESTED ARTICLE",ascending=True).reset_index(drop=True)
            # Save the updated data
            update_file(ord_req_id, updated_df)
            st.success("Ordered quantity updated successfully!")

        # Download the updated summary
        st.download_button(
            label="Download Summary",
            data=updated_df.to_csv(index=False).encode("utf-8"),
            file_name="Inventory_Summary.csv",
            mime="text/csv"
        )
        st.write("***Update Before Download**")


if selected_tab == "All Records":

    district_df = read_file(master_data_id)
    district_df["App. No."] = ""
    cnt = 1
    for names in district_df["NAME OF THE DISTRICT"].unique():
        district_df.loc[district_df["NAME OF THE DISTRICT"] == names, "App. No."] = "D " + str(f"{cnt:03}")
        cnt += 1
    # District
    df1 = district_df[["App. No.", "NAME OF THE DISTRICT", "REQUESTED ARTICLE", "ITEM TYPE", "QUANTITY", "COST PER UNIT",
         "TOTAL COST", "Beneficiary Type", "COMMENTS"]]
    df1 = df1.rename(columns={"NAME OF THE DISTRICT": "Name", "REQUESTED ARTICLE": "Article Name",
                              "COST PER UNIT": "Cost Per Unit", "QUANTITY": "Quantity", "TOTAL COST": "Total Value",
                              "COMMENTS": "Comments"})
    # Public
    df2 = read_file(public_master_id)[["App. No.", "Name", "Article Name", "ITEM TYPE", "Quantity", "Cost Per Unit", "Total Value",
         "Beneficiary Type", "Comments"]]
    # Instn and Others
    inst_df = read_file(inst_data_id)[["App. No.", "Institution Name", "Article Name", "ITEM TYPE", "Quantity", "Cost Per Unit", "Total Value",
         "Beneficiary Type", "Comments"]]
    df3 = inst_df.rename(columns={"Institution Name": "Name"})


    # Consolidated
    consoldi = pd.concat([df1, df2, df3]).reset_index(drop=True)
    ad = article[["Articles", "Category","Sequence List"]].rename(columns={"Articles": "Article Name","Category": "Article Category"})
    consold = consoldi.merge(ad, on="Article Name", how='left').reset_index(drop=True)

    sl_box=st.selectbox("Beneficiary Type", consold["Beneficiary Type"].unique())
    st.dataframe(consold[consold["Beneficiary Type"] == sl_box])


    # Download Functionality
    st.download_button(
        label="Download All Records",
        data=consold.to_csv(index=False).encode('utf-8'),
        file_name="Master_Records.csv",
        mime="text/csv"
    )

    st.write("Total Beneficiaries: ", "{:,}".format(consold["Quantity"].sum()).replace(",", "X").replace("X", ","))
    st.write("No. of Articles: ","{:,}".format(consold["Article Name"].nunique()).replace(",", "X").replace("X", ","))

    st.write("District Value(₹): ", "{:,.0f}".format(df1["Total Value"].sum()).replace(",", "X").replace("X", ","))
    st.write("Public Value(₹): ", "{:,.0f}".format(df2["Total Value"].sum()).replace(",", "X").replace("X", ","))
    st.write("Institution Value(₹): ", "{:,.0f}".format(df3[df3["Beneficiary Type"]=="Institution"]["Total Value"].sum()).replace(",", "X").replace("X", ","))
    st.write("Others Value(₹): ", "{:,.0f}".format(df3[df3["Beneficiary Type"]=="Others"]["Total Value"].sum()).replace(",", "X").replace("X", ","))
    st.write("Total Value(₹): ", "{:,.0f}".format(consold["Total Value"].sum()).replace(",", "X").replace("X", ","))


# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state['authentication_status'] is None:
#     alert5 = st.info('Please enter your username and password')
#     time.sleep(1)
#     alert5.empty()