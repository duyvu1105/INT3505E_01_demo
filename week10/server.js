const express = require('express');
const logger = require('./config/logger');
const { register, metricsMiddleware } = require('./config/metrics');
const { generalLimiter, strictLimiter, apiLimiter } = require('./middleware/rateLimiter');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(logger.httpLogger); // Log mọi HTTP request
app.use(metricsMiddleware); // Track metrics

// Apply general rate limiter cho toàn bộ app
app.use(generalLimiter);

// Routes

// 1. Health check endpoint (không rate limit)
app.get('/health', (req, res) => {
  logger.info('Health check accessed');
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// 2. Metrics endpoint cho Prometheus (không rate limit)
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// 3. API endpoints với rate limiting
app.get('/api/data', apiLimiter, (req, res) => {
  logger.info('Data endpoint accessed', { query: req.query });
  res.json({ 
    message: 'Data retrieved successfully',
    data: [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
      { id: 3, name: 'Item 3' }
    ],
    timestamp: new Date().toISOString()
  });
});

app.get('/api/users', apiLimiter, (req, res) => {
  logger.info('Users endpoint accessed');
  res.json({
    message: 'Users retrieved successfully',
    users: [
      { id: 1, username: 'user1', email: 'user1@example.com' },
      { id: 2, username: 'user2', email: 'user2@example.com' }
    ],
    timestamp: new Date().toISOString()
  });
});

// 4. Endpoint quan trọng với strict rate limiting
app.post('/api/auth/login', strictLimiter, (req, res) => {
  const { username, password } = req.body;
  
  logger.info('Login attempt', { username });
  
  if (!username || !password) {
    logger.warn('Login failed - missing credentials', { username });
    return res.status(400).json({ 
      error: 'Username and password are required' 
    });
  }

  // Demo: simple check (thực tế cần kiểm tra database)
  if (username === 'admin' && password === 'password123') {
    logger.info('Login successful', { username });
    res.json({ 
      message: 'Login successful',
      token: 'demo-jwt-token-here',
      user: { username }
    });
  } else {
    logger.warn('Login failed - invalid credentials', { username });
    res.status(401).json({ 
      error: 'Invalid credentials' 
    });
  }
});

// 5. Endpoint để test logging ở các level khác nhau
app.get('/api/test/logs', (req, res) => {
  logger.debug('This is a debug message');
  logger.info('This is an info message');
  logger.warn('This is a warning message');
  logger.error('This is an error message');

  res.json({ 
    message: 'Check your console and log files for different log levels' 
  });
});

// 6. Endpoint để test error logging
app.get('/api/test/error', (req, res) => {
  try {
    throw new Error('This is a test error');
  } catch (error) {
    logger.error('Error occurred in test endpoint', { 
      error: error.message, 
      stack: error.stack 
    });
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
});

// 404 handler
app.use((req, res) => {
  logger.warn('404 - Route not found', { 
    method: req.method, 
    url: req.originalUrl 
  });
  res.status(404).json({ 
    error: 'Route not found',
    path: req.originalUrl 
  });
});

// Global error handler
app.use((err, req, res, next) => {
  logger.error('Unhandled error', { 
    error: err.message, 
    stack: err.stack,
    url: req.originalUrl,
    method: req.method
  });

  res.status(err.status || 500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Server started on port ${PORT}`, { 
    environment: process.env.NODE_ENV || 'development',
    port: PORT 
  });
  console.log(`
╔════════════════════════════════════════════════════════╗
║         Week 10 - Logging & Monitoring Demo            ║
╠════════════════════════════════════════════════════════╣
║  Server running on: http://localhost:${PORT}           ║
║                                                        ║
║  Endpoints:                                            ║
║  • GET  /health              - Health check            ║
║  • GET  /metrics             - Prometheus metrics      ║
║  • GET  /api/data            - Get data (30/min)       ║
║  • GET  /api/users           - Get users (30/min)      ║
║  • POST /api/auth/login      - Login (5/15min)         ║
║  • GET  /api/test/logs       - Test log levels         ║
║  • GET  /api/test/error      - Test error logging      ║
║                                                        ║
║  Logs saved to: ./logs/                                ║
╚════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
