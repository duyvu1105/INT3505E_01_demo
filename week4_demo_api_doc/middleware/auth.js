const jwt = require("jsonwebtoken");

// Secret key để mã hóa JWT (trong production nên đặt trong biến môi trường)
const JWT_SECRET = "your-secret-key-change-this-in-production";
const JWT_EXPIRES_IN = "24h";

// Middleware xác thực JWT token
const authenticateToken = (req, res, next) => {
  // Lấy token từ header Authorization
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1]; // Format: "Bearer TOKEN"

  if (!token) {
    return res.status(401).json({
      success: false,
      message: "Token không được cung cấp",
    });
  }

  // Xác thực token
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({
        success: false,
        message: "Token không hợp lệ hoặc đã hết hạn",
      });
    }

    // Lưu thông tin user vào request để sử dụng trong các route handlers
    req.user = user;
    next();
  });
};

/**
 * Tạo JWT token mới
 */
const generateToken = (payload) => {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
};

/**
 * Middleware kiểm tra quyền admin (optional - để mở rộng sau)
 */
const requireAdmin = (req, res, next) => {
  if (!req.user || req.user.role !== "admin") {
    return res.status(403).json({
      success: false,
      message: "Bạn không có quyền truy cập",
    });
  }
  next();
};

module.exports = {
  authenticateToken,
  generateToken,
  requireAdmin,
  JWT_SECRET,
  JWT_EXPIRES_IN,
};
