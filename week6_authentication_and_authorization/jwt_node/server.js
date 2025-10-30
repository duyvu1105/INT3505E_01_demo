const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const bodyParser = require("body-parser");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// JWT config
const JWT_SECRET = "your-secret-key-change-this-in-production";
const JWT_EXPIRES_IN = 60; // seconds (1 minute)
const JWT_REFRESH_EXPIRES_IN = 7 * 24 * 60 * 60; // 7 days in seconds

// In-memory DB
let books = [
  {
    id: 1,
    title: "Clean Code",
    author: "Robert C. Martin",
    year: 2008,
    price: 45.99,
  },
  {
    id: 2,
    title: "The Pragmatic Programmer",
    author: "Andrew Hunt",
    year: 1999,
    price: 42.5,
  },
  {
    id: 3,
    title: "Design Patterns",
    author: "Gang of Four",
    year: 1994,
    price: 54.99,
  },
];
let nextBookId = 4;

let users = [
  {
    id: 1,
    username: "admin",
    password: "admin123",
    email: "admin@example.com",
    role: "admin",
  },
  {
    id: 2,
    username: "user",
    password: "user123",
    email: "user@example.com",
    role: "user",
  },
];
let nextUserId = 3;

// In-memory refresh token store
const refreshTokens = {};

// JWT utilities
function generateToken(payload, expiresIn = JWT_EXPIRES_IN) {
  return jwt.sign({ ...payload }, JWT_SECRET, { expiresIn });
}
function generateRefreshToken(payload) {
  return jwt.sign({ ...payload, type: "refresh" }, JWT_SECRET, {
    expiresIn: JWT_REFRESH_EXPIRES_IN,
  });
}

function authenticateToken(req, res, next) {
  const authHeader = req.headers["authorization"];
  if (!authHeader)
    return res
      .status(401)
      .json({ success: false, message: "Token không được cung cấp" });
  const token = authHeader.split(" ")[1] || authHeader;
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err)
      return res
        .status(403)
        .json({
          success: false,
          message:
            err.name === "TokenExpiredError"
              ? "Token đã hết hạn"
              : "Token không hợp lệ",
        });
    req.user = user;
    next();
  });
}

function requireAdmin(req, res, next) {
  if (!req.user || req.user.role !== "admin") {
    return res
      .status(403)
      .json({ success: false, message: "Bạn không có quyền truy cập" });
  }
  next();
}

// AUTH ROUTES
app.post("/api/auth/register", (req, res) => {
  const { username, password, email } = req.body;
  if (!username || !password || !email) {
    return res
      .status(400)
      .json({
        success: false,
        message: "Username, password và email là bắt buộc",
      });
  }
  if (users.some((u) => u.username === username)) {
    return res
      .status(400)
      .json({ success: false, message: "Username đã tồn tại" });
  }
  const newUser = { id: nextUserId++, username, password, email, role: "user" };
  users.push(newUser);
  const accessToken = generateToken({
    id: newUser.id,
    username,
    role: newUser.role,
  });
  const refreshToken = generateRefreshToken({
    id: newUser.id,
    username,
    role: newUser.role,
  });
  refreshTokens[newUser.id] = refreshToken;
  res.status(201).json({
    success: true,
    message: "Đăng ký thành công",
    data: {
      user: { id: newUser.id, username, email, role: newUser.role },
      access_token: accessToken,
      refresh_token: refreshToken,
    },
  });
});

app.post("/api/auth/login", (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res
      .status(400)
      .json({ success: false, message: "Username và password là bắt buộc" });
  }
  const user = users.find(
    (u) => u.username === username && u.password === password
  );
  if (!user) {
    return res
      .status(401)
      .json({ success: false, message: "Username hoặc password không đúng" });
  }
  const accessToken = generateToken({
    id: user.id,
    username: user.username,
    role: user.role,
  });
  const refreshToken = generateRefreshToken({
    id: user.id,
    username: user.username,
    role: user.role,
  });
  refreshTokens[user.id] = refreshToken;
  res.json({
    success: true,
    message: "Đăng nhập thành công",
    data: {
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
      },
      access_token: accessToken,
      refresh_token: refreshToken,
    },
  });
});

app.post("/api/auth/refresh", (req, res) => {
  const { refresh_token } = req.body;
  if (!refresh_token)
    return res
      .status(400)
      .json({ success: false, message: "Refresh token là bắt buộc" });
  jwt.verify(refresh_token, JWT_SECRET, (err, decoded) => {
    if (err || decoded.type !== "refresh")
      return res
        .status(403)
        .json({ success: false, message: "Refresh token không hợp lệ" });
    const userId = decoded.id;
    if (refreshTokens[userId] !== refresh_token)
      return res
        .status(403)
        .json({ success: false, message: "Refresh token không hợp lệ" });
    const user = users.find((u) => u.id === userId);
    if (!user)
      return res
        .status(404)
        .json({ success: false, message: "Không tìm thấy user" });
    const accessToken = generateToken({
      id: user.id,
      username: user.username,
      role: user.role,
    });
    res.json({ success: true, access_token: accessToken });
  });
});

app.get("/api/auth/me", authenticateToken, (req, res) => {
  const user = users.find((u) => u.id === req.user.id);
  if (!user)
    return res
      .status(404)
      .json({ success: false, message: "Không tìm thấy user" });
  res.json({
    success: true,
    data: {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    },
  });
});

// BOOKS ROUTES
app.get("/api/books", (req, res) => {
  res.json({ success: true, data: books });
});

app.get("/api/books/:bookId", (req, res) => {
  const book = books.find((b) => b.id === parseInt(req.params.bookId));
  if (!book)
    return res
      .status(404)
      .json({ success: false, message: "Không tìm thấy sách" });
  res.json({ success: true, data: book });
});

app.post("/api/books", authenticateToken, (req, res) => {
  const { title, author, year, price } = req.body;
  if (!title || !author) {
    return res
      .status(400)
      .json({ success: false, message: "Title và Author là bắt buộc" });
  }
  const newBook = {
    id: nextBookId++,
    title,
    author,
    year: year || new Date().getFullYear(),
    price: price || 0,
  };
  books.push(newBook);
  res.status(201).json({ success: true, data: newBook });
});

app.put("/api/books/:bookId", authenticateToken, (req, res) => {
  const book = books.find((b) => b.id === parseInt(req.params.bookId));
  if (!book)
    return res
      .status(404)
      .json({ success: false, message: "Không tìm thấy sách" });
  const { title, author, year, price } = req.body;
  if (!title || !author) {
    return res
      .status(400)
      .json({ success: false, message: "Title và Author là bắt buộc" });
  }
  book.title = title;
  book.author = author;
  book.year = year || book.year;
  book.price = price || book.price;
  res.json({ success: true, data: book });
});

app.delete(
  "/api/books/:bookId",
  authenticateToken,
  requireAdmin,
  (req, res) => {
    const book = books.find((b) => b.id === parseInt(req.params.bookId));
    if (!book)
      return res
        .status(404)
        .json({ success: false, message: "Không tìm thấy sách" });
    books = books.filter((b) => b.id !== book.id);
    res.json({ success: true, message: "Xóa sách thành công" });
  }
);

// Server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server đang chạy tại: http://localhost:${PORT}`);
  console.log(`API endpoint: http://localhost:${PORT}/api/books`);
});
