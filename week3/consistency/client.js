// Thư viện client chỉ cần "nắm quy tắc" (data, pagination)
// Viết MỘT hàm duy nhất
async function fetchList(endpoint) {
  const res = await fetch(`http://localhost:3001${endpoint}`);
  const json = await res.json();

  // Thư viện chỉ cần biết quy tắc: dữ liệu luôn nằm trong key 'data'
  // Nó không cần biết data đó là 'user' hay 'product'
  return json.data;
}

// Dùng chung 1 hàm cho mọi endpoint
const users2 = await fetchList('/users');
console.log("Data Users (Consistent):", users2);

const products2 = await fetchList('/products');
console.log("Data Products (Consistent):", products2[0].name); // 'name' thay vì 'productName'