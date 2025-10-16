const axios = require("axios");

const BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: BASE_URL,
});

async function getItems() {
  try {
    const response = await api.get("/items");
    console.log("Items:", response.data);
    console.log("Cache-Control:", response.headers["cache-control"]);
  } catch (error) {
    console.error("Error fetching items:", error.message);
  }
}

async function getItem(id) {
  try {
    const response = await api.get(`/items/${id}`);
    console.log("Item:", response.data);
    console.log("Cache-Control:", response.headers["cache-control"]);
  } catch (error) {
    console.error("Error fetching item:", error.message);
  }
}

// Example usage
(async () => {
  console.log("1. GET /items (with cache)");
  await getItems();
  console.log();

  console.log("2. GET /items/1 (no cache)");
  await getItem(1);
  console.log();
})();
