import json
import os
import matplotlib.pyplot as plt

def generate_performance_graphs():
    data_file = os.path.join("results", "observation_table.json")
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found. Run workload_benchmark.py first.")
        return

    with open(data_file, "r") as f:
        data = json.load(f)

    concurrency = [d["concurrency"] for d in data]
    workloads = [d["workload"] for d in data]
    response_times = [d["avg_response_time_ms"] for d in data]
    throughputs = [d["throughput_req_per_sec"] for d in data]
    cpu_usages = [d["avg_cpu_percent"] for d in data]
    mem_usages = [d["avg_memory_mib"] for d in data]

    # Styling settings
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Graph: Concurrency vs Response Time
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(concurrency, response_times, marker='o', color='#d9534f', linewidth=2.5, markersize=8)
    for x, y in zip(concurrency, response_times):
        ax.annotate(f"{y:.1f} ms", (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
    ax.set_title("Concurrent Requests vs Average Response Time", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Concurrent Requests (Concurrency Level)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Average Response Time (ms)", fontsize=11, fontweight='bold')
    ax.set_xticks(concurrency)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("results/graph_response_time.png", dpi=300)
    plt.close()
    print("Generated: results/graph_response_time.png")

    # 2. Graph: Concurrency vs Throughput
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(concurrency, throughputs, marker='s', color='#0275d8', linewidth=2.5, markersize=8)
    for x, y in zip(concurrency, throughputs):
        ax.annotate(f"{y:.1f} req/s", (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
    ax.set_title("Concurrent Requests vs Throughput", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Concurrent Requests (Concurrency Level)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Throughput (Requests / Second)", fontsize=11, fontweight='bold')
    ax.set_xticks(concurrency)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("results/graph_throughput.png", dpi=300)
    plt.close()
    print("Generated: results/graph_throughput.png")

    # 3. Graph: Concurrency vs CPU Utilization
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(concurrency, cpu_usages, marker='^', color='#f0ad4e', linewidth=2.5, markersize=8)
    for x, y in zip(concurrency, cpu_usages):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
    ax.set_title("Concurrent Requests vs CPU Utilization", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Concurrent Requests (Concurrency Level)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Total CPU Utilization (%)", fontsize=11, fontweight='bold')
    ax.set_xticks(concurrency)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("results/graph_cpu.png", dpi=300)
    plt.close()
    print("Generated: results/graph_cpu.png")

    # 4. Graph: Concurrency vs Memory Utilization
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(concurrency, mem_usages, marker='D', color='#5cb85c', linewidth=2.5, markersize=8)
    for x, y in zip(concurrency, mem_usages):
        ax.annotate(f"{y:.1f} MB", (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
    ax.set_title("Concurrent Requests vs Memory Utilization", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Concurrent Requests (Concurrency Level)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Total Memory Utilization (MiB)", fontsize=11, fontweight='bold')
    ax.set_xticks(concurrency)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("results/graph_memory.png", dpi=300)
    plt.close()
    print("Generated: results/graph_memory.png")

    # 5. Combined Performance Dashboard (2x2 Grid)
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Food Delivery Microservices - Workload & Resource Performance Dashboard", fontsize=16, fontweight='bold', y=0.98)

    # Subplot (0,0) - Response Time
    axs[0, 0].plot(concurrency, response_times, marker='o', color='#d9534f', linewidth=2)
    for x, y in zip(concurrency, response_times):
        axs[0, 0].annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=9)
    axs[0, 0].set_title("Response Time vs Concurrency", fontsize=12, fontweight='bold')
    axs[0, 0].set_xlabel("Concurrency", fontsize=10)
    axs[0, 0].set_ylabel("Response Time (ms)", fontsize=10)
    axs[0, 0].set_xticks(concurrency)
    axs[0, 0].grid(True, linestyle='--', alpha=0.6)

    # Subplot (0,1) - Throughput
    axs[0, 1].plot(concurrency, throughputs, marker='s', color='#0275d8', linewidth=2)
    for x, y in zip(concurrency, throughputs):
        axs[0, 1].annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=9)
    axs[0, 1].set_title("Throughput vs Concurrency", fontsize=12, fontweight='bold')
    axs[0, 1].set_xlabel("Concurrency", fontsize=10)
    axs[0, 1].set_ylabel("Throughput (req/sec)", fontsize=10)
    axs[0, 1].set_xticks(concurrency)
    axs[0, 1].grid(True, linestyle='--', alpha=0.6)

    # Subplot (1,0) - CPU
    axs[1, 0].plot(concurrency, cpu_usages, marker='^', color='#f0ad4e', linewidth=2)
    for x, y in zip(concurrency, cpu_usages):
        axs[1, 0].annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=9)
    axs[1, 0].set_title("CPU Utilization vs Concurrency", fontsize=12, fontweight='bold')
    axs[1, 0].set_xlabel("Concurrency", fontsize=10)
    axs[1, 0].set_ylabel("CPU Usage (%)", fontsize=10)
    axs[1, 0].set_xticks(concurrency)
    axs[1, 0].grid(True, linestyle='--', alpha=0.6)

    # Subplot (1,1) - Memory
    axs[1, 1].plot(concurrency, mem_usages, marker='D', color='#5cb85c', linewidth=2)
    for x, y in zip(concurrency, mem_usages):
        axs[1, 1].annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=9)
    axs[1, 1].set_title("Memory Utilization vs Concurrency", fontsize=12, fontweight='bold')
    axs[1, 1].set_xlabel("Concurrency", fontsize=10)
    axs[1, 1].set_ylabel("Memory (MiB)", fontsize=10)
    axs[1, 1].set_xticks(concurrency)
    axs[1, 1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("results/performance_dashboard.png", dpi=300)
    plt.close()
    print("Generated: results/performance_dashboard.png")

if __name__ == "__main__":
    generate_performance_graphs()
