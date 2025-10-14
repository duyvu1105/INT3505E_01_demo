const db = require("../data/database");

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
  const { name, email, phone, address } = req.body;

  // Validation
  if (!name || !email || !phone) {
    return res.status(400).json({
      success: false,
      message: "Name, Email và Phone là bắt buộc",
    });
  }

  // Kiểm tra email đã tồn tại
  const existingUser = db.users.find((u) => u.email === email);
  if (existingUser) {
    return res.status(400).json({
      success: false,
      message: "Email đã tồn tại",
    });
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({
      success: false,
      message: "Email không hợp lệ",
    });
  }

  const newUser = {
    id: db.getNextUserId(),
    name,
    email,
    phone,
    address: address || "",
    membershipDate: new Date().toISOString().split("T")[0],
    status: "active",
    borrowedBooks: [],
  };

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
  const { name, email, phone, address, status } = req.body;

  const userIndex = db.users.findIndex((u) => u.id === parseInt(id));

  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy người dùng",
    });
  }

  // Validation
  if (!name || !email || !phone) {
    return res.status(400).json({
      success: false,
      message: "Name, Email và Phone là bắt buộc",
    });
  }

  const currentUser = db.users[userIndex];

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

  // Kiểm tra user có sách đang mượn không
  const user = db.users[userIndex];
  if (user.borrowedBooks.length > 0) {
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
