const axios = require('axios');

// Dùng jwt để thay thế cho stateless
const jwt = require('jsonwebtoken');
let authToken = null;


const BASE_URL = 'http://localhost:3000'; 

// Axios instance với auto token
const api = axios.create({
    baseURL: BASE_URL
});

// user login sẽ trả về token
// token này sẽ được lưu trong biến authToken và được gửi kèm trong header Authorization của các request sau
// Interceptor: Chặn mọi request trước khi gửi đi
api.interceptors.request.use(config => {
    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    return config;
});

async function login(username, password) {
    const response = await api.post('/login', { username, password });
    authToken = response.data.token;
    console.log(' Logged in, token saved');
}


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
        console.log('Deleted Item:', response.data);
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

// Example usage
(async () => {
    await login('admin', '123');


    await getItems();
    await createItem({ name: 'New Item', description: 'This is a new item.' });
    await updateItem(1, { name: 'Updated Item', description: 'This item has been updated.' });
    await deleteItem(1);
})();