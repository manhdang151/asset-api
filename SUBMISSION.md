# Homework Submission

**Họ tên:** **ĐẶNG HOÀNG MẠNH**

**Ngôn ngữ sử dụng:** Python 3.11 + FastAPI

---

## Cách cài đặt và chạy project

### Yêu cầu
- Python 3.11
- Git

### Các bước cài đặt

```bash
# 1. Clone repository
git clone <your-repo-url>
cd asset-api

# 2. Tạo môi trường ảo
py -3.11 -m venv venv

# 3. Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Cài đặt thư viện
pip install fastapi uvicorn

# 5. Chạy server
uvicorn main:app --reload --port 8080
```

Server sẽ chạy tại: http://localhost:8080

Trang tài liệu API (Swagger UI): http://localhost:8080/docs

---

## Cấu trúc project

```
asset-api/
├── main.py                    # Entry point - khởi động server, wire up các layer
├── model/
│   └── asset.py               # Entity layer - định nghĩa Asset model
├── storage/
│   └── asset_storage.py       # Infrastructure layer - lưu data trong RAM với lock
├── service/
│   └── asset_service.py       # Use case layer - business logic, validation
├── handler/
│   └── asset_handler.py       # Presentation layer - nhận/trả HTTP request
├── homeworks/
│   └── submissions/           # Screenshots minh chứng
└── SUBMISSION.md
```

### Lý do chọn Python + FastAPI
- FastAPI hỗ trợ Clean Architecture rõ ràng
- Tự động sinh trang docs tại `/docs` để test tiện
- Pydantic tích hợp sẵn cho model và validation

---

## Các bài đã hoàn thành

- [x] Bài 1: Statistics APIs (20 điểm)
- [x] Bài 2: Batch Create Assets (25 điểm)
- [x] Bài 3: Batch Delete Assets (20 điểm)
- [x] Bài 4: Concurrent-safe Create (25 điểm)
- [x] Bài 5: In-memory Health Check (15 điểm)
- [x] Bài 6: Pagination & Filtering (15 điểm) - BONUS
- [x] Bài 7: Search by Name (10 điểm) - BONUS

---

## Bài 1: Statistics APIs (20 điểm)

### Giải pháp
- `GET /assets/stats` — duyệt toàn bộ assets trong memory, đếm theo `type` và `status`
- `GET /assets/count` — filter theo query params `type`, `status` rồi đếm

### Clean Architecture
- **Handler** (`handler/asset_handler.py`): nhận query params, gọi service
- **Service** (`service/asset_service.py`): hàm `get_stats()`, `count_assets()`
- **Storage** (`storage/asset_storage.py`): hàm `get_all()`, `filter()`

### Screenshots cần chụp

**[SCREENSHOT 1.1]** — GET /assets/stats
> Vào http://localhost:8080/docs → click GET /assets/stats → Try it out → Execute
> Chụp phần "Server response" hiển thị JSON có `total`, `by_type`, `by_status`

**[SCREENSHOT 1.2]** — GET /assets/count?type=domain
> Click GET /assets/count → Try it out → điền `type = domain` → Execute
> Chụp phần response hiển thị `count` và `filters`

---

## Bài 2: Batch Create Assets (25 điểm)

### Giải pháp
Implement nguyên tắc **all or nothing**:
1. Validate toàn bộ list trước trong vòng lặp đầu tiên
2. Nếu bất kỳ asset nào không hợp lệ → raise lỗi ngay, không insert gì cả
3. Chỉ gọi `storage.batch_create()` khi tất cả đều hợp lệ

```python
# Validate ALL trước
for i, inp in enumerate(asset_inputs):
    error = self._validate_asset(name, asset_type, status)
    if error:
        raise ValueError(f"asset[{i}]: {error}")  # dừng ngay

# Chỉ insert khi tất cả OK
self._storage.batch_create(validated)
```

### Screenshots cần chụp

**[SCREENSHOT 2.1]** — Success case
> POST /assets/batch → Try it out → dùng body:
> ```json
> {"assets": [{"name": "test1.com", "type": "domain"}, {"name": "test2.com", "type": "domain"}]}
> ```
> Chụp response 201 có `created: 2` và `ids`

**[SCREENSHOT 2.2]** — Error case (all or nothing)
> Dùng body có 1 asset type sai:
> ```json
> {"assets": [{"name": "test1.com", "type": "domain"}, {"name": "test2.com", "type": "INVALID"}]}
> ```
> Chụp response 400 — chứng minh không asset nào được tạo

---

## Bài 3: Batch Delete Assets (20 điểm)

### Giải pháp
- Nhận danh sách IDs từ query param `?ids=id1,id2,id3`
- Với mỗi ID: xóa nếu tồn tại, bỏ qua nếu không có
- Trả về `deleted` và `not_found`

### Screenshots cần chụp

**[SCREENSHOT 3.1]** — Batch delete thành công
> DELETE /assets/batch → Try it out → điền `ids` = các ID thật lấy từ bài 2 + thêm `fake-id-999`
> Chụp response: `{"deleted": 2, "not_found": 1}`

**[SCREENSHOT 3.2]** — Verify đã xóa
> GET /assets/{asset_id} → điền 1 ID vừa xóa → Execute
> Chụp response 404 Not Found

---

## Bài 4: Concurrent-safe Create (25 điểm)

### Giải pháp
Dùng `threading.Lock()` trong `AssetStorage`:

```python
class AssetStorage:
    def __init__(self):
        self._data: dict[str, Asset] = {}
        self._lock = threading.Lock()  # Đảm bảo thread-safe

    def create(self, asset: Asset) -> None:
        with self._lock:  # Chỉ 1 thread được write tại 1 thời điểm
            self._data[asset.id] = asset
```

Khi nhiều request đến cùng lúc, `threading.Lock()` đảm bảo:
- Không race condition
- Không data corruption
- Không trùng ID (UUID được sinh trước khi acquire lock)

### Screenshots cần chụp

**[SCREENSHOT 4.1]** — Trước khi bắn concurrent
> GET /assets/count → Execute → chụp count hiện tại (ví dụ: 5)

**[SCREENSHOT 4.2]** — Chạy test concurrent trong PowerShell
> Mở PowerShell mới (KHÔNG phải terminal đang chạy server), chạy:
> ```powershell
> 1..20 | ForEach-Object -Parallel {
>     Invoke-RestMethod -Uri "http://localhost:8080/assets" `
>         -Method POST `
>         -ContentType "application/json" `
>         -Body "{`"name`":`"concurrent-$_.com`",`"type`":`"domain`"}"
> }
> ```
> Chụp màn hình đang chạy (thấy 20 dòng response)

**[SCREENSHOT 4.3]** — Sau khi bắn concurrent
> GET /assets/count → Execute → chụp count tăng thêm đúng 20

---

## Bài 5: In-memory Health Check (15 điểm)

### Giải pháp
- Track `START_TIME = time.time()` khi server khởi động
- `uptime_seconds = int(time.time() - START_TIME)`
- Gọi `service.get_asset_count()` để lấy số asset hiện tại

### Screenshots cần chụp

**[SCREENSHOT 5.1]** — Health check lần 1
> GET /health → Try it out → Execute
> Chụp response có `status: ok`, `asset_count`, `uptime_seconds`, `timestamp`

**[SCREENSHOT 5.2]** — Health check sau khi tạo thêm asset
> Tạo thêm 1 asset bằng POST /assets
> Rồi GET /health lại → chụp — thấy `asset_count` tăng lên 1

---

## Bài 6: Pagination & Filtering (15 điểm) — BONUS

### Giải pháp
- Filter trong memory bằng hàm `storage.filter(type, status)`
- Tính `total_pages = ceil(total / limit)`
- Slice list: `assets[start:end]`

### Screenshots cần chụp

**[SCREENSHOT 6.1]** — Pagination
> GET /assets → Try it out → điền `page=1`, `limit=2` → Execute
> Chụp response có `data` và `pagination` object

**[SCREENSHOT 6.2]** — Filter kết hợp
> GET /assets → điền `type=domain`, `status=active` → Execute
> Chụp response chỉ hiển thị assets đúng filter

---

## Bài 7: Search by Name (10 điểm) — BONUS

### Giải pháp
- Case-insensitive: so sánh `query.lower()` với `asset.name.lower()`
- Partial match: dùng `query in name`
- Giới hạn 100 kết quả

```python
def search_by_name(self, query: str) -> list[Asset]:
    q = query.lower()
    return [a for a in self._data.values() if q in a.name.lower()]
```

### Screenshots cần chụp

**[SCREENSHOT 7.1]** — Search partial match
> GET /assets/search → Try it out → điền `q = .com` → Execute
> Chụp response trả về các asset có ".com" trong tên

**[SCREENSHOT 7.2]** — Search case-insensitive
> Điền `q = DOMAIN` hoặc `q = IP` (chữ hoa) → Execute
> Chụp response vẫn tìm được kết quả

---

## Ghi chú về Git

Repository được tổ chức:
- Branch `main`: code gốc
- Branch `homework`: toàn bộ bài làm
- Pull Request từ `homework` → `main`, reviewer: `dinhmanhtan`

