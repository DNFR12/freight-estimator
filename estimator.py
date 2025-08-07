from geopy.distance import geodesic

def estimate_freight(df, shipment_type, origin, destination, city_coords):
    filtered = df[(df['Type'] == shipment_type) &
                  (df['ORIGIN'] == origin) &
                  (df['DESTINATION'] == destination)]

    if not filtered.empty:
        avg_total = filtered['TOTAL'].mean()
        avg_fuel = filtered['FUEL'].mean() if 'FUEL' in filtered.columns else 0
        avg_miles = filtered['Miles'].mean() if 'Miles' in filtered.columns else None
        return round(avg_total, 2), round(avg_fuel, 2), round(avg_miles, 2) if avg_miles else None

    # If new destination, fallback to distance estimate
    if city_coords is None:
        return "Cannot calculate", "N/A", "N/A"

    origin_coords = df[
        (df['Type'] == shipment_type) & (df['ORIGIN'] == origin)
    ][['Origin Latitude', 'Origin Longitude']].dropna().iloc[0]

    dest_coords = city_coords
    distance_miles = geodesic(
        (origin_coords['Origin Latitude'], origin_coords['Origin Longitude']),
        (dest_coords[0], dest_coords[1])
    ).miles

    # Fallback logic: use $/mile and fuel % averages
    type_df = df[df['Type'] == shipment_type].dropna(subset=['TOTAL'])
    if type_df.empty:
        return "Cannot calculate", "N/A", f"{distance_miles:.0f} mi"

    type_df = type_df.assign(
        LinehaulOnly=type_df['TOTAL'] - type_df.get('FUEL', 0),
        Miles=type_df.apply(
            lambda row: geodesic(
                (row['Origin Latitude'], row['Origin Longitude']),
                (row['Destination Latitude'], row['Destination Longitude'])
            ).miles,
            axis=1
        )
    )

    type_df = type_df[type_df['Miles'] > 0]

    type_df = type_df.assign(
        RatePerMile=type_df['LinehaulOnly'] / type_df['Miles']
    )

    avg_rate_per_mile = type_df['RatePerMile'].mean()
    avg_fuel_pct = (type_df['FUEL'] / type_df['LinehaulOnly']).mean() if 'FUEL' in type_df.columns else 0

    est_linehaul = avg_rate_per_mile * distance_miles
    est_fuel = est_linehaul * avg_fuel_pct
    total = est_linehaul + est_fuel

    return round(total, 2), round(est_fuel, 2), f"{distance_miles:.0f} mi"
