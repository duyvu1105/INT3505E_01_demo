const express = require("express");
const router = express.Router();
const borrowingController = require("../controllers/borrowingController");


// GET /api/borrowings - Lấy tất cả phiếu mượn
router.get("/", borrowingController.getAllBorrowings);

// GET /api/borrowings/overdue - Lấy danh sách quá hạn
router.get("/overdue", borrowingController.getOverdueBorrowings);

// GET /api/borrowings/:id - Lấy phiếu mượn theo ID
router.get("/:id", borrowingController.getBorrowingById);

// POST /api/borrowings - Mượn sách
router.post("/", borrowingController.createBorrowing);

// PATCH /api/borrowings/:id/return - Trả sách
router.patch("/:id/return", borrowingController.returnBook);

module.exports = router;
