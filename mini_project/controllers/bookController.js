const db = require("../data/database");

/**
 * Books Controller - Xử lý logic cho sách
 */

// GET /api/books - Lấy tất cả sách với filter và phân trang
const getAllBooks = (req, res) => {
  const {
    category,
    author,
    available,
    page = 1, // Trang hiện tại
    limit = 10, // Số items per page
    sortBy = "id", // Sắp xếp theo field (id, title, author, publishedYear)
    order = "asc", // Thứ tự sắp xếp (asc, desc)
  } = req.query;

  let filteredBooks = [...db.books];

  // Filter by category
  if (category) {
    filteredBooks = filteredBooks.filter(
      (b) => b.category.toLowerCase() === category.toLowerCase()
    );
  }

  // Filter by author
  if (author) {
    filteredBooks = filteredBooks.filter((b) =>
      b.author.toLowerCase().includes(author.toLowerCase())
    );
  }

  // Filter by available
  if (available === "true") {
    filteredBooks = filteredBooks.filter((b) => b.available > 0);
  }

  // Sorting
  filteredBooks.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];

    // Handle string comparison
    if (typeof aValue === "string") {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (order === "desc") {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    } else {
      return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
    }
  });

  // Pagination
  const pageNum = parseInt(page);
  const limitNum = parseInt(limit);
  const startIndex = (pageNum - 1) * limitNum;
  const endIndex = startIndex + limitNum;
  const totalBooks = filteredBooks.length;
  const totalPages = Math.ceil(totalBooks / limitNum);
  const paginatedBooks = filteredBooks.slice(startIndex, endIndex);

  // Pagination info
  const pagination = {
    currentPage: pageNum,
    totalPages: totalPages,
    totalItems: totalBooks,
    itemsPerPage: limitNum,
    hasNextPage: pageNum < totalPages,
    hasPrevPage: pageNum > 1,
  };

  res.json({
    success: true,
    count: paginatedBooks.length,
    pagination: pagination,
    data: paginatedBooks,
  });
};

// GET /api/books/:id - Lấy sách theo ID
const getBookById = (req, res) => {
  const { id } = req.params;
  const book = db.books.find((b) => b.id === parseInt(id));

  if (!book) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  res.json({
    success: true,
    data: book,
  });
};

// POST /api/books - Tạo sách mới
const createBook = (req, res) => {
  const { title, author, isbn, publishedYear, category, quantity } = req.body;

  // Validation
  if (!title || !author || !isbn) {
    return res.status(400).json({
      success: false,
      message: "Title, Author và ISBN là bắt buộc",
    });
  }

  // Kiểm tra ISBN đã tồn tại
  const existingBook = db.books.find((b) => b.isbn === isbn);
  if (existingBook) {
    return res.status(400).json({
      success: false,
      message: "ISBN đã tồn tại",
    });
  }

  const newBook = {
    id: db.getNextBookId(),
    title,
    author,
    isbn,
    publishedYear: publishedYear || null,
    category: category || "Uncategorized",
    quantity: quantity || 1,
    available: quantity || 1,
  };

  db.books.push(newBook);

  res.status(201).json({
    success: true,
    message: "Tạo sách thành công",
    data: newBook,
  });
};

// PUT /api/books/:id - Cập nhật sách
const updateBook = (req, res) => {
  const { id } = req.params;
  const { title, author, isbn, publishedYear, category, quantity } = req.body;

  const bookIndex = db.books.findIndex((b) => b.id === parseInt(id));

  if (bookIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  // Validation
  if (!title || !author || !isbn) {
    return res.status(400).json({
      success: false,
      message: "Title, Author và ISBN là bắt buộc",
    });
  }

  const currentBook = db.books[bookIndex];
  const borrowed = currentBook.quantity - currentBook.available;

  // Update book
  db.books[bookIndex] = {
    ...currentBook,
    title,
    author,
    isbn,
    publishedYear: publishedYear || currentBook.publishedYear,
    category: category || currentBook.category,
    quantity: quantity || currentBook.quantity,
    available: (quantity || currentBook.quantity) - borrowed,
  };

  res.json({
    success: true,
    message: "Cập nhật sách thành công",
    data: db.books[bookIndex],
  });
};

// DELETE /api/books/:id - Xóa sách
const deleteBook = (req, res) => {
  const { id } = req.params;
  const bookIndex = db.books.findIndex((b) => b.id === parseInt(id));

  if (bookIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  // Kiểm tra sách có đang được mượn không
  const book = db.books[bookIndex];
  if (book.available < book.quantity) {
    return res.status(400).json({
      success: false,
      message: "Không thể xóa sách đang được mượn",
    });
  }

  db.books.splice(bookIndex, 1);

  res.json({
    success: true,
    message: "Xóa sách thành công",
  });
};

// GET /api/books/search - Tìm kiếm nâng cao
const searchBooks = (req, res) => {
  const {
    q, // Query string chung
    title, 
    author, 
    isbn, 
    category, 
    yearFrom, // Năm xuất bản từ
    yearTo, // Năm xuất bản đến
    minAvailable, // Số lượng available tối thiểu
    page = 1,
    limit = 10,
    sortBy = "id",
    order = "asc",
  } = req.query;

  let results = [...db.books];

  // General search (q)
  if (q) {
    const qLower = q.toLowerCase();
    results = results.filter(
      (b) =>
        b.title.toLowerCase().includes(qLower) ||
        b.author.toLowerCase().includes(qLower) ||
        b.isbn.includes(q) ||
        b.category.toLowerCase().includes(qLower)
    );
  }

  // Specific field searches
  if (title) {
    results = results.filter((b) =>
      b.title.toLowerCase().includes(title.toLowerCase())
    );
  }

  if (author) {
    results = results.filter((b) =>
      b.author.toLowerCase().includes(author.toLowerCase())
    );
  }

  if (isbn) {
    results = results.filter((b) => b.isbn.includes(isbn));
  }

  if (category) {
    results = results.filter(
      (b) => b.category.toLowerCase() === category.toLowerCase()
    );
  }

  // Year range filter
  if (yearFrom) {
    results = results.filter(
      (b) => b.publishedYear && b.publishedYear >= parseInt(yearFrom)
    );
  }

  if (yearTo) {
    results = results.filter(
      (b) => b.publishedYear && b.publishedYear <= parseInt(yearTo)
    );
  }

  // Minimum available filter
  if (minAvailable) {
    results = results.filter((b) => b.available >= parseInt(minAvailable));
  }

  // Sorting
  results.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];

    if (typeof aValue === "string") {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (order === "desc") {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    } else {
      return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
    }
  });

  // Pagination
  const pageNum = parseInt(page);
  const limitNum = parseInt(limit);
  const startIndex = (pageNum - 1) * limitNum;
  const endIndex = startIndex + limitNum;
  const totalBooks = results.length;
  const totalPages = Math.ceil(totalBooks / limitNum);
  const paginatedResults = results.slice(startIndex, endIndex);

  const pagination = {
    currentPage: pageNum,
    totalPages: totalPages,
    totalItems: totalBooks,
    itemsPerPage: limitNum,
    hasNextPage: pageNum < totalPages,
    hasPrevPage: pageNum > 1,
  };

  res.json({
    success: true,
    count: paginatedResults.length,
    pagination: pagination,
    filters: {
      q,
      title,
      author,
      isbn,
      category,
      yearFrom,
      yearTo,
      minAvailable,
      sortBy,
      order,
    },
    data: paginatedResults,
  });
};

module.exports = {
  getAllBooks,
  getBookById,
  createBook,
  updateBook,
  deleteBook,
  searchBooks,
};
