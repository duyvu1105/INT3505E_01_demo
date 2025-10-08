const express = require('express');

const app = express();
const PORT = 3000;

app.use(express.json());

// Sample data
let items = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' },
];

app.get('/items', (req, res) => {
    const response = {
        data: items,
        _links: {
            self: { href: '/items' },
            find: { href: '/items/{id}', method: 'GET'}
        }
    };
    res.json(response);

});

// 1. Tài nguyên được xác định bằng URL
// 2. Thao tác qua biểu diễn (server trả về JSON)
// 3. Thông điệp tự mô tả (Mỗi message chứa đủ thông tin)
// 4. Phản hồi bao gồm các liên kết (HATEOAS)
app.get('/items/:id', (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    if (!item) return res.status(404).send('Item not found');
    
    // HATEOAS: Thêm links để client biết các hành động có thể thực hiện
    const response = {
        ...item,
        _links: {
            self: { href: `/items/${item.id}` },           // Link đến chính nó
            update: { href: `/items/${item.id}`, method: 'PUT' },    // Link để update
            delete: { href: `/items/${item.id}`, method: 'DELETE' }, // Link để delete
            collection: { href: '/items' }                 // Link về collection
        }
    };
    
    res.json(response);
});

app.post('/items', (req, res) => {
    const newItem = {
        id: items.length + 1,
        name: req.body.name,
    };
    items.push(newItem);
    res.status(201).json(newItem);
});

app.put('/items/:id', (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    if (!item) return res.status(404).send('Item not found');
    
    item.name = req.body.name;
    res.json(item);
});

app.delete('/items/:id', (req, res) => {
    
    const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
    if (itemIndex === -1) return res.status(404).send('Item not found');
    
    items.splice(itemIndex, 1);
    res.status(204).send();
});


// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});