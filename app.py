from flask import Flask, render_template, request
from estimator import (
    get_types,
    get_origins,
    get_destinations,
    calculate_quote,
    get_coordinates
)
from map_utils import generate_map

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    types = get_types()
    selected_type = request.form.get("type")
    origin = request.form.get("origin")
    destination = request.form.get("destination")
    new_city = request.form.get("new_city")

    origins = get_origins(selected_type) if selected_type else []
    destinations = get_destinations(selected_type, origin) if origin else []

    quote_result = None
    map_html = None

    if request.method == "POST" and selected_type and origin:
        if destination:
            quote_result = calculate_quote(selected_type, origin, destination)
            coords_origin = get_coordinates(selected_type, origin)
            coords_dest = get_coordinates(selected_type, destination)
        elif new_city:
            quote_result = calculate_quote(selected_type, origin, new_city, is_new=True)
            coords_origin = get_coordinates(selected_type, origin)
            coords_dest = quote_result.get("coords")  # assume this was returned
        else:
            quote_result = {"error": "Please select or enter a destination."}
            coords_origin = coords_dest = None

        if coords_origin and coords_dest:
            map_html = generate_map(coords_origin, coords_dest, selected_type)

    return render_template(
        "index.html",
        types=types,
        selected_type=selected_type,
        origins=origins,
        origin=origin,
        destinations=destinations,
        destination=destination,
        new_city=new_city,
        quote=quote_result,
        map_html=map_html
    )

if __name__ == "__main__":
    app.run(debug=True)
