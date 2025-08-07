try:
    from flask import Flask, render_template, request
    from estimator import (
        get_types,
        get_origins,
        get_destinations,
        calculate_quote,
        get_coordinates,
        calculate_distance,
    )
    import folium

    app = Flask(__name__)

    @app.route('/')
    def index():
        print("✅ Loading index")
        types = get_types()
        return render_template('index.html', types=types)

    @app.route('/get_origins', methods=['POST'])
    def get_origins_route():
        shipment_type = request.form['shipment_type']
        origins = get_origins(shipment_type)
        return {'origins': origins}

    @app.route('/get_destinations', methods=['POST'])
    def get_destinations_route():
        shipment_type = request.form['shipment_type']
        origin = request.form['origin']
        destinations = get_destinations(shipment_type, origin)
        return {'destinations': destinations}

    @app.route('/calculate', methods=['POST'])
    def calculate():
        shipment_type = request.form['shipment_type']
        origin = request.form['origin']
        destination = request.form['destination']

        print(f"🔍 Calculating quote for: {shipment_type}, {origin} → {destination}")

        try:
            coords = get_coordinates(shipment_type, origin, destination)
            origin_coords, dest_coords = coords

            distance = calculate_distance(origin_coords, dest_coords)
            result, direct = calculate_quote(shipment_type, origin, destination, distance)

            return {
                'quote': result,
                'direct': direct,
                'origin_lat': origin_coords[0],
                'origin_lon': origin_coords[1],
                'dest_lat': dest_coords[0],
                'dest_lon': dest_coords[1],
            }

        except Exception as e:
            print(f"❌ Error during calculation: {e}")
            return {'quote': 'Error during calculation', 'direct': False}

    if __name__ == '__main__':
        print("✅ app.py started successfully")
        app.run(host='0.0.0.0', port=10000)

except Exception as e:
    print("❌ Error starting app.py:", e)
    raise
