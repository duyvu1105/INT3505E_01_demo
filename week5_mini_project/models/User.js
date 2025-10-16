class User {
  /**
   * Validate dữ liệu User
   * @param {Object} data - Dữ liệu user cần validate
   * @returns {Object} { isValid: boolean, errors: string[] }
   */
  static validate(data) {
    const errors = [];

    // Required fields
    if (!data.name || data.name.trim() === "") {
      errors.push("Name là bắt buộc");
    }

    if (!data.email || data.email.trim() === "") {
      errors.push("Email là bắt buộc");
    }

    if (!data.phone || data.phone.trim() === "") {
      errors.push("Phone là bắt buộc");
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (data.email && !emailRegex.test(data.email)) {
      errors.push("Email không hợp lệ");
    }

    // Validate phone format (10-11 chữ số cho số điện thoại VN)
    const phoneRegex = /^[0-9]{10,11}$/;
    if (data.phone && !phoneRegex.test(data.phone.replace(/[\s-]/g, ""))) {
      errors.push("Phone phải có 10-11 chữ số");
    }

    // Validate status
    if (data.status) {
      const validStatuses = ["active", "inactive", "suspended"];
      if (!validStatuses.includes(data.status)) {
        errors.push("Status phải là: active, inactive, hoặc suspended");
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Tạo object User mới với giá trị mặc định
   * @param {Object} data - Dữ liệu user
   * @param {number} id - ID của user
   * @returns {Object} User object
   */
  static create(data, id) {
    return {
      id: id,
      name: data.name,
      email: data.email,
      phone: data.phone,
      address: data.address || "",
      membershipDate:
        data.membershipDate || new Date().toISOString().split("T")[0],
      status: data.status || "active",
      borrowedBooks: data.borrowedBooks || [],
    };
  }

  /**
   * Kiểm tra user có thể mượn sách không
   * @param {Object} user - User object
   * @returns {boolean}
   */
  static canBorrow(user) {
    return user.status === "active" && user.borrowedBooks.length < 5;
  }

  /**
   * Kiểm tra user đang active không
   * @param {Object} user - User object
   * @returns {boolean}
   */
  static isActive(user) {
    return user.status === "active";
  }

  /**
   * Kiểm tra user có sách đang mượn không
   * @param {Object} user - User object
   * @returns {boolean}
   */
  static hasBorrowedBooks(user) {
    return user.borrowedBooks.length > 0;
  }

  /**
   * Lấy số lượng sách đang mượn
   * @param {Object} user - User object
   * @returns {number}
   */
  static getBorrowedCount(user) {
    return user.borrowedBooks.length;
  }

  /**
   * Kiểm tra giới hạn mượn sách (tối đa 5 cuốn)
   * @param {Object} user - User object
   * @returns {boolean}
   */
  static hasReachedBorrowLimit(user) {
    return user.borrowedBooks.length >= 5;
  }
}

module.exports = User;
