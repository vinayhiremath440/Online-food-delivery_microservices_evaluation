from flask import Flask, request, jsonify
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory payments ledger
payments_db = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "service": "payment-service",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/payments/process', methods=['POST'])
def process_payment():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    amount = data.get("amount")
    payment_method = data.get("payment_method", "CREDIT_CARD")

    if not order_id or amount is None:
        return jsonify({
            "status": "FAILED",
            "message": "Missing required fields: order_id and amount"
        }), 400

    if float(amount) <= 0:
        return jsonify({
            "status": "FAILED",
            "message": "Payment amount must be greater than zero"
        }), 400

    # Simulate payment authorization
    transaction_id = f"txn_{uuid.uuid4().hex[:10]}"
    payment_record = {
        "transaction_id": transaction_id,
        "order_id": order_id,
        "amount": float(amount),
        "payment_method": payment_method,
        "status": "SUCCESS",
        "processed_at": datetime.utcnow().isoformat()
    }

    payments_db[transaction_id] = payment_record

    return jsonify({
        "status": "SUCCESS",
        "message": "Payment processed successfully",
        "payment": payment_record
    }), 200

@app.route('/payments/<transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    payment = payments_db.get(transaction_id)
    if not payment:
        return jsonify({"status": "FAILED", "message": "Transaction not found"}), 404
    return jsonify({"status": "SUCCESS", "payment": payment}), 200

@app.route('/payments', methods=['GET'])
def list_payments():
    return jsonify({
        "status": "SUCCESS",
        "count": len(payments_db),
        "payments": list(payments_db.values())
    }), 200

if __name__ == '__main__':
    # Listen on all interfaces on port 5002
    app.run(host='0.0.0.0', port=5002, debug=False)
