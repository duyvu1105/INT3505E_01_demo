/**
 * In-Memory Data Store
 * Trong thực tế, đây sẽ được thay thế bằng database
 */

let books = [
  {
    id: 1,
    title: "Clean Code",
    author: "Robert C. Martin",
    isbn: "9780132350884",
    publishedYear: 2008,
    category: "Programming",
    quantity: 5,
    available: 5,
  },
  {
    id: 2,
    title: "The Pragmatic Programmer",
    author: "Andrew Hunt, David Thomas",
    isbn: "9780201616224",
    publishedYear: 1999,
    category: "Programming",
    quantity: 3,
    available: 3,
  },
  {
    id: 3,
    title: "Design Patterns",
    author: "Gang of Four",
    isbn: "9780201633610",
    publishedYear: 1994,
    category: "Programming",
    quantity: 4,
    available: 4,
  },
  {
    id: 4,
    title: "Introduction to Algorithms",
    author: "Thomas H. Cormen",
    isbn: "9780262033848",
    publishedYear: 2009,
    category: "Algorithms",
    quantity: 2,
    available: 2,
  },
  {
    id: 5,
    title: "JavaScript: The Good Parts",
    author: "Douglas Crockford",
    isbn: "9780596517748",
    publishedYear: 2008,
    category: "Programming",
    quantity: 6,
    available: 6,
  },
  {
    id: 6,
    title: "You Don't Know JS",
    author: "Kyle Simpson",
    isbn: "9781491904244",
    publishedYear: 2015,
    category: "Programming",
    quantity: 7,
    available: 7,
  },
];

let users = [
  {
    id: 1,
    name: "Nguyễn Văn A",
    email: "nguyenvana@example.com",
    phone: "0123456789",
    address: "Hà Nội",
    membershipDate: "2024-01-01",
    status: "active",
    borrowedBooks: [],
  },
  {
    id: 2,
    name: "Trần Thị B",
    email: "tranthib@example.com",
    phone: "0987654321",
    address: "TP. HCM",
    membershipDate: "2024-02-15",
    status: "active",
    borrowedBooks: [],
  },
];

let borrowings = [];

// Counters for auto-increment IDs
let nextBookId = 4;
let nextUserId = 3;
let nextBorrowingId = 1;

module.exports = {
  books,
  users,
  borrowings,
  getNextBookId: () => nextBookId++,
  getNextUserId: () => nextUserId++,
  getNextBorrowingId: () => nextBorrowingId++,
};
