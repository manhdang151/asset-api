from model.asset import new_asset, VALID_TYPES, VALID_STATUSES


def test_new_asset_creates_valid_domain():
    """Tạo asset domain hợp lệ phải có đủ các field"""
    asset = new_asset("example.com", "domain", "active")

    assert asset.name == "example.com"
    assert asset.type == "domain"
    assert asset.status == "active"
    assert asset.id is not None
    assert asset.created_at is not None


def test_new_asset_generates_unique_id():
    """Mỗi lần tạo asset phải có ID khác nhau"""
    asset1 = new_asset("test1.com", "domain")
    asset2 = new_asset("test2.com", "domain")

    assert asset1.id != asset2.id


def test_new_asset_default_status_is_active():
    """Nếu không truyền status, mặc định phải là active"""
    asset = new_asset("example.com", "domain")

    assert asset.status == "active"


def test_valid_types_contains_expected_values():
    """VALID_TYPES phải chứa đúng 3 loại: domain, ip, service"""
    assert "domain" in VALID_TYPES
    assert "ip" in VALID_TYPES
    assert "service" in VALID_TYPES
    assert len(VALID_TYPES) == 3


def test_valid_statuses_contains_expected_values():
    """VALID_STATUSES phải chứa đúng 2 loại: active, inactive"""
    assert "active" in VALID_STATUSES
    assert "inactive" in VALID_STATUSES