from flask import Flask, render_template, request
from estimator import get_types, get_origins, get_destinations, calculate_quote
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    types = get_types()

    selected_type = request.form.get("type")
    selected_origin = request.form.get("origin")
    selected_dest = request.form.get("destination")
    dest_lat = request.form.get("dest_lat")
    dest_lon = request.form.get("dest_lon")

    origins = get_origins(selected_type) if selected_type else []
    destinations = get_destinations(selected_type, selected_origin) if selected_origin else []

    if request.method == "POST":
        result = calculate_quote(selected_type, selected_origin, selected_dest, dest_lat, dest_lon)

    return render_template("index.html",
                           types=types,
                           origins=origins,
                           destinations=destinations,
                           selected_type=selected_type,
                           selected_origin=selected_origin,
                           selected_dest=selected_dest,
                           dest_lat=dest_lat,
                           dest_lon=dest_lon,
                           result=result)

# ✅ Render requires binding to 0.0.0.0 and using os.environ["PORT"]
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
