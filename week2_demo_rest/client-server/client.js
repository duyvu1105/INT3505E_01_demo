const axios = require('axios');

const BASE_URL = 'http://localhost:3000'; 

const api = axios.create({
    baseURL: BASE_URL
});

async function getItems() {
    try {
        const response = await api.get('/items');
        console.log('Items:', response.data);
    } catch (error) {
        console.error('Error fetching items:', error);
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
    await getItem(1);
})();