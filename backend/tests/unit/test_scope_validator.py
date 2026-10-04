import pytest
from app.models.scope import Scope, ScopeType
from app.models.target import ScopeStatus
from app.scope.validator import ScopeValidator


def test_resolve_single_ip() -> None:
    ok, ips, msg = ScopeValidator.resolve_target("192.168.1.50")
    assert ok is True
    assert ips == ["192.168.1.50"]


def test_resolve_cidr() -> None:
    ok, ips, msg = ScopeValidator.resolve_target("192.168.1.0/30")
    assert ok is True
    assert "192.168.1.1" in ips
    assert "192.168.1.2" in ips


def test_scope_allowed_single_ip() -> None:
    scope = Scope(
        id="scope-1",
        project_id="proj-1",
        scope_type=ScopeType.SINGLE_IP,
        value="192.168.1.10",
        is_exclusion=False,
        enabled=True,
    )
    decision = ScopeValidator.evaluate_target_against_scopes("192.168.1.10", [scope])
    assert decision.is_allowed is True
    assert decision.status == ScopeStatus.ALLOWED


def test_scope_denied_out_of_bounds() -> None:
    scope = Scope(
        id="scope-1",
        project_id="proj-1",
        scope_type=ScopeType.SINGLE_IP,
        value="192.168.1.10",
        is_exclusion=False,
        enabled=True,
    )
    decision = ScopeValidator.evaluate_target_against_scopes("192.168.1.99", [scope])
    assert decision.is_allowed is False
    assert decision.status == ScopeStatus.DENIED
    assert "outside all permitted inclusion scopes" in decision.message


def test_scope_exclusion_takes_priority() -> None:
    inc_scope = Scope(
        id="scope-inc",
        project_id="proj-1",
        scope_type=ScopeType.CIDR,
        value="192.168.1.0/24",
        is_exclusion=False,
        enabled=True,
    )
    ex_scope = Scope(
        id="scope-ex",
        project_id="proj-1",
        scope_type=ScopeType.SINGLE_IP,
        value="192.168.1.254",
        is_exclusion=True,
        enabled=True,
    )
    # Target inside inclusion CIDR but explicitly excluded
    decision = ScopeValidator.evaluate_target_against_scopes(
        "192.168.1.254", [inc_scope, ex_scope]
    )
    assert decision.is_allowed is False
    assert decision.status == ScopeStatus.DENIED
    assert "explicit exclusion rule" in decision.message


def test_resolve_cidr_rejects_more_than_256_hosts() -> None:
    for network in ("10.0.0.0/8", "2001:db8::/64"):
        ok, ips, msg = ScopeValidator.resolve_target(network)
        assert ok is False
        assert ips == []
        assert "256-host validation limit" in msg


def test_resolve_cidr_accepts_254_hosts() -> None:
    ok, ips, _ = ScopeValidator.resolve_target("192.168.1.0/24")
    assert ok is True
    assert len(ips) == 254
