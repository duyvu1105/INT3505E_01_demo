const API_BASE = 'http://localhost:5000';

// State management
let books = [];
let users = [];
let loans = [];
let currentEditingBook = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    checkHealth();
    loadAllData();
    setupEventListeners();
});

// Tab functionality
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
    
    // Load data for specific tab
    if (tabName === 'books') loadBooks();
    else if (tabName === 'users') loadUsers();
    else if (tabName === 'loans') loadLoans();
}

// Health check
async function checkHealth() {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Hệ thống hoạt động';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Hệ thống lỗi';
    }
}

// API calls
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'API call failed');
        }
        
        return response.status === 204 ? null : await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert(`Lỗi: ${error.message}`);
        throw error;
    }
}

// Load data functions
async function loadAllData() {
    await Promise.all([loadBooks(), loadUsers(), loadLoans()]);
}

async function loadBooks() {
    try {
        books = await apiCall('/books');
        renderBooks();
        updateBorrowBookSelect();
    } catch (error) {
        console.error('Failed to load books:', error);
    }
}

async function loadUsers() {
    try {
        users = await apiCall('/users');
        renderUsers();
        updateBorrowUserSelect();
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

async function loadLoans() {
    try {
        loans = await apiCall('/loans');
        renderLoans();
        updateReturnLoanSelect();
    } catch (error) {
        console.error('Failed to load loans:', error);
    }
}

// Render functions
function renderBooks() {
    const grid = document.getElementById('booksGrid');
    grid.innerHTML = books.map(book => `
        <div class="book-card">
            <div class="book-title">${book.title}</div>
            <div class="book-author">Tác giả: ${book.author}</div>
            <div class="book-info">
                <span>Tổng: ${book.total_copies}</span>
                <span class="available">Còn: ${book.available}</span>
            </div>
            <div class="book-actions">
                <button class="btn btn-warning" onclick="editBook(${book.id})">Sửa</button>
                <button class="btn btn-danger" onclick="deleteBook(${book.id})">Xóa</button>
            </div>
        </div>
    `).join('');
}

function renderUsers() {
    const list = document.getElementById('usersList');
    list.innerHTML = users.map(user => `
        <div class="user-card">
            <div class="user-info">
                <h4>${user.name}</h4>
                <div class="user-id">ID: ${user.id}</div>
            </div>
        </div>
    `).join('');
}

function renderLoans() {
    const list = document.getElementById('loansList');
    list.innerHTML = loans.map(loan => {
        const book = books.find(b => b.id === loan.book_id);
        const user = users.find(u => u.id === loan.user_id);
        const isOverdue = new Date(loan.due_at) < new Date() && !loan.returned_at;
        const status = loan.returned_at ? 'returned' : (isOverdue ? 'overdue' : 'active');
        
        return `
            <div class="loan-card ${status}">
                <div class="loan-header">
                    <div>
                        <strong>${book?.title || 'N/A'}</strong> - ${user?.name || 'N/A'}
                    </div>
                    <span class="loan-status status-${status}">
                        ${status === 'returned' ? 'Đã trả' : status === 'overdue' ? 'Quá hạn' : 'Đang mượn'}
                    </span>
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    <div>Mượn: ${formatDate(loan.borrowed_at)}</div>
                    <div>Hạn trả: ${formatDate(loan.due_at)}</div>
                    ${loan.returned_at ? `<div>Đã trả: ${formatDate(loan.returned_at)}</div>` : ''}
                </div>
                ${!loan.returned_at ? `
                    <div style="margin-top: 10px;">
                        <button class="btn btn-secondary" onclick="returnBook(${loan.id})">Trả sách</button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Modal functions
function showAddBookModal() {
    currentEditingBook = null;
    document.getElementById('bookModalTitle').textContent = 'Thêm sách mới';
    document.getElementById('bookForm').reset();
    document.getElementById('bookModal').style.display = 'block';
}

function showAddUserModal() {
    document.getElementById('userForm').reset();
    document.getElementById('userModal').style.display = 'block';
}

function showBorrowModal() {
    updateBorrowBookSelect();
    updateBorrowUserSelect();
    document.getElementById('borrowForm').reset();
    document.getElementById('borrowModal').style.display = 'block';
}

function showReturnModal() {
    updateReturnLoanSelect();
    document.getElementById('returnForm').reset();
    document.getElementById('returnModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Book operations
async function editBook(bookId) {
    const book = books.find(b => b.id === bookId);
    if (!book) return;
    
    currentEditingBook = book;
    document.getElementById('bookModalTitle').textContent = 'Sửa thông tin sách';
    document.getElementById('bookTitle').value = book.title;
    document.getElementById('bookAuthor').value = book.author;
    document.getElementById('totalCopies').value = book.total_copies;
    document.getElementById('bookModal').style.display = 'block';
}

async function deleteBook(bookId) {
    if (!confirm('Bạn có chắc chắn muốn xóa sách này?')) return;
    
    try {
        await apiCall(`/books/${bookId}`, { method: 'DELETE' });
        await loadBooks();
    } catch (error) {
        console.error('Failed to delete book:', error);
    }
}

async function returnBook(loanId) {
    try {
        await apiCall('/return', {
            method: 'POST',
            body: JSON.stringify({ loan_id: loanId })
        });
        await loadAllData();
    } catch (error) {
        console.error('Failed to return book:', error);
    }
}

// Update select options
function updateBorrowBookSelect() {
    const select = document.getElementById('borrowBookSelect');
    select.innerHTML = '<option value="">-- Chọn sách --</option>' +
        books.filter(book => book.available > 0)
             .map(book => `<option value="${book.id}">${book.title} (Còn: ${book.available})</option>`)
             .join('');
}

function updateBorrowUserSelect() {
    const select = document.getElementById('borrowUserSelect');
    select.innerHTML = '<option value="">-- Chọn người dùng --</option>' +
        users.map(user => `<option value="${user.id}">${user.name}</option>`).join('');
}

function updateReturnLoanSelect() {
    const select = document.getElementById('returnLoanSelect');
    const activeLoans = loans.filter(loan => !loan.returned_at);
    select.innerHTML = '<option value="">-- Chọn lượt mượn --</option>' +
        activeLoans.map(loan => {
            const book = books.find(b => b.id === loan.book_id);
            const user = users.find(u => u.id === loan.user_id);
            return `<option value="${loan.id}">${book?.title} - ${user?.name} (${formatDate(loan.borrowed_at)})</option>`;
        }).join('');
}

// Event listeners
function setupEventListeners() {
    // Book form
    document.getElementById('bookForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            title: document.getElementById('bookTitle').value,
            author: document.getElementById('bookAuthor').value,
            total_copies: parseInt(document.getElementById('totalCopies').value)
        };
        
        try {
            if (currentEditingBook) {
                await apiCall(`/books/${currentEditingBook.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(formData)
                });
            } else {
                await apiCall('/books', {
                    method: 'POST',
                    body: JSON.stringify(formData)
                });
            }
            closeModal('bookModal');
            await loadBooks();
        } catch (error) {
            console.error('Failed to save book:', error);
        }
    });
    
    // User form
    document.getElementById('userForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            name: document.getElementById('userName').value
        };
        
        try {
            await apiCall('/users', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            closeModal('userModal');
            await loadUsers();
        } catch (error) {
            console.error('Failed to create user:', error);
        }
    });
    
    // Borrow form
    document.getElementById('borrowForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            book_id: parseInt(document.getElementById('borrowBookSelect').value),
            user_id: parseInt(document.getElementById('borrowUserSelect').value),
            days: parseInt(document.getElementById('borrowDays').value)
        };
        
        try {
            await apiCall('/borrow', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            closeModal('borrowModal');
            await loadAllData();
        } catch (error) {
            console.error('Failed to borrow book:', error);
        }
    });
    
    // Return form
    document.getElementById('returnForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const loanId = parseInt(document.getElementById('returnLoanSelect').value);
        
        try {
            await apiCall('/return', {
                method: 'POST',
                body: JSON.stringify({ loan_id: loanId })
            });
            closeModal('returnModal');
            await loadAllData();
        } catch (error) {
            console.error('Failed to return book:', error);
        }
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// Filter loans
function filterLoans() {
    const filter = document.getElementById('loanFilter').value;
    let filteredLoans = loans;
    
    if (filter === 'active') {
        filteredLoans = loans.filter(loan => !loan.returned_at);
    } else if (filter === 'returned') {
        filteredLoans = loans.filter(loan => loan.returned_at);
    }
    
    loans = filteredLoans;
    renderLoans();
    
    // Restore original loans data
    setTimeout(() => loadLoans(), 100);
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleString('vi-VN');
}