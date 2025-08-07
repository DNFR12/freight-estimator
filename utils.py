import pandas as pd
from geopy.distance import geodesic

def safe_float_conversion(series):
    """Remove $, %, and invalid entries, then convert to float safely."""
    return pd.to_numeric(series.replace(r'[\$,%,]', '', regex=True), errors='coerce')

def combine_all_datasets(file_paths):
    """Combine datasets from multiple shipment types into one unified DataFrame."""
    all_dfs = []

    for shipment_type, path in file_paths.items():
        df = pd.read_excel(path)
        df.columns = [col.strip() for col in df.columns]
        df['Type'] = shipment_type

        # Normalize origin and destination column names
        if 'Origin' in df.columns:
            df['ORIGIN'] = df['Origin']
        if 'Designation' in df.columns:
            df['DESTINATION'] = df['Designation']
        if 'Destination' in df.columns and 'DESTINATION' not in df.columns:
            df['DESTINATION'] = df['Destination']

        if 'ORIGIN' not in df.columns:
            df['ORIGIN'] = df.get('Origin', '')

        # Latitude and Longitude conversions
        df['Origin Latitude'] = pd.to_numeric(df.get('Origin Latitude', None), errors='coerce')
        df['Origin Longitude'] = pd.to_numeric(df.get('Origin Longitude', None), errors='coerce')
        df['Destination Latitude'] = pd.to_numeric(df.get('Destination Latitude', None), errors='coerce')
        df['Destination Longitude'] = pd.to_numeric(df.get('Destination Longitude', None), errors='coerce')

        # Shipment-type-specific processing
        if shipment_type == 'OTR Bulk':
            df['LINEHAUL'] = safe_float_conversion(df.get('LINEHAUL', 0))
            df['FUEL_PCT'] = safe_float_conversion(df.get('FUEL', '0')) / 100
            df['TOTAL'] = safe_float_conversion(df.get('TOTAL', 0))
        elif shipment_type in ['Iso Tank Bulk', 'Containers Freight']:
            df['TOTAL'] = safe_float_conversion(df.get('Total', 0))
        elif shipment_type == 'LTL & FTL':
            df['TOTAL'] = safe_float_conversion(df.get('TOTAL', 0))

        all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True)

def estimate_freight(df, shipment_type, origin, destination, distance=None):
    """Estimate the freight cost based on historical averages or fallback if unknown."""
    filtered = df[
        (df['Type'] == shipment_type) &
        (df['ORIGIN'] == origin) &
        (df['DESTINATION'] == destination)
    ]

    if not filtered.empty:
        avg_total = filtered['TOTAL'].mean()
        return round(avg_total, 2), True

    # Fallback estimation using $/mile and fuel % average
    type_subset = df[df['Type'] == shipment_type].copy()
    type_subset = type_subset[type_subset['LINEHAUL'].notna()]
    if distance and not type_subset.empty:
        avg_rate_per_mile = (type_subset['LINEHAUL'] / distance).mean()
        avg_fuel_pct = type_subset['FUEL_PCT'].mean()
        est_linehaul = avg_rate_per_mile * distance
        est_fuel = est_linehaul * avg_fuel_pct
        estimate = est_linehaul + est_fuel
        return round(estimate, 2), False

    return "Cannot Calculate", False

def get_coordinates(df, shipment_type, origin, destination):
    """Get coordinates for the origin and destination."""
    filtered = df[
        (df['Type'] == shipment_type) &
        (df['ORIGIN'] == origin) &
        (df['DESTINATION'] == destination)
    ]
    if filtered.empty:
        return None, None

    first = filtered.iloc[0]
    origin_coords = (first['Origin Latitude'], first['Origin Longitude'])
    dest_coords = (first['Destination Latitude'], first['Destination Longitude'])

    if None in origin_coords or None in dest_coords:
        return None, None

    return origin_coords, dest_coords

def calculate_distance(origin_coords, dest_coords):
    """Calculate the geodesic distance between two coordinates."""
    if origin_coords is None or dest_coords is None:
        return None
    return geodesic(origin_coords, dest_coords).miles
