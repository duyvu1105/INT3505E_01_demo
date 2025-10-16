class Book {
  /**
   * Validate dữ liệu Book
   * @param {Object} data - Dữ liệu sách cần validate
   * @returns {Object} { isValid: boolean, errors: string[] }
   */
  static validate(data) {
    const errors = [];

    // Required fields
    if (!data.title || data.title.trim() === "") {
      errors.push("Title là bắt buộc");
    }

    if (!data.author || data.author.trim() === "") {
      errors.push("Author là bắt buộc");
    }

    if (!data.isbn || data.isbn.trim() === "") {
      errors.push("ISBN là bắt buộc");
    }

    // Validate ISBN format (chỉ số và dấu gạch ngang)
    if (data.isbn && !/^[0-9-]+$/.test(data.isbn)) {
      errors.push("ISBN chỉ được chứa số và dấu gạch ngang");
    }

    // Validate publishedYear
    if (data.publishedYear !== null && data.publishedYear !== undefined) {
      const year = parseInt(data.publishedYear);
      const currentYear = new Date().getFullYear();
      if (isNaN(year) || year < 1000 || year > currentYear) {
        errors.push(`Năm xuất bản phải từ 1000 đến ${currentYear}`);
      }
    }

    // Validate quantity
    if (data.quantity !== undefined && data.quantity < 0) {
      errors.push("Quantity không được âm");
    }

    // Validate available
    if (data.available !== undefined && data.available < 0) {
      errors.push("Available không được âm");
    }

    if (data.available !== undefined && data.quantity !== undefined) {
      if (data.available > data.quantity) {
        errors.push("Available không được lớn hơn Quantity");
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Tạo object Book mới với giá trị mặc định
   * @param {Object} data - Dữ liệu sách
   * @param {number} id - ID của sách
   * @returns {Object} Book object
   */
  static create(data, id) {
    return {
      id: id,
      title: data.title,
      author: data.author,
      isbn: data.isbn,
      publishedYear: data.publishedYear || null,
      category: data.category || "Uncategorized",
      quantity: data.quantity || 1,
      available:
        data.available !== undefined ? data.available : data.quantity || 1,
    };
  }

  /**
   * Kiểm tra sách có sẵn để mượn không
   * @param {Object} book - Book object
   * @returns {boolean}
   */
  static isAvailable(book) {
    return book.available > 0;
  }

  /**
   * Kiểm tra sách có đang được mượn không
   * @param {Object} book - Book object
   * @returns {boolean}
   */
  static hasBorrowedBooks(book) {
    return book.available < book.quantity;
  }

  /**
   * Tính số sách đang được mượn
   * @param {Object} book - Book object
   * @returns {number}
   */
  static getBorrowedCount(book) {
    return book.quantity - book.available;
  }
}

module.exports = Book;
