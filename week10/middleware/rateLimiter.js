const rateLimit = require('express-rate-limit');
const logger = require('../config/logger');
const { rateLimitCounter } = require('../config/metrics');

// Rate limiter chung cho toàn bộ API
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 phút
  max: 100, // Giới hạn 100 requests mỗi windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true, // Trả về rate limit info trong headers `RateLimit-*`
  legacyHeaders: false, // Tắt headers `X-RateLimit-*`
  handler: (req, res) => {
    const route = req.route ? req.route.path : req.path;
    rateLimitCounter.inc({ route });
    
    logger.warn('Rate limit exceeded', {
      ip: req.ip,
      route: route,
      method: req.method
    });

    res.status(429).json({
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: '15 minutes'
    });
  }
});

// Rate limiter nghiêm ngặt hơn cho các endpoint quan trọng (ví dụ: auth, payment)
const strictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 phút
  max: 5, // Chỉ 5 requests mỗi 15 phút
  message: {
    error: 'Too many attempts, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: false,
  handler: (req, res) => {
    const route = req.route ? req.route.path : req.path;
    rateLimitCounter.inc({ route });
    
    logger.warn('Strict rate limit exceeded', {
      ip: req.ip,
      route: route,
      method: req.method
    });

    res.status(429).json({
      error: 'Too many attempts, please try again later.',
      retryAfter: '15 minutes'
    });
  }
});

// Rate limiter cho API endpoints (ít nghiêm ngặt hơn)
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 phút
  max: 30, // 30 requests mỗi phút
  message: {
    error: 'API rate limit exceeded.',
    retryAfter: '1 minute'
  },
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    const route = req.route ? req.route.path : req.path;
    rateLimitCounter.inc({ route });
    
    logger.warn('API rate limit exceeded', {
      ip: req.ip,
      route: route,
      method: req.method
    });

    res.status(429).json({
      error: 'API rate limit exceeded.',
      retryAfter: '1 minute'
    });
  }
});

module.exports = {
  generalLimiter,
  strictLimiter,
  apiLimiter
};
