const db = require("../data/database");
const { Borrowing, Book, User } = require("../models");

// GET /api/borrowings - Lấy tất cả phiếu mượn
const getAllBorrowings = (req, res) => {
  const { status, userId, bookId } = req.query;

  let filteredBorrowings = [...db.borrowings];

  // Filter by status
  if (status) {
    filteredBorrowings = filteredBorrowings.filter((b) => b.status === status);
  }

  // Filter by userId
  if (userId) {
    filteredBorrowings = filteredBorrowings.filter(
      (b) => b.userId === parseInt(userId)
    );
  }

  // Filter by bookId
  if (bookId) {
    filteredBorrowings = filteredBorrowings.filter(
      (b) => b.bookId === parseInt(bookId)
    );
  }

  res.json({
    success: true,
    count: filteredBorrowings.length,
    data: filteredBorrowings,
  });
};

// GET /api/borrowings/:id - Lấy phiếu mượn theo ID
const getBorrowingById = (req, res) => {
  const { id } = req.params;
  const borrowing = db.borrowings.find((b) => b.id === parseInt(id));

  if (!borrowing) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy phiếu mượn",
    });
  }

  res.json({
    success: true,
    data: borrowing,
  });
};

// POST /api/borrowings - Mượn sách
const createBorrowing = (req, res) => {
  // Validate using Borrowing model
  const validation = Borrowing.validate(req.body);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: validation.errors,
    });
  }

  const { userId, bookId } = req.body;

  // Kiểm tra user tồn tại
  const user = db.users.find((u) => u.id === parseInt(userId));
  if (!user) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy người dùng",
    });
  }

  // Kiểm tra book tồn tại
  const book = db.books.find((b) => b.id === parseInt(bookId));
  if (!book) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  // Kiểm tra user có thể mượn sách không bằng User model
  if (!User.canBorrow(user)) {
    if (!User.isActive(user)) {
      return res.status(400).json({
        success: false,
        message: "Tài khoản không ở trạng thái active",
      });
    }
    if (User.hasReachedBorrowLimit(user)) {
      return res.status(400).json({
        success: false,
        message: "Đã đạt giới hạn mượn sách (tối đa 5 quyển)",
      });
    }
  }

  // Kiểm tra sách có sẵn bằng Book model
  if (!Book.isAvailable(book)) {
    return res.status(400).json({
      success: false,
      message: "Sách không còn sẵn để mượn",
    });
  }

  // Tạo borrowing mới sử dụng Borrowing model
  const newBorrowing = Borrowing.create(req.body, db.getNextBorrowingId());

  // Cập nhật database
  db.borrowings.push(newBorrowing);
  book.available--;
  user.borrowedBooks.push(parseInt(bookId));

  res.status(201).json({
    success: true,
    message: "Mượn sách thành công",
    data: newBorrowing,
  });
};

// PATCH /api/borrowings/:id/return - Trả sách
const returnBook = (req, res) => {
  const { id } = req.params;

  const borrowing = db.borrowings.find((b) => b.id === parseInt(id));

  if (!borrowing) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy phiếu mượn",
    });
  }

  if (borrowing.status === "returned") {
    return res.status(400).json({
      success: false,
      message: "Sách đã được trả trước đó",
    });
  }

  // Tính phí phạt bằng Borrowing model
  const returnDateStr = new Date().toISOString().split("T")[0];
  const fine = Borrowing.calculateFine(borrowing, returnDateStr);

  // Cập nhật borrowing
  borrowing.returnDate = returnDateStr;
  borrowing.status = "returned";
  borrowing.fine = fine;

  // Cập nhật book và user
  const book = db.books.find((b) => b.id === borrowing.bookId);
  const user = db.users.find((u) => u.id === borrowing.userId);

  if (book) {
    book.available++;
  }

  if (user) {
    const index = user.borrowedBooks.indexOf(borrowing.bookId);
    if (index > -1) {
      user.borrowedBooks.splice(index, 1);
    }
  }

  res.json({
    success: true,
    message:
      fine > 0
        ? `Trả sách thành công. Phí phạt: ${fine.toLocaleString()} VNĐ`
        : "Trả sách thành công",
    data: borrowing,
  });
};

// GET /api/borrowings/overdue - Lấy danh sách quá hạn
const getOverdueBorrowings = (req, res) => {
  const today = new Date().toISOString().split("T")[0];

  const overdueBorrowings = db.borrowings.filter(
    (b) => b.status === "borrowed" && b.dueDate < today
  );

  // Cập nhật status thành overdue bằng Borrowing model
  overdueBorrowings.forEach((b) => {
    Borrowing.updateOverdueStatus(b);
  });

  res.json({
    success: true,
    count: overdueBorrowings.length,
    data: overdueBorrowings,
  });
};

module.exports = {
  getAllBorrowings,
  getBorrowingById,
  createBorrowing,
  returnBook,
  getOverdueBorrowings,
};
