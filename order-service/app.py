import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurable Service URLs (defaults to Docker network names, fallback to localhost)
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:5002")
DELIVERY_SERVICE_URL = os.environ.get("DELIVERY_SERVICE_URL", "http://delivery-service:5003")

# In-memory orders database
orders_db = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "service": "order-service",
        "dependencies": {
            "payment_service_url": PAYMENT_SERVICE_URL,
            "delivery_service_url": DELIVERY_SERVICE_URL
        },
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/orders', methods=['POST'])
def create_order():
    """
    End-to-End Orchestration:
    Client -> order-service -> payment-service & delivery-service
    """
    data = request.get_json() or {}

    customer_name = data.get("customer_name", "Anonymous Customer")
    delivery_address = data.get("delivery_address", "123 Main St, Tech City")
    items = data.get("items", [{"item": "Margherita Pizza", "quantity": 1, "price": 14.99}])
    payment_method = data.get("payment_method", "CREDIT_CARD")

    # Compute total amount if not explicitly passed
    total_amount = data.get("total_amount")
    if total_amount is None:
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        if total_amount <= 0:
            total_amount = 19.99

    order_id = f"ord_{uuid.uuid4().hex[:10]}"

    # Step 1: Call Payment Service (Service 2)
    payment_payload = {
        "order_id": order_id,
        "amount": round(total_amount, 2),
        "payment_method": payment_method
    }

    try:
        payment_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payments/process",
            json=payment_payload,
            timeout=5
        )
        if payment_resp.status_code != 200:
            return jsonify({
                "status": "FAILED",
                "message": "Payment processing failed",
                "details": payment_resp.json() if payment_resp.content else {}
            }), 400
        payment_data = payment_resp.json().get("payment", {})
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Unable to reach payment-service at {PAYMENT_SERVICE_URL}",
            "error": str(e)
        }), 503

    # Step 2: Call Delivery Service (Service 3)
    delivery_payload = {
        "order_id": order_id,
        "delivery_address": delivery_address
    }

    try:
        delivery_resp = requests.post(
            f"{DELIVERY_SERVICE_URL}/deliveries/assign",
            json=delivery_payload,
            timeout=5
        )
        if delivery_resp.status_code != 200:
            return jsonify({
                "status": "FAILED",
                "message": "Delivery partner assignment failed",
                "details": delivery_resp.json() if delivery_resp.content else {}
            }), 400
        delivery_data = delivery_resp.json().get("delivery", {})
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Unable to reach delivery-service at {DELIVERY_SERVICE_URL}",
            "error": str(e)
        }), 503

    # Step 3: Consolidate Order Object
    order_record = {
        "order_id": order_id,
        "customer_name": customer_name,
        "delivery_address": delivery_address,
        "items": items,
        "total_amount": round(total_amount, 2),
        "order_status": "CONFIRMED",
        "payment_details": {
            "transaction_id": payment_data.get("transaction_id"),
            "status": payment_data.get("status"),
            "amount": payment_data.get("amount"),
            "payment_method": payment_data.get("payment_method"),
            "processed_at": payment_data.get("processed_at")
        },
        "delivery_details": {
            "delivery_id": delivery_data.get("delivery_id"),
            "status": delivery_data.get("status"),
            "rider_name": delivery_data.get("rider_name"),
            "rider_contact": delivery_data.get("rider_contact"),
            "vehicle_type": delivery_data.get("vehicle_type"),
            "estimated_time_mins": delivery_data.get("estimated_time_mins")
        },
        "created_at": datetime.utcnow().isoformat()
    }

    orders_db[order_id] = order_record

    return jsonify({
        "status": "SUCCESS",
        "message": "Food order successfully placed and confirmed",
        "order": order_record
    }), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    if not order:
        return jsonify({"status": "FAILED", "message": "Order not found"}), 404
    return jsonify({"status": "SUCCESS", "order": order}), 200

@app.route('/orders', methods=['GET'])
def list_orders():
    return jsonify({
        "status": "SUCCESS",
        "count": len(orders_db),
        "orders": list(orders_db.values())
    }), 200

if __name__ == '__main__':
    # Listen on all interfaces on port 5001
    app.run(host='0.0.0.0', port=5001, debug=False)
