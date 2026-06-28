import threading
from typing import Optional
from model.scan_job import ScanJob


class ScanJobStorage:
    """Lưu các scan job trong RAM (giống AssetStorage cũ)"""

    def __init__(self):
        self._data: dict[str, ScanJob] = {}
        self._lock = threading.Lock()

    def create(self, job: ScanJob) -> None:
        with self._lock:
            self._data[job.id] = job

    def get_by_id(self, job_id: str) -> Optional[ScanJob]:
        with self._lock:
            return self._data.get(job_id)

    def update(self, job: ScanJob) -> None:
        """Cập nhật job sau khi scan xong (đổi status, results...)"""
        with self._lock:
            self._data[job.id] = job

    def get_by_asset_id(self, asset_id: str) -> list[ScanJob]:
        """Lấy tất cả scan jobs của 1 asset"""
        with self._lock:
            return [j for j in self._data.values() if j.asset_id == asset_id]