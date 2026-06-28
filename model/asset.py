from pydantic import BaseModel    # thư viện tạo khuôn có validation
from typing import Optional       # để dùng Optional[str]
from datetime import datetime, timezone  # kiểu dữ liệu thời gian
import uuid                       # thư viện sinh ID ngẫu nhiên

VALID_TYPES = {"domain", "ip", "service", "ssl", "whois", "certificate", "port"}
VALID_STATUSES = {"active", "inactive"}

class Asset(BaseModel):
    id: str
    name: str
    type: str
    status: str
    tags: list[str] = []
    created_at: datetime

def new_asset(name: str, asset_type: str, status: str = "active", tags: list[str] = None) -> Asset:
    return Asset(
        id=str(uuid.uuid4()),
        name=name,
        type=asset_type,
        status=status,
        tags=tags or [],
        created_at=datetime.now(timezone.utc)
    )