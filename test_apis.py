import requests
import json
import time

ORDER_URL = "http://localhost:5001"
PAYMENT_URL = "http://localhost:5002"
DELIVERY_URL = "http://localhost:5003"

def print_section(title):
    print("\n" + "="*70)
    print(f" {title} ")
    print("="*70)

def test_independent_services():
    print_section("CHECKPOINT 1 & 2: Testing Microservices Independently")

    # 1. Payment Service
    print("\n[1] Testing Payment Service (/health & /payments/process)...")
    try:
        res = requests.get(f"{PAYMENT_URL}/health", timeout=3)
        print(f"Payment Health Status: {res.status_code} -> {res.json()}")
        
        pay_payload = {"order_id": "test_ord_101", "amount": 25.50, "payment_method": "UPI"}
        res = requests.post(f"{PAYMENT_URL}/payments/process", json=pay_payload, timeout=3)
        print(f"Payment Process Status: {res.status_code}")
        print("Response:", json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"Payment Service test failed: {e}")

    # 2. Delivery Service
    print("\n[2] Testing Delivery Service (/health & /deliveries/assign)...")
    try:
        res = requests.get(f"{DELIVERY_URL}/health", timeout=3)
        print(f"Delivery Health Status: {res.status_code} -> {res.json()}")

        del_payload = {"order_id": "test_ord_101", "delivery_address": "45 Park Avenue, Block C"}
        res = requests.post(f"{DELIVERY_URL}/deliveries/assign", json=del_payload, timeout=3)
        print(f"Delivery Assign Status: {res.status_code}")
        print("Response:", json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"Delivery Service test failed: {e}")

    # 3. Order Service Health
    print("\n[3] Testing Order Service Health (/health)...")
    try:
        res = requests.get(f"{ORDER_URL}/health", timeout=3)
        print(f"Order Service Health Status: {res.status_code} -> {res.json()}")
    except Exception as e:
        print(f"Order Service health test failed: {e}")

def test_end_to_end_communication():
    print_section("CHECKPOINT 3: Testing End-to-End Inter-Service Communication")
    print("Flow: Client -> Order Service -> Payment Service & Delivery Service\n")

    order_payload = {
        "customer_name": "Vinay Sharma",
        "delivery_address": "Flat 402, Sunshine Towers, Bangalore",
        "items": [
            {"item": "Paneer Butter Masala", "quantity": 1, "price": 12.50},
            {"item": "Garlic Naan", "quantity": 2, "price": 3.50},
            {"item": "Mango Lassi", "quantity": 1, "price": 4.50}
        ],
        "payment_method": "CREDIT_CARD"
    }

    try:
        start_time = time.time()
        res = requests.post(f"{ORDER_URL}/orders", json=order_payload, timeout=5)
        elapsed = (time.time() - start_time) * 1000

        print(f"Order Creation HTTP Status: {res.status_code} (took {elapsed:.2f} ms)")
        order_data = res.json()
        print("End-to-End Response Payload:")
        print(json.dumps(order_data, indent=2))

        if res.status_code == 201:
            order_id = order_data["order"]["order_id"]
            print(f"\n[Verification] Fetching Order by ID ({order_id})...")
            get_res = requests.get(f"{ORDER_URL}/orders/{order_id}")
            print(f"Get Order Status: {get_res.status_code}")
            print(f"Order Status: {get_res.json()['order']['order_status']}")
            print(f"Transaction ID: {get_res.json()['order']['payment_details']['transaction_id']}")
            print(f"Assigned Rider: {get_res.json()['order']['delivery_details']['rider_name']}")
            print("\n>>> Checkpoint 3 PASSED: Inter-service communication verified successfully! <<<")
        else:
            print(">>> Order creation failed! Check logs. <<<")

    except Exception as e:
        print(f"End-to-End communication test failed: {e}")

if __name__ == "__main__":
    test_independent_services()
    test_end_to_end_communication()
