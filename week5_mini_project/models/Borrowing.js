class Borrowing {
  /**
   * Validate dữ liệu Borrowing
   * @param {Object} data - Dữ liệu borrowing cần validate
   * @returns {Object} { isValid: boolean, errors: string[] }
   */
  static validate(data) {
    const errors = [];

    // Required fields
    if (!data.userId) {
      errors.push("User ID là bắt buộc");
    }

    if (!data.bookId) {
      errors.push("Book ID là bắt buộc");
    }

    // Validate status
    if (data.status) {
      const validStatuses = ["borrowed", "returned", "overdue"];
      if (!validStatuses.includes(data.status)) {
        errors.push("Status phải là: borrowed, returned, hoặc overdue");
      }
    }

    // Validate fine
    if (data.fine !== undefined && data.fine < 0) {
      errors.push("Fine không được âm");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Tạo object Borrowing mới với giá trị mặc định
   * @param {Object} data - Dữ liệu borrowing
   * @param {number} id - ID của borrowing
   * @returns {Object} Borrowing object
   */
  static create(data, id) {
    const borrowDate =
      data.borrowDate || new Date().toISOString().split("T")[0];
    const dueDate = data.dueDate || this.calculateDueDate(borrowDate);

    return {
      id: id,
      userId: parseInt(data.userId),
      bookId: parseInt(data.bookId),
      borrowDate: borrowDate,
      dueDate: dueDate,
      returnDate: data.returnDate || null,
      status: data.status || "borrowed",
      fine: data.fine || 0,
    };
  }

  /**
   * Tính ngày hạn trả (14 ngày sau ngày mượn)
   * @param {string} borrowDate - Ngày mượn (YYYY-MM-DD)
   * @returns {string} Ngày hạn trả (YYYY-MM-DD)
   */
  static calculateDueDate(borrowDate = null) {
    const borrow = borrowDate ? new Date(borrowDate) : new Date();
    const due = new Date(borrow);
    due.setDate(due.getDate() + 14); // 14 ngày mượn
    return due.toISOString().split("T")[0];
  }

  /**
   * Kiểm tra borrowing có quá hạn không
   * @param {Object} borrowing - Borrowing object
   * @returns {boolean}
   */
  static isOverdue(borrowing) {
    if (borrowing.status === "returned") {
      return false;
    }
    const today = new Date().toISOString().split("T")[0];
    return borrowing.dueDate < today;
  }

  /**
   * Tính phí phạt khi trả muộn
   * @param {Object} borrowing - Borrowing object
   * @param {string} returnDate - Ngày trả (YYYY-MM-DD), null = hôm nay
   * @returns {number} Số tiền phạt (VNĐ)
   */
  static calculateFine(borrowing, returnDate = null) {
    const actualReturnDate =
      returnDate || new Date().toISOString().split("T")[0];
    const dueDate = new Date(borrowing.dueDate);
    const returnD = new Date(actualReturnDate);

    if (returnD <= dueDate) {
      return 0; // Không phạt nếu trả đúng hạn
    }

    // Tính số ngày quá hạn
    const daysOverdue = Math.ceil((returnD - dueDate) / (1000 * 60 * 60 * 24));
    const finePerDay = 1000; // 1000 VNĐ/ngày

    return daysOverdue * finePerDay;
  }

  /**
   * Lấy số ngày quá hạn
   * @param {Object} borrowing - Borrowing object
   * @returns {number}
   */
  static getDaysOverdue(borrowing) {
    if (!this.isOverdue(borrowing)) {
      return 0;
    }

    const today = new Date();
    const dueDate = new Date(borrowing.dueDate);
    return Math.ceil((today - dueDate) / (1000 * 60 * 60 * 24));
  }

  /**
   * Cập nhật status thành overdue và tính fine
   * @param {Object} borrowing - Borrowing object
   * @returns {Object} Updated borrowing object
   */
  static updateOverdueStatus(borrowing) {
    if (this.isOverdue(borrowing) && borrowing.status === "borrowed") {
      borrowing.status = "overdue";
      borrowing.fine = this.calculateFine(borrowing);
    }
    return borrowing;
  }
}

module.exports = Borrowing;
