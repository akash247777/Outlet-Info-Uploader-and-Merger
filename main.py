import streamlit as st
import pandas as pd
import re
import io
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Streamlit UI
st.title("Outlet Info Uploader and Merger")

uploaded_file = st.file_uploader("Upload Cisco Working On Sim.xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Show progress indicator
    with st.spinner("Processing files..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Load site_info.xlsx from disk
        status_text.text("Loading site_info.xlsx...")
        site_df = pd.read_excel("site_info.xlsx")
        progress_bar.progress(20)
        
        # Load uploaded outlet_info.xlsx
        status_text.text("Loading uploaded file...")
        outlet_df = pd.read_excel(uploaded_file)
        progress_bar.progress(40)
        
        outlet_df.columns = outlet_df.columns.str.lower()
        
        # Check if 'name' column exists after conversion
        if 'name' not in outlet_df.columns:
            st.error(f"Column 'name' not found. Available columns: {list(outlet_df.columns)}")
            st.stop()
        
        # Extract numeric shop ID from 'Name' using regex
        status_text.text("Processing shop IDs...")
        outlet_df["shopid"] = outlet_df["name"].apply(lambda x: int(re.findall(r"\d+", str(x))[0]))
        progress_bar.progress(60)

        # Merge on shopid and SITEID
        status_text.text("Merging data...")
        merged_df = pd.merge(outlet_df, site_df, left_on="shopid", right_on="SITEID", how="left")
        progress_bar.progress(70)

        # Filter for Karnataka region only
        merged_df = merged_df[merged_df["region"] == "Karnataka"]

        # Rename columns for final format
        final_df = merged_df.rename(columns={
            "CLUSTER_MANAGER": "mgr"
        })[["shopid", "mgr", "name", "region", "eco/izo"]]
        progress_bar.progress(80)

        # Generate summary by manager
        status_text.text("Generating summary...")
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
        progress_bar.progress(90)

        # Save outputs to buffers using threading
        status_text.text("Preparing downloads...")
        
        def save_merged_output():
            merged_buffer = io.BytesIO()
            final_df.to_excel(merged_buffer, index=False)
            merged_buffer.seek(0)
            return merged_buffer
        
        def save_summary_output():
            summary_buffer = io.BytesIO()
            summary_df.to_excel(summary_buffer, index=False)
            summary_buffer.seek(0)
            return summary_buffer
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_merged = executor.submit(save_merged_output)
            future_summary = executor.submit(save_summary_output)
            
            merged_buffer = future_merged.result()
            summary_buffer = future_summary.result()
        
        progress_bar.progress(100)
        status_text.text("Complete!")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

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
