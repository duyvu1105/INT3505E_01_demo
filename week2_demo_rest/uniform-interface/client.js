const axios = require('axios');

const BASE_URL = 'http://localhost:3000'; 

const api = axios.create({
    baseURL: BASE_URL
});

async function getItems() {
    try {
        // Client giao tiếp với server qua API
        const response = await api.get('/items');
        console.log('Items:', response.data);
    } catch (error) {
        console.error('Error fetching items:', error);
    }
}


async function updateItem(id, item) {
    try {
        const response = await api.put(`/items/${id}`, item);
        console.log('Updated Item:', response.data);
    } catch (error) {
        console.error('Error updating item:', error);
    }
}

async function deleteItem(id) {
    try {
        const response = await api.delete(`/items/${id}`);
        console.log('Deleted Item:', id);
    } catch (error) {
        console.error('Error deleting item:', error);
    }
}

async function createItem(item) {
    try {
        const response = await api.post('/items', item, {
            headers: {
                'Cache-Control': 'no-cache' // không cache cho POST request
            }
        });
        console.log('Created item:', response.data);
    } catch (error) {
        console.error('Error creating item:', error);
    }
}
async function getItem(id) {
    try {
        const response = await api.get(`/items/${id}`);
        console.log('Item:', response.data);
    } catch (error) {
        console.error('Error fetching item:', error);
    }
}

// Example usage
(async () => {

    await getItems();
    await createItem({ name: 'New Item', description: 'This is a new item.' });
    await updateItem(1, { name: 'Updated Item', description: 'This item has been updated.' });
    await deleteItem(1);
    await getItem(2);
})();