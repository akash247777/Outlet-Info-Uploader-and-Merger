# Outlet-Info-Uploader-and-Merger

# 📊 Outlet Info Uploader and Merger

This Streamlit web app allows users to upload outlet data, merge it with site metadata, filter results for Karnataka region, and generate two downloadable Excel reports: a detailed merged output and a summary grouped by cluster manager.

## 🚀 Features

- 📥 Upload outlet data file (`Cisco Working On Sim.xlsx`)
- 🧠 Automatically extracts `shopid` from outlet `Name`
- 🔗 Merges uploaded data with local `site_info.xlsx` via `shopid` and `SITEID`
- 🌍 Filters merged data for Karnataka region
- 📋 Summarizes outlet count by manager, including serial numbers and a total row
- 📤 Download final reports:
  - `merged_output.xlsx`
  - `outlet_summary.xlsx`

## 📂 Required Files

- **Input via UI**: `Cisco Working On Sim.xlsx` (containing outlet info)
- **Local file**: `site_info.xlsx` (must be present in the app directory)

## 🛠 How to Run

1. Install dependencies:
   ```bash
   pip install streamlit pandas openpyxl
   ```
2. Place site_info.xlsx in the same folder as your script.
3. Run the app:
```
streamlit run your_script_name.py
```

- Upload the outlet file and download results once processing is complete.
📎 Output Files
- merged_output.xlsx: Contains merged details with columns:
- shopid, mgr (Cluster Manager), name, region, eco/izo
- outlet_summary.xlsx: Manager-wise summary:
- Includes serial numbers and total count

📌 Notes

- Ensure  column in the uploaded file contains numeric  values.

- The application filters exclusively for rows with.

🙌 Acknowledgements

Built with ❤️ using Streamlit and Pandas for easy outlet info processing.
