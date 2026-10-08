import requests
import time
from concurrent.futures import ThreadPoolExecutor

ORDER_URL = "http://localhost:5001"
PAYMENT_URL = "http://localhost:5002"
DELIVERY_URL = "http://localhost:5003"

def test_services():
    print("--- 1. Testing Services ---")
    try:
        print("Payment Health:", requests.get(f"{PAYMENT_URL}/health").json()["status"])
        print("Delivery Health:", requests.get(f"{DELIVERY_URL}/health").json()["status"])
        print("Order Health:", requests.get(f"{ORDER_URL}/health").json()["status"])
    except Exception as e:
        print("Error checking services:", e)
        return False
    return True

def place_order():
    print("\n--- 2. Placing an End-to-End Order ---")
    payload = {
        "customer_name": "Vinay",
        "delivery_address": "Hostel Block B, Room 204",
        "items": [{"item": "Pizza", "quantity": 1, "price": 15.0}],
        "payment_method": "UPI"
    }
    res = requests.post(f"{ORDER_URL}/orders", json=payload)
    if res.status_code == 201:
        data = res.json()["order"]
        print("Order Placed Successfully!")
        print("Order ID:", data["order_id"])
        print("Payment Status:", data["payment_details"]["status"])
        print("Rider Assigned:", data["delivery_details"]["rider_name"])
    else:
        print("Failed to place order:", res.text)

def run_workload():
    print("\n--- 3. Running Workload Testing (W1 to W5) ---")
    concurrency_levels = [1, 2, 4, 8, 16]
    total_reqs = 50

    print(f"{'Workload':<10}{'Concurrency':<14}{'Avg Latency (ms)':<20}{'Throughput (req/s)':<20}")
    print("-" * 64)

    for i, c in enumerate(concurrency_levels, start=1):
        def send_req(_):
            t0 = time.time()
            requests.post(f"{ORDER_URL}/orders", json={"customer_name": "Test", "items": [{"item": "Burger", "price": 10}]})
            return (time.time() - t0) * 1000

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=c) as ex:
            latencies = list(ex.map(send_req, range(total_reqs)))
        total_time = time.time() - start_time

        avg_lat = sum(latencies) / len(latencies)
        throughput = total_reqs / total_time

        print(f"W{i:<9}{c:<14}{avg_lat:<20.2f}{throughput:<20.2f}")

if __name__ == "__main__":
    if test_services():
        place_order()
        run_workload()
