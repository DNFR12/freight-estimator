# estimator.py
from geopy.distance import geodesic
from utils import clean_and_combine_data
import pandas as pd

file_paths = [
    'data/otr_bulk.xlsx',
    'data/iso_tank.xlsx',
    'data/container_freight.xlsx',
    'data/ltl_ftl.xlsx'
]

DATA = clean_and_combine_data()

def get_types():
    return sorted(DATA["Type"].dropna().unique())

def get_origins(shipment_type):
    df = DATA[DATA["Type"] == shipment_type]
    return sorted(df["Origin"].dropna().unique())

def get_destinations(shipment_type, origin):
    df = DATA[(DATA["Type"] == shipment_type) & (DATA["Origin"] == origin)]
    return sorted(df["Destination"].dropna().unique())

def calculate_quote(shipment_type, origin, destination, dest_lat=None, dest_lon=None):
    df_match = DATA[(DATA["Type"] == shipment_type) &
                    (DATA["Origin"] == origin) &
                    (DATA["Destination"] == destination)]

    if not df_match.empty:
        return {
            "status": "Quoted",
            "total": round(df_match["Total"].mean(), 2)
        }

    try:
        df_type = DATA[DATA["Type"] == shipment_type]
        valid = df_type[(df_type["Linehaul"].notna()) &
                        (df_type["Fuel"].notna()) &
                        (df_type["Origin Latitude"].notna()) &
                        (df_type["Destination Latitude"].notna())]

        valid = valid.copy()
        valid["Distance"] = valid.apply(lambda row: geodesic(
            (row["Origin Latitude"], row["Origin Longitude"]),
            (row["Destination Latitude"], row["Destination Longitude"])).miles, axis=1)

        valid["$/mile"] = valid["Linehaul"] / valid["Distance"]
        avg_rate = valid["$/mile"].mean()
        avg_fuel = valid["Fuel"].mean()

        origin_row = df_type[df_type["Origin"] == origin].iloc[0]
        origin_coords = (origin_row["Origin Latitude"], origin_row["Origin Longitude"])
        dest_coords = (float(dest_lat), float(dest_lon))

        distance = geodesic(origin_coords, dest_coords).miles
        linehaul = avg_rate * distance
        total = linehaul * (1 + avg_fuel)

        return {
            "status": "Estimated",
            "total": round(total, 2),
            "distance": round(distance, 1)
        }

    except:
        return {"status": "Cannot Calculate"}

