import pandas as pd
from utils import combine_all_datasets, estimate_freight

# File paths for each shipment type
file_paths = {
    'OTR Bulk': 'data/otr_bulk.xlsx',
    'Iso Tank Bulk': 'data/iso_tank.xlsx',
    'Containers Freight': 'data/container_freight.xlsx',
    'LTL & FTL': 'data/ltl_ftl.xlsx'
}

# Combine all datasets into a single DataFrame with a column for Type
DATA = combine_all_datasets(file_paths)

# Extract options for dropdowns
def get_types():
    return sorted(DATA['Type'].unique())

def get_origins(shipment_type):
    df = DATA[DATA['Type'] == shipment_type]
    return sorted(df['ORIGIN'].unique())

def get_destinations(shipment_type, origin):
    df = DATA[(DATA['Type'] == shipment_type) & (DATA['ORIGIN'] == origin)]
    return sorted(df['DESTINATION'].unique())

# Main quote calculator
def calculate_quote(shipment_type, origin, destination, city_coords):
    return estimate_freight(DATA, shipment_type, origin, destination, city_coords)
