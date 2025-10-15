const axios = require("axios");

let authToken = null;

const BASE_URL = "http://localhost:5000";

// Axios instance với auto token
const api = axios.create({
  baseURL: BASE_URL,
});

// Interceptor: Chặn mọi request trước khi gửi đi
// Token sẽ được tự động thêm vào header Authorization
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers["Authorization"] = `Bearer ${authToken}`;
  }
  return config;
});

async function login(username, password) {
  try {
    const response = await api.post("/login", { username, password });
    authToken = response.data.token;
    console.log("Logged in successfully");
    console.log("User:", response.data.user);
    console.log("Token saved\n");
    return response.data;
  } catch (error) {
    console.error("Login failed:", error.response?.data || error.message);
  }
}

async function getItems() {
  try {
    const response = await api.get("/items");
    console.log("Items:", response.data);
  } catch (error) {
    console.error(
      "Error fetching items:",
      error.response?.data || error.message
    );
  }
}

async function createItem(item) {
  try {
    const response = await api.post("/items", item);
    console.log("Created item:", response.data);
  } catch (error) {
    console.error(
      "Error creating item:",
      error.response?.data || error.message
    );
  }
}

async function updateItem(id, item) {
  try {
    const response = await api.put(`/items/${id}`, item);
    console.log("Updated Item:", response.data);
  } catch (error) {
    console.error(
      "Error updating item:",
      error.response?.data || error.message
    );
  }
}

async function deleteItem(id) {
  try {
    const response = await api.delete(`/items/${id}`);
    console.log("Deleted Item:", id);
  } catch (error) {
    console.error(
      "Error deleting item:",
      error.response?.data || error.message
    );
  }
}

// Example usage
(async () => {
  // Test 1: Login as user
  console.log("1. Login as user");
  await login("user", "123");
  const userToken = authToken;

  // Test 2: Login as admin
  console.log("2. Login as admin");
  await login("admin", "123");
  const adminToken = authToken;

  // Test 3: GET /items (no auth needed)
  authToken = null;
  console.log("3. GET /items (no auth)");
  await getItems();
  console.log();

  // Test 4: POST /items (with user token)
  authToken = userToken;
  console.log("4. POST /items (with user token)");
  await createItem({ name: "Item 3" });
  console.log();

  // Test 5: PUT /items/1 (with user token)
  console.log("5. PUT /items/1 (with user token)");
  await updateItem(1, { name: "Updated Item 1" });
  console.log();

  // Test 6: DELETE /items/1 (with user token - should fail)
  console.log("6. DELETE /items/1 (with user token - should fail)");
  await deleteItem(1);
  console.log();

  // Test 7: DELETE /items/1 (with admin token - should succeed)
  authToken = adminToken;
  console.log("7. DELETE /items/1 (with admin token - should succeed)");
  await deleteItem(1);
  console.log();

  // Test 8: GET /items (verify deletion)
  authToken = null;
  console.log("8. GET /items (verify deletion)");
  await getItems();
  console.log();

  // Test 9: Request without token
  console.log("9. POST /items (no token - should fail)");
  await createItem({ name: "Item 4" });
})();
