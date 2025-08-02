import streamlit as st
import pandas as pd
import re
import io

# Streamlit UI
st.title("Outlet Info Uploader and Merger")

uploaded_file = st.file_uploader("Upload Cisco Working On Sim.xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Load site_info.xlsx from disk
    site_df = pd.read_excel("site_info.xlsx")
    # Load uploaded outlet_info.xlsx
    outlet_df = pd.read_excel(uploaded_file)
    

    
    outlet_df.columns = outlet_df.columns.str.lower()
    
    # Check if 'name' column exists after conversion
    if 'name' not in outlet_df.columns:
        st.error(f"Column 'name' not found. Available columns: {list(outlet_df.columns)}")
        st.stop()
    
    # Extract numeric shop ID from 'Name' using regex
    outlet_df["shopid"] = outlet_df["name"].apply(lambda x: int(re.findall(r"\d+", str(x))[0]))

    # Merge on shopid and SITEID
    merged_df = pd.merge(outlet_df, site_df, left_on="shopid", right_on="SITEID", how="left")

    # Filter for Karnataka region only
    merged_df = merged_df[merged_df["region"] == "Karnataka"]

    # Rename columns for final format
    final_df = merged_df.rename(columns={
        "CLUSTER_MANAGER": "mgr"
    })[["shopid", "mgr", "name", "region", "eco/izo"]]

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
    
    # Display outlet summary in frontend
    st.subheader("Outlet Summary by Manager")
    st.dataframe(summary_df, use_container_width=True)
    
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
    st.info("Please upload your `Cisco Working On Sim.xlsx` file to proceed.")
