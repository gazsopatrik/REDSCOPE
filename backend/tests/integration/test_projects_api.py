import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_project_scope_target_workflow() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Create a Project
        proj_resp = await client.post(
            "/api/projects",
            json={
                "name": "Audit Test Project",
                "client_name": "Acme Corp",
                "authorization_reference": "AUTH-2026-99",
            },
        )
        assert proj_resp.status_code == 201
        proj_data = proj_resp.json()
        project_id = proj_data["id"]
        assert proj_data["name"] == "Audit Test Project"

        # 2. Add Scope (192.168.10.0/24)
        scope_resp = await client.post(
            f"/api/projects/{project_id}/scopes",
            json={
                "scope_type": "cidr",
                "value": "192.168.10.0/24",
                "is_exclusion": False,
            },
        )
        assert scope_resp.status_code == 201

        # Add Exclusion Scope (192.168.10.1)
        ex_resp = await client.post(
            f"/api/projects/{project_id}/scopes",
            json={
                "scope_type": "single_ip",
                "value": "192.168.10.1",
                "is_exclusion": True,
            },
        )
        assert ex_resp.status_code == 201

        # 3. Add Authorized Target (192.168.10.50) -> Should be ALLOWED
        target_1 = await client.post(
            f"/api/projects/{project_id}/targets",
            json={"target_value": "192.168.10.50", "target_type": "ip"},
        )
        assert target_1.status_code == 201
        t1_data = target_1.json()
        assert t1_data["scope_status"] == "allowed"

        # 4. Add Excluded Target (192.168.10.1) -> Should be DENIED
        target_2 = await client.post(
            f"/api/projects/{project_id}/targets",
            json={"target_value": "192.168.10.1", "target_type": "ip"},
        )
        assert target_2.status_code == 201
        t2_data = target_2.json()
        assert t2_data["scope_status"] == "denied"

        # 5. Add Out of Scope Target (10.0.0.1) -> Should be DENIED
        target_3 = await client.post(
            f"/api/projects/{project_id}/targets",
            json={"target_value": "10.0.0.1", "target_type": "ip"},
        )
        assert target_3.status_code == 201
        t3_data = target_3.json()
        assert t3_data["scope_status"] == "denied"

        # 6. Check Audit Logs
        audit_resp = await client.get(f"/api/projects/{project_id}/audit-logs")
        assert audit_resp.status_code == 200
        logs = audit_resp.json()
        assert len(logs) >= 5
