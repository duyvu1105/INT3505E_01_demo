const client = require('prom-client');

// Tạo Registry để chứa các metrics
const register = new client.Registry();

// Thêm default metrics (CPU, Memory, etc.)
client.collectDefaultMetrics({ 
  register,
  prefix: 'week10_api_'
});

// Custom metrics
// 1. Counter - đếm số lượng HTTP requests
const httpRequestCounter = new client.Counter({
  name: 'week10_api_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

// 2. Histogram - đo thời gian xử lý request
const httpRequestDuration = new client.Histogram({
  name: 'week10_api_http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  registers: [register]
});

// 3. Gauge - số lượng requests đang xử lý
const activeRequests = new client.Gauge({
  name: 'week10_api_active_requests',
  help: 'Number of requests currently being processed',
  registers: [register]
});

// 4. Counter - đếm số lượng rate limit hits
const rateLimitCounter = new client.Counter({
  name: 'week10_api_rate_limit_hits_total',
  help: 'Total number of rate limit hits',
  labelNames: ['route'],
  registers: [register]
});

// Middleware để track metrics
const metricsMiddleware = (req, res, next) => {
  const start = Date.now();
  activeRequests.inc();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route ? req.route.path : req.path;
    const labels = {
      method: req.method,
      route: route,
      status_code: res.statusCode
    };

    httpRequestCounter.inc(labels);
    httpRequestDuration.observe(labels, duration);
    activeRequests.dec();
  });

  next();
};

module.exports = {
  register,
  metricsMiddleware,
  httpRequestCounter,
  httpRequestDuration,
  activeRequests,
  rateLimitCounter
};
