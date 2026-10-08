from flask import Flask, request, jsonify
import uuid
import random
from datetime import datetime

app = Flask(__name__)

# In-memory delivery records
deliveries_db = {}

# Available delivery partners pool
RIDERS = [
    {"name": "Alex Mercer", "phone": "+1-555-0101", "vehicle": "E-Bike"},
    {"name": "Sarah Connor", "phone": "+1-555-0102", "vehicle": "Motorcycle"},
    {"name": "David Miller", "phone": "+1-555-0103", "vehicle": "Scooter"},
    {"name": "Elena Rostova", "phone": "+1-555-0104", "vehicle": "Bicycle"},
    {"name": "Marcus Vance", "phone": "+1-555-0105", "vehicle": "Motorcycle"}
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "service": "delivery-service",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/deliveries/assign', methods=['POST'])
def assign_delivery():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    delivery_address = data.get("delivery_address", "Default City Address")

    if not order_id:
        return jsonify({
            "status": "FAILED",
            "message": "Missing required field: order_id"
        }), 400

    delivery_id = f"del_{uuid.uuid4().hex[:10]}"
    assigned_rider = random.choice(RIDERS)
    estimated_minutes = random.randint(20, 45)

    delivery_record = {
        "delivery_id": delivery_id,
        "order_id": order_id,
        "delivery_address": delivery_address,
        "status": "ASSIGNED",
        "rider_name": assigned_rider["name"],
        "rider_contact": assigned_rider["phone"],
        "vehicle_type": assigned_rider["vehicle"],
        "estimated_time_mins": estimated_minutes,
        "assigned_at": datetime.utcnow().isoformat()
    }

    deliveries_db[delivery_id] = delivery_record

    return jsonify({
        "status": "SUCCESS",
        "message": "Delivery partner successfully assigned",
        "delivery": delivery_record
    }), 200

@app.route('/deliveries/<delivery_id>', methods=['GET'])
def get_delivery(delivery_id):
    delivery = deliveries_db.get(delivery_id)
    if not delivery:
        return jsonify({"status": "FAILED", "message": "Delivery record not found"}), 404
    return jsonify({"status": "SUCCESS", "delivery": delivery}), 200

@app.route('/deliveries', methods=['GET'])
def list_deliveries():
    return jsonify({
        "status": "SUCCESS",
        "count": len(deliveries_db),
        "deliveries": list(deliveries_db.values())
    }), 200

if __name__ == '__main__':
    # Listen on all interfaces on port 5003
    app.run(host='0.0.0.0', port=5003, debug=False)
