from scanners.dns_scanner import scan_dns
from scanners.ip_scanner import scan_ip


def test_scan_dns_returns_records_for_valid_domain():
    """Scan DNS cho domain thật phải trả về có A record"""
    result = scan_dns("google.com")

    assert result["domain"] == "google.com"
    assert "records" in result
    assert len(result["records"]["A"]) > 0


def test_scan_dns_returns_empty_for_invalid_domain():
    """Scan domain không tồn tại phải trả về list rỗng, không crash"""
    result = scan_dns("this-domain-definitely-does-not-exist-12345.com")

    assert result["records"]["A"] == []


def test_scan_ip_returns_geolocation_for_valid_ip():
    """Scan IP công khai (Google DNS) phải trả về geolocation"""
    result = scan_ip("8.8.8.8")

    assert result["ip_address"] == "8.8.8.8"
    assert "geolocation" in result
    assert result["geolocation"]["country"] is not None


def test_scan_ip_returns_error_for_invalid_ip():
    """Scan IP không hợp lệ phải trả về error, không crash"""
    result = scan_ip("999.999.999.999")

    assert "error" in result