import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="freight_estimator")

def geocode_city(city):
    try:
        loc = geolocator.geocode(city)
        return (loc.latitude, loc.longitude) if loc else None
    except:
        return None

def compute_distance(origin_coords, dest_coords, shipment_type):
    base_distance = geodesic(origin_coords, dest_coords).miles
    if shipment_type == 'Iso Tank Bulk':
        return base_distance * 1.3  # Rail multiplier
    elif shipment_type == 'Containers Freight':
        return base_distance * 1.1  # Ship multiplier
    else:
        return base_distance  # Road is most direct

def clean_currency_column(df, column):
    df[column] = df[column].replace('[\$,]', '', regex=True).astype(float)
    return df

def combine_all_datasets(file_paths):
    all_dfs = []
    for shipment_type, path in file_paths.items():
        df = pd.read_excel(path)
        df = df.rename(columns=lambda x: x.strip())
        df['Type'] = shipment_type

        if shipment_type == 'OTR Bulk':
            df = clean_currency_column(df, 'LINEHAUL')
            df = clean_currency_column(df, 'TOTAL')
            df['FUEL_PCT'] = df['FUEL'].str.replace('%', '').astype(float) / 100
        elif shipment_type == 'LTL & FTL':
            df = clean_currency_column(df, 'TOTAL')
        elif shipment_type == 'Iso Tank Bulk':
            df = clean_currency_column(df, 'Total')
            df = df.rename(columns={'Total': 'TOTAL'})
        elif shipment_type == 'Containers Freight':
            df = clean_currency_column(df, 'Total')
            df = df.rename(columns={'Total': 'TOTAL'})

        # Normalize column names
        df['ORIGIN'] = df['Origin'] if 'Origin' in df.columns else df['ORIGIN']
        df['DESTINATION'] = df['Designation'] if 'Designation' in df.columns else df['DESTINATION']
        df['Origin Latitude'] = df['Origin Latitude'].astype(float)
        df['Origin Longitude'] = df['Origin Longitude'].astype(float)

        all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True)

def find_matching_routes(df):
    if df.empty:
        return {'total': 'Cannot Calculate'}

    avg = df['TOTAL'].mean()
    return {
        'total': round(avg, 2)
    }

def calculate_estimate(df, miles):
    df = df[df['LINEHAUL'] > 0] if 'LINEHAUL' in df.columns else df
    df = df[df['TOTAL'] > 0]

    avg_linehaul_per_mile = df['LINEHAUL'].div(miles).mean() if 'LINEHAUL' in df.columns else df['TOTAL'].div(miles).mean()
    avg_fuel_pct = df['FUEL_PCT'].mean() if 'FUEL_PCT' in df.columns else 0.2  # fallback

    linehaul = avg_linehaul_per_mile * miles
    fuel = linehaul * avg_fuel_pct
    total = linehaul + fuel

    return {
        'linehaul': round(linehaul, 2),
        'fuel': round(fuel, 2),
        'total': round(total, 2)
    }
