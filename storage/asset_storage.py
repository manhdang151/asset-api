import threading
from typing import Optional
from model.asset import Asset


class AssetStorage:
    def __init__(self):
        # Dict lưu toàn bộ assets: {id: Asset}
        self._data: dict[str, Asset] = {}
        # Lock để tránh race condition - Bài 4
        self._lock = threading.Lock()

    def create(self, asset: Asset) -> None:
        with self._lock:
            self._data[asset.id] = asset

    def batch_create(self, assets: list[Asset]) -> None:
        with self._lock:
            for asset in assets:
                self._data[asset.id] = asset

    def get_by_id(self, asset_id: str) -> Optional[Asset]:
        with self._lock:
            return self._data.get(asset_id)

    def get_all(self) -> list[Asset]:
        with self._lock:
            return list(self._data.values())

    def delete(self, asset_id: str) -> bool:
        """Trả về True nếu xóa được, False nếu không tìm thấy"""
        with self._lock:
            if asset_id in self._data:
                del self._data[asset_id]
                return True
            return False

    def count(self) -> int:
        with self._lock:
            return len(self._data)

    def filter(self, asset_type: str = None, status: str = None) -> list[Asset]:
        with self._lock:
            result = []
            for asset in self._data.values():
                if asset_type and asset.type != asset_type:
                    continue
                if status and asset.status != status:
                    continue
                result.append(asset)
            return result

    def search_by_name(self, query: str) -> list[Asset]:
        """Tìm kiếm partial match, case-insensitive"""
        with self._lock:
            q = query.lower()
            return [a for a in self._data.values() if q in a.name.lower()]