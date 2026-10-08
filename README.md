# Food Delivery Microservices (CC Lab Experiment)

Cloud Computing Lab evaluation project containing 3 independent microservices containerized with Docker and deployed using Docker Compose.

## Architecture
- **Order Service** (`port 5001`): Accepts orders from client, calls payment and delivery services.
- **Payment Service** (`port 5002`): Processes payments and returns status.
- **Delivery Service** (`port 5003`): Assigns delivery rider and ETA.

Communication flow: `Client -> Order Service -> Payment Service / Delivery Service`

## How to Run

1. Build and start containers:
```bash
docker compose up -d
```

2. Run testing and workload benchmarks (W1 to W5):
```bash
python test.py
```

## Workload Observation Table

| Workload | Concurrency | Avg Latency (ms) | Throughput (req/s) |
|---|---|---|---|
| W1 | 1 | 8.99 ms | 110.80 req/s |
| W2 | 2 | 12.07 ms | 164.97 req/s |
| W3 | 4 | 17.11 ms | 228.59 req/s |
| W4 | 8 | 32.82 ms | 232.61 req/s |
| W5 | 16 | 59.97 ms | 236.14 req/s |

Graph is saved in `results/performance_graph.png`.

## Stop containers
```bash
docker compose down
```
