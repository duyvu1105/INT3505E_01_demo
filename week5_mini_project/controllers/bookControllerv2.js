const db = require("../data/database");
const { Book } = require("../models");

/**
 * Books Controller v2 - Xử lý logic cho sách với cursor pagination
 */

// GET /api/books - Lấy tất cả sách với filter và cursor pagination
const getAllBooks = (req, res) => {
  const {
    category,
    author,
    available,
    cursor, // Base64-encoded cursor
    limit = 10, // Số items per page (mặc định: 10)
    sortBy = "id", // Sắp xếp theo field (id, title, author, publishedYear)
    order = "asc", // Thứ tự sắp xếp (asc, desc)
  } = req.query;

  // Validate and normalize
  const MAX_LIMIT = 100;
  let limitNum = parseInt(limit, 10) || 10;
  if (limitNum <= 0) limitNum = 10;
  if (limitNum > MAX_LIMIT) limitNum = MAX_LIMIT;

  const ALLOWED_SORT = [
    "id",
    "title",
    "author",
    "publishedYear",
    "available",
    "quantity",
  ];
  const sortField = ALLOWED_SORT.includes(sortBy) ? sortBy : "id";
  const sortOrder = order === "desc" ? "desc" : "asc";

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

  // Sorting with stable tie-breaker
  filteredBooks.sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    // Handle string comparison
    if (typeof aValue === "string") {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    // Primary sort
    let comparison = 0;
    if (aValue < bValue) comparison = -1;
    else if (aValue > bValue) comparison = 1;

    if (sortOrder === "desc") comparison = -comparison;

    // Tie-breaker by id for stable pagination
    if (comparison === 0) {
      comparison = a.id - b.id;
    }

    return comparison;
  });

  // Decode cursor and find start position
  let startIndex = 0;
  let paginatedBooks = filteredBooks.slice(startIndex, startIndex + limitNum);

  if (cursor) {
    try {
      const decoded = Buffer.from(cursor, "base64").toString("utf8");
      const parsed = JSON.parse(decoded);

      if (parsed.direction === "prev") {
        // For previous page, find LAST item with key < cursor key
        let cursorIndex = -1;

        // Duyệt ngược để tìm index LỚN NHẤT thỏa mãn điều kiện
        for (let i = filteredBooks.length - 1; i >= 0; i--) {
          const item = filteredBooks[i];
          const itemKey = item[sortField];
          const cursorKey = parsed.key;

          // Compare by sort key first
          let keyComparison = 0;
          if (typeof itemKey === "string") {
            keyComparison = itemKey
              .toLowerCase()
              .localeCompare(String(cursorKey).toLowerCase());
          } else {
            if (itemKey < cursorKey) keyComparison = -1;
            else if (itemKey > cursorKey) keyComparison = 1;
          }

          if (sortOrder === "desc") keyComparison = -keyComparison;

          // Find LAST item with key < cursor key (or same key but smaller id)
          if (keyComparison < 0) {
            cursorIndex = i;
            break;
          } else if (keyComparison === 0 && item.id < parsed.id) {
            cursorIndex = i;
            break;
          }
        }

        if (cursorIndex !== -1) {
          // Tính startIndex để lấy limitNum items kết thúc tại cursorIndex
          startIndex = Math.max(0, cursorIndex - limitNum + 1);
          paginatedBooks = filteredBooks.slice(startIndex, cursorIndex + 1);
        } else {
          // Không tìm thấy item nào < cursor → trả về empty
          paginatedBooks = [];
        }
      } else {
        // Forward pagination (default)
        startIndex = filteredBooks.findIndex((item) => {
          const itemKey = item[sortField];
          const cursorKey = parsed.key;

          // Compare by sort key first
          let keyComparison = 0;
          if (typeof itemKey === "string") {
            keyComparison = itemKey
              .toLowerCase()
              .localeCompare(String(cursorKey).toLowerCase());
          } else {
            if (itemKey < cursorKey) keyComparison = -1;
            else if (itemKey > cursorKey) keyComparison = 1;
          }

          if (sortOrder === "desc") keyComparison = -keyComparison;

          // If sort keys are equal, compare by id
          if (keyComparison === 0) {
            return item.id > parsed.id;
          }

          return keyComparison > 0;
        });
        paginatedBooks = filteredBooks.slice(startIndex, startIndex + limitNum);
      }

      if (startIndex === -1) startIndex = filteredBooks.length;
    } catch (err) {
      return res.status(400).json({
        success: false,
        message: "Invalid cursor format",
      });
    }
  }

  // Build nextCursor if there are more items
  let nextCursor = null;
  if (startIndex + limitNum < filteredBooks.length) {
    const lastItem = paginatedBooks[paginatedBooks.length - 1];
    const cursorObj = {
      key: lastItem[sortField],
      id: lastItem.id,
      direction: "next",
    };
    nextCursor = Buffer.from(JSON.stringify(cursorObj)).toString("base64");
  }

  // Build prevCursor if we're not at the beginning
  let prevCursor = null;
  if (startIndex > 0) {
    // Use the first item of the current page for prev cursor
    const firstItem = paginatedBooks[0];
    const prevCursorObj = {
      key: firstItem[sortField],
      id: firstItem.id,
      direction: "prev",
    };
    prevCursor = Buffer.from(JSON.stringify(prevCursorObj)).toString("base64");
  }

  res.json({
    success: true,
    count: paginatedBooks.length,
    itemsPerPage: limitNum,
    nextCursor,
    prevCursor,
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
  // Validate using Book model
  const validation = Book.validate(req.body);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: validation.errors,
    });
  }

  // Kiểm tra ISBN đã tồn tại
  const existingBook = db.books.find((b) => b.isbn === req.body.isbn);
  if (existingBook) {
    return res.status(400).json({
      success: false,
      message: "ISBN đã tồn tại",
    });
  }

  // Tạo book mới sử dụng Book model
  const newBook = Book.create(req.body, db.getNextBookId());
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

  const bookIndex = db.books.findIndex((b) => b.id === parseInt(id));

  if (bookIndex === -1) {
    return res.status(404).json({
      success: false,
      message: "Không tìm thấy sách",
    });
  }

  // Validate using Book model
  const validation = Book.validate(req.body);
  if (!validation.isValid) {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: validation.errors,
    });
  }

  const currentBook = db.books[bookIndex];
  const borrowed = Book.getBorrowedCount(currentBook);

  // Update book với data mới
  const { title, author, isbn, publishedYear, category, quantity } = req.body;
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

  // Kiểm tra sách có đang được mượn không bằng Book model
  const book = db.books[bookIndex];
  if (Book.hasBorrowedBooks(book)) {
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

// GET /api/books/search - Tìm kiếm nâng cao với cursor pagination
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
    cursor, // Base64-encoded cursor
    limit = 10,
    sortBy = "id",
    order = "asc",
  } = req.query;

  const MAX_LIMIT = 100;
  let limitNum = parseInt(limit, 10) || 10;
  if (limitNum <= 0) limitNum = 10;
  if (limitNum > MAX_LIMIT) limitNum = MAX_LIMIT;

  const ALLOWED_SORT = [
    "id",
    "title",
    "author",
    "publishedYear",
    "available",
    "quantity",
  ];
  const sortField = ALLOWED_SORT.includes(sortBy) ? sortBy : "id";
  const sortOrder = order === "desc" ? "desc" : "asc";

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

  // Sorting with stable tie-breaker
  results.sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (typeof aValue === "string") {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    // Primary sort
    let comparison = 0;
    if (aValue < bValue) comparison = -1;
    else if (aValue > bValue) comparison = 1;

    if (sortOrder === "desc") comparison = -comparison;

    // Tie-breaker by id for stable pagination
    if (comparison === 0) {
      comparison = a.id - b.id;
    }

    return comparison;
  });

  // Decode cursor and find start position
  let startIndex = 0;
  let paginatedResults = results.slice(startIndex, startIndex + limitNum);

  if (cursor) {
    try {
      const decoded = Buffer.from(cursor, "base64").toString("utf8");
      const parsed = JSON.parse(decoded);

      if (parsed.direction === "prev") {
        // For previous page, find LAST item with key < cursor key
        let cursorIndex = -1;

        // Duyệt ngược để tìm index LỚN NHẤT thỏa mãn điều kiện
        for (let i = results.length - 1; i >= 0; i--) {
          const item = results[i];
          const itemKey = item[sortField];
          const cursorKey = parsed.key;

          // Compare by sort key first
          let keyComparison = 0;
          if (typeof itemKey === "string") {
            keyComparison = itemKey
              .toLowerCase()
              .localeCompare(String(cursorKey).toLowerCase());
          } else {
            if (itemKey < cursorKey) keyComparison = -1;
            else if (itemKey > cursorKey) keyComparison = 1;
          }

          if (sortOrder === "desc") keyComparison = -keyComparison;

          // Find LAST item with key < cursor key (or same key but smaller id)
          if (keyComparison < 0) {
            cursorIndex = i;
            break;
          } else if (keyComparison === 0 && item.id < parsed.id) {
            cursorIndex = i;
            break;
          }
        }

        if (cursorIndex !== -1) {
          // Tính startIndex để lấy limitNum items kết thúc tại cursorIndex
          startIndex = Math.max(0, cursorIndex - limitNum + 1);
          paginatedResults = results.slice(startIndex, cursorIndex + 1);
        } else {
          // Không tìm thấy item nào < cursor → trả về empty
          paginatedResults = [];
        }
      } else {
        // Forward pagination (default)
        startIndex = results.findIndex((item) => {
          const itemKey = item[sortField];
          const cursorKey = parsed.key;

          // Compare by sort key first
          let keyComparison = 0;
          if (typeof itemKey === "string") {
            keyComparison = itemKey
              .toLowerCase()
              .localeCompare(String(cursorKey).toLowerCase());
          } else {
            if (itemKey < cursorKey) keyComparison = -1;
            else if (itemKey > cursorKey) keyComparison = 1;
          }

          if (sortOrder === "desc") keyComparison = -keyComparison;

          // If sort keys are equal, compare by id
          if (keyComparison === 0) {
            return item.id > parsed.id;
          }

          return keyComparison > 0;
        });
        paginatedResults = results.slice(startIndex, startIndex + limitNum);
      }

      if (startIndex === -1) startIndex = results.length;
    } catch (err) {
      return res.status(400).json({
        success: false,
        message: "Invalid cursor format",
      });
    }
  }

  // Build nextCursor if there are more items
  let nextCursor = null;
  if (startIndex + limitNum < results.length) {
    const lastItem = paginatedResults[paginatedResults.length - 1];
    const cursorObj = {
      key: lastItem[sortField],
      id: lastItem.id,
      direction: "next",
    };
    nextCursor = Buffer.from(JSON.stringify(cursorObj)).toString("base64");
  }

  let prevCursor = null;
  if (startIndex > 0) {
    const firstItem = paginatedResults[0];
    const prevCursorObj = {
      key: firstItem[sortField],
      id: firstItem.id,
      direction: "prev",
    };
    prevCursor = Buffer.from(JSON.stringify(prevCursorObj)).toString("base64");
  }

  res.json({
    success: true,
    count: paginatedResults.length,
    itemsPerPage: limitNum,
    nextCursor,
    prevCursor,
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

//http://localhost:3000/api/books?limit=2&sortBy=id
