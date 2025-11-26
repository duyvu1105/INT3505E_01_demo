# Week 10 - Logging, Monitoring & Rate Limiting Demo

Demo về cài đặt logging (Winston), monitoring (Prometheus), và rate limiting trong Node.js/Express.

## 📁 Cấu trúc thư mục

```
week10/
├── config/
│   ├── logger.js          # Cấu hình Winston logger
│   └── metrics.js         # Cấu hình Prometheus metrics
├── middleware/
│   └── rateLimiter.js     # Middleware rate limiting
├── logs/                  # Folder chứa log files (tự động tạo)
│   ├── combined.log
│   └── error.log
└── server.js             # Main server file
```

## 🚀 Chạy server

```bash
# Từ thư mục week10
node server.js
```

Server sẽ chạy tại: `http://localhost:3000`

## 📋 Các tính năng

### 1. **Logging với Winston**

- **Log Levels**: debug, info, warn, error
- **Log Format**: JSON với timestamp
- **Log Storage**:
  - `logs/combined.log` - Tất cả logs
  - `logs/error.log` - Chỉ errors
  - Console - Development mode
- **HTTP Request Logging**: Tự động log mọi HTTP request với thông tin:
  - Method, URL, Status code
  - Response time
  - IP address, User agent

**Ví dụ log output:**
```json
{
  "timestamp": "2025-11-26 10:30:15",
  "level": "info",
  "message": "HTTP Request",
  "method": "GET",
  "url": "/api/data",
  "status": 200,
  "duration": "15ms",
  "ip": "::1"
}
```

### 2. **Monitoring với Prometheus**

- **Endpoint**: `GET /metrics`
- **Default Metrics**: CPU, Memory, Event Loop, etc.
- **Custom Metrics**:
  - `week10_api_http_requests_total` - Counter: Tổng số HTTP requests
  - `week10_api_http_request_duration_seconds` - Histogram: Thời gian xử lý request
  - `week10_api_active_requests` - Gauge: Số requests đang xử lý
  - `week10_api_rate_limit_hits_total` - Counter: Số lần hit rate limit

**Xem metrics:**
```bash
curl http://localhost:3000/metrics
```

### 3. **Rate Limiting**

Ba loại rate limiter:

#### a) General Limiter (áp dụng toàn bộ app)
- **Limit**: 100 requests / 15 phút
- **Áp dụng**: Tất cả endpoints (trừ /health, /metrics)

#### b) API Limiter
- **Limit**: 30 requests / 1 phút
- **Áp dụng**: `/api/data`, `/api/users`

#### c) Strict Limiter
- **Limit**: 5 requests / 15 phút
- **Áp dụng**: `/api/auth/login`

**Response khi bị rate limit:**
```json
{
  "error": "Too many requests from this IP, please try again later.",
  "retryAfter": "15 minutes"
}
```

**Headers trả về:**
- `RateLimit-Limit`: Giới hạn tối đa
- `RateLimit-Remaining`: Số requests còn lại
- `RateLimit-Reset`: Thời gian reset

## 🧪 Testing

### 1. Test Health Check
```bash
curl http://localhost:3000/health
```

### 2. Test API với Rate Limiting
```bash
# Gọi nhiều lần để test rate limit
for i in {1..35}; do curl http://localhost:3000/api/data; echo ""; done
```

### 3. Test Login với Strict Rate Limiting
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

Gọi 6 lần liên tiếp sẽ bị rate limit.

### 4. Test Log Levels
```bash
curl http://localhost:3000/api/test/logs
```
Kiểm tra console và file `logs/combined.log`

### 5. Test Error Logging
```bash
curl http://localhost:3000/api/test/error
```
Kiểm tra file `logs/error.log`

### 6. Test Metrics
```bash
curl http://localhost:3000/metrics
```

## 📊 Setup Prometheus & Grafana với Docker

### Cấu trúc folder mới:

```
week10/
├── prometheus/
│   ├── prometheus.yml     # Prometheus config
│   └── alerts.yml         # Alert rules
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/   # Datasource config
│   │   └── dashboards/    # Dashboard provisioning
│   └── dashboards/
│       └── week10-dashboard.json  # Main dashboard
└── docker-compose.yml     # Docker setup
```

### 🚀 Chạy Prometheus + Grafana

**Bước 1: Chạy API server**
```bash
# Từ thư mục week10
node server.js
```

**Bước 2: Start Prometheus & Grafana bằng Docker Compose**
```bash
# Từ thư mục week10
docker-compose up -d
```

**Bước 3: Truy cập các services**
- **API Server**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123`

**Bước 4: Xem metrics trong Prometheus**
- Mở http://localhost:9090
- Vào tab "Graph" và thử các query:
  ```promql
  # Request rate
  rate(week10_api_http_requests_total[1m])
  
  # P95 latency
  histogram_quantile(0.95, sum(rate(week10_api_http_request_duration_seconds_bucket[5m])) by (le))
  
  # Active requests
  week10_api_active_requests
  
  # Error rate
  sum(rate(week10_api_http_requests_total{status_code=~"5.."}[5m])) / sum(rate(week10_api_http_requests_total[5m]))
  ```

**Bước 5: Xem Dashboard trong Grafana**
- Mở http://localhost:3001 và login
- Dashboard "Week 10 - API Monitoring Dashboard" đã được tự động import
- Dashboard bao gồm:
  - Request rate by status code
  - Total request rate (gauge)
  - Active requests (gauge)
  - Error rate 5xx (gauge)
  - P95 latency (gauge)
  - Request latency percentiles (P50, P95, P99)
  - Request rate by route
  - Rate limit hits
  - Memory usage

**Bước 6: Kiểm tra Alerts**
- Vào Prometheus: http://localhost:9090/alerts
- Các alert rules đã được cấu hình:
  - **HighErrorRate**: Error rate > 5% trong 2 phút
  - **HighClientErrorRate**: 4xx rate > 20% trong 5 phút
  - **HighRequestLatency**: P95 > 1s trong 3 phút
  - **VeryHighRequestLatency**: P99 > 2s trong 2 phút
  - **HighRateLimitHits**: Rate limit hits > 0.5/sec
  - **ApplicationDown**: App down > 1 phút
  - **HighMemoryUsage**: Memory > 500MB trong 5 phút
  - **NoRequestsReceived**: Không có request trong 5 phút
  - **HighActiveRequests**: > 50 active requests trong 2 phút
  - **LoginEndpointErrors**: Login errors > 0.1/sec

### 🛑 Stop services

```bash
# Stop Prometheus & Grafana
docker-compose down

# Stop và xóa volumes (data sẽ mất)
docker-compose down -v
```

### 📊 Custom PromQL Queries hữu ích

```promql
# 1. Request rate by route
sum(rate(week10_api_http_requests_total[5m])) by (route)

# 2. Success rate (non-error requests)
sum(rate(week10_api_http_requests_total{status_code!~"5.."}[5m])) / sum(rate(week10_api_http_requests_total[5m]))

# 3. Average response time
rate(week10_api_http_request_duration_seconds_sum[5m]) / rate(week10_api_http_request_duration_seconds_count[5m])

# 4. Request rate by method
sum(rate(week10_api_http_requests_total[1m])) by (method)

# 5. Top 5 slowest routes (P99)
topk(5, histogram_quantile(0.99, sum(rate(week10_api_http_request_duration_seconds_bucket[5m])) by (le, route)))

# 6. Rate limit hits by route
sum(rate(week10_api_rate_limit_hits_total[5m])) by (route)

# 7. Memory usage trend
process_resident_memory_bytes / 1024 / 1024

# 8. CPU usage
rate(process_cpu_seconds_total[5m])
```

### 🔔 Cấu hình Alertmanager (Optional)

Nếu muốn nhận alert qua email/Slack:

1. Uncomment phần `alertmanager` trong `docker-compose.yml`
2. Tạo file `alertmanager/config.yml`:

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Week10 API Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

3. Uncomment phần `alerting` trong `prometheus/prometheus.yml`
4. Restart: `docker-compose down && docker-compose up -d`

## 🔧 Cấu hình

### Environment Variables

```bash
# Log level (debug, info, warn, error)
LOG_LEVEL=info

# Environment
NODE_ENV=development

# Port
PORT=3000
```

### Tùy chỉnh Rate Limit

Sửa file `middleware/rateLimiter.js`:

```javascript
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000,  // Thay đổi thời gian window
  max: 30,                   // Thay đổi số requests tối đa
  // ...
});
```

### Tùy chỉnh Logger

Sửa file `config/logger.js`:

```javascript
const logger = winston.createLogger({
  level: 'debug',  // Thay đổi log level
  // ...
});
```

## 📝 API Endpoints

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/health` | None | Health check |
| GET | `/metrics` | None | Prometheus metrics |
| GET | `/api/data` | 30/min | Get sample data |
| GET | `/api/users` | 30/min | Get sample users |
| POST | `/api/auth/login` | 5/15min | Login (strict) |
| GET | `/api/test/logs` | 100/15min | Test log levels |
| GET | `/api/test/error` | 100/15min | Test error logging |

## 🎯 Best Practices

1. **Logging**:
   - Không log sensitive data (passwords, tokens)
   - Sử dụng đúng log level
   - Thêm context vào logs (request ID, user ID, etc.)
   - Rotate log files để tránh đầy disk

2. **Monitoring**:
   - Track business metrics, không chỉ technical metrics
   - Set up alerts cho các metrics quan trọng
   - Monitor error rates và latency

3. **Rate Limiting**:
   - Khác nhau cho từng endpoint dựa trên mức độ quan trọng
   - Inform users về rate limits trong documentation
   - Consider API keys/authentication cho higher limits
   - Log rate limit violations để phát hiện abuse

## 🐛 Troubleshooting

### Không tạo được log files
- Kiểm tra permissions của folder `logs/`
- Đảm bảo folder tồn tại

### Rate limit không hoạt động
- Kiểm tra thứ tự middleware trong server.js
- Xác nhận IP address được track đúng (có thể cần trust proxy)

### Metrics không hiển thị
- Truy cập `/metrics` để xem raw metrics
- Kiểm tra Prometheus configuration nếu sử dụng

## 📚 Dependencies

Các package đã cài trong `package.json`:
- `express` - Web framework
- `winston` - Logging library
- `prom-client` - Prometheus metrics
- `express-rate-limit` - Rate limiting middleware

## 💡 Mở rộng

Đã implement:
- ✅ Prometheus scraping & metrics collection
- ✅ Grafana dashboard với 9 panels
- ✅ Alert rules (10 alerts cơ bản)
- ✅ Docker Compose setup
- ✅ Rate limiting exempt cho /metrics và /health

Có thể thêm:
- Alertmanager với Slack/Email notifications
- Redis để store rate limit state (distributed systems)
- ELK stack (Elasticsearch, Logstash, Kibana) cho advanced log analysis
- OpenTelemetry tracing để track request flow
- Custom business metrics (orders, revenue, etc.)
- ServiceNow/PagerDuty integration
- Multi-environment monitoring (dev, staging, prod)
