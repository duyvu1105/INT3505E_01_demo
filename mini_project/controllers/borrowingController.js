const db = require("../data/database");

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
  const { userId, bookId } = req.body;

  // Validation
  if (!userId || !bookId) {
    return res.status(400).json({
      success: false,
      message: "User ID và Book ID là bắt buộc",
    });
  }

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

  // Kiểm tra user status
  if (user.status !== "active") {
    return res.status(400).json({
      success: false,
      message: "Tài khoản không ở trạng thái active",
    });
  }

  // Kiểm tra giới hạn mượn sách (tối đa 5 quyển)
  if (user.borrowedBooks.length >= 5) {
    return res.status(400).json({
      success: false,
      message: "Đã đạt giới hạn mượn sách (tối đa 5 quyển)",
    });
  }

  // Kiểm tra sách có sẵn
  if (book.available <= 0) {
    return res.status(400).json({
      success: false,
      message: "Sách không còn sẵn để mượn",
    });
  }

  // Tạo ngày mượn và ngày trả dự kiến
  const borrowDate = new Date();
  const dueDate = new Date();
  dueDate.setDate(dueDate.getDate() + 14); // 14 ngày mượn

  const newBorrowing = {
    id: db.getNextBorrowingId(),
    userId: parseInt(userId),
    bookId: parseInt(bookId),
    borrowDate: borrowDate.toISOString().split("T")[0],
    dueDate: dueDate.toISOString().split("T")[0],
    returnDate: null,
    status: "borrowed",
    fine: 0,
  };

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

  // Tính phí phạt nếu trả muộn
  const returnDate = new Date();
  const dueDate = new Date(borrowing.dueDate);
  const returnDateStr = returnDate.toISOString().split("T")[0];

  let fine = 0;
  if (returnDate > dueDate) {
    const daysOverdue = Math.ceil(
      (returnDate - dueDate) / (1000 * 60 * 60 * 24)
    );
    fine = daysOverdue * 1000; // 1000 VNĐ/ngày
  }

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

  // Cập nhật status thành overdue
  overdueBorrowings.forEach((b) => {
    b.status = "overdue";

    // Tính fine
    const dueDate = new Date(b.dueDate);
    const todayDate = new Date(today);
    const daysOverdue = Math.ceil(
      (todayDate - dueDate) / (1000 * 60 * 60 * 24)
    );
    b.fine = daysOverdue * 1000;
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
