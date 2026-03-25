"""
Скрипт для порівняння продуктивності монолітної та мікросервісної архітектури.
Використання:
  1. Запустити моноліт: docker-compose up -d
  2. python benchmark.py --url http://localhost:5000 --label monolith
  3. Зупинити моноліт, запустити мікросервіси: docker-compose -f docker-compose.micro.yml up -d
  4. python benchmark.py --url http://localhost:8080 --label microservices
"""
import requests
import time
import argparse
import json
from statistics import mean, stdev


def benchmark_endpoint(base_url, method, path, data=None, n=50):
    """Виміряти час відповіді для endpoint."""
    times = []
    url = f"{base_url}{path}"
    for _ in range(n):
        start = time.perf_counter()
        if method == 'GET':
            r = requests.get(url, timeout=10)
        elif method == 'POST':
            r = requests.post(url, json=data, timeout=10)
        elif method == 'DELETE':
            r = requests.delete(url, timeout=10)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        if r.status_code < 400:
            times.append(elapsed)
    return times


def run_benchmark(base_url, label):
    print(f"\n{'='*60}")
    print(f"  Benchmark: {label} ({base_url})")
    print(f"{'='*60}\n")

    results = {}

    # 1. Health check
    times = benchmark_endpoint(base_url, 'GET', '/health', n=100)
    results['health'] = times
    print(f"  GET /health:       avg={mean(times):.1f}ms  std={stdev(times):.1f}ms")

    # 2. Create tasks
    times = benchmark_endpoint(base_url, 'POST', '/api/tasks',
                                data={'title': 'Benchmark task'}, n=50)
    results['create_task'] = times
    print(f"  POST /api/tasks:   avg={mean(times):.1f}ms  std={stdev(times):.1f}ms")

    # 3. Get all tasks
    times = benchmark_endpoint(base_url, 'GET', '/api/tasks', n=50)
    results['get_tasks'] = times
    print(f"  GET /api/tasks:    avg={mean(times):.1f}ms  std={stdev(times):.1f}ms")

    # Summary
    all_times = results['create_task'] + results['get_tasks']
    print(f"\n  Overall API avg:   {mean(all_times):.1f}ms")
    print(f"  Overall API std:   {stdev(all_times):.1f}ms")

    # Save results
    filename = f"benchmark_{label}.json"
    with open(filename, 'w') as f:
        json.dump({k: {'avg': mean(v), 'std': stdev(v), 'min': min(v), 'max': max(v), 'n': len(v)}
                    for k, v in results.items()}, f, indent=2)
    print(f"\n  Results saved to {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Base URL (e.g. http://localhost:5000)')
    parser.add_argument('--label', required=True, help='Label (monolith / microservices)')
    args = parser.parse_args()
    run_benchmark(args.url, args.label)
