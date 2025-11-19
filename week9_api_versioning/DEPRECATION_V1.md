# Thông báo Ngưng Hỗ trợ (Deprecation): API v1

**Phiên bản bị ảnh hưởng:** API v1 (/payments v1)

**Ngày ngưng hỗ trợ (Retirement Date):** 2026-03-31

## Tại sao phải nâng cấp

- Bảo mật: `v2` chuyển sang xác thực theo chuẩn Bearer token (OAuth2-style) giúp tăng cường bảo mật và quản lý khóa tốt hơn.
- Hiệu năng & mở rộng: `v2` hỗ trợ pagination và định dạng phản hồi nhẹ/extended để giảm tải và dễ mở rộng.
- Tính năng mới: `v2` hỗ trợ `metadata`, định dạng `payer` thay cho `customer_email`, và partial updates (PATCH).

## Ảnh hưởng

- Các endpoint `v1` sẽ không còn được bảo trì và có thể bị chặn sau `2026-03-31`.
- Sau ngày này, chỉ `v2` nhận bản vá bảo mật và tính năng.

## Hành động cần làm (Call to Action)

Vui lòng **nâng cấp lên `v2`** trước `2026-03-31`. Xem hướng dẫn chi tiết di trú (Migration Guide):

- Local file: `./MIGRATION_V1_TO_V2.md`
- GitHub: `https://github.com/duyvu1105/INT3505E_01_demo/blob/main/week9_api_versioning/MIGRATION_V1_TO_V2.md`

Nếu cần hỗ trợ nâng cấp, open issue hoặc liên hệ nhóm phát triển.

## Tóm tắt thay đổi chính (Quick Checklist)

- Xác thực: thay `X-API-Key` hoặc header cũ bằng `Authorization: Bearer <TOKEN>`.
- Payload: thay `customer_email` -> `payer.email`; sử dụng `metadata` cho dữ liệu tuỳ chỉnh.
- Response: có thể yêu cầu `?format=extended` để nhận envelope (`data` + `meta`) và pagination (`limit`/`offset`).
- Error: kiểm tra cấu trúc lỗi mới (ví dụ `invalid_request`, `not_found`).

## Ví dụ nhanh (curl)

```bash
curl -X POST "https://api.example.com/v2/payments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"payer":{"email":"user@example.com","name":"User"}}'
```

---

File này được lưu trong `week9_api_versioning/` để dễ tìm. Nếu bạn muốn, tôi có thể mở Pull Request chứa thay đổi này.
