import psycopg2
import psycopg2.extras
import uuid
from typing import Optional
from model.asset import Asset
import config


class PostgresAssetStorage:
    """Storage layer dùng PostgreSQL thay cho in-memory dict"""

    def __init__(self):
        try:
            self._conn = psycopg2.connect(config.get_dsn())
            self._conn.autocommit = True
            self._run_migration()
        except psycopg2.OperationalError as e:
            print(f"❌ Không thể kết nối PostgreSQL: {e}")
            print("👉 Kiểm tra: docker compose ps (database có đang chạy không?)")
            raise SystemExit(1)

    def _run_migration(self):
        """Tạo table assets nếu chưa tồn tại - đọc từ file SQL"""
        with open("migrations/001_create_assets.sql", "r") as f:
            sql = f.read()
        with self._conn.cursor() as cur:
            cur.execute(sql)

    def create(self, asset: Asset) -> None:
        query = """
            INSERT INTO assets (id, name, type, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        with self._conn.cursor() as cur:
            cur.execute(query, (asset.id, asset.name, asset.type, asset.status, asset.created_at))

    def batch_create(self, assets: list[Asset]) -> None:
        query = """
            INSERT INTO assets (id, name, type, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = [(a.id, a.name, a.type, a.status, a.created_at) for a in assets]
        with self._conn.cursor() as cur:
            cur.executemany(query, values)

    def get_by_id(self, asset_id: str) -> Optional[Asset]:
        query = "SELECT id, name, type, status, created_at FROM assets WHERE id = %s"
        with self._conn.cursor() as cur:
            cur.execute(query, (asset_id,))
            row = cur.fetchone()
            if row is None:
                return None
            return Asset(id=str(row[0]), name=row[1], type=row[2], status=row[3], created_at=row[4])

    def get_all(self) -> list[Asset]:
        query = "SELECT id, name, type, status, created_at FROM assets ORDER BY created_at DESC"
        with self._conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [Asset(id=str(r[0]), name=r[1], type=r[2], status=r[3], created_at=r[4]) for r in rows]

    def delete(self, asset_id: str) -> bool:
        query = "DELETE FROM assets WHERE id = %s"
        with self._conn.cursor() as cur:
            cur.execute(query, (asset_id,))
            return cur.rowcount > 0

    def count(self) -> int:
        query = "SELECT COUNT(*) FROM assets"
        with self._conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0]

    def filter(self, asset_type: str = None, status: str = None) -> list[Asset]:
        query = "SELECT id, name, type, status, created_at FROM assets WHERE 1=1"
        params = []
        if asset_type:
            query += " AND type = %s"
            params.append(asset_type)
        if status:
            query += " AND status = %s"
            params.append(status)
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [Asset(id=str(r[0]), name=r[1], type=r[2], status=r[3], created_at=r[4]) for r in rows]

    def search_by_name(self, query_str: str) -> list[Asset]:
        query = "SELECT id, name, type, status, created_at FROM assets WHERE name ILIKE %s"
        with self._conn.cursor() as cur:
            cur.execute(query, (f"%{query_str}%",))
            rows = cur.fetchall()
            return [Asset(id=str(r[0]), name=r[1], type=r[2], status=r[3], created_at=r[4]) for r in rows]