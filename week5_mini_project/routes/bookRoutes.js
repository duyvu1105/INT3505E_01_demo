const express = require("express");
const router = express.Router();
const bookController = require("../controllers/bookController");

// GET /api/books/search - Tìm kiếm nâng cao
router.get("/search", bookController.searchBooks);

// GET /api/books - Lấy tất cả sách với filter và pagination
router.get("/", bookController.getAllBooks);

// GET /api/books/:id - Lấy sách theo ID
router.get("/:id", bookController.getBookById);

// POST /api/books - Tạo sách mới
router.post("/", bookController.createBook);

// PUT /api/books/:id - Cập nhật sách
router.put("/:id", bookController.updateBook);

// DELETE /api/books/:id - Xóa sách
router.delete("/:id", bookController.deleteBook);

module.exports = router;
