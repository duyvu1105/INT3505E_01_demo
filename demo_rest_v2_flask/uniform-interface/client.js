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
    return response.data;
  } catch (error) {
    console.error("Error fetching item:", error.message);
  }
}

async function createItem(item) {
  try {
    const response = await api.post("/items", item);
    console.log("Created item:", response.data);
  } catch (error) {
    console.error("Error creating item:", error.message);
  }
}

async function updateItem(id, item) {
  try {
    const response = await api.put(`/items/${id}`, item);
    console.log("Updated Item:", response.data);
  } catch (error) {
    console.error("Error updating item:", error.message);
  }
}

async function deleteItem(id) {
  try {
    const response = await api.delete(`/items/${id}`);
    console.log("Deleted Item:", id);
  } catch (error) {
    console.error("Error deleting item:", error.message);
  }
}

// Example usage
(async () => {
  console.log("=== Testing Uniform Interface (HATEOAS) - Flask ===\n");

  // Test 1: GET /items (with HATEOAS links)
  console.log("1. GET /items (with HATEOAS)");
  await getItems();
  console.log();

  // Test 2: GET /items/:id (with HATEOAS links)
  console.log("2. GET /items/1 (with HATEOAS)");
  const itemData = await getItem(1);
  console.log();

  // Test 3: Follow HATEOAS links
  console.log("3. Following HATEOAS links");
  if (itemData && itemData._links) {
    console.log("Available links:");
    for (const [linkName, linkInfo] of Object.entries(itemData._links)) {
      console.log(`  - ${linkName}:`, linkInfo);
    }
  }
  console.log();

  // Test 4: POST /items
  console.log("4. POST /items");
  await createItem({ name: "Item 3" });
  console.log();

  // Test 5: PUT /items/1
  console.log("5. PUT /items/1");
  await updateItem(1, { name: "Updated Item 1" });
  console.log();

  // Test 6: DELETE /items/2
  console.log("6. DELETE /items/2");
  await deleteItem(2);
  console.log();

  // Test 7: Verify changes
  console.log("7. GET /items (verify changes)");
  await getItems();
})();
