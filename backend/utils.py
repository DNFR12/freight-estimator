import pandas as pd
import os

def clean_and_combine_data():
    file_map = {
        "OTR Bulk": "otr_bulk.xlsx",
        "Iso Tank Bulk": "iso_tank_bulk.xlsx",
        "Containers Freight": "containers_freight.xlsx",
        "LTL & FTL": "ltl_ftl.xlsx"
    }

    all_dfs = []

    for shipment_type, filename in file_map.items():
        path = os.path.join("backend", "data", filename)
        df = pd.read_excel(path)

        # Normalize headers
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Base schema to map into
        standard_cols = {
            "origin": "Origin",
            "destination": "Destination",
            "designation": "Destination",
            "total": "Total",
            "linehaul": "Linehaul",
            "fuel": "Fuel",
            "origin_latitude": "Origin Latitude",
            "origin_longitude": "Origin Longitude",
            "destination_latitude": "Destination Latitude",
            "destination_longitude": "Destination Longitude",
            "designation_latitude": "Destination Latitude",
            "designation_longitude": "Destination Longitude"
        }

        df = df.rename(columns={k: v for k, v in standard_cols.items() if k in df.columns})

        # Add missing columns if necessary
        for col in ["Linehaul", "Fuel", "Origin", "Destination", "Total", 
                    "Origin Latitude", "Origin Longitude", 
                    "Destination Latitude", "Destination Longitude"]:
            if col not in df.columns:
                df[col] = pd.NA

        # Standardize Fuel (convert "25%" → 0.25)
        def parse_fuel(val):
            if isinstance(val, str) and "%" in val:
                return float(val.replace("%", "").strip()) / 100
            try:
                return float(val)
            except:
                return pd.NA

        df["Fuel"] = df["Fuel"].apply(parse_fuel)

        # Add Type
        df["Type"] = shipment_type

        # Final selection + order
        final_cols = [
            "Type", "Origin", "Destination", "Linehaul", "Fuel", "Total",
            "Origin Latitude", "Origin Longitude", 
            "Destination Latitude", "Destination Longitude"
        ]

        df = df[final_cols]
        all_dfs.append(df)

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.to_csv("backend/data/all_quotes.csv", index=False)  # Optional: for inspection
    return combined_df

