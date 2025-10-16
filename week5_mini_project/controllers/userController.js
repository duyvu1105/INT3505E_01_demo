const db = require("../data/database");
const { User } = require("../models");

// GET /api/users - Lấy tất cả người dùng
const getAllUsers = (req, res) => {
  const { status } = req.query;

  let filteredUsers = [...db.users];

  // Filter by status
  if (status) {
    filteredUsers = filteredUsers.filter((u) => u.status === status);
  }

  res.json({
    success: true,
    count: filteredUsers.length,
    data: filteredUsers,
  });
};

// GET /api/users/:id - Lấy người dùng theo ID
const getUserById = (req, res) => {
  const { id } = req.params;
  const user = db.users.find((u) => u.id === parseInt(id));

  if (!user) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy người dùng",
    });
  }

  res.json({
    success: true,
    data: user,
  });
};

// POST /api/users - Tạo người dùng mới
const createUser = (req, res) => {
  // Validate using User model
  const validation = User.validate(req.body);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: validation.errors,
    });
  }

  // Kiểm tra email đã tồn tại
  const existingUser = db.users.find((u) => u.email === req.body.email);
  if (existingUser) {
    return res.status(400).json({
      success: false,
      message: "Email đã tồn tại",
    });
  }

  // Tạo user mới sử dụng User model
  const newUser = User.create(req.body, db.getNextUserId());
  db.users.push(newUser);

  res.status(201).json({
    success: true,
    message: "Tạo người dùng thành công",
    data: newUser,
  });
};

// PUT /api/users/:id - Cập nhật người dùng
const updateUser = (req, res) => {
  const { id } = req.params;

  const userIndex = db.users.findIndex((u) => u.id === parseInt(id));

  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy người dùng",
    });
  }

  // Validate using User model
  const validation = User.validate(req.body);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: validation.errors,
    });
  }

  const currentUser = db.users[userIndex];
  const { name, email, phone, address, status } = req.body;

  // Update user
  db.users[userIndex] = {
    ...currentUser,
    name,
    email,
    phone,
    address: address || currentUser.address,
    status: status || currentUser.status,
  };

  res.json({
    success: true,
    message: "Cập nhật người dùng thành công",
    data: db.users[userIndex],
  });
};

// DELETE /api/users/:id - Xóa người dùng
const deleteUser = (req, res) => {
  const { id } = req.params;
  const userIndex = db.users.findIndex((u) => u.id === parseInt(id));

  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy người dùng",
    });
  }

  // Kiểm tra user có sách đang mượn không bằng User model
  const user = db.users[userIndex];
  if (User.hasBorrowedBooks(user)) {
    return res.status(400).json({
      success: false,
      message: "Không thể xóa người dùng đang mượn sách",
    });
  }

  db.users.splice(userIndex, 1);

  res.json({
    success: true,
    message: "Xóa người dùng thành công",
  });
};

module.exports = {
  getAllUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser,
};
