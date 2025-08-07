import pandas as pd
from utils import combine_all_datasets, compute_distance, find_matching_routes, calculate_estimate

# File paths
file_paths = {
    'OTR Bulk': 'data/otr_bulk.xlsx',
    'Iso Tank Bulk': 'data/iso_tank.xlsx',
    'Containers Freight': 'data/container_freight.xlsx',
    'LTL & FTL': 'data/ltl_ftl.xlsx'
}

# Preload data
DATA = combine_all_datasets(file_paths)

def get_types():
    return sorted(DATA['Type'].unique())

def get_origins(shipment_type):
    return sorted(DATA[DATA['Type'] == shipment_type]['ORIGIN'].unique())

def get_destinations(shipment_type, origin):
    df = DATA[(DATA['Type'] == shipment_type) & (DATA['ORIGIN'] == origin)]
    return sorted(df['DESTINATION'].unique())

def calculate_quote(shipment_type, origin, destination, dest_coords):
    df = DATA[(DATA['Type'] == shipment_type) & (DATA['ORIGIN'] == origin)]

    if dest_coords:
        # New destination
        origin_row = df.iloc[0]
        origin_coords = (origin_row['Origin Latitude'], origin_row['Origin Longitude'])
        miles = compute_distance(origin_coords, dest_coords, shipment_type)
        result = calculate_estimate(df, miles)
        result['note'] = "Estimated using distance to new city"
    else:
        # Use actual quote
        matched = df[df['DESTINATION'] == destination]
        result = find_matching_routes(matched)
        result['note'] = "Average of known quotes" if not matched.empty else "No direct match, estimation unavailable"

    return result
