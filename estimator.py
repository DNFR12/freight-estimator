import pandas as pd
from geopy.geocoders import Nominatim
from utils import combine_all_datasets, estimate_freight, create_route_map

geolocator = Nominatim(user_agent="freight-estimator")

file_paths = ["data/otr_bulk.xlsx", "data/rail_bulk.xlsx", "data/ocean_bulk.xlsx", "data/ltl_ftl.xlsx"]
DATA = combine_all_datasets(file_paths)

def get_types():
    return ["OTR Bulk", "Iso Tank Bulk", "Containers Freight", "LTL & FTL"]

def get_origins():
    return sorted(DATA["Origin"].dropna().unique())

def get_destinations():
    return sorted(DATA["Destination"].dropna().unique())

def calculate_quote(shipment_type, origin, destination):
    return estimate_freight(DATA, shipment_type, origin, destination)

def geocode_city(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return (location.latitude, location.longitude)
    return None

def generate_map(origin, destination, shipment_type):
    origin_coords = geocode_city(origin)
    destination_coords = geocode_city(destination)
    if origin_coords and destination_coords:
        return create_route_map(origin_coords, destination_coords, shipment_type)
    return None
