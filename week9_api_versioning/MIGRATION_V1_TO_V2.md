# Migration Guide: V1 → V2

Mục đích: hướng dẫn chi tiết để nâng cấp client sử dụng API `v1` sang `v2`.

## Tổng quan thay đổi

- Xác thực: `v2` dùng `Authorization: Bearer <TOKEN>` (Bearer token). Vui lòng yêu cầu token tương ứng từ hệ thống quản lý API/Quản trị.
- Payload: `payer` object thay cho `customer_email`.
- Response: `v2` hỗ trợ `?format=extended` để nhận envelope `{data, meta}` cùng pagination. Nếu không dùng `extended`, vẫn có format backward-compatible.
- Endpoints: đường dẫn cơ bản `/v2/payments` và `/v2/payments/<id>`; phương thức PATCH hỗ trợ partial update.

## 1) Xác thực

- Trước (v1) có thể dùng header `X-API-Key: <KEY>` hoặc header khác.
- Giờ (v2) dùng header:

```
Authorization: Bearer <TOKEN>
```

Ví dụ (curl):

```bash
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"amount":200, "payer":{"email":"a@b.com"}}' \
     https://api.example.com/v2/payments
```

## 2) Mapping payload (v1 -> v2)

- Nếu client gửi `customer_email` (v1), chuyển thành `payer.email`:
  - v1: `{ "amount": 100, "customer_email": "x@y.com" }`
  - v2: `{ "amount": 100, "payer": { "email": "x@y.com" } }`
- `amount` phải là `integer`. Nếu bạn dùng float hoặc decimal ở client, chuyển sang cents hoặc integer theo spec của dịch vụ.
- `metadata` có thể được thêm vào bất kỳ request nào: `{ "metadata": {"order_id": "123"} }`

## 3) Response & Error handling

- Standard (backward compatible):
  ```json
  { "success": true, "payment": { ... } }
  ```
- Extended (mới):
  - Thêm query param `?format=extended` để nhận:
    ```json
    { "data": { ... }, "meta": { "version": "v2", "request_id": "..." } }
    ```
- Pagination cho danh sách payments khi dùng `format=extended`: `?limit=N&offset=M`.
- Lỗi có cấu trúc chi tiết:
  ```json
  { "error": { "type": "invalid_request", "message": "..." } }
  ```

## 4) Ví dụ nâng cấp cho từng hành động

- Create payment (v1 -> v2):

  - v1:
    ```bash
    curl -X POST https://api.example.com/v1/payments \
      -H "X-API-Key: $KEY" \
      -H "Content-Type: application/json" \
      -d '{"amount":100, "customer_email":"u@e.com"}'
    ```
  - v2:
    ```bash
    curl -X POST https://api.example.com/v2/payments \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"amount":100,"payer":{"email":"u@e.com","name":"User"}}'
    ```

- Get payment:

  - thêm `?format=extended` nếu muốn meta:
    `GET /v2/payments/<id>?format=extended`

- List payments with pagination:

  ```
  GET /v2/payments?format=extended&limit=20&offset=0
  ```

- Update (PATCH):
  ```bash
  curl -X PATCH https://api.example.com/v2/payments/<id> \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status":"completed","metadata":{"ref":"abc"}}'
  ```

## 5) Kiểm tra & triển khai

- Test các kịch bản sau trên môi trường staging trước khi chuyển production:
  - Tạo payment mới với `payer.email`.
  - Gọi list với pagination.
  - Cập nhật status bằng `PATCH`.
  - Kiểm thử lỗi (missing email, invalid amount …).
- Cập nhật documentations và SDKs nội bộ để dùng header Bearer.

## 6) Timeline

- Hiện tại: bắt đầu migrate và thử nghiệm trên `v2`.
- **2026-03-31**: `v1` retirement — sau ngày này `v1` sẽ không được hỗ trợ.

## 7) Hỗ trợ

- Kiểm tra `week9_api_versioning/controllers/v2_controller.py` để xem ví dụ xử lý `v2`.
- Nếu cần, tôi có thể mở PR hỗ trợ thay đổi sample client hoặc SDK.

---

File này lưu trong `week9_api_versioning/` và được đồng bộ với `DEPRECATION_V1.md`.
