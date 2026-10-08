# Cloud Computing Lab Evaluation: Complete Project Report & Demonstration Manual

**Experiment Title:** Build, Deploy and Analyze a Containerized Microservice Application Under Varying Workloads  
**Domain:** Food Delivery Microservices Platform (`QuickBite`)  
**Student Name:** Vinay Sharma  
**Semester:** 5th Semester  
**Evaluation Marks Weightage:** 5 Marks (1 Mark per Checkpoint)  

---

## 📋 Executive Summary & Deliverables Checklist

| Deliverable | Required | Status | File / Location |
| :--- | :---: | :---: | :--- |
| **Source Code of 3 Microservices** | Yes | Completed | `order-service/`, `payment-service/`, `delivery-service/` |
| **Three Dockerfiles** | Yes | Completed | `order-service/Dockerfile`, `payment-service/Dockerfile`, `delivery-service/Dockerfile` |
| **docker-compose.yml** | Yes | Completed | `./docker-compose.yml` |
| **Running Docker Containers** | Yes | Verified | `food_order_service`, `food_payment_service`, `food_delivery_service` |
| **Inter-Service Communication Demo** | Yes | Verified | `test_apis.py` (Composite flow tested and verified) |
| **Workload Test Script & Generator** | Yes | Completed | `workload_benchmark.py` |
| **Performance Observation Table** | Yes | Completed | Measured actual values recorded below & in `results/observation_table.json` |
| **Performance Graphs** | Yes | Generated | `results/graph_*.png` & `results/performance_dashboard.png` |
| **Analysis & Conclusion** | Yes | Completed | Detailed analytical discussion in Section 5 & 6 |

---

## 1. System Architecture & Design

### 1.1 Architecture Flow
```text
                          +-------------------------+
                          |   Client / User Agent   |
                          +------------+------------+
                                       |
                     HTTP POST /orders | (Port 5001)
                                       v
                     +-----------------------------------+
                     |      Service 1: order-service     |
                     |     (Orchestrator & Gateway)      |
                     +---------+---------------+---------+
                               |               |
          HTTP POST /payments/process          | HTTP POST /deliveries/assign
                  (Port 5002)  |               | (Port 5003)
                               v               v
                +----------------------+   +----------------------+
                |      Service 2:      |   |      Service 3:      |
                |   payment-service    |   |   delivery-service   |
                |  (Ledger & Billing)  |   | (Rider & Dispatch)   |
                +----------------------+   +----------------------+
```

### 1.2 Microservice Responsibilities & REST APIs

| Service | Port | Internal Docker URL | Primary Responsibility | Key REST Endpoints |
| :--- | :---: | :--- | :--- | :--- |
| **`order-service`** (Service 1) | `5001` | `http://order-service:5001` | Coordinates order placement, orchestrates payment & delivery verification, consolidates client responses. | • `GET /health`<br>• `POST /orders`<br>• `GET /orders/<id>`<br>• `GET /orders` |
| **`payment-service`** (Service 2) | `5002` | `http://payment-service:5002` | Validates transaction amounts, authorizes digital payments (UPI/Card), maintains transaction ledger. | • `GET /health`<br>• `POST /payments/process`<br>• `GET /payments/<txn_id>`<br>• `GET /payments` |
| **`delivery-service`** (Service 3) | `5003` | `http://delivery-service:5003` | Assigns available delivery rider fleet, computes dynamic ETA, issues live tracking records. | • `GET /health`<br>• `POST /deliveries/assign`<br>• `GET /deliveries/<del_id>`<br>• `GET /deliveries` |

---

## 2. Checkpoint 1: Design and Independent Verification

All three services are built using Python with Flask. Each service can be run standalone and possesses its own REST API endpoints.

### Verification of Independent Services:
- **Payment Service Health:** `GET http://localhost:5002/health`
  ```json
  {"service": "payment-service", "status": "UP", "timestamp": "2026-10-08T18:09:43.338158"}
  ```
- **Independent Payment Execution:** `POST http://localhost:5002/payments/process`
  ```json
  {
    "message": "Payment processed successfully",
    "payment": {
      "amount": 25.5,
      "order_id": "test_ord_101",
      "payment_method": "UPI",
      "status": "SUCCESS",
      "transaction_id": "txn_99bc1dcf64"
    },
    "status": "SUCCESS"
  }
  ```
- **Delivery Service Health:** `GET http://localhost:5003/health`
  ```json
  {"service": "delivery-service", "status": "UP", "timestamp": "2026-10-08T18:09:43.359173"}
  ```
- **Independent Delivery Assignment:** `POST http://localhost:5003/deliveries/assign`
  ```json
  {
    "delivery": {
      "delivery_id": "del_86f29266d9",
      "estimated_time_mins": 31,
      "order_id": "test_ord_101",
      "rider_contact": "+1-555-0102",
      "rider_name": "Sarah Connor",
      "status": "ASSIGNED",
      "vehicle_type": "Motorcycle"
    },
    "message": "Delivery partner successfully assigned",
    "status": "SUCCESS"
  }
  ```

---

## 3. Checkpoint 2: Containerization and Docker Compose Deployment

### 3.1 Dockerfile Structure
Each service contains an isolated, container-ready `Dockerfile` inheriting from the optimized base environment, copying dependencies, setting environment variables, exposing ports, and running the microservice.

### 3.2 Docker Compose Configuration (`docker-compose.yml`)
- Orchestrates all three services.
- Connects them to a shared bridge network: `food-delivery-net`.
- Injects network DNS names via environment variables (`PAYMENT_SERVICE_URL=http://payment-service:5002`, `DELIVERY_SERVICE_URL=http://delivery-service:5003`).
- Handles service dependency graphs (`depends_on`).

### 3.3 Container Runtime Status
Running `docker compose ps` verifies:
```text
NAME                    IMAGE                                   STATUS         PORTS
food_delivery_service   food-delivery-delivery-service:latest   Up             0.0.0.0:5003->5003/tcp
food_order_service      food-delivery-order-service:latest      Up             0.0.0.0:5001->5001/tcp
food_payment_service    food-delivery-payment-service:latest    Up             0.0.0.0:5002->5002/tcp
```

---

## 4. Checkpoint 3: Inter-Service Communication

### Communication Mechanism:
1. Client issues `POST http://localhost:5001/orders`.
2. `order-service` validates the incoming JSON payload and computes the bill total.
3. `order-service` sends an HTTP POST request to `http://payment-service:5002/payments/process` over the Docker bridge network.
4. `payment-service` checks the amount, confirms the transaction, and returns transaction details.
5. `order-service` sends an HTTP POST request to `http://delivery-service:5003/deliveries/assign` over the Docker bridge network.
6. `delivery-service` assigns a rider and calculates ETA.
7. `order-service` consolidates all responses into a single master order object, persists it in memory, and returns HTTP 201 Created to the client.

### End-to-End Test Payload & Response:
**Request:**
```bash
curl -X POST http://localhost:5001/orders \
     -H "Content-Type: application/json" \
     -d '{
       "customer_name": "Vinay Sharma",
       "delivery_address": "Flat 402, Sunshine Towers, Bangalore",
       "items": [
         {"item": "Paneer Butter Masala", "quantity": 1, "price": 12.50},
         {"item": "Garlic Naan", "quantity": 2, "price": 3.50},
         {"item": "Mango Lassi", "quantity": 1, "price": 4.50}
       ],
       "payment_method": "CREDIT_CARD"
     }'
```

**Response (HTTP 201 Created):**
```json
{
  "message": "Food order successfully placed and confirmed",
  "order": {
    "order_id": "ord_4a74d6c1aa",
    "customer_name": "Vinay Sharma",
    "delivery_address": "Flat 402, Sunshine Towers, Bangalore",
    "total_amount": 24.0,
    "order_status": "CONFIRMED",
    "payment_details": {
      "transaction_id": "txn_bbc38f0b10",
      "status": "SUCCESS",
      "amount": 24.0,
      "payment_method": "CREDIT_CARD",
      "processed_at": "2026-10-08T18:09:43.403477"
    },
    "delivery_details": {
      "delivery_id": "del_00f063f601",
      "status": "ASSIGNED",
      "rider_name": "Sarah Connor",
      "rider_contact": "+1-555-0102",
      "vehicle_type": "Motorcycle",
      "estimated_time_mins": 31
    },
    "created_at": "2026-10-08T18:09:43.406667"
  },
  "status": "SUCCESS"
}
```

---

## 5. Checkpoint 4 & 5: Workload Testing, Measured Observations & Graphs

### 5.1 Workload Testing Methodology
- **Target Endpoint:** Composite `POST http://localhost:5001/orders` (exercises all 3 microservices simultaneously).
- **Concurrency Levels:** W1 (1), W2 (2), W3 (4), W4 (8), W5 (16 concurrent threads).
- **Requests per Level:** 120 requests per workload level (600 composite requests total).
- **Monitoring Tool:** Real-time Docker daemon container stats (`docker stats`) across all 3 containers.

### 5.2 Measured Observation Table
*(Actual empirical measurements recorded directly from test execution)*

| Workload | Concurrency | Average Response Time (ms) | Throughput (Requests/sec) | Failed Requests | Total CPU Utilization (%) | Total Memory Utilization (MiB) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **W1** | **1** | **22.85 ms** | **43.66 req/s** | **0** | **5.50 %** | **72.02 MiB** |
| **W2** | **2** | **19.37 ms** | **102.52 req/s** | **0** | **6.09 %** | **72.04 MiB** |
| **W3** | **4** | **17.17 ms** | **225.45 req/s** | **0** | **5.56 %** | **72.29 MiB** |
| **W4** | **8** | **32.79 ms** | **238.60 req/s** | **0** | **5.87 %** | **72.21 MiB** |
| **W5** | **16** | **66.05 ms** | **228.67 req/s** | **0** | **6.24 %** | **72.55 MiB** |

---

## 6. Performance Analysis & Technical Inferences

### 6.1 Impact of Workload on Response Time
1. **Low Concurrency (W1 - W3, 1 to 4 threads):**
   - Response time stays remarkably low, decreasing from **22.85 ms** to an optimal **17.17 ms** at concurrency 4.
   - This occurs because connection keep-alive reuse and multi-core CPU scheduling parallelize the incoming requests without any thread contention.
2. **High Concurrency (W4 - W5, 8 to 16 threads):**
   - Response time increases from **17.17 ms** to **32.79 ms** at concurrency 8, and further surges to **66.05 ms** at concurrency 16.
   - **Reason:** As concurrency exceeds the number of available worker processes/threads, incoming requests enter the OS socket listen queue and await worker thread availability. The serial serialization/deserialization of JSON in Python's GIL also introduces thread queuing delay.

### 6.2 Impact of Workload on Throughput
1. **Linear Scaling Phase (W1 to W3):**
   - Throughput scales almost linearly with concurrency:
     - W1: 43.66 req/s
     - W2: 102.52 req/s
     - W3: 225.45 req/s
2. **Peak Saturation Point (W4):**
   - Peak throughput is reached at **238.60 req/s** at Concurrency 8.
3. **Plateau and Slight Degradation (W5):**
   - At Concurrency 16, throughput plateaus and slightly drops to **228.67 req/s**.
   - **Reason:** The system reaches CPU and I/O saturation. Beyond 8 concurrent requests, the context-switching overhead and network socket contention across the Docker bridge network exceed the marginal benefit of adding more concurrency.

### 6.3 Resource Utilization Breakdown (CPU & Memory)
- **Which microservice consumes the most resources?**
  - **`food_order_service`** consumed the highest CPU and memory among all 3 services (~40% of total CPU and 27.1 MiB memory).
  - **Reason:** `order-service` acts as the orchestrator. For every client request, it performs 2 outbound HTTP requests (`payment` and `delivery`), parses 2 responses, constructs the aggregate JSON, and handles client ingress/egress.
  - In contrast, `food_payment_service` and `food_delivery_service` are leaf nodes handling single focused tasks with minimal compute overhead (~22.0 MiB each).
- **Failure Rate:**
  - `Failed Requests = 0` across all workload levels (100% reliability).

---

## 7. Evaluator Viva Questions & Ready Answers

**Q1: Why did you choose a microservices architecture instead of a monolith for Food Delivery?**  
*Answer:* A food delivery application has varying scaling requirements. For example, order search and tracking experience high read traffic, while payment processing requires strict isolation and PCI compliance. Decoupling into `order`, `payment`, and `delivery` services allows each service to be scaled, deployed, and updated independently without risking system-wide failure.

**Q2: How do the microservices communicate inside Docker?**  
*Answer:* All services reside on a custom Docker bridge network (`food-delivery-net`). Docker provides embedded DNS resolution, so `order-service` can reach the other services directly via their service names (`http://payment-service:5002` and `http://delivery-service:5003`) instead of hardcoded container IP addresses.

**Q3: What happened to application performance when concurrency reached 16?**  
*Answer:* As concurrency increased to 16, throughput plateaued at ~228 req/s while average response time rose to 66 ms. This is due to thread queueing at the HTTP server level and network socket contention across the container bridge network.

**Q4: Which service was the performance bottleneck?**  
*Answer:* `order-service` was the primary bottleneck because it orchestrates the entire workflow synchronously. It must wait for both `payment-service` and `delivery-service` before responding to the client.

**Q5: How would you improve this system in production?**  
*Answer:* 
1. Use asynchronous communication with a message broker like RabbitMQ or Apache Kafka (e.g., publish `OrderCreated` event).
2. Deploy multiple replicas of `order-service` behind an Nginx reverse proxy load balancer (`docker compose up --scale order-service=3`).
3. Implement circuit breakers (e.g. pybreaker) and request caching with Redis.

---

## 8. Exact Step-by-Step Demonstration Commands for the Evaluator

When showing the evaluator your screen, run these exact commands in order:

```powershell
# Step 1: Show running containers (Checkpoint 2)
docker compose ps

# Step 2: Demonstrate independent service endpoints (Checkpoint 1)
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5001/health

# Step 3: Demonstrate inter-service communication (Checkpoint 3)
python test_apis.py

# Step 4: Run workload benchmark (Checkpoint 4)
python workload_benchmark.py

# Step 5: Render and show performance graphs (Checkpoint 5)
python generate_graphs.py
Invoke-Item results\performance_dashboard.png
```
