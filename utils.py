import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Helper for safe geocoding
def geocode_city(city_name):
    geolocator = Nominatim(user_agent="freight-estimator")
    try:
        location = geolocator.geocode(city_name)
        if location:
            return (location.latitude, location.longitude)
    except GeocoderTimedOut:
        return None
    return None

# Clean & normalize each quote file
def load_and_clean(file_path, mode):
    df = pd.read_excel(file_path)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename common fields
    df = df.rename(columns={
        'origin': 'origin',
        'destination': 'destination',
        'linehaul': 'linehaul',
        'fuel': 'fuel',
        'total': 'total'
    })

    # Clean currency columns
    for col in ['linehaul', 'total']:
        if col in df.columns:
            df[col] = df[col].replace(r'[\$,]', '', regex=True).astype(float)

    # Fuel as percentage (e.g., "25%" → 0.25)
    if 'fuel' in df.columns:
        df['fuel'] = df['fuel'].astype(str).str.replace('%', '').astype(float) / 100

    # Add distance if not present
    if 'distance' not in df.columns and 'origin latitude' in df.columns and 'origin longitude' in df.columns:
        df['origin latitude'] = pd.to_numeric(df['origin latitude'], errors='coerce')
        df['origin longitude'] = pd.to_numeric(df['origin longitude'], errors='coerce')
        df['destination latitude'] = pd.to_numeric(df['destination latitude'], errors='coerce')
        df['destination longitude'] = pd.to_numeric(df['destination longitude'], errors='coerce')
        df['distance'] = df.apply(lambda row: (
            ((row['origin latitude'] - row['destination latitude']) ** 2 + 
             (row['origin longitude'] - row['destination longitude']) ** 2) ** 0.5
        ) * 69, axis=1)  # rough miles per degree

    df['mode'] = mode
    return df

# Combine all mode files
def combine_all_datasets(file_paths_by_mode):
    all_dfs = []
    for mode, path in file_paths_by_mode.items():
        df = load_and_clean(path, mode)
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)

# Estimate $/mile and fuel from all quotes
def get_average_metrics(df, mode):
    df_mode = df[df['mode'] == mode]
    if df_mode.empty:
        return None, None
    df_mode = df_mode[df_mode['distance'] > 0]
    df_mode['dollar_per_mile'] = df_mode['linehaul'] / df_mode['distance']
    avg_rate = df_mode['dollar_per_mile'].mean()
    avg_fuel_pct = df_mode['fuel'].mean()
    return avg_rate, avg_fuel_pct

# Optional legacy support
def clean_and_combine_data(file_paths):
    all_dfs = []
    for file in file_paths:
        df = pd.read_excel(file)
        df.columns = [col.lower().strip() for col in df.columns]
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)
