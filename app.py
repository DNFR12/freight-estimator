# app.py
from flask import Flask, render_template, request
from estimator import get_types, get_origins, get_destinations, calculate_quote
from geopy.geocoders import Nominatim
import os
import pandas as pd
from utils import clean_and_combine_data

app = Flask(__name__)
geolocator = Nominatim(user_agent="freight-estimator")
DATA = clean_and_combine_data()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    types = get_types()

    selected_type = request.form.get("type")
    selected_origin = request.form.get("origin")
    selected_dest = request.form.get("destination")
    dest_city = request.form.get("dest_city")
    dest_lat = request.form.get("dest_lat")
    dest_lon = request.form.get("dest_lon")

    origin_row = None

    # Geocode destination city if entered
    if dest_city and not dest_lat and not dest_lon:
        try:
            location = geolocator.geocode(dest_city)
            if location:
                dest_lat = location.latitude
                dest_lon = location.longitude
        except:
            dest_lat = dest_lon = None

    origins = get_origins(selected_type) if selected_type else []
    destinations = get_destinations(selected_type, selected_origin) if selected_origin else []

    if selected_type and selected_origin:
        df = DATA[(DATA["Type"] == selected_type) & (DATA["Origin"] == selected_origin)]
        if not df.empty:
            origin_row = df.iloc[0].to_dict()

    if request.method == "POST":
        result = calculate_quote(selected_type, selected_origin, selected_dest, dest_lat, dest_lon)

    return render_template("index.html",
                           types=types,
                           origins=origins,
                           destinations=destinations,
                           selected_type=selected_type,
                           selected_origin=selected_origin,
                           selected_dest=selected_dest,
                           dest_city=dest_city,
                           dest_lat=dest_lat,
                           dest_lon=dest_lon,
                           result=result,
                           origin_row=origin_row)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
