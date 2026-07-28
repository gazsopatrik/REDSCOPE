from app.intelligence.cpe_matcher import CPEMatcher


def test_normalize_nginx() -> None:
    norm = CPEMatcher.normalize_service(
        product="nginx", version="1.22.1", service_name="http"
    )
    assert norm.vendor == "nginx"
    assert norm.product == "nginx"
    assert norm.cpe_23 == "cpe:2.3:a:nginx:nginx:1.22.1:*:*:*:*:*:*:*"
    assert norm.confidence == "high"


def test_normalize_apache() -> None:
    norm = CPEMatcher.normalize_service(
        product="Apache httpd", version="2.4.57", service_name="http"
    )
    assert norm.vendor == "apache"
    assert norm.product == "http_server"
    assert norm.confidence == "high"


def test_normalize_raw_cpe() -> None:
    norm = CPEMatcher.normalize_service(
        product=None,
        version=None,
        service_name=None,
        cpe_raw="cpe:/a:openbsd:openssh:7.2p1",
    )
    assert norm.vendor == "openbsd"
    assert norm.product == "openssh"
    assert norm.confidence == "exact"
