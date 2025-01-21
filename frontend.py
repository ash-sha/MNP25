import streamlit as st
import pandas as pd
import os

# Check if the data file exists
article = "articles.csv"
saved_data_file = "saved_data.csv"

# if not os.path.exists(data_file):
#     st.error(f"The file '{data_file}' was not found.")
#     st.stop()

# Load data
article = pd.read_csv(article)
district = pd.read_csv("District_beneficiary.csv")

# Initialize app
st.set_page_config(page_title="மக்கள் நல பணி", layout="wide")
st.title("மக்கள் நல பணி")

# Sidebar navigation
selected_tab = st.sidebar.radio("Select Tab", ["Input"])

if selected_tab == "Input":
    # Radio buttons to select type
    type_choice = st.radio("Beneficiary Type", ["District", "Public", "Institutions"], horizontal=True)

    if type_choice == "District":
        # Input fields
        name = st.selectbox("District Name", district["District Name"].unique().tolist())
        article_name = st.selectbox("Enter Article Name", article["Articles"].unique().tolist())
        quantity = st.number_input("Quantity", min_value=1, step=1)

        # Calculate and display total value
        total_value = quantity * article[article["Articles"]==article_name]["Cost per unit"].tolist()[0]
        st.subheader(f"₹ {total_value:,}")

        # Load saved data
        if os.path.exists(saved_data_file):
            saved_data = pd.read_csv(saved_data_file)
        else:
            saved_data = pd.DataFrame(columns=["District Name", "Article Name", "Quantity", "Total Value"])

        # Save button
        if st.button("Save"):
            if not name or not article_name:
                st.warning("Please fill all fields before saving.")
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
        st.subheader("Saved Data")
        st.dataframe(saved_data[saved_data["District Name"] == name])

        st.download_button(
            label="Download Records",
            data=saved_data.to_csv(index=False).encode('utf-8'),
            file_name="District Beneficiaries Records.csv",
            mime = "text/csv"
        )





