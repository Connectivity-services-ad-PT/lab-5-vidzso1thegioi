# Readiness Checklist – Lab 05 Analytics (team-analytics)

## Checklist 6 điểm sẵn sàng

- [x] DB đã khởi động và sẵn sàng (`pg_isready`) — timescale/timescaledb:latest-pg15
- [x] AI service đã tải mô hình và có health check trả 200 — http://localhost:9000/health
- [x] API có thể kết nối DB và AI — http://localhost:8000/health trả {"status":"ok"}
- [x] Các biến môi trường (.env) được đặt đúng, không dùng secret thật
- [x] `team-internal` network hoạt động: service gọi nội bộ qua tên container
- [x] Version/tag của image đúng quy ước — `analytics-service:v0.1.0-analytics`