from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timezone
import uuid

VALID_SCAN_TYPES = {"dns", "whois", "subdomain", "cert_trans", "asn", "all", "ip", "port"}
VALID_SCAN_STATUSES = {"pending", "running", "completed", "failed", "partial"}


class ScanJob(BaseModel):
    id: str
    asset_id: str
    scan_type: str
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    error: str = ""
    results: list[Any] = []
    created_at: datetime


def new_scan_job(asset_id: str, scan_type: str) -> ScanJob:
    """Tạo 1 scan job mới ở trạng thái pending"""
    return ScanJob(
        id=str(uuid.uuid4()),
        asset_id=asset_id,
        scan_type=scan_type,
        status="pending",
        started_at=None,
        ended_at=None,
        error="",
        results=[],
        created_at=datetime.now(timezone.utc)
    )