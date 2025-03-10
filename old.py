# =
#
#         # Input fields
#         name = st.selectbox("District Name*", district["District Name"].unique().tolist())
#
#         article_name = st.selectbox("Enter Article Name*", article["Articles"].unique().tolist() + ["Add New"])
#
#
#         else:
#             cpu = st.number_input("Cost Per Unit",
#                                   value=article[article["Articles"] == article_name]["Cost per unit"].tolist()[0],
#                                   disabled=True)
#
#             # Retrieve existing quantity for the selected district and article
#             saved_data = read_file(master_data_id)
#             existing_record = saved_data[
#                 (saved_data["NAME OF THE DISTRICT"] == name) &
#                 (saved_data["REQUESTED ARTICLE"] == article_name)
#                 ]
#
#             # Set default quantity to existing value if record exists, else 0
#             default_quantity = existing_record["QUANTITY"].values[0] if not existing_record.empty else 0
#
#             # Input field for quantity with default value
#             quantity = st.number_input("Quantity* (0 to delete)", min_value=0, step=1, value=default_quantity)
#
#             # Auto-calculate total value
#             default_total_value = quantity * cpu
#             # Allow user to edit if needed (pre-filled with the calculated value)
#             total_value = st.number_input("Total Value", value=default_total_value, min_value=0, disabled=(cpu != 0))
#
#             comment = st.text_area("Enter Comment* (Add 'No' if Nothing)", placeholder="Must for Aid and Projects",
#                                    value="No")
#             # Read the saved data from Google Drive
#             saved_data = read_file(master_data_id)
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
#             if st.button("Submit"):
#                 if not name or not article_name:
#                     st.warning("Please fill all fields before saving.")
#                 else:
#                     # Check if quantity is 0 (delete the record)
#                     if quantity == 0:
#                         # Find and remove the selected row from the DataFrame
#                         delete_condition = (
#                                 (saved_data["NAME OF THE DISTRICT"] == name) &
#                                 (saved_data["REQUESTED ARTICLE"] == article_name) &
#                                 (saved_data["COMMENTS"] == comment)
#                         )
#                         saved_data = saved_data[~delete_condition]  # Remove the record
#                         alert2 = st.success(f"Record for {name} and {article_name} deleted successfully!")
#                         time.sleep(1)
#                         alert2.empty()
#
#                     else:
#                         # Check for duplicates and replace if necessary
#                         duplicate_condition = (
#                                 (saved_data["NAME OF THE DISTRICT"] == name) &
#                                 (saved_data["REQUESTED ARTICLE"] == article_name) &
#                                 (saved_data["COMMENTS"] == comment)
#                         )
#                         if duplicate_condition.any():
#                             saved_data.loc[duplicate_condition, ["QUANTITY", "COST PER UNIT", "TOTAL COST"]] = [
#                                 quantity, total_value / quantity if cpu == 0 else cpu, total_value]
#                             alert3 = st.info("Duplicate entry found. Existing record updated.")
#                             time.sleep(2)
#                             alert3.empty()
#
#                         else:
#                             new_entry = {
#                                 "NAME OF THE DISTRICT": name,
#                                 "REQUESTED ARTICLE": article_name,
#                                 "QUANTITY": quantity,
#                                 "TOTAL COST": total_value,
#                                 "COST PER UNIT": total_value / quantity if cpu == 0 else cpu,
#                                 "COMMENTS": comment,
#                                 "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],
#                                 "Beneficiary Type": "District",
#                             }
#
#                             saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])],
#                                                    ignore_index=True).sort_values(
#                                 by=["NAME OF THE DISTRICT", "REQUESTED ARTICLE"], ascending=True).reset_index(drop=True)
#
#                     alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#                     remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name][
#                         "TOTAL COST"].sum()
#                     try:
#                         last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[-1]
#                         first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[0]
#
#                         # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
#                         saved_data.loc[
#                             saved_data["NAME OF THE DISTRICT"] == name, ["ALLOTTED FUNDS", "EXCESS/SHORTAGE"]] = None
#                         saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_fund
#                         saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
#                     except IndexError:
#                         pass
#
#                     saved_data = saved_data.reset_index(drop=True)
#                     alert4 = st.success("Data saved successfully!")
#                     time.sleep(1)
#                     alert4.empty()
#
#                     # Save to CSV
#                     update_file(master_data_id, saved_data)
#
#             # Display the table below
#             st.subheader("Summary")
#             st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == name])
#             remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#             if remaining_fund > 0:
#                 color = "green"
#             else:
#                 color = "red"
#             st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>",
#                         unsafe_allow_html=True)
#
#             st.download_button(
#                 label="Download Records",
#                 data=saved_data.to_csv(index=False).encode('utf-8'),
#                 file_name="District Beneficiaries Records.csv",
#                 mime="text/csv")
#
# elif type_choice == "Public":
# public_data_id = "1sO08BfwN1gzNs_N7XDq1RnqMgJDDKMdq_nsaNhmjKhs"
# public = read_file(public_data_id)
# public_master_id = "1EdEySmYe6ZJUW16f65_q30nkqfbvDADjcmEkAEJrrL4"
# public_master = read_file(public_master_id)
# public_master["Aadhar (Without Space)"] = public_master["Aadhar (Without Space)"].astype(str)
# checked_id = "1X12wSEFnt7mivh5dysPSnH4nVZZPfPJgWBUk3e_oO7c"
# check_file = read_file(checked_id)
#
# # Initialize session state for checked Aadhaar numbers
# p_choice = st.radio("", ["Validation", "Entry"], horizontal=True)
# if p_choice == "Validation":
#
#     # if "checked_aadhar" not in st.session_state:
#     #     st.session_state["checked_aadhar"] = set()
#     # # Input for Aadhaar Number
#     aadhar_no = st.text_input("Enter Aadhaar Number")
#     if aadhar_no:
#         # # Check if the Aadhaar number has already been checked
#         # if aadhar_no in st.session_state["checked_aadhar"]:
#         #     st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
#         # else:
#         #     # Add the Aadhaar number to the checked list
#         #     st.session_state["checked_aadhar"].add(aadhar_no)
#         if aadhar_no in check_file["checked_aadhar_no"].astype(str).values:
#             st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
#         else:
#             check_file = pd.concat([check_file, pd.DataFrame([{"checked_aadhar_no": str(aadhar_no)}])],
#                                    ignore_index=True)
#             update_file(checked_id, check_file)
#
#         # Check if the Aadhaar number exists in the database
#         if aadhar_no in public["AADHAR No.1"].astype(str).values:
#             Name_b = public[public["AADHAR No.1"] == aadhar_no]["NAME"].values.tolist()[0]
#             Art_n = public[public["AADHAR No.1"] == aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
#             year_p = public[public["AADHAR No.1"] == aadhar_no]["YEAR"].values.tolist()[0]
#             st.error(
#                 f"Aadhaar Number {aadhar_no} is present in the database. Beneficiary: {Name_b}, Item: {Art_n}, Year: {year_p}.")
#         else:
#             st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")
#
# if p_choice == "Entry":
#     # Input fields for adding new details or searching for existing ones
#     st.header("Public Request")
#
#     # Choose action
#     action = st.radio("Action", options=["Add", "Edit", "Delete"], horizontal=True)
#
#     # Input common fields
#     app_no = st.text_input("Application Number (e.g., P 001)")
#
#     if action == "Add":
#         aadhar = st.text_input("Aadhaar Number")
#         name = st.text_input("Name")
#         handicapped = st.radio("Handicapped", options=["Yes", "No"], horizontal=True, index=1)
#         address = st.text_area("Address")
#         mobile = st.text_input("Mobile Number")
#         article_name = st.selectbox("Select Article Name", article["Articles"].unique().tolist())
#
#         cpu = st.number_input("Cost Per Unit",
#                               value=article[article["Articles"] == article_name]["Cost per unit"].tolist()[
#                                   0], disabled=True)
#
#         quantity = st.number_input("Quantity*", min_value=1, step=1)
#
#         default_total_value = quantity * cpu
#         # Allow user to edit if needed (pre-filled with the calculated value)
#         total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
#                                       disabled=(cpu != 0))
#         comment = st.text_area("Comments", height=68, value="No")
#         # Submit button for adding new records
#         if st.button("Submit"):
#             try:
#                 # Validate application number and Aadhaar
#                 if not app_no:
#                     st.warning("Application Number cannot be empty.")
#                 elif app_no in public_master["App. No."].values:
#                     st.error("Application Number already added to the Application.")
#                 elif not aadhar:
#                     st.warning("Aadhaar Number cannot be empty.")
#                 elif aadhar in public["AADHAR No.1"].astype(str).values:
#                     st.error("Aadhaar number is already present in the database.")
#                 elif aadhar in public_master["Aadhar (Without Space)"].values:
#                     st.error("Aadhaar Number is already added to an application.")
#                 else:
#                     # Create a new entry
#                     new_entry = {
#                         "App. No.": str(app_no),
#                         "Aadhar (Without Space)": str(aadhar),
#                         "Name": str(name),
#                         "Handicapped (Yes / No)": handicapped,
#                         "Address": address,
#                         "Mobile": str(mobile),
#                         "Article Name": article_name,
#                         "Comments": comment,
#                         "Cost Per Unit": int(total_value / quantity if cpu == 0 else cpu),
#                         "Total Value": int(total_value),
#                         "Quantity": int(quantity),
#                         "Beneficiary Type": "Public"
#                     }
#
#                     # Append the new entry to the DataFrame
#                     public_master = pd.concat([public_master, pd.DataFrame([new_entry])], ignore_index=True
#                                               ).sort_values(by=["App. No."], ascending=True).reset_index(drop=True)
#
#                     # Save the updated data back to the file
#                     update_file(public_master_id, public_master)
#
#                     # Success message and updated DataFrame display
#                     st.success(f"Application {app_no} added successfully!")
#                     st.data_editor(public_master)
#             except Exception as e:
#                 st.error(f"An error occurred: {str(e)}")
#
#     elif action == "Edit":
#
#         if st.button("Search", key="search_button"):
#             # Search for the record by Application Number
#             record = public_master[public_master["App. No."] == app_no.strip()]
#
#             if not record.empty:
#                 # Store record in session state for persistence
#                 st.session_state["edit_record"] = record.iloc[0].to_dict()
#             else:
#                 st.error("Application not found.")
#
#         if "edit_record" in st.session_state:
#
#             # Retrieve the stored record from session state
#             record = st.session_state["edit_record"]
#
#             # Display fields for editing
#             aadhar = st.text_input("Aadhaar Number", value=record["Aadhar (Without Space)"])
#             name = st.text_input("Name", value=record["Name"])
#             handicapped = st.radio("Handicapped", options=["Yes", "No"], horizontal=True,
#                                    index=["Yes", "No"].index(record["Handicapped (Yes / No)"]))
#             address = st.text_area("Address", value=record["Address"])
#             mobile = st.text_input("Mobile Number", value=record["Mobile"])
#             article_name = st.selectbox("Select Article Name",
#                                         article["Articles"].unique().tolist(),
#                                         index=article["Articles"].tolist().index(record["Article Name"]))
#             cpu = st.number_input("Cost Per Unit", value=record["Cost Per Unit"], disabled=True)
#             quantity = st.number_input("Quantity*", min_value=1, step=1, value=record["Quantity"])
#
#             default_total_value = quantity * cpu
#             total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
#                                           disabled=(cpu != 0))
#             comment = st.text_area("Comments", value=record["Comments"], height=68)
#
#             if st.button("Update", key="update_button"):
#                 try:
#                     # Update the record in the DataFrame
#                     public_master.loc[public_master["App. No."] == app_no, "Aadhar (Without Space)"] = aadhar
#                     public_master.loc[public_master["App. No."] == app_no, "Name"] = name
#                     public_master.loc[public_master["App. No."] == app_no, "Handicapped (Yes / No)"] = handicapped
#                     public_master.loc[public_master["App. No."] == app_no, "Address"] = address
#                     public_master.loc[public_master["App. No."] == app_no, "Mobile"] = str(mobile)
#                     public_master.loc[public_master["App. No."] == app_no, "Article Name"] = article_name
#                     public_master.loc[public_master["App. No."] == app_no, "Comments"] = comment
#                     public_master.loc[public_master["App. No."] == app_no, "Cost Per Unit"] = int(
#                         total_value / quantity if cpu == 0 else cpu)
#                     public_master.loc[public_master["App. No."] == app_no, "Quantity"] = int(quantity)
#                     public_master.loc[public_master["App. No."] == app_no, "Total Value"] = int(total_value)
#                     public_master.loc[public_master["App. No."] == app_no, "Beneficiary Type"] = "Public"
#
#                     # Save the updated data back to the file
#                     update_file(public_master_id, public_master)
#                     st.success(f"Application {app_no} updated successfully!")
#                     st.session_state.pop("edit_record")  # Clear session state after update
#                     st.dataframe(public_master)
#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#
#     elif action == "Delete":
#         if st.button("Delete"):
#             # Check if the record exists
#             if app_no in public_master["App. No."].values:
#                 # Delete the record
#                 public_master = public_master[public_master["App. No."] != app_no]
#
#                 # Save the updated data back to the file
#                 update_file(public_master_id, public_master)
#
#                 st.success(f"Application {app_no} deleted successfully!")
#             else:
#                 st.error("Application not found.")
#         st.dataframe(public_master)
#
#     pub_fund = 5000000 - public_master['Total Value'].sum()
#     # color = ?
#     st.markdown(
#         f"<h5>Remaining Fund: ₹ <span style='color:{'Green' if pub_fund >= 0 else 'Red'};'>{pub_fund:,.0f}</span></h5>",
#         unsafe_allow_html=True)
#     st.download_button(
#         label="Download Records",
#         data=public_master.to_csv(index=False).encode('utf-8'),
#         file_name="Public Beneficiaries Records.csv",
#         mime="text/csv")
#
#
# elif type_choice == "Institutions & Others":
#
# # Streamlit UI
# st.header("Institution & Other Requests")
#
# # Load institution data (replace with your actual file reading)
# inst_data_id = "1dOMubywUqJId2gXHwNWp185L3QmadUnwxyFf0DC9M1s"
# inst_data = read_file(inst_data_id)
#
#
# # Function to reset form fields
# def reset_form():
#     st.session_state.clear()
#     st.session_state["app_number"] = ""
#     st.session_state["institution_name"] = ""
#     st.session_state["institution_type"] = "Institution"  # Default to "Institution"
#     st.session_state["address"] = ""
#     st.session_state["mobile"] = ""
#     st.session_state["selected_articles"] = []
#     st.session_state["article_comments"] = {}
#
#
# # Initialize session state for form fields if not already set
# if "app_number" not in st.session_state:
#     reset_form()
#
# # User action selection
# action = st.radio("Select Action", ["Add", "Edit", "Delete"], horizontal=True)
#
# if action == "Add":
#
#     # Application Number
#     st.session_state["app_number"] = st.text_input("Application No.*(Eg. 'I 001', 'O 001')",
#                                                    value=st.session_state["app_number"])
#
#     # Institution Details
#     st.session_state["institution_name"] = st.text_input("Institution Name*",
#                                                          value=st.session_state["institution_name"])
#     st.session_state["institution_type"] = st.radio("Institution Type*",
#                                                     ["Institution", "Others"],
#                                                     index=0 if st.session_state.get("institution_type",
#                                                                                     "Institution") == "Institution" else 1,
#                                                     horizontal=True)
#
#     st.session_state["address"] = st.text_area("Address*", value=st.session_state["address"])
#     st.session_state["mobile"] = st.text_input("Mobile*", value=st.session_state["mobile"])
#
#     # Article Selection
#     st.session_state["selected_articles"] = st.multiselect("Select Articles*", article["Articles"].tolist(),
#                                                            default=st.session_state["selected_articles"])
#
#     # Article Details
#
#     article_entries = []
#     article_comments = {}
#
#     for article_name in st.session_state["selected_articles"]:
#         col1, col2, col3, col4 = st.columns(4)
#
#         with col1:
#             # Use a unique key by combining article name and application number
#             quantity = st.number_input(
#                 f"Quantity of {article_name}*",
#                 min_value=1,
#                 step=1,
#                 key=f"qty_{article_name}_{st.session_state['app_number']}"  # Unique key
#             )
#         cost_per_unit = article.loc[article["Articles"] == article_name, "Cost per unit"].values[0]
#
#         with col2:
#             st.write(f"Cost per Unit: ₹{cost_per_unit}")
#
#         with col3:
#             if cost_per_unit == 0:
#                 total_value = st.number_input(
#                     f"Total Value for {article_name}*",
#                     min_value=0.0,
#                     step=1.0,
#                     key=f"total_value_{article_name}_{st.session_state['app_number']}")
#
#             else:
#                 total_value = quantity * cost_per_unit
#                 st.write(f"Total: ₹{total_value}")
#
#         with col4:
#             comment = st.text_area(
#                 f"Comment for {article_name}",
#                 key=f"comment_{article_name}_{st.session_state['app_number']}",  # Unique key
#                 value="No", height=68
#             )
#             article_comments[article_name] = comment
#
#         article_entries.append({
#             "Article Name": article_name,
#             "Quantity": quantity,
#             "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
#             "Total Value": total_value,
#             "Comments": article_comments[article_name]
#
#         })
#
#     # Submit Button for new requests
#     if st.button("Add"):
#         if not st.session_state["app_number"] or not st.session_state["institution_name"] or not \
#                 st.session_state["address"] or not st.session_state["mobile"] or not st.session_state[
#             "selected_articles"]:
#             st.error("Please fill all required fields (*) before submitting.")
#
#         else:
#             # Check for duplicate entries (same App. No., Article Name, and Comments)
#             duplicate_entries = []
#
#             for entry in article_entries:
#                 duplicate = inst_data[
#                     (inst_data["App. No."] == st.session_state["app_number"]) &
#                     (inst_data["Article Name"] == entry["Article Name"]) &
#                     (inst_data["Comments"] == entry["Comments"])
#                     ]
#                 if not duplicate.empty:
#                     duplicate_entries.append(entry["Article Name"])
#
#             if duplicate_entries:
#                 st.error(
#                     f"Duplicate entries found for the following articles with the same comments: {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")
#
#             else:
#                 # Flatten the article entries into individual rows
#                 flattened_articles = []
#
#                 for entry in article_entries:
#                     flattened_articles.append({
#                         "App. No.": st.session_state["app_number"],
#                         "Institution Name": st.session_state["institution_name"],
#                         "Beneficiary Type": st.session_state["institution_type"],
#                         "Address": st.session_state["address"],
#                         "Mobile": str(st.session_state["mobile"]),
#                         "Article Name": entry["Article Name"],
#                         "Quantity": entry["Quantity"],
#                         "Cost Per Unit": entry["Cost Per Unit"],
#                         "Total Value": entry["Total Value"],
#                         "Comments": entry["Comments"]
#                     })
#
#                 # Convert the flattened articles into a DataFrame
#                 flattened_df = pd.DataFrame(flattened_articles)
#
#                 # Append the new flattened data to the existing institution data
#                 inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
#                     by="App. No.", ascending=True).reset_index(drop=True)
#
#                 # Save the updated data back to storage
#                 update_file(inst_data_id, inst_data)
#
#                 # Clear form fields after successful submission
#                 reset_form()
#
#                 # Success message
#                 st.success("Request submitted successfully!")
#                 st.dataframe(inst_data)
#
#
# elif action == "Edit":
#
#     # Select an entry to edit
#     if not inst_data.empty:
#         app_numbers = inst_data["App. No."].unique()
#         selected_app_number = st.selectbox("Select Application Number to Edit", app_numbers)
#
#         # Filter the data for the selected application number
#         selected_entries = inst_data[inst_data["App. No."] == selected_app_number]
#
#         # Display the selected entries for editing
#         st.write("Edit the selected entries:")
#
#         # Institution Details
#         institution_name = st.text_input("Institution Name*",
#                                          value=selected_entries["Institution Name"].values[0])
#         institution_type = st.radio("Institution Type*", ["Institution", "Others"], horizontal=True,
#                                     index=0 if st.session_state.get("institution_type",
#                                                                     "Institution") == "Institution" else 1)
#         address = st.text_area("Address*", value=selected_entries["Address"].values[0])
#         mobile = st.text_input("Mobile*", value=selected_entries["Mobile"].values[0])
#
#         # Article Details
#
#         article_entries = []
#
#         for index, row in selected_entries.iterrows():
#
#             col1, col2, col3, col4 = st.columns(4)
#
#             with col1:
#                 # Use a unique key by combining article name, application number, and index
#                 quantity = st.number_input(
#                     f"Quantity of {row['Article Name']}*", min_value=1, step=1,
#                     value=int(row["Quantity"]),
#                     key=f"qty_{row['Article Name']}_{selected_app_number}_{index}"  # Unique key
#                 )
#
#             cost_per_unit = article.loc[article["Articles"] == row["Article Name"], "Cost per unit"].values[0]
#
#             with col2:
#                 st.write(f"Cost per Unit: ₹{cost_per_unit}")
#
#             with col3:
#                 if cost_per_unit == 0:
#                     total_value = st.number_input(
#                         f"Total Value for {row['Article Name']}*",
#                         min_value=0.0,
#                         step=1.0,
#                         value=float(row["Total Value"]),
#                         key=f"total_value_{row['Article Name']}_{selected_app_number}_{index}"
#                     )
#                 else:
#                     total_value = quantity * cost_per_unit
#                     st.write(f"Total: ₹{total_value}")
#
#             with col4:
#                 comment = st.text_area(f"Comment for {row['Article Name']}",
#                                        key=f"comment_{row['Article Name']}_{selected_app_number}_{index}",  # Unique key
#                                        value=row["Comments"], height=68)
#
#             article_entries.append({
#                 "Article Name": row["Article Name"],
#                 "Quantity": quantity,
#                 "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
#                 "Total Value": total_value,
#                 "Comments": comment
#
#             })
#
#         # Update Button for editing
#         if st.button("Update"):
#             if not institution_name or not address or not mobile or not article_entries:
#                 st.error("Please fill all required fields (*) before updating.")
#
#             else:
#                 # Check for duplicate entries (same App. No., Article Name, and Comments)
#                 duplicate_entries = []
#
#                 for entry in article_entries:
#                     duplicate = inst_data[
#                         (inst_data["App. No."] == selected_app_number) &
#                         (inst_data["Article Name"] == entry["Article Name"]) &
#                         (inst_data["Comments"] == entry["Comments"]) &
#                         (inst_data.index != index)  # Exclude the current entry being edited
#                         ]
#                     if not duplicate.empty:
#                         duplicate_entries.append(entry["Article Name"])
#
#                 if duplicate_entries:
#                     st.error(
#                         f"Duplicate entries found : {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")
#
#                 else:
#                     # Remove the old entries
#                     inst_data = inst_data[inst_data["App. No."] != selected_app_number]
#
#                     # Flatten the article entries into individual rows
#                     flattened_articles = []
#
#                     for entry in article_entries:
#                         flattened_articles.append({
#                             "App. No.": selected_app_number,
#                             "Institution Name": institution_name,
#                             "Beneficiary Type": institution_type,
#                             "Address": address,
#                             "Mobile": str(mobile),
#                             "Article Name": entry["Article Name"],
#                             "Quantity": entry["Quantity"],
#                             "Cost Per Unit": entry["Cost Per Unit"],
#                             "Total Value": entry["Total Value"],
#                             "Comments": entry["Comments"]
#                         })
#
#                     # Convert the flattened articles into a DataFrame
#                     flattened_df = pd.DataFrame(flattened_articles)
#
#                     # Append the updated data to the existing institution data
#                     inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
#                         by="App. No.", ascending=True).reset_index(drop=True)
#
#                     # Save the updated data back to storage
#                     update_file(inst_data_id, inst_data)
#                     # Success message
#                     st.success("Request updated successfully!")
#                     st.dataframe(inst_data)
#
#     else:
#         st.write("No entries available to edit.")
#
#
# elif action == "Delete":
#
#     # Select an entry to delete
#     if not inst_data.empty:
#         app_numbers = inst_data["App. No."].unique()
#         selected_app_number = st.selectbox("Select Application Number to Delete", app_numbers)
#         # Filter the data for the selected application number
#         selected_entries = inst_data[inst_data["App. No."] == selected_app_number]
#         # Add a checkbox for each record to allow selection
#         st.write("Select records to delete:")
#
#         delete_indices = []
#         for index, row in selected_entries.iterrows():
#             if st.checkbox(
#                     f"Delete {row['Article Name']} (Qty: {row['Quantity']}, Total: ₹{row['Total Value']}, Comments: {row['Comments']})",
#                     key=f"delete_{index}"):
#                 delete_indices.append(index)
#
#         # Delete Button
#         if st.button("Delete Selection"):
#
#             if not delete_indices:
#                 st.error("Please select at least one record to delete.")
#
#             else:
#                 # Remove the selected records
#                 inst_data = inst_data.drop(delete_indices).sort_values(by="App. No.",
#                                                                        ascending=True).reset_index(drop=True)
#                 # Save the updated data back to storage
#                 update_file(inst_data_id, inst_data)
#                 # Success message
#                 st.success("Selected records deleted successfully!")
#                 st.dataframe(inst_data)
#     else:
#         st.write("No entries available to delete.")
#
# inst_fund = inst_data['Total Value'].sum()
# # color = ?
# st.markdown(
#     f"<h5>Total Accrued: ₹ <span style='color:{'Green' if inst_fund >= 0 else 'Red'};'>{inst_fund:,.0f}</span></h5>",
#     unsafe_allow_html=True)
#
# st.download_button(
#     label="Download Institution Records",
#     data=inst_data.to_csv(index=False).encode('utf-8'),
#     file_name="Institution_Records.csv",
#     mime="text/csv"
#
# )
#
#
# #__________________________________
#
# import io
# import json
# import streamlit as st
# import pandas as pd
# from googleapiclient.http import  MediaIoBaseUpload, MediaIoBaseDownload
# from googleapiclient.discovery import build
# from google.oauth2 import service_account
# import streamlit_authenticator as stauth
# import yaml
# import time
# from yaml.loader import SafeLoader
#
#
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
#     master_data_id = "1ry614-7R4-s0uQcv0zrNeS4O0KAbhVEC67rl5_VllGI"  # Replace with your file's ID
#     article_data_id = "1b7eyqlN3lTapBRYcO1VrXGsj_gBVSxQLIyLCPu3UcG8"
#     district_data_id = "1lwJL-_KQaOY3VSd2cOeOdiR5QOn8yvX3zp6xNfQJo9U"
#
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
#         time.sleep(1)
#         alert1.empty()
#
#
#
#     # Load Data
#     article = read_file(article_data_id)
#     district = read_file(district_data_id)
#
#
#     # Sidebar Navigation
#     selected_tab = st.sidebar.radio("Select Tab", ["Beneficiary Entry"])
#
#     if selected_tab == "Beneficiary Entry":
#         # Radio buttons to select type
#         type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions & Others"], horizontal=True)
#
#         if type_choice == "District":
#
#             # Input fields
#             name = st.selectbox("District Name*", district["District Name"].unique().tolist())
#             pname = district[district["District Name"]==name]["President Name"].values.tolist()[0]
#             pno = str(district[district["District Name"]==name]["Mobile Number"].values.tolist()[0])
#             st.markdown(f"<h4>President: <b>{pname}</b>, Mobile: <b>{pno}</b></h4>",unsafe_allow_html=True,)
#             article_name = st.selectbox("Enter Article Name*", article["Articles"].unique().tolist() + ["Add New"])
#             #new article
#             if article_name == "Add New":
#                 new_article =  st.text_input("Enter Article Name*")
#                 if new_article:
#                     new_cpu = st.number_input("Enter Cost Per Unit*", min_value=0)
#                     new_item_type = st.radio("Select Type", ["Article", "Aid", "Project"], horizontal=True)
#                     if st.button("Save Article"):
#                         new_article_entry = {
#                             "Articles": new_article,
#                             "Cost per unit": new_cpu,
#                             "Item Type": new_item_type,
#                         }
#                         new_article_data = pd.concat([article, pd.DataFrame([new_article_entry])], ignore_index=True).sort_values(by=["Articles"],ascending=True).reset_index(drop=True)
#                         new_article_data.drop_duplicates(subset=["Articles"], inplace=True)
#                         update_file(article_data_id, new_article_data)
#
#             else:
#                 cpu = st.number_input("Cost Per Unit",value = article[article["Articles"] == article_name]["Cost per unit"].tolist()[0],disabled=True)
#
#                 # Retrieve existing quantity for the selected district and article
#                 saved_data = read_file(master_data_id)
#                 existing_record = saved_data[
#                     (saved_data["NAME OF THE DISTRICT"] == name) &
#                     (saved_data["REQUESTED ARTICLE"] == article_name)
#                     ]
#
#                 # Set default quantity to existing value if record exists, else 0
#                 default_quantity = existing_record["QUANTITY"].values[0] if not existing_record.empty else 0
#
#                 # Input field for quantity with default value
#                 quantity = st.number_input( "Quantity* (0 to delete)",min_value=0,step=1, value=default_quantity)
#
#                 # Auto-calculate total value
#                 default_total_value = quantity * cpu
#                 # Allow user to edit if needed (pre-filled with the calculated value)
#                 total_value = st.number_input("Total Value", value=default_total_value, min_value=0,disabled = (cpu != 0))
#
#                 comment = st.text_area("Enter Comment* (Add 'No' if Nothing)",placeholder="Must for Aid and Projects",value="No")
#                 # Read the saved data from Google Drive
#                 saved_data = read_file(master_data_id)
#
#                 # Dynamic Remaining Funds Display
#                 if name:  # Ensure district is selected
#                     alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#                     # Calculate remaining funds dynamically based on current inputs (without saving)
#                     current_total_cost = saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#                     dynamic_remaining_fund = alloted_fund - (current_total_cost + total_value)
#
#                     # Display dynamically
#                     st.markdown(f"<h5>Alloted Fund: ₹ <span style='color:black;'>{alloted_fund:,}</span></h5>",
#                                 unsafe_allow_html=True)
#                     if dynamic_remaining_fund > 0:
#                         fund_color = "green"
#                     else:
#                         fund_color = "red"
#                     st.markdown(
#                         f"<h5>Remaining Fund (Projected): ₹ <span style='color:{fund_color};'>{dynamic_remaining_fund:,}</span></h5>",
#                         unsafe_allow_html=True, )
#
#                 # Save button
#                 if st.button("Submit"):
#                     if not name or not article_name:
#                         st.warning("Please fill all fields before saving.")
#                     else:
#                         # Check if quantity is 0 (delete the record)
#                         if quantity == 0:
#                             # Find and remove the selected row from the DataFrame
#                             delete_condition = (
#                                 (saved_data["NAME OF THE DISTRICT"] == name) &
#                                 (saved_data["REQUESTED ARTICLE"] == article_name) &
#                                 (saved_data["COMMENTS"] == comment)
#                             )
#                             saved_data = saved_data[~delete_condition]  # Remove the record
#                             alert2 = st.success(f"Record for {name} and {article_name} deleted successfully!")
#                             time.sleep(1)
#                             alert2.empty()
#
#                         else:
#                             # Check for duplicates and replace if necessary
#                             duplicate_condition = (
#                                 (saved_data["NAME OF THE DISTRICT"] == name) &
#                                 (saved_data["REQUESTED ARTICLE"] == article_name) &
#                                 (saved_data["COMMENTS"] == comment)
#                             )
#                             if duplicate_condition.any():
#                                 saved_data.loc[duplicate_condition, ["QUANTITY", "COST PER UNIT","TOTAL COST"]] = [quantity, total_value/quantity if cpu == 0 else cpu, total_value]
#                                 alert3 = st.info("Duplicate entry found. Existing record updated.")
#                                 time.sleep(2)
#                                 alert3.empty()
#
#                             else:
#                                 new_entry = {
#                                     "NAME OF THE DISTRICT": name,
#                                     "REQUESTED ARTICLE": article_name,
#                                     "QUANTITY": quantity,
#                                     "TOTAL COST": total_value,
#                                     "COST PER UNIT": total_value/quantity if cpu == 0 else cpu,
#                                     "COMMENTS":comment,
#                                     "ITEM TYPE": article[article["Articles"] == article_name]["Item Type"].tolist()[0],
#                                     "Beneficiary Type": "District",
#                                 }
#
#                                 saved_data = pd.concat([saved_data, pd.DataFrame([new_entry])], ignore_index=True).sort_values(by=["NAME OF THE DISTRICT","REQUESTED ARTICLE"],ascending=True).reset_index(drop=True)
#
#                         alloted_fund = district[district["District Name"] == name]["Alloted Budget"].values.tolist()[0]
#                         remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#                         try:
#                             last_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[-1]
#                             first_row_index = saved_data[saved_data["NAME OF THE DISTRICT"] == name].index[0]
#
#                             # Add 'ALLOTTED FUND' and 'REMAINING FUND' to the last row
#                             saved_data.loc[saved_data["NAME OF THE DISTRICT"] == name, ["ALLOTTED FUNDS","EXCESS/SHORTAGE"]] = None
#                             saved_data.loc[first_row_index, "ALLOTTED FUNDS"] = alloted_fund
#                             saved_data.loc[last_row_index, "EXCESS/SHORTAGE"] = remaining_fund
#                         except IndexError:
#                             pass
#
#                         saved_data = saved_data.reset_index(drop=True)
#                         alert4 = st.success("Data saved successfully!")
#                         time.sleep(1)
#                         alert4.empty()
#
#                         # Save to CSV
#                         update_file(master_data_id, saved_data)
#
#
#                 # Display the table below
#                 st.subheader("Summary")
#                 st.dataframe(saved_data[saved_data["NAME OF THE DISTRICT"] == name])
#                 remaining_fund = alloted_fund - saved_data[saved_data["NAME OF THE DISTRICT"] == name]["TOTAL COST"].sum()
#                 if remaining_fund > 0:
#                     color = "green"
#                 else:
#                     color = "red"
#                 st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{color};'>{remaining_fund:,}</span></h5>", unsafe_allow_html=True)
#
#
#                 st.download_button(
#                     label="Download Records",
#                     data=saved_data.to_csv(index=False).encode('utf-8'),
#                     file_name="District Beneficiaries Records.csv",
#                     mime="text/csv")
#
#
#         elif type_choice == "Public":
#             public_data_id = "1sO08BfwN1gzNs_N7XDq1RnqMgJDDKMdq_nsaNhmjKhs"
#             public = read_file(public_data_id)
#             public_master_id = "1EdEySmYe6ZJUW16f65_q30nkqfbvDADjcmEkAEJrrL4"
#             public_master = read_file(public_master_id)
#             public_master["Aadhar (Without Space)"] = public_master["Aadhar (Without Space)"].astype(str)
#             checked_id = "1X12wSEFnt7mivh5dysPSnH4nVZZPfPJgWBUk3e_oO7c"
#             check_file = read_file(checked_id)
#
#             # Initialize session state for checked Aadhaar numbers
#             p_choice = st.radio("", ["Validation", "Entry"], horizontal=True)
#             if p_choice == "Validation":
#
#                 # if "checked_aadhar" not in st.session_state:
#                 #     st.session_state["checked_aadhar"] = set()
#                 # # Input for Aadhaar Number
#                 aadhar_no = st.text_input("Enter Aadhaar Number")
#                 if aadhar_no:
#                     # # Check if the Aadhaar number has already been checked
#                     # if aadhar_no in st.session_state["checked_aadhar"]:
#                     #     st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
#                     # else:
#                     #     # Add the Aadhaar number to the checked list
#                     #     st.session_state["checked_aadhar"].add(aadhar_no)
#                     if aadhar_no in check_file["checked_aadhar_no"].astype(str).values:
#                         st.warning(f"You have already checked Aadhaar Number {aadhar_no}.")
#                     else:
#                         check_file = pd.concat([check_file, pd.DataFrame([{"checked_aadhar_no":str(aadhar_no)}])], ignore_index=True)
#                         update_file(checked_id,check_file)
#
#                     # Check if the Aadhaar number exists in the database
#                     if aadhar_no in public["AADHAR No.1"].astype(str).values:
#                         Name_b = public[public["AADHAR No.1"] == aadhar_no]["NAME"].values.tolist()[0]
#                         Art_n = public[public["AADHAR No.1"] == aadhar_no]["BENEFICIARY ITEM"].values.tolist()[0]
#                         year_p = public[public["AADHAR No.1"] == aadhar_no]["YEAR"].values.tolist()[0]
#                         st.error(
#                             f"Aadhaar Number {aadhar_no} is present in the database. Beneficiary: {Name_b}, Item: {Art_n}, Year: {year_p}.")
#                     else:
#                         st.success(f"Aadhaar Number {aadhar_no} is NOT present in the database.")
#
#             if p_choice == "Entry":
#                 # Input fields for adding new details or searching for existing ones
#                 st.header("Public Request")
#
#                 # Choose action
#                 action = st.radio("Action", options=["Add", "Edit", "Delete"], horizontal=True)
#
#                 # Input common fields
#                 app_no = st.text_input("Application Number (e.g., P 001)")
#
#                 if action == "Add":
#                     aadhar = st.text_input("Aadhaar Number")
#                     name = st.text_input("Name")
#                     handicapped = st.radio("Handicapped", options=["Yes", "No"], horizontal=True,index=1)
#                     address = st.text_area("Address")
#                     mobile = st.text_input("Mobile Number")
#                     article_name = st.selectbox("Select Article Name", article["Articles"].unique().tolist())
#
#                     cpu = st.number_input("Cost Per Unit",
#                                           value=article[article["Articles"] == article_name]["Cost per unit"].tolist()[
#                                               0], disabled=True)
#
#                     quantity = st.number_input("Quantity*", min_value=1, step=1)
#
#
#                     default_total_value = quantity * cpu
#                     # Allow user to edit if needed (pre-filled with the calculated value)
#                     total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
#                                                   disabled=(cpu != 0))
#                     comment = st.text_area("Comments",height=68,value="No")
#                     # Submit button for adding new records
#                     if st.button("Submit"):
#                         try:
#                             # Validate application number and Aadhaar
#                             if not app_no:
#                                 st.warning("Application Number cannot be empty.")
#                             elif app_no in public_master["App. No."].values:
#                                 st.error("Application Number already added to the Application.")
#                             elif not aadhar:
#                                 st.warning("Aadhaar Number cannot be empty.")
#                             elif aadhar in public["AADHAR No.1"].astype(str).values:
#                                 st.error("Aadhaar number is already present in the database.")
#                             elif aadhar in public_master["Aadhar (Without Space)"].values:
#                                 st.error("Aadhaar Number is already added to an application.")
#                             else:
#                                 # Create a new entry
#                                 new_entry = {
#                                     "App. No.": str(app_no),
#                                     "Aadhar (Without Space)": str(aadhar),
#                                     "Name": str(name),
#                                     "Handicapped (Yes / No)": handicapped,
#                                     "Address": address,
#                                     "Mobile": str(mobile),
#                                     "Article Name": article_name,
#                                     "Comments": comment,
#                                     "Cost Per Unit": int(total_value/quantity if cpu == 0 else cpu),
#                                     "Total Value": int(total_value),
#                                     "Quantity": int(quantity),
#                                     "Beneficiary Type":"Public"
#                                 }
#
#                                 # Append the new entry to the DataFrame
#                                 public_master = pd.concat([public_master, pd.DataFrame([new_entry])],ignore_index=True
#                                 ).sort_values(by=["App. No."], ascending=True).reset_index(drop=True)
#
#                                 # Save the updated data back to the file
#                                 update_file(public_master_id, public_master)
#
#                                 # Success message and updated DataFrame display
#                                 st.success(f"Application {app_no} added successfully!")
#                                 st.data_editor(public_master)
#                         except Exception as e:
#                             st.error(f"An error occurred: {str(e)}")
#
#                 elif action == "Edit":
#
#                     if st.button("Search", key="search_button"):
#                         # Search for the record by Application Number
#                         record = public_master[public_master["App. No."] == app_no.strip()]
#
#                         if not record.empty:
#                             # Store record in session state for persistence
#                             st.session_state["edit_record"] = record.iloc[0].to_dict()
#                         else:
#                             st.error("Application not found.")
#
#                     if "edit_record" in st.session_state:
#
#                         # Retrieve the stored record from session state
#                         record = st.session_state["edit_record"]
#
#                         # Display fields for editing
#                         aadhar = st.text_input("Aadhaar Number", value=record["Aadhar (Without Space)"])
#                         name = st.text_input("Name", value=record["Name"])
#                         handicapped = st.radio("Handicapped",options=["Yes", "No"],horizontal=True,
#                             index=["Yes", "No"].index(record["Handicapped (Yes / No)"]))
#                         address = st.text_area("Address", value=record["Address"])
#                         mobile = st.text_input("Mobile Number", value=record["Mobile"])
#                         article_name = st.selectbox("Select Article Name",
#                             article["Articles"].unique().tolist(),
#                             index=article["Articles"].tolist().index(record["Article Name"]))
#                         cpu = st.number_input("Cost Per Unit",value= record["Cost Per Unit"],disabled=True)
#                         quantity = st.number_input("Quantity*", min_value=1, step=1,value=record["Quantity"])
#
#                         default_total_value = quantity * cpu
#                         total_value = st.number_input("Total Value", value=default_total_value, min_value=0,
#                                                       disabled=(cpu != 0))
#                         comment = st.text_area("Comments", value=record["Comments"],height=68)
#
#                         if st.button("Update", key="update_button"):
#                             try:
#                                 # Update the record in the DataFrame
#                                 public_master.loc[public_master["App. No."] == app_no, "Aadhar (Without Space)"] = aadhar
#                                 public_master.loc[public_master["App. No."] == app_no, "Name"] = name
#                                 public_master.loc[public_master["App. No."] == app_no, "Handicapped (Yes / No)"] = handicapped
#                                 public_master.loc[public_master["App. No."] == app_no, "Address"] = address
#                                 public_master.loc[public_master["App. No."] == app_no, "Mobile"] = str(mobile)
#                                 public_master.loc[public_master["App. No."] == app_no, "Article Name"] = article_name
#                                 public_master.loc[public_master["App. No."] == app_no, "Comments"] = comment
#                                 public_master.loc[public_master["App. No."] == app_no, "Cost Per Unit"] = int(total_value/quantity if cpu == 0 else cpu)
#                                 public_master.loc[public_master["App. No."] == app_no, "Quantity"] = int(quantity)
#                                 public_master.loc[public_master["App. No."] == app_no, "Total Value"] = int(total_value)
#                                 public_master.loc[public_master["App. No."] == app_no, "Beneficiary Type"] = "Public"
#
#                                 # Save the updated data back to the file
#                                 update_file(public_master_id, public_master)
#                                 st.success(f"Application {app_no} updated successfully!")
#                                 st.session_state.pop("edit_record")  # Clear session state after update
#                                 st.dataframe(public_master)
#                             except Exception as e:
#                                 st.error(f"An error occurred: {str(e)}")
#
#                 elif action == "Delete":
#                     if st.button("Delete"):
#                         # Check if the record exists
#                         if app_no in public_master["App. No."].values:
#                             # Delete the record
#                             public_master = public_master[public_master["App. No."] != app_no]
#
#                             # Save the updated data back to the file
#                             update_file(public_master_id, public_master)
#
#                             st.success(f"Application {app_no} deleted successfully!")
#                         else:
#                             st.error("Application not found.")
#                     st.dataframe(public_master)
#
#                 pub_fund = 5000000 - public_master['Total Value'].sum()
#                 # color = ?
#                 st.markdown(f"<h5>Remaining Fund: ₹ <span style='color:{'Green' if pub_fund >= 0 else 'Red'};'>{pub_fund:,.0f}</span></h5>",
#                             unsafe_allow_html=True)
#                 st.download_button(
#                     label="Download Records",
#                     data=public_master.to_csv(index=False).encode('utf-8'),
#                     file_name="Public Beneficiaries Records.csv",
#                     mime="text/csv")
#
#
#         elif type_choice == "Institutions & Others":
#
#             # Streamlit UI
#             st.header("Institution & Other Requests")
#
#             # Load institution data (replace with your actual file reading)
#             inst_data_id = "1dOMubywUqJId2gXHwNWp185L3QmadUnwxyFf0DC9M1s"
#             inst_data = read_file(inst_data_id)
#
#
#             # Function to reset form fields
#             def reset_form():
#                 st.session_state.clear()
#                 st.session_state["app_number"] = ""
#                 st.session_state["institution_name"] = ""
#                 st.session_state["institution_type"] = "Institution"  # Default to "Institution"
#                 st.session_state["address"] = ""
#                 st.session_state["mobile"] = ""
#                 st.session_state["selected_articles"] = []
#                 st.session_state["article_comments"] = {}
#
#
#             # Initialize session state for form fields if not already set
#             if "app_number" not in st.session_state:
#                 reset_form()
#
#             # User action selection
#             action = st.radio("Select Action", ["Add", "Edit", "Delete"], horizontal=True)
#
#             if action == "Add":
#
#                 # Application Number
#                 st.session_state["app_number"] = st.text_input("Application No.*(Eg. 'I 001', 'O 001')",
#                                                                value=st.session_state["app_number"])
#
#                 # Institution Details
#                 st.session_state["institution_name"] = st.text_input("Institution Name*",
#                                                                      value=st.session_state["institution_name"])
#                 st.session_state["institution_type"] = st.radio("Institution Type*",
#                     ["Institution", "Others"],
#                     index=0 if st.session_state.get("institution_type", "Institution") == "Institution" else 1,
#                     horizontal=True)
#
#                 st.session_state["address"] = st.text_area("Address*", value=st.session_state["address"])
#                 st.session_state["mobile"] = st.text_input("Mobile*", value=st.session_state["mobile"])
#
#                 # Article Selection
#                 st.session_state["selected_articles"] = st.multiselect("Select Articles*", article["Articles"].tolist(),
#                                                                        default=st.session_state["selected_articles"])
#
#                 # Article Details
#
#                 article_entries = []
#                 article_comments = {}
#
#                 for article_name in st.session_state["selected_articles"]:
#                     col1, col2, col3, col4 = st.columns(4)
#
#                     with col1:
#                         # Use a unique key by combining article name and application number
#                         quantity = st.number_input(
#                             f"Quantity of {article_name}*",
#                             min_value=1,
#                             step=1,
#                             key=f"qty_{article_name}_{st.session_state['app_number']}"  # Unique key
#                         )
#                     cost_per_unit = article.loc[article["Articles"] == article_name, "Cost per unit"].values[0]
#
#                     with col2:
#                         st.write(f"Cost per Unit: ₹{cost_per_unit}")
#
#                     with col3:
#                         if cost_per_unit == 0:
#                             total_value = st.number_input(
#                                 f"Total Value for {article_name}*",
#                                 min_value=0.0,
#                                 step=1.0,
#                                 key=f"total_value_{article_name}_{st.session_state['app_number']}")
#
#                         else:
#                             total_value = quantity * cost_per_unit
#                             st.write(f"Total: ₹{total_value}")
#
#                     with col4:
#                         comment = st.text_area(
#                             f"Comment for {article_name}",
#                             key=f"comment_{article_name}_{st.session_state['app_number']}",  # Unique key
#                             value="No", height=68
#                         )
#                         article_comments[article_name] = comment
#
#                     article_entries.append({
#                         "Article Name": article_name,
#                         "Quantity": quantity,
#                         "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
#                         "Total Value": total_value,
#                         "Comments": article_comments[article_name]
#
#                     })
#
#                 # Submit Button for new requests
#                 if st.button("Add"):
#                     if not st.session_state["app_number"] or not st.session_state["institution_name"] or not \
#                     st.session_state["address"] or not st.session_state["mobile"] or not st.session_state[
#                         "selected_articles"]:
#                         st.error("Please fill all required fields (*) before submitting.")
#
#                     else:
#                         # Check for duplicate entries (same App. No., Article Name, and Comments)
#                         duplicate_entries = []
#
#                         for entry in article_entries:
#                             duplicate = inst_data[
#                                 (inst_data["App. No."] == st.session_state["app_number"]) &
#                                 (inst_data["Article Name"] == entry["Article Name"]) &
#                                 (inst_data["Comments"] == entry["Comments"])
#                                 ]
#                             if not duplicate.empty:
#                                 duplicate_entries.append(entry["Article Name"])
#
#                         if duplicate_entries:
#                             st.error(
#                                 f"Duplicate entries found for the following articles with the same comments: {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")
#
#                         else:
#                             # Flatten the article entries into individual rows
#                             flattened_articles = []
#
#                             for entry in article_entries:
#                                 flattened_articles.append({
#                                     "App. No.": st.session_state["app_number"],
#                                     "Institution Name": st.session_state["institution_name"],
#                                     "Beneficiary Type": st.session_state["institution_type"],
#                                     "Address": st.session_state["address"],
#                                     "Mobile": str(st.session_state["mobile"]),
#                                     "Article Name": entry["Article Name"],
#                                     "Quantity": entry["Quantity"],
#                                     "Cost Per Unit": entry["Cost Per Unit"],
#                                     "Total Value": entry["Total Value"],
#                                     "Comments": entry["Comments"]
#                                 })
#
#                             # Convert the flattened articles into a DataFrame
#                             flattened_df = pd.DataFrame(flattened_articles)
#
#                             # Append the new flattened data to the existing institution data
#                             inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
#                                 by="App. No.", ascending=True).reset_index(drop=True)
#
#                             # Save the updated data back to storage
#                             update_file(inst_data_id, inst_data)
#
#                             # Clear form fields after successful submission
#                             reset_form()
#
#                             # Success message
#                             st.success("Request submitted successfully!")
#                             st.dataframe(inst_data)
#
#
#             elif action == "Edit":
#
#                 # Select an entry to edit
#                 if not inst_data.empty:
#                     app_numbers = inst_data["App. No."].unique()
#                     selected_app_number = st.selectbox("Select Application Number to Edit", app_numbers)
#
#                     # Filter the data for the selected application number
#                     selected_entries = inst_data[inst_data["App. No."] == selected_app_number]
#
#                     # Display the selected entries for editing
#                     st.write("Edit the selected entries:")
#
#                     # Institution Details
#                     institution_name = st.text_input("Institution Name*",
#                                                      value=selected_entries["Institution Name"].values[0])
#                     institution_type = st.radio("Institution Type*", ["Institution", "Others"], horizontal=True,
#                                                 index=0 if st.session_state.get("institution_type",
#                                                                                 "Institution") == "Institution" else 1)
#                     address = st.text_area("Address*", value=selected_entries["Address"].values[0])
#                     mobile = st.text_input("Mobile*", value=selected_entries["Mobile"].values[0])
#
#                     # Article Details
#
#                     article_entries = []
#
#                     for index, row in selected_entries.iterrows():
#
#                         col1, col2, col3, col4 = st.columns(4)
#
#                         with col1:
#                             # Use a unique key by combining article name, application number, and index
#                             quantity = st.number_input(
#                                 f"Quantity of {row['Article Name']}*",min_value=1,step=1,
#                                 value=int(row["Quantity"]),
#                                 key=f"qty_{row['Article Name']}_{selected_app_number}_{index}"  # Unique key
#                             )
#
#                         cost_per_unit = article.loc[article["Articles"] == row["Article Name"], "Cost per unit"].values[0]
#
#                         with col2:
#                             st.write(f"Cost per Unit: ₹{cost_per_unit}")
#
#                         with col3:
#                             if cost_per_unit == 0:
#                                 total_value = st.number_input(
#                                     f"Total Value for {row['Article Name']}*",
#                                     min_value=0.0,
#                                     step=1.0,
#                                     value=float(row["Total Value"]),
#                                     key=f"total_value_{row['Article Name']}_{selected_app_number}_{index}"
#                                 )
#                             else:
#                                 total_value = quantity * cost_per_unit
#                                 st.write(f"Total: ₹{total_value}")
#
#                         with col4:
#                             comment = st.text_area(f"Comment for {row['Article Name']}",
#                                 key=f"comment_{row['Article Name']}_{selected_app_number}_{index}",  # Unique key
#                                 value=row["Comments"], height=68)
#
#                         article_entries.append({
#                             "Article Name": row["Article Name"],
#                             "Quantity": quantity,
#                             "Cost Per Unit": total_value / quantity if cost_per_unit == 0 else cost_per_unit,
#                             "Total Value": total_value,
#                             "Comments": comment
#
#                         })
#
#                     # Update Button for editing
#                     if st.button("Update"):
#                         if not institution_name or not address or not mobile or not article_entries:
#                             st.error("Please fill all required fields (*) before updating.")
#
#                         else:
#                             # Check for duplicate entries (same App. No., Article Name, and Comments)
#                             duplicate_entries = []
#
#                             for entry in article_entries:
#                                 duplicate = inst_data[
#                                     (inst_data["App. No."] == selected_app_number) &
#                                     (inst_data["Article Name"] == entry["Article Name"]) &
#                                     (inst_data["Comments"] == entry["Comments"]) &
#                                     (inst_data.index != index)  # Exclude the current entry being edited
#                                     ]
#                                 if not duplicate.empty:
#                                     duplicate_entries.append(entry["Article Name"])
#
#                             if duplicate_entries:
#                                 st.error(
#                                     f"Duplicate entries found : {', '.join(duplicate_entries)}. Please modify the comments or remove duplicates.")
#
#                             else:
#                                 # Remove the old entries
#                                 inst_data = inst_data[inst_data["App. No."] != selected_app_number]
#
#                                 # Flatten the article entries into individual rows
#                                 flattened_articles = []
#
#                                 for entry in article_entries:
#                                     flattened_articles.append({
#                                         "App. No.": selected_app_number,
#                                         "Institution Name": institution_name,
#                                         "Beneficiary Type": institution_type,
#                                         "Address": address,
#                                         "Mobile": str(mobile),
#                                         "Article Name": entry["Article Name"],
#                                         "Quantity": entry["Quantity"],
#                                         "Cost Per Unit": entry["Cost Per Unit"],
#                                         "Total Value": entry["Total Value"],
#                                         "Comments": entry["Comments"]
#                                     })
#
#                                 # Convert the flattened articles into a DataFrame
#                                 flattened_df = pd.DataFrame(flattened_articles)
#
#                                 # Append the updated data to the existing institution data
#                                 inst_data = pd.concat([inst_data, flattened_df], ignore_index=True).sort_values(
#                                     by="App. No.", ascending=True).reset_index(drop=True)
#
#                                 # Save the updated data back to storage
#                                 update_file(inst_data_id, inst_data)
#                                 # Success message
#                                 st.success("Request updated successfully!")
#                                 st.dataframe(inst_data)
#
#                 else:
#                     st.write("No entries available to edit.")
#
#
#             elif action == "Delete":
#
#                 # Select an entry to delete
#                 if not inst_data.empty:
#                     app_numbers = inst_data["App. No."].unique()
#                     selected_app_number = st.selectbox("Select Application Number to Delete", app_numbers)
#                     # Filter the data for the selected application number
#                     selected_entries = inst_data[inst_data["App. No."] == selected_app_number]
#                     # Add a checkbox for each record to allow selection
#                     st.write("Select records to delete:")
#
#                     delete_indices = []
#                     for index, row in selected_entries.iterrows():
#                         if st.checkbox(
#                                 f"Delete {row['Article Name']} (Qty: {row['Quantity']}, Total: ₹{row['Total Value']})",
#                                 key=f"delete_{index}"):
#                             delete_indices.append(index)
#
#                     # Delete Button
#                     if st.button("Delete Selection"):
#
#                         if not delete_indices:
#                             st.error("Please select at least one record to delete.")
#
#                         else:
#                             # Remove the selected records
#                             inst_data = inst_data.drop(delete_indices).sort_values(by="App. No.",
#                                                                                    ascending=True).reset_index(drop=True)
#                             # Save the updated data back to storage
#                             update_file(inst_data_id, inst_data)
#                             # Success message
#                             st.success("Selected records deleted successfully!")
#                             st.dataframe(inst_data)
#                 else:
#                     st.write("No entries available to delete.")
#
#             inst_fund = inst_data['Total Value'].sum()
#             # color = ?
#             st.markdown(
#                 f"<h5>Total Accrued: ₹ <span style='color:{'Green' if inst_fund >= 0 else 'Red'};'>{inst_fund:,.0f}</span></h5>",
#                 unsafe_allow_html=True)
#
#             st.download_button(
#                 label="Download Institution Records",
#                 data=inst_data.to_csv(index=False).encode('utf-8'),
#                 file_name="Institution_Records.csv",
#                 mime="text/csv"
#
#             )
#
#
#
# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state['authentication_status'] is None:
#     alert5 = st.info('Please enter your username and password')
#     time.sleep(1)
#     alert5.empty()