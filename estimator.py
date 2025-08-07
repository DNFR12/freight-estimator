from utils import (
    combine_all_datasets,
    estimate_freight,
    get_coordinates,
    calculate_distance,
)

# Mapping of shipment types to filenames
file_paths = {
    "OTR Bulk": "data/otr_bulk.xlsx",
    "Iso tank Bulk": "data/iso_tank_bulk.xlsx",
    "Containers Freight": "data/containers_freight.xlsx",
    "LTL & FTL": "data/ltl_ftl.xlsx"
}

# Load and clean all data once at startup
DATA = combine_all_datasets(file_paths)

def get_types():
    return list(DATA.keys())

def get_origins(shipment_type):
    df = DATA.get(shipment_type)
    if df is not None:
        return sorted(df['ORIGIN'].dropna().unique().tolist())
    return []

def get_destinations(shipment_type, origin):
    df = DATA.get(shipment_type)
    if df is not None:
        filtered = df[df['ORIGIN'] == origin]
        return sorted(filtered['DESTINATION'].dropna().unique().tolist())
    return []

def calculate_quote(shipment_type, origin, destination, distance):
    df = DATA.get(shipment_type)
    if df is None:
        return "Can not calculate", False

    filtered = df[
        (df['ORIGIN'] == origin) & (df['DESTINATION'] == destination)
    ]

    if not filtered.empty:
        total = filtered['TOTAL'].mean()
        return f"${total:,.2f}", False
    else:
        est = estimate_freight(df, origin, distance)
        return (f"${est:,.2f}", True) if est is not None else ("Can not calculate", False)

def get_coordinates(shipment_type, origin, destination):
    df = DATA.get(shipment_type)
    if df is None:
        raise ValueError("Invalid shipment type")

    row = df[
        (df['ORIGIN'] == origin) & (df['DESTINATION'] == destination)
    ].head(1)

    if not row.empty:
        origin_coords = (row.iloc[0]['Origin Latitude'], row.iloc[0]['Origin Longitude'])
        dest_coords = (row.iloc[0]['Destination Latitude'], row.iloc[0]['Destination Longitude'])
        return origin_coords, dest_coords

    # Fallback: just use first instance of ORIGIN
    origin_row = df[df['ORIGIN'] == origin].head(1)
    if not origin_row.empty:
        origin_coords = (origin_row.iloc[0]['Origin Latitude'], origin_row.iloc[0]['Origin Longitude'])
    else:
        raise ValueError("Origin coordinates not found")

    # Assume new destination has already been geocoded by client
    raise ValueError("Destination coordinates must be handled externally")
