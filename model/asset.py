from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

VALID_TYPES = {"domain", "ip", "service"}
VALID_STATUSES = {"active", "inactive"}

class Asset(BaseModel):
    id: str
    name: str
    type: str
    status: str
    created_at: datetime

def new_asset(name: str, asset_type: str, status: str = "active") -> Asset:
    """Tạo một Asset mới với ID tự động sinh"""
    return Asset(
        id=str(uuid.uuid4()),
        name=name,
        type=asset_type,
        status=status,
        created_at=datetime.now(timezone.utc)
    )