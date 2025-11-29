"""Traffic generator for testing SecuraFlow."""
import requests
import time
import random
from datetime import datetime
from typing import List

API_URL = "http://localhost:8000/api/traffic"

# Sample endpoints
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/auth/login",
    "/api/auth/register",
    "/api/cart",
    "/api/checkout",
    "/api/payments",
]

METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES_NORMAL = [200, 201, 204]
STATUS_CODES_ERROR = [400, 401, 403, 404, 500, 502, 503]


def generate_traffic_data() -> dict:
    """Generate a single traffic data point."""
    endpoint = random.choice(ENDPOINTS)
    method = random.choice(METHODS)
    
    # 90% normal traffic, 10% errors
    is_error = random.random() < 0.1
    
    if is_error:
        status_code = random.choice(STATUS_CODES_ERROR)
        response_time = random.randint(100, 5000)  # Slower for errors
    else:
        status_code = random.choice(STATUS_CODES_NORMAL)
        response_time = random.randint(20, 200)  # Normal response time
    
    return {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time_ms": response_time,
        "request_size_bytes": random.randint(100, 5000),
        "response_size_bytes": random.randint(500, 10000),
        "ip_address": f"192.168.1.{random.randint(1, 255)}",
        "user_agent": "TrafficGenerator/1.0",
        "timestamp": datetime.now().isoformat(),
    }


def generate_anomaly_traffic() -> dict:
    """Generate anomalous traffic data."""
    endpoint = random.choice(ENDPOINTS)
    
    anomaly_type = random.choice(["slow", "error", "large"])
    
    if anomaly_type == "slow":
        return {
            "endpoint": endpoint,
            "method": "GET",
            "status_code": 200,
            "response_time_ms": random.randint(2000, 10000),  # Very slow
            "request_size_bytes": random.randint(100, 1000),
            "response_size_bytes": random.randint(500, 5000),
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "user_agent": "TrafficGenerator/1.0",
            "timestamp": datetime.now().isoformat(),
        }
    elif anomaly_type == "error":
        return {
            "endpoint": endpoint,
            "method": random.choice(["GET", "POST"]),
            "status_code": random.choice([500, 502, 503]),
            "response_time_ms": random.randint(500, 2000),
            "request_size_bytes": random.randint(100, 1000),
            "response_size_bytes": random.randint(100, 500),
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "user_agent": "TrafficGenerator/1.0",
            "timestamp": datetime.now().isoformat(),
        }
    else:  # large
        return {
            "endpoint": endpoint,
            "method": "POST",
            "status_code": 200,
            "response_time_ms": random.randint(100, 500),
            "request_size_bytes": random.randint(1000000, 10000000),  # Very large
            "response_size_bytes": random.randint(5000000, 20000000),
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "user_agent": "TrafficGenerator/1.0",
            "timestamp": datetime.now().isoformat(),
        }


def send_traffic(requests_per_second: int = 10, duration_seconds: int = 60, anomaly_rate: float = 0.05):
    """
    Generate and send traffic to the API.
    
    Args:
        requests_per_second: Number of requests per second
        duration_seconds: How long to generate traffic
        anomaly_rate: Percentage of requests that should be anomalies (0.0 to 1.0)
    """
    print(f"Starting traffic generation...")
    print(f"Rate: {requests_per_second} req/s")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Anomaly rate: {anomaly_rate * 100}%")
    print("-" * 50)
    
    start_time = time.time()
    request_count = 0
    error_count = 0
    
    try:
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Send a batch of requests
            for _ in range(requests_per_second):
                try:
                    # Generate anomaly or normal traffic
                    if random.random() < anomaly_rate:
                        data = generate_anomaly_traffic()
                    else:
                        data = generate_traffic_data()
                    
                    response = requests.post(API_URL, json=data, timeout=5)
                    request_count += 1
                    
                    if response.status_code != 200:
                        error_count += 1
                        print(f"Error: {response.status_code} - {response.text}")
                    
                    if response.json().get("anomaly_detected"):
                        print(f"⚠️  Anomaly detected! Score: {response.json().get('anomaly_score', 0):.2f}")
                
                except requests.exceptions.RequestException as e:
                    error_count += 1
                    print(f"Request error: {e}")
            
            # Sleep to maintain rate
            elapsed = time.time() - batch_start
            sleep_time = max(0, 1.0 - elapsed)
            time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\nTraffic generation stopped by user")
    
    finally:
        total_time = time.time() - start_time
        print("-" * 50)
        print(f"Traffic generation complete!")
        print(f"Total requests: {request_count}")
        print(f"Errors: {error_count}")
        print(f"Duration: {total_time:.2f} seconds")
        print(f"Average rate: {request_count / total_time:.2f} req/s")


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    rps = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    anomaly_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
    
    send_traffic(requests_per_second=rps, duration_seconds=duration, anomaly_rate=anomaly_rate)

