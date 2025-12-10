"""
Tests for leads endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.models import Lead, Message, Source, Rule, LeadStatus
from datetime import datetime, timedelta


@pytest.fixture
def test_source(db_session, test_tenant):
    """Create a test source."""
    source = Source(
        telegram_id=12345,
        title="Test Channel",
        username="testchannel",
        source_type="channel",
        is_active=True,
        tenant_id=test_tenant.id,
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def test_rule(db_session, test_tenant):
    """Create a test rule."""
    rule = Rule(
        name="Test Rule",
        description="Looking for test leads",
        llm_prompt="Find test opportunities",
        match_threshold=0.7,
        is_active=True,
        tenant_id=test_tenant.id,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def test_message(db_session, test_source, test_tenant):
    """Create a test message."""
    message = Message(
        telegram_id=9999,
        source_id=test_source.id,
        text="Looking for Python developer for startup project",
        sender_name="John Doe",
        sent_at=datetime.utcnow(),
        tenant_id=test_tenant.id,
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message


@pytest.fixture
def test_lead(db_session, test_message, test_rule, test_tenant):
    """Create a test lead."""
    lead = Lead(
        message_id=test_message.id,
        rule_id=test_rule.id,
        status=LeadStatus.NEW,
        score=0.85,
        reasoning="This is a potential job opportunity",
        extracted_entities={
            "contacts": ["john@example.com"],
            "keywords": ["Python", "developer"],
        },
        tenant_id=test_tenant.id,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


class TestLeads:
    """Test leads endpoints."""

    def test_list_leads_empty(self, authenticated_client: TestClient):
        """Test listing leads when none exist."""
        response = authenticated_client.get("/api/v1/leads/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_leads(self, authenticated_client: TestClient, test_lead):
        """Test listing leads."""
        response = authenticated_client.get("/api/v1/leads/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(test_lead.id)
        assert data[0]["status"] == test_lead.status
        assert data[0]["score"] == test_lead.score

    def test_list_leads_filter_by_status(
        self, authenticated_client: TestClient, test_lead
    ):
        """Test filtering leads by status."""
        # Create another lead with different status
        test_lead.status = LeadStatus.CONTACTED
        authenticated_client.app.dependency_overrides[get_db].session.commit()

        response = authenticated_client.get(
            "/api/v1/leads/", params={"status": LeadStatus.CONTACTED}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == LeadStatus.CONTACTED

    def test_get_lead_by_id(self, authenticated_client: TestClient, test_lead):
        """Test getting a specific lead by ID."""
        response = authenticated_client.get(f"/api/v1/leads/{test_lead.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_lead.id)
        assert data["score"] == test_lead.score
        assert data["reasoning"] == test_lead.reasoning
        assert "message" in data
        assert "rule" in data

    def test_get_lead_not_found(self, authenticated_client: TestClient):
        """Test getting a non-existent lead."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.get(f"/api/v1/leads/{fake_uuid}")
        assert response.status_code == 404

    def test_update_lead_status(self, authenticated_client: TestClient, test_lead):
        """Test updating lead status."""
        response = authenticated_client.patch(
            f"/api/v1/leads/{test_lead.id}",
            json={"status": LeadStatus.CONTACTED},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == LeadStatus.CONTACTED

    def test_update_lead_notes(self, authenticated_client: TestClient, test_lead):
        """Test updating lead notes."""
        response = authenticated_client.patch(
            f"/api/v1/leads/{test_lead.id}",
            json={"notes": "Called and left message"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Called and left message"

    def test_delete_lead(self, authenticated_client: TestClient, test_lead, db_session):
        """Test deleting a lead."""
        lead_id = test_lead.id
        response = authenticated_client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 204

        # Verify lead is deleted
        deleted_lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        assert deleted_lead is None

    def test_get_lead_stats(self, authenticated_client: TestClient, test_lead):
        """Test getting lead statistics."""
        response = authenticated_client.get("/api/v1/leads/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert data["total"] == 1
        assert data["by_status"][LeadStatus.NEW] == 1

    def test_export_leads_csv(self, authenticated_client: TestClient, test_lead):
        """Test exporting leads to CSV."""
        response = authenticated_client.get("/api/v1/leads/export/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Content-Disposition" in response.headers

        # Check CSV content
        content = response.text
        assert "Lead ID" in content
        assert str(test_lead.id) in content

    def test_list_leads_unauthorized(self, client: TestClient):
        """Test listing leads without authentication."""
        response = client.get("/api/v1/leads/")
        assert response.status_code == 401
