import os
import sys
import time

# Ensure backend directory is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app

CATEGORIES = {
    "Greeting / Simple": {
        "query": "Hello, who are you?",
        "target": 2.0
    },
    "Navigation": {
        "query": "Where is the Central Library?",
        "target": 3.0
    },
    "Student Dashboard": {
        "query": "What is my CGPA?",
        "target": 4.0
    },
    "RAG Question": {
        "query": "Tell me about Aryabhatta Hostel messing rules.",
        "target": 5.0
    },
    "Complex AI": {
        "query": "Compare Aryabhatta Hostel and Raman Hostel mess fees, facilities, and rules.",
        "target": 8.0
    }
}

def get_mean(lst):
    return sum(lst) / len(lst)

def get_percentile(lst, q):
    s = sorted(lst)
    idx = (len(s) - 1) * (q / 100.0)
    floor_idx = int(idx)
    ceil_idx = floor_idx + 1
    if ceil_idx < len(s):
        return s[floor_idx] + (idx - floor_idx) * (s[ceil_idx] - s[floor_idx])
    return s[floor_idx]

def run_benchmark():
    print("=" * 80)
    print("RUNNING PIPELINE PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    results = {}
    session_id = "benchmark-session-123"
    
    for cat_name, info in CATEGORIES.items():
        query = info["query"]
        target = info["target"]
        
        print(f"\nBenchmarking Category: {cat_name}")
        print(f"Query: '{query}'")
        print(f"Target: < {target}s")
        
        latencies = []
        diagnostics_list = []
        
        # Warm up once
        try:
            with TestClient(app) as client:
                client.post("/chat", json={"message": query, "sessionId": session_id})
        except Exception:
            pass
            
        for i in range(3):
            t0 = time.time()
            try:
                # Use "with" statement to cleanly initialize and destroy the TestClient/event loop context
                with TestClient(app) as client:
                    response = client.post("/chat", json={"message": query, "sessionId": session_id})
                    latency = time.time() - t0
                    latencies.append(latency)
                    
                    if response.status_code == 200:
                        data = response.json()
                        diag = data.get("diagnostics")
                        if diag:
                            diagnostics_list.append(diag)
                    else:
                        print(f"  Iteration {i+1} failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"  Iteration {i+1} error: {e}")
                
        if not latencies:
            print(f"Category {cat_name} failed entirely.")
            continue
            
        avg_lat = get_mean(latencies)
        p95_lat = get_percentile(latencies, 95)
        max_lat = max(latencies)
        
        # Find slowest stage if diagnostics are available
        slowest_stage = "N/A"
        slowest_time = 0.0
        if diagnostics_list:
            stages_avg = {}
            for diag in diagnostics_list:
                stages = diag.get("stages", {})
                for stage_name, stage_val in stages.items():
                    stages_avg[stage_name] = stages_avg.get(stage_name, 0.0) + stage_val
            
            for stage_name in stages_avg:
                stages_avg[stage_name] /= len(diagnostics_list)
                if stages_avg[stage_name] > slowest_time:
                    slowest_time = stages_avg[stage_name]
                    slowest_stage = stage_name.replace("_time_seconds", "").replace("_seconds", "")
                    
        status = "PASS" if p95_lat < target else "FAIL"
        
        results[cat_name] = {
            "avg": avg_lat,
            "p95": p95_lat,
            "max": max_lat,
            "slowest_stage": f"{slowest_stage} ({slowest_time:.4f}s)",
            "status": status,
            "target": target
        }
        
        print(f"  Avg Latency: {avg_lat:.4f}s")
        print(f"  P95 Latency: {p95_lat:.4f}s")
        print(f"  Slowest Stage: {slowest_stage} ({slowest_time:.4f}s)")
        print(f"  Status: {status}")
        
    print("\n" + "=" * 95)
    print(f"{'Category':<25} | {'P95 Lat (s)':<12} | {'Avg Lat (s)':<12} | {'Target (s)':<10} | {'Slowest Stage':<20} | {'Status':<6}")
    print("-" * 95)
    for cat_name, res in results.items():
        print(f"{cat_name:<25} | {res['p95']:<12.4f} | {res['avg']:<12.4f} | {res['target']:<10.1f} | {res['slowest_stage']:<20} | {res['status']:<6}")
    print("=" * 95)
    
    # Calculate overall metrics
    all_p95s = [res["p95"] for res in results.values()]
    all_avgs = [res["avg"] for res in results.values()]
    overall_avg = get_mean(all_avgs)
    overall_p95 = get_percentile(all_p95s, 95)
    
    print(f"\nOverall Average Response Time: {overall_avg:.4f}s")
    print(f"Overall P95 Response Time:     {overall_p95:.4f}s")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
