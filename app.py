from flask import Flask, render_template, request, jsonify
from estimator import get_types, get_origins, get_destinations, calculate_quote
from utils import geocode_city

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_origins')
def get_origin_list():
    shipment_type = request.args.get('shipment_type')
    return jsonify(get_origins(shipment_type))

@app.route('/get_destinations')
def get_destination_list():
    shipment_type = request.args.get('shipment_type')
    origin = request.args.get('origin')
    return jsonify(get_destinations(shipment_type, origin))

@app.route('/calculate', methods=['POST'])
def get_estimate():
    data = request.json
    shipment_type = data['type']
    origin = data['origin']
    destination = data['destination']
    new_destination = data.get('new_destination')

    dest_coords = geocode_city(new_destination) if new_destination else None
    result = calculate_quote(shipment_type, origin, destination, dest_coords)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
