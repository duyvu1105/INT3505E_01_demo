const express = require("express");
const cors = require("cors");

const bookRoutes = require("./routes/bookRoutes");
const userRoutes = require("./routes/userRoutes");
const borrowingRoutes = require("./routes/borrowingRoutes");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Routes
app.use("/api/books", bookRoutes);
app.use("/api/users", userRoutes);
app.use("/api/borrowings", borrowingRoutes);

// Root route
app.get("/", (req, res) => {
  res.json({
    message: "Library Management System API",
    version: "1.0.0",
    endpoints: {
      books: "/api/books",
      users: "/api/users",
      borrowings: "/api/borrowings",
    },
  });
});

// 404 Handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: "Endpoint not found",
  });
});

// Error Handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: "Internal Server Error",
    error: process.env.NODE_ENV === "development" ? err.message : undefined,
  });
});

// Start server
app.listen(PORT, () => {
  console.log("Available Endpoints:");
  console.log(`   Books:      http://localhost:${PORT}/api/books`);
  console.log(`   Users:      http://localhost:${PORT}/api/users`);
  console.log(`   Borrowings: http://localhost:${PORT}/api/borrowings`);
});

module.exports = app;
