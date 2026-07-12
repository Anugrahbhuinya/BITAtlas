"""
Performance benchmarking and load testing script for Phase 11 QA.
"""
from __future__ import annotations

import asyncio
import os
import time
import math
from unittest.mock import AsyncMock, patch

# Configure PYTHONPATH imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.context.orchestrator import ContextOrchestrator
from app.services.llm.intent_router import RoutingDecision

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


async def benchmark_context_pipeline():
    """Measures component-level latency and token usage inside the context engine."""
    print("Benchmarking Context Engine Pipeline...")
    orchestrator = ContextOrchestrator()
    
    decision = RoutingDecision(
        intent="Campus Information",
        primary_service="Hybrid RAG",
        fallback_service="Gemini",
        confidence=1.0,
        reason="Performance test",
        requires_rag=True,
        requires_gemini=False,
        requires_navigation=False,
        requires_workspace=False,
        requires_conversation_memory=True
    )

    student = {
        "_id": "student_test_id",
        "name": "Test Student",
        "department": "Computer Science",
        "semester": 6,
        "program": "B.Tech",
        "roll_number": "BTECH/99999/23"
    }

    mock_rag_result = {
        "documents": ["BIT Mesra was established in 1955. It is located in Ranchi, Jharkhand."],
        "confidence": 0.95,
        "source": "handbook",
        "rejected_documents": []
    }

    with patch("app.services.rag.rag_service.query_rag", return_value=mock_rag_result), \
         patch("app.services.history_service.get_chat_history", new_callable=AsyncMock) as mock_history:
        
        mock_history.return_value = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"}
        ]

        t0 = time.time()
        prompt_ctx, diagnostics, package = await orchestrator.build_context(
            query="tell me about bit",
            routing_decision=decision,
            session_id="perf_session",
            current_student=student
        )
        elapsed = time.time() - t0

    # Extract component times
    stages = {}
    for pd in diagnostics.provider_diagnostics:
        stages[pd.provider_id] = pd.execution_time_s

    stages["total_pipeline_time"] = elapsed
    stages["token_count"] = package.total_tokens
    
    print(f"[OK] Context pipeline benchmark completed in {elapsed:.4f}s.")
    return stages


async def simulate_user_request(orchestrator, decision, student, request_idx: int) -> float:
    """Simulates a single async request and returns its latency."""
    mock_rag_result = {
        "documents": [f"Chroma Document chunk reference {request_idx}"],
        "confidence": 0.9,
        "source": "rag",
        "rejected_documents": []
    }

    with patch("app.services.rag.rag_service.query_rag", return_value=mock_rag_result), \
         patch("app.services.history_service.get_chat_history", new_callable=AsyncMock) as mock_history:
        
        mock_history.return_value = [{"role": "user", "content": "test query"}]

        t0 = time.time()
        await orchestrator.build_context(
            query="tell me about mess timings",
            routing_decision=decision,
            session_id=f"session_{request_idx}",
            current_student=student
        )
        return time.time() - t0


async def run_load_test(concurrent_users: int = 50, total_requests: int = 200):
    """Simulates multiple concurrent users to measure concurrency throughput and latencies."""
    print(f"Running Load Test: {concurrent_users} concurrent users, {total_requests} total requests...")
    
    orchestrator = ContextOrchestrator()
    decision = RoutingDecision(
        intent="Campus Information",
        primary_service="Hybrid RAG",
        fallback_service="Gemini",
        confidence=1.0,
        reason="Load test",
        requires_rag=True,
        requires_gemini=False,
        requires_navigation=False,
        requires_workspace=False,
        requires_conversation_memory=True
    )

    student = {
        "_id": "student_test_id",
        "name": "Test Student"
    }

    latencies = []
    sem = asyncio.Semaphore(concurrent_users)

    async def worker(idx):
        async with sem:
            try:
                lat = await simulate_user_request(orchestrator, decision, student, idx)
                latencies.append(lat)
            except Exception as e:
                print(f"Request {idx} failed: {e}")

    t0 = time.time()
    await asyncio.gather(*(worker(i) for i in range(total_requests)))
    total_time = time.time() - t0

    if not latencies:
        return {}

    latencies.sort()
    avg_lat = sum(latencies) / len(latencies)
    p95_lat = latencies[int(len(latencies) * 0.95)]
    max_lat = max(latencies)
    throughput = len(latencies) / total_time

    print(f"[OK] Load test completed. Avg Latency: {avg_lat:.4f}s, p95: {p95_lat:.4f}s, Throughput: {throughput:.2f} req/s")

    return {
        "concurrent_users": concurrent_users,
        "total_requests": total_requests,
        "total_duration_s": total_time,
        "avg_latency_s": avg_lat,
        "p95_latency_s": p95_lat,
        "max_latency_s": max_lat,
        "throughput_req_s": throughput,
        "error_rate_pct": ((total_requests - len(latencies)) / total_requests) * 100
    }


async def main():
    stages = await benchmark_context_pipeline()
    load_metrics = await run_load_test()

    # Generate Performance Benchmark Report
    report_path = os.path.join(REPORTS_DIR, "performance_report.md")
    with open(report_path, "w") as f:
        f.write("# Performance Benchmarking & Load Test Report\n\n")
        f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 1. Context Engine Pipeline Benchmarks\n")
        f.write("| Component | Metric / Duration (s) |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| **Total Pipeline Latency** | {stages.get('total_pipeline_time', 0.0):.4f}s |\n")
        f.write(f"| Conversation Provider Time | {stages.get('conversation', 0.0):.4f}s |\n")
        f.write(f"| RAG Provider Time | {stages.get('rag', 0.0):.4f}s |\n")
        f.write(f"| Workspace Provider Time | {stages.get('workspace', 0.0):.4f}s |\n")
        f.write(f"| System Provider Time | {stages.get('system', 0.0):.4f}s |\n")
        f.write(f"| **Context Tokens Generated** | {stages.get('token_count', 0)} tokens |\n\n")

        f.write("## 2. Asynchronous Load Testing Benchmarks\n")
        f.write(f"- **Simulated Concurrent Users**: {load_metrics.get('concurrent_users', 0)}\n")
        f.write(f"- **Total Requests Dispatched**: {load_metrics.get('total_requests', 0)}\n")
        f.write(f"- **Throughput Rate**: {load_metrics.get('throughput_req_s', 0.0):.2f} req/s\n")
        f.write(f"- **Average Latency**: {load_metrics.get('avg_latency_s', 0.0):.4f}s\n")
        f.write(f"- **95th Percentile Latency (P95)**: {load_metrics.get('p95_latency_s', 0.0):.4f}s\n")
        f.write(f"- **Maximum Latency**: {load_metrics.get('max_latency_s', 0.0):.4f}s\n")
        f.write(f"- **Error Rate**: {load_metrics.get('error_rate_pct', 0.0):.2f}%\n")

    print(f"Performance report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
