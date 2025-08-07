from flask import Flask, render_template, request
from estimator import get_types, get_origins, get_destinations, calculate_quote
from utils import geocode_city
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    types = get_types()
    selected_type = request.form.get('type') or types[0]
    origins = get_origins(selected_type)
    destinations = get_destinations(selected_type)

    selected_origin = request.form.get('origin')
    selected_destination = request.form.get('destination')
    new_destination = request.form.get('new_destination')

    quote = None
    origin_coords = None
    dest_coords = None

    if selected_origin:
        df = pd.read_excel(os.path.join('data', f"{selected_type.lower().replace(' ', '_')}.xlsx"))
        origin_row = df[df['ORIGIN'].str.strip().str.lower() == selected_origin.strip().lower()]
        if not origin_row.empty:
            row = origin_row.iloc[0]
            origin_coords = (row['Origin Latitude'], row['Origin Longitude'])

    if request.method == 'POST':
        quote, dest_lat, dest_lon = calculate_quote(
            selected_type,
            selected_origin,
            selected_destination,
            new_destination
        )

        if dest_lat and dest_lon:
            dest_coords = (dest_lat, dest_lon)

    return render_template(
        'index.html',
        types=types,
        origins=origins,
        destinations=destinations,
        selected_type=selected_type,
        selected_origin=selected_origin,
        selected_destination=selected_destination,
        new_destination=new_destination,
        quote=quote,
        origin_coords=origin_coords,
        dest_coords=dest_coords
    )

if __name__ == '__main__':
    app.run(debug=True)
