const express = require('express');
const jwt = require('jsonwebtoken');

const SECRET_KEY = 'my-secret-key-2025';
const app = express();
const PORT = 3000;

app.use(express.json());

const users = [
    { id: 1, username: 'admin', password: '123', role: 'admin' },
    { id: 2, username: 'user', password: '123', role: 'user' }
];

// Sample data
let items = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' },
];
// Stateless: Mỗi request là độc lập
// Server không cần lưu trạng thái giữa các request

app.get('/items', (req, res) => {
    res.json(items);
});

app.get('/items/:id', (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    if (!item) return res.status(404).send('Item not found');

    res.json(item);
});

app.post('/items', authenticateToken, (req, res) => {
    const newItem = {
        id: items.length + 1,
        name: req.body.name,
    };
    items.push(newItem);
    res.status(201).json(newItem);
});

app.put('/items/:id', authenticateToken, (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    if (!item) return res.status(404).send('Item not found');
    
    item.name = req.body.name;
    res.json(item);
});

// Chỉ admin mới được phép xóa
app.delete('/items/:id', authenticateToken, (req, res) => {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Forbidden: Admins only' });
    }

    const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
    if (itemIndex === -1) return res.status(404).send('Item not found');
    
    items.splice(itemIndex, 1);
    res.status(204).send();
});


// Verify JWT Token
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
    
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, SECRET_KEY);
        req.user = decoded;
        console.log('Authenticated user:', decoded.username);
        next();
    } catch (error) {
        return res.status(403).json({ error: 'Invalid or expired token' });
    }
}

//  POST /login - Tạo JWT token khi đăng nhập
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    console.log(' Login attempt:', { username });
    
    // Tìm user
    const user = users.find(u => u.username === username && u.password === password);
    
    if (!user) {
        console.log(' Invalid credentials');
        return res.status(401).json({ error: 'Invalid username or password' });
    }
    
    // Tạo JWT token
    const token = jwt.sign(
        { 
            userId: user.id,
            username: user.username,
            role: user.role
        },
        SECRET_KEY,
        { expiresIn: '1h' }
    );
    
    console.log(' Login successful for:', user.username);
    
    res.json({ 
        message: 'Login successful',
        token,
        user: {
            id: user.id,
            username: user.username,
            role: user.role
        },
        expiresIn: 3600
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});