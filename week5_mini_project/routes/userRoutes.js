const express = require("express");
const router = express.Router();
const userController = require("../controllers/userController");

// GET /api/users - Lấy tất cả người dùng
router.get("/", userController.getAllUsers);

// GET /api/users/:id - Lấy người dùng theo ID
router.get("/:id", userController.getUserById);

// POST /api/users - Tạo người dùng mới
router.post("/", userController.createUser);

// PUT /api/users/:id - Cập nhật người dùng
router.put("/:id", userController.updateUser);

// DELETE /api/users/:id - Xóa người dùng
router.delete("/:id", userController.deleteUser);

module.exports = router;
