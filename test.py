import streamlit as st
import pandas as pd

# Function to find record index
def find_record_index(df, district, article):
    return df[(df["NAME OF THE DISTRICT"] == district) & (df["REQUESTED ARTICLE"] == article)].index

# Display the summary table
st.subheader("Summary")
district_data = saved_data[saved_data["NAME OF THE DISTRICT"] == name]

if not district_data.empty:
    for index, row in district_data.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        col1.write(f"**{row['REQUESTED ARTICLE']}**")
        col2.write(f"Qty: {row['QUANTITY']}")
        col3.write(f"₹ {row['TOTAL COST']:,}")

        # Edit Button
        if col4.button("✏️", key=f"edit_{index}"):
            st.session_state["edit_index"] = index  # Store index in session state
            st.session_state["edit_mode"] = True

        # Delete Button
        if col4.button("🗑️", key=f"delete_{index}"):
            saved_data.drop(index, inplace=True)
            update_file(master_data_id, saved_data)
            st.success("Record deleted successfully!")
            st.experimental_rerun()

# Edit Mode: Pre-fill fields with selected record's details
if "edit_mode" in st.session_state and st.session_state["edit_mode"]:
    edit_index = st.session_state["edit_index"]
    row = saved_data.loc[edit_index]

    st.subheader("Edit Entry")
    new_quantity = st.number_input("Quantity*", min_value=0, value=row["QUANTITY"])
    new_total_value = st.number_input("Total Value", value=row["TOTAL COST"], min_value=0)

    if st.button("Update Record"):
        saved_data.loc[edit_index, ["QUANTITY", "TOTAL COST"]] = [new_quantity, new_total_value]
        update_file(master_data_id, saved_data)
        st.success("Record updated successfully!")
        st.session_state["edit_mode"] = False
        st.experimental_rerun()