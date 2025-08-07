from utils import combine_all_datasets, estimate_freight

# Define paths to your quote files
file_paths = {
    'OTR Bulk': 'data/otr_bulk.xlsx',
    'Iso Tank Bulk': 'data/isotank_bulk.xlsx',
    'Containers Freight': 'data/containers_freight.xlsx',
    'LTL & FTL': 'data/ltl_ftl.xlsx',
}

# Combine and clean all quote datasets
DATA = combine_all_datasets(file_paths)

def get_types():
    # ✅ Return the unique shipment types, not column headers
    return sorted(DATA['TYPE'].dropna().unique().tolist())

def get_origins(shipment_type):
    df = DATA[DATA['TYPE'] == shipment_type]
    return sorted(df['ORIGIN'].dropna().unique().tolist())

def get_destinations(shipment_type, origin):
    df = DATA[(DATA['TYPE'] == shipment_type) & (DATA['ORIGIN'] == origin)]
    return sorted(df['DESTINATION'].dropna().unique().tolist())

def calculate_quote(shipment_type, origin, destination, new_city_coords=None):
    df = DATA[(DATA['TYPE'] == shipment_type)]

    if origin not in df['ORIGIN'].values:
        return "Origin not found."

    if destination in df['DESTINATION'].values:
        # Known destination: return average total
        lanes = df[(df['ORIGIN'] == origin) & (df['DESTINATION'] == destination)]
        if not lanes.empty:
            avg_total = lanes['TOTAL'].mean()
            return f"${avg_total:,.2f}"
        else:
            return "Can not Calculate"

    # Unknown destination: Estimate using $/mile + fuel logic
    if new_city_coords is None:
        return "Can not Calculate"

    estimate = estimate_freight(df, origin, new_city_coords)
    return estimate
