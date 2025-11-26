# Prometheus Monitoring - Quick Start Guide

## 🚀 Khởi động nhanh (3 bước)

### 1. Chạy API
```bash
cd week10
node server.js
```

### 2. Chạy Prometheus + Grafana
```bash
docker-compose up -d
```

### 3. Truy cập
- **API**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin123)

---

## 📊 Metrics đã implement

### Default Metrics (từ prom-client)
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage
- `nodejs_eventloop_lag_seconds` - Event loop lag
- `nodejs_heap_size_total_bytes` - Heap size
- `nodejs_gc_duration_seconds` - GC duration

### Custom Metrics

#### 1. HTTP Request Counter
```
week10_api_http_requests_total{method="GET", route="/api/data", status_code="200"}
```
Đếm tổng số requests theo method, route và status code.

#### 2. Request Duration Histogram
```
week10_api_http_request_duration_seconds_bucket{method="GET", route="/api/data", status_code="200", le="0.1"}
```
Đo thời gian xử lý request (buckets: 1ms → 5s).

#### 3. Active Requests Gauge
```
week10_api_active_requests
```
Số request đang được xử lý tại thời điểm hiện tại.

#### 4. Rate Limit Hits Counter
```
week10_api_rate_limit_hits_total{route="/api/auth/login"}
```
Đếm số lần bị rate limit theo route.

---

## 📈 PromQL Queries thường dùng

### Request Rate
```promql
# Request per second (RPS)
rate(week10_api_http_requests_total[1m])

# RPS by route
sum(rate(week10_api_http_requests_total[1m])) by (route)

# RPS by status code
sum(rate(week10_api_http_requests_total[1m])) by (status_code)
```

### Latency
```promql
# P50 (median)
histogram_quantile(0.50, sum(rate(week10_api_http_request_duration_seconds_bucket[5m])) by (le))

# P95
histogram_quantile(0.95, sum(rate(week10_api_http_request_duration_seconds_bucket[5m])) by (le))

# P99
histogram_quantile(0.99, sum(rate(week10_api_http_request_duration_seconds_bucket[5m])) by (le))

# Average latency
rate(week10_api_http_request_duration_seconds_sum[5m]) / rate(week10_api_http_request_duration_seconds_count[5m])
```

### Error Rate
```promql
# 5xx error rate
sum(rate(week10_api_http_requests_total{status_code=~"5.."}[5m])) 
/ 
sum(rate(week10_api_http_requests_total[5m]))

# 4xx error rate
sum(rate(week10_api_http_requests_total{status_code=~"4.."}[5m])) 
/ 
sum(rate(week10_api_http_requests_total[5m]))

# Success rate (2xx và 3xx)
sum(rate(week10_api_http_requests_total{status_code=~"[23].."}[5m])) 
/ 
sum(rate(week10_api_http_requests_total[5m]))
```

### Rate Limiting
```promql
# Rate limit hits per second
rate(week10_api_rate_limit_hits_total[1m])

# Total rate limit hits
sum(increase(week10_api_rate_limit_hits_total[1h]))
```

### Resource Usage
```promql
# Memory in MB
process_resident_memory_bytes / 1024 / 1024

# CPU usage
rate(process_cpu_seconds_total[5m]) * 100
```

### Active Requests
```promql
# Current active requests
week10_api_active_requests

# Max active requests in last 5 minutes
max_over_time(week10_api_active_requests[5m])
```

---

## 🔔 Alert Rules

### Critical Alerts
- **HighErrorRate**: Error rate > 5% trong 2 phút
- **VeryHighRequestLatency**: P99 > 2s trong 2 phút
- **ApplicationDown**: App down > 1 phút

### Warning Alerts
- **HighClientErrorRate**: 4xx rate > 20% trong 5 phút
- **HighRequestLatency**: P95 > 1s trong 3 phút
- **HighRateLimitHits**: Rate limit hits > 0.5/sec
- **HighMemoryUsage**: Memory > 500MB trong 5 phút
- **NoRequestsReceived**: Không có request trong 5 phút
- **HighActiveRequests**: > 50 active requests trong 2 phút
- **LoginEndpointErrors**: Login errors > 0.1/sec

---

## 🎯 Testing Metrics

### 1. Generate traffic
```bash
# Normal requests
for /L %i in (1,1,100) do @curl http://localhost:3000/api/data

# Trigger rate limit
for /L %i in (1,1,35) do @curl http://localhost:3000/api/data

# Generate errors
curl http://localhost:3000/api/test/error
```

### 2. View raw metrics
```bash
curl http://localhost:3000/metrics
```

### 3. Check in Prometheus
- Mở http://localhost:9090/graph
- Paste query và click "Execute"

### 4. View in Grafana Dashboard
- Mở http://localhost:3001
- Dashboard auto-refresh mỗi 5 giây

---

## 🛠️ Troubleshooting

### Prometheus không scrape được metrics
1. Kiểm tra app đang chạy: `curl http://localhost:3000/health`
2. Kiểm tra metrics endpoint: `curl http://localhost:3000/metrics`
3. Xem Prometheus targets: http://localhost:9090/targets
4. Nếu target DOWN, kiểm tra `docker-compose.yml` có dùng `host.docker.internal` cho Windows/Mac

### Grafana không hiển thị data
1. Kiểm tra Prometheus datasource: Configuration → Data Sources
2. Click "Test" để kiểm tra connection
3. Kiểm tra time range trong dashboard (góc phải trên)
4. Query trực tiếp trong Prometheus trước để đảm bảo có data

### Alerts không firing
1. Vào Prometheus: http://localhost:9090/alerts
2. Kiểm tra alert rules có được load không
3. Generate traffic để trigger alerts
4. Wait for evaluation interval (30s)

---

## 📚 Best Practices

### Metrics Design
- ✅ Dùng Counter cho events tăng dần (requests, errors)
- ✅ Dùng Gauge cho giá trị hiện tại (active requests, memory)
- ✅ Dùng Histogram cho latency/duration
- ✅ Giữ cardinality thấp (tránh dùng userId làm label)
- ❌ Không dùng timestamps trong metric names
- ❌ Không tạo quá nhiều labels

### Query Optimization
- Dùng `rate()` cho Counter thay vì `increase()` nếu muốn per-second
- Dùng `irate()` cho spike detection (2 samples gần nhất)
- Aggregate trước khi tính histogram_quantile
- Dùng recording rules cho queries phức tạp chạy thường xuyên

### Alert Rules
- Set threshold dựa trên baseline và business requirements
- Dùng `for` clause để tránh flapping alerts
- Group alerts theo severity (critical, warning, info)
- Include helpful annotations (runbook, dashboard links)

### Dashboard Design
- Top row: Key metrics (RPS, latency, error rate, saturation)
- Use gauges cho instant values
- Use time series cho trends
- Add legends với calculations (mean, max, current)
- Set appropriate time ranges và refresh intervals

---

## 📖 Tham khảo

- [Prometheus Query Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [PromQL Functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
