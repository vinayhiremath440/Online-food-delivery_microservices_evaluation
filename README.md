# Food Delivery Containerized Microservices Platform

A 3-tier microservice architecture designed, containerized, and benchmarked under varying workloads according to the Cloud Computing Lab Evaluation Manual.

---

## 📌 Architecture Overview

```text
                  +--------------------------------+
                  |         Client / Browser       |
                  +---------------+----------------+
                                  |
               HTTP POST /orders  | (Port 5001)
                                  v
                  +--------------------------------+
                  |         order-service          |
                  |     (Gateway & Orchestrator)   |
                  +-------+----------------+-------+
                          |                |
HTTP POST /payments/process|                | HTTP POST /deliveries/assign
              (Port 5002) |                | (Port 5003)
                          v                v
          +-----------------------+   +-----------------------+
          |    payment-service    |   |   delivery-service    |
          |  (Ledger & Processing)|   |  (Rider & Tracking)   |
          +-----------------------+   +-----------------------+
```

### Microservices Specification:
1. **`order-service` (Port 5001)**:
   - Primary orchestrator and entry point.
   - Accepts order requests, coordinates transaction flow by invoking Payment and Delivery services, and compiles the final order status.
2. **`payment-service` (Port 5002)**:
   - Simulates secure payment processing and authorization.
   - Issues transaction IDs and tracks billing records.
3. **`delivery-service` (Port 5003)**:
   - Manages delivery fleet assignments, vehicle selection, and real-time delivery ETA estimations.

---

## 🚀 Quick Start Guide

### Prerequisites
- Docker Engine & Docker Compose
- Python 3.8+ (for local test & benchmark scripts)
- Python packages: `requests`, `matplotlib`

### 1. Build & Start All Microservices
```bash
docker compose up -d --build
```

### 2. Verify Running Containers
```bash
docker compose ps
```
All three containers (`food_order_service`, `food_payment_service`, `food_delivery_service`) will show `Up`.

---

## 🧪 Checkpoint Demonstrations

### Checkpoint 1: Independent Services & Endpoints
You can test each service independently:

- **Payment Health:**
  ```bash
  curl http://localhost:5002/health
  ```
- **Process Independent Payment:**
  ```bash
  curl -X POST http://localhost:5002/payments/process \
       -H "Content-Type: application/json" \
       -d '{"order_id": "test_1", "amount": 29.99, "payment_method": "UPI"}'
  ```

- **Delivery Health:**
  ```bash
  curl http://localhost:5003/health
  ```
- **Assign Delivery Partner Independently:**
  ```bash
  curl -X POST http://localhost:5003/deliveries/assign \
       -H "Content-Type: application/json" \
       -d '{"order_id": "test_1", "delivery_address": "12 Baker Street"}'
  ```

---

### Checkpoint 2: Docker Containers & Images
- **List Built Images:**
  ```bash
  docker images | grep food-delivery
  ```
- **Inspect Network:**
  ```bash
  docker network inspect cc-evalution_food-delivery-net
  ```

---

### Checkpoint 3: End-to-End Inter-Service Communication
Execute the automated test script:
```bash
python test_apis.py
```
Or test via curl:
```bash
curl -X POST http://localhost:5001/orders \
     -H "Content-Type: application/json" \
     -d '{
       "customer_name": "Vinay Sharma",
       "delivery_address": "45 Park Avenue, Bangalore",
       "items": [{"item": "Biryani", "quantity": 2, "price": 12.0}],
       "payment_method": "CREDIT_CARD"
     }'
```

---

### Checkpoint 4 & 5: Workload Testing, Stats & Graphs
Execute the workload benchmark across 5 concurrency levels (1, 2, 4, 8, 16):
```bash
python workload_benchmark.py
```
This tests:
- **W1 (1 concurrent)**
- **W2 (2 concurrent)**
- **W3 (4 concurrent)**
- **W4 (8 concurrent)**
- **W5 (16 concurrent)**

And collects Docker stats (CPU & Memory) during execution.

To render the publication-ready performance graphs:
```bash
python generate_graphs.py
```
Output charts generated in `results/`:
- `graph_response_time.png`
- `graph_throughput.png`
- `graph_cpu.png`
- `graph_memory.png`
- `performance_dashboard.png`
