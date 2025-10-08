const express = require("express");
const path = require("path");
const cors = require("cors");
const swaggerUi = require("swagger-ui-express");
const YAML = require("yamljs");

const app = express();
const PORT = 3000;

// Load OpenAPI specification
const swaggerDocument = YAML.load(path.join(__dirname, "books-api.yaml"));

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Database giả lập
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

let nextId = 4;

// Tích hợp Swagger UI để xem tài liệu API
app.use(
  "/api-docs",
  swaggerUi.serve,
  swaggerUi.setup(swaggerDocument, {
    customSiteTitle: "Books API Documentation",
    customCss: ".swagger-ui .topbar { display: none }",
  })
);


// GET /api/books - Lấy tất cả sách
app.get("/api/books", (req, res) => {
  res.json({
    success: true,
    data: books,
  });
});

// GET /api/books/:id - Lấy sách theo ID
app.get("/api/books/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const book = books.find((b) => b.id === id);

  if (!book) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  res.json({
    success: true,
    data: book,
  });
});

// POST /api/books - Tạo sách mới
app.post("/api/books", (req, res) => {
  const { title, author, year, price } = req.body;

  // Validation
  if (!title || !author) {
    return res.status(400).json({
      success: false,
      message: "Title và Author là bắt buộc",
    });
  }

  const newBook = {
    id: nextId++,
    title,
    author,
    year: year || new Date().getFullYear(),
    price: price || 0,
  };

  books.push(newBook);

  res.status(201).json({
    success: true,
    data: newBook,
  });
});

// PUT /api/books/:id - Cập nhật sách
app.put("/api/books/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const bookIndex = books.findIndex((b) => b.id === id);

  if (bookIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  const { title, author, year, price } = req.body;

  if (!title || !author) {
    return res.status(400).json({
      success: false,
      message: "Title và Author là bắt buộc",
    });
  }

  books[bookIndex] = {
    id,
    title,
    author,
    year: year || books[bookIndex].year,
    price: price !== undefined ? price : books[bookIndex].price,
  };

  res.json({
    success: true,
    data: books[bookIndex],
  });
});

// DELETE /api/books/:id - Xóa sách
app.delete("/api/books/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const bookIndex = books.findIndex((b) => b.id === id);

  if (bookIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  books.splice(bookIndex, 1);

  res.json({
    success: true,
    message: "Xóa sách thành công",
  });
});


// Route để serve YAML file
app.get("/books-api.yaml", (req, res) => {
  res.sendFile(path.join(__dirname, "books-api.yaml"));
});

// Redirect root to API documentation
app.get("/", (req, res) => {
  res.redirect("/api-docs");
});


app.listen(PORT, () => {
  console.log(`Server đang chạy tại: http://localhost:${PORT}`);
  console.log(`API endpoint: http://localhost:${PORT}/api/books`);
  console.log(`Swagger UI (API Docs): http://localhost:${PORT}/api-docs`);
  console.log(`OpenAPI YAML: http://localhost:${PORT}/books-api.yaml`);
});
