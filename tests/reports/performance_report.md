# Performance Benchmarking & Load Test Report

Generated at: 2026-07-12 23:49:40

## 1. Context Engine Pipeline Benchmarks
| Component | Metric / Duration (s) |
| :--- | :--- |
| **Total Pipeline Latency** | 0.2080s |
| Conversation Provider Time | 0.0000s |
| RAG Provider Time | 0.0012s |
| Workspace Provider Time | 0.0000s |
| System Provider Time | 0.0001s |
| **Context Tokens Generated** | 89 tokens |

## 2. Asynchronous Load Testing Benchmarks
- **Simulated Concurrent Users**: 50
- **Total Requests Dispatched**: 200
- **Throughput Rate**: 1213.10 req/s
- **Average Latency**: 0.0282s
- **95th Percentile Latency (P95)**: 0.0352s
- **Maximum Latency**: 0.0508s
- **Error Rate**: 0.00%
