from model.asset import Asset, VALID_TYPES, VALID_STATUSES, new_asset
from storage.asset_storage import AssetStorage


class AssetService:
    def __init__(self, storage: AssetStorage):
        self._storage = storage

    # --- Validation helper ---
    def _validate_asset(self, name: str, asset_type: str, status: str = "active"):
        """Trả về thông báo lỗi nếu không hợp lệ, None nếu OK"""
        if not name or not name.strip():
            return "name is required"
        if asset_type not in VALID_TYPES:
            return f"invalid type '{asset_type}', must be one of: {', '.join(VALID_TYPES)}"
        if status not in VALID_STATUSES:
            return f"invalid status '{status}', must be one of: {', '.join(VALID_STATUSES)}"
        return None

    # --- Bài 1: Statistics ---
    def get_stats(self) -> dict:
        assets = self._storage.get_all()
        by_type = {}
        by_status = {}
        for a in assets:
            by_type[a.type] = by_type.get(a.type, 0) + 1
            by_status[a.status] = by_status.get(a.status, 0) + 1
        return {
            "total": len(assets),
            "by_type": by_type,
            "by_status": by_status,
        }

    def count_assets(self, asset_type: str = None, status: str = None) -> dict:
        assets = self._storage.filter(asset_type, status)
        filters = {}
        if asset_type:
            filters["type"] = asset_type
        if status:
            filters["status"] = status
        return {"count": len(assets), "filters": filters}

    # --- Bài 2: Batch Create ---
    def batch_create(self, asset_inputs: list[dict]) -> dict:
        if len(asset_inputs) > 100:
            raise ValueError("maximum 100 assets per request")

        # Validate ALL trước - all or nothing
        validated = []
        for i, inp in enumerate(asset_inputs):
            name = inp.get("name", "")
            asset_type = inp.get("type", "")
            status = inp.get("status", "active")
            error = self._validate_asset(name, asset_type, status)
            if error:
                raise ValueError(f"asset[{i}]: {error}")
            validated.append(new_asset(name, asset_type, status))

        # Chỉ insert khi tất cả đều hợp lệ
        self._storage.batch_create(validated)
        return {"created": len(validated), "ids": [a.id for a in validated]}

    # --- Bài 3: Batch Delete ---
    def batch_delete(self, ids: list[str]) -> dict:
        deleted = 0
        not_found = 0
        for asset_id in ids:
            if self._storage.delete(asset_id):
                deleted += 1
            else:
                not_found += 1
        return {"deleted": deleted, "not_found": not_found}

    # --- Bài 4: Create đơn lẻ (an toàn nhờ lock trong storage) ---
    def create_asset(self, name: str, asset_type: str, status: str = "active") -> Asset:
        error = self._validate_asset(name, asset_type, status)
        if error:
            raise ValueError(error)
        asset = new_asset(name, asset_type, status)
        self._storage.create(asset)
        return asset

    def get_all(self) -> list[Asset]:
        return self._storage.get_all()

    def get_by_id(self, asset_id: str):
        return self._storage.get_by_id(asset_id)

    def get_asset_count(self) -> int:
        return self._storage.count()

    # --- Bài 6: Pagination + Filter ---
    def list_assets(self, page: int = 1, limit: int = 20,
                    asset_type: str = None, status: str = None) -> dict:
        limit = min(limit, 100)
        all_assets = self._storage.filter(asset_type, status)
        total = len(all_assets)
        total_pages = max(1, (total + limit - 1) // limit)
        start = (page - 1) * limit
        end = start + limit
        return {
            "data": all_assets[start:end],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
            }
        }

    # --- Bài 7: Search ---
    def search_by_name(self, query: str) -> list[Asset]:
        if not query:
            raise ValueError("search query 'q' is required")
        results = self._storage.search_by_name(query)
        return results[:100]