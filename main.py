from fastapi import FastAPI
from datetime import datetime, timezone
import time

from storage.postgres_asset_storage import PostgresAssetStorage
from service.asset_service import AssetService
import handler.asset_handler as asset_handler

# Ghi lại thời điểm server khởi động - dùng cho Bài 5
START_TIME = time.time()

app = FastAPI(title="Asset API")

# === Wire up: storage → service → handler ===
storage = PostgresAssetStorage()
service = AssetService(storage)
asset_handler.set_service(service)

# Đăng ký các routes từ handler
app.include_router(asset_handler.router)

# ========== Bài 5: Health Check ==========
@app.get("/health")
def health_check():
    uptime = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "storage": {
            "type": "in-memory",
            "asset_count": service.get_asset_count(),
        },
        "uptime_seconds": uptime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }