import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os

DATA_DIR = "data"

FILES = {
    "OTR Bulk": "otr_bulk.xlsx",
    "Iso Tank Bulk": "iso_tank_bulk.xlsx",
    "Containers Freight": "containers_freight.xlsx",
    "LTL & FTL": "ltl_ftl.xlsx"
}


def load_data(shipment_type):
    file_name = FILES.get(shipment_type)
    if not file_name:
        return pd.DataFrame()
    
    path = os.path.join(DATA_DIR, file_name)
    df = pd.read_excel(path)
    
    # Normalize columns for consistency
    df.columns = [col.strip().lower() for col in df.columns]

    # Clean currency and percent columns if needed
    for col in ['linehaul', 'fuel', 'total']:
        if col in df.columns:
            df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)

    if 'fuel' in df.columns and df['fuel'].dtype == object:
        # If fuel is in percentage format like '25%' convert to decimal
        df['fuel'] = df['fuel'].replace('%', '', regex=True).astype(float) / 100

    return df


def get_types():
    return list(FILES.keys())


def get_origins(shipment_type):
    df = load_data(shipment_type)
    return sorted(df['origin'].dropna().unique()) if 'origin' in df.columns else []


def get_destinations(shipment_type, origin):
    df = load_data(shipment_type)
    if 'origin' in df.columns and 'destination' in df.columns:
        return sorted(df[df['origin'] == origin]['destination'].dropna().unique())
    return []


def geocode_city(city_name):
    try:
        geolocator = Nominatim(user_agent="freight-estimator")
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception:
        return None, None


def calculate_quote(shipment_type, origin, destination=None, new_destination=None):
    df = load_data(shipment_type)

    if not origin:
        return "Invalid input", None, None

    origin_row = df[df['origin'] == origin]
    if origin_row.empty:
        return "Invalid origin", None, None

    origin_coords = (origin_row.iloc[0]['origin latitude'], origin_row.iloc[0]['origin longitude'])

    if new_destination:
        dest_coords = geocode_city(new_destination)
        if not all(dest_coords):
            return "Could not geocode new city", origin_coords, None

        # Calculate geodesic distance
        distance_miles = geodesic(origin_coords, dest_coords).miles

        # Use average $/mile and average fuel% for estimation
        df = df.dropna(subset=['linehaul', 'total'])
        df['dollars_per_mile'] = df['total'] / df.apply(
            lambda row: geodesic((row['origin latitude'], row['origin longitude']),
                                 (row['destination latitude'], row['destination longitude'])).miles
            if pd.notnull(row['destination latitude']) and pd.notnull(row['destination longitude']) else None,
            axis=1
        )
        df = df[df['dollars_per_mile'].notnull()]
        avg_per_mile = df['dollars_per_mile'].mean()
        avg_fuel_pct = df['fuel'].mean()

        if pd.isna(avg_per_mile) or pd.isna(avg_fuel_pct):
            return "Can not Calculate", origin_coords, dest_coords

        base = avg_per_mile * distance_miles
        fuel = base * avg_fuel_pct
        estimated_total = round(base + fuel, 2)
        return f"${estimated_total:,.2f}", origin_coords, dest_coords

    # Else use quoted lane
    if not destination:
        return "No destination selected", origin_coords, None

    match = df[(df['origin'] == origin) & (df['destination'] == destination)]
    if match.empty:
        return "No quoted lane found", origin_coords, None

    origin_coords = (match.iloc[0]['origin latitude'], match.iloc[0]['origin longitude'])
    dest_coords = (match.iloc[0]['destination latitude'], match.iloc[0]['destination longitude'])

    avg_total = match['total'].mean()
    return f"${avg_total:,.2f}", origin_coords, dest_coords
