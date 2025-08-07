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
    return sorted(DATA['TYPE'].dropna().unique().tolist())

def get_origins(shipment_type):
    df = DATA[DATA['TYPE'] == shipment_type]
    return sorted(df['ORIGIN'].dropna().unique().tolist())

def get_destinations(shipment_type, origin):
    df = DATA[(DATA['TYPE'] == shipment_type) & (DATA['ORIGIN'] == origin)]
    return sorted(df['DESTINATION'].dropna().unique().tolist())

def calculate_quote(shipment_type, origin, destination, new_city_coords=None):
    df = DATA[DATA['TYPE'] == shipment_type]

    if origin not in df['ORIGIN'].values:
        return "Origin not found."

    if destination in df['DESTINATION'].values:
        lanes = df[(df['ORIGIN'] == origin) & (df['DESTINATION'] == destination)]
        if not lanes.empty:
            avg_total = lanes['TOTAL'].mean()
            return f"${avg_total:,.2f}"
        else:
            return "Can not Calculate"

    if new_city_coords is None:
        return "Can not Calculate"

    return estimate_freight(df, origin, new_city_coords)

def get_coordinates(shipment_type, origin, destination):
    df = DATA[(DATA['TYPE'] == shipment_type) & (DATA['ORIGIN'] == origin)]

    # If it's a known destination
    row = df[df['DESTINATION'] == destination]
    if not row.empty:
        dest_lat = row.iloc[0]['Destination Latitude']
        dest_lon = row.iloc[0]['Destination Longitude']
        origin_lat = row.iloc[0]['Origin Latitude']
        origin_lon = row.iloc[0]['Origin Longitude']
        return (origin_lat, origin_lon), (dest_lat, dest_lon)

    return None, None
