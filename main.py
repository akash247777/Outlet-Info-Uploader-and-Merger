import streamlit as st
import pandas as pd
import re
import io

# Streamlit UI
st.title("Outlet Info Uploader and Merger")

uploaded_file = st.file_uploader("Upload outlet_info.xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Load site_info.xlsx from disk
    site_df = pd.read_excel("site_info.xlsx")
    # Load uploaded outlet_info.xlsx
    outlet_df = pd.read_excel(uploaded_file)

    # Extract numeric shop ID from 'Name' using regex
    outlet_df["shopid"] = outlet_df["Name"].apply(lambda x: int(re.findall(r"\d+", str(x))[0]))

    # Merge on shopid and SITEID
    merged_df = pd.merge(outlet_df, site_df, left_on="shopid", right_on="SITEID", how="left")

    # Rename columns for final format
    final_df = merged_df.rename(columns={
        "CLUSTER_MANAGER": "mgr"
    })[["shopid", "mgr", "Name", "Region", "ECO/IZO"]]

    # Save detailed merged output to buffer
    merged_buffer = io.BytesIO()
    final_df.to_excel(merged_buffer, index=False)
    merged_buffer.seek(0)

    # Generate summary by manager
    summary_df = (
        final_df.groupby("mgr")
        .size()
        .reset_index(name="Count of Outlets")
        .sort_values(by="Count of Outlets", ascending=False)
    )

    # Add serial numbers
    summary_df.insert(0, "S.no", range(1, len(summary_df) + 1))

    # Add total row
    total = pd.DataFrame({
        "S.no": ["total"],
        "mgr": [""],
        "Count of Outlets": [summary_df["Count of Outlets"].sum()]
    })
    summary_df = pd.concat([summary_df, total], ignore_index=True)

    # Save summary output to buffer
    summary_buffer = io.BytesIO()
    summary_df.to_excel(summary_buffer, index=False)
    summary_buffer.seek(0)

    st.success("Processing complete!")
    st.download_button(
        label="Download Merged Output (merged_output.xlsx)",
        data=merged_buffer,
        file_name="merged_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        label="Download Outlet Summary (outlet_summary.xlsx)",
        data=summary_buffer,
        file_name="outlet_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload the outlet_info.xlsx file to proceed.")