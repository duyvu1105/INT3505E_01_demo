const axios = require("axios");

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: BASE_URL,
});

async function getItems() {
  try {
    const response = await api.get("/items");
    console.log("Items:", response.data);
  } catch (error) {
    console.error("Error fetching items:", error.message);
  }
}

async function getItem(id) {
  try {
    const response = await api.get(`/items/${id}`);
    console.log("Item:", response.data);
  } catch (error) {
    console.error("Error fetching item:", error.message);
  }
}

// Example usage
(async () => {
  console.log("1. GET /items");
  await getItems();
  console.log();

  console.log("2. GET /items/1");
  await getItem(1);
  console.log();

  console.log("3. GET /items/999 (not found)");
  await getItem(999);
  console.log();
})();
