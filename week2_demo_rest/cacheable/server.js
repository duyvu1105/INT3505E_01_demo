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
    res.set('Cache-Control', 'public, max-age=3600'); // Cache for 1 hour
    res.json(items);
});


app.get('/items/:id', (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    if (!item) return res.status(404).send('Item not found');
    res.set('Cache-Control', 'no-cache'); // No cache
    res.json(item);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});