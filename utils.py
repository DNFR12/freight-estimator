import pandas as pd
import folium

def clean_currency_column(df, column):
    df[column] = df[column].replace(r'[\$,]', '', regex=True)
    df[column] = df[column].replace('-', '0')
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)
    return df

def combine_all_datasets(file_paths):
    combined = pd.DataFrame()
    for path in file_paths:
        df = pd.read_excel(path)
        df.columns = [col.strip() for col in df.columns]

        for col in ["LINEHAUL", "TANK WASH", "OTHER", "Demurrage", "TOTAL"]:
            if col in df.columns:
                df = clean_currency_column(df, col)

        if "FUEL" in df.columns:
            df["FUEL_PCT"] = df["FUEL"].replace('%', '', regex=True).replace('-', '0')
            df["FUEL_PCT"] = pd.to_numeric(df["FUEL_PCT"], errors="coerce").fillna(0.0) / 100
        else:
            df["FUEL_PCT"] = 0.0

        df["Type"] = infer_type_from_filename(path)
        combined = pd.concat([combined, df], ignore_index=True)
    
    return combined

def infer_type_from_filename(filename):
    if "otr" in filename.lower():
        return "OTR Bulk"
    elif "rail" in filename.lower():
        return "Iso Tank Bulk"
    elif "ocean" in filename.lower():
        return "Containers Freight"
    elif "ltl" in filename.lower():
        return "LTL & FTL"
    return "Unknown"

def estimate_freight(df, shipment_type, origin, destination):
    subset = df[(df["Type"] == shipment_type) & 
                (df["Origin"] == origin) & 
                (df["Destination"] == destination)]

    if subset.empty:
        return "No quote found for this route."

    avg_total = subset["TOTAL"].mean()
    return f"Estimated Quote: ${avg_total:,.2f}"

def create_route_map(origin_coords, destination_coords, shipment_type):
    m = folium.Map(location=[(origin_coords[0] + destination_coords[0]) / 2,
                             (origin_coords[1] + destination_coords[1]) / 2],
                   zoom_start=5)

    color = {
        "OTR Bulk": "blue",
        "Iso Tank Bulk": "green",
        "Containers Freight": "orange",
        "LTL & FTL": "purple"
    }.get(shipment_type, "gray")

    folium.Marker(location=origin_coords, popup="Origin", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(location=destination_coords, popup="Destination", icon=folium.Icon(color="green")).add_to(m)

    folium.PolyLine(locations=[origin_coords, destination_coords], color=color, weight=4.5).add_to(m)

    return m._repr_html_()
