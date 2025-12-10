"""
Tests for analytics endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.models import Lead, Message, Source, Rule, LeadStatus
from datetime import datetime, timedelta


@pytest.fixture
def analytics_data(db_session, test_tenant, test_source, test_rule, test_message):
    """Create analytics test data with multiple leads."""
    # Create multiple leads with different statuses and dates
    leads = []
    for i in range(10):
        message = Message(
            telegram_id=10000 + i,
            source_id=test_source.id,
            text=f"Test message {i}",
            sender_name=f"Sender {i}",
            sent_at=datetime.utcnow() - timedelta(days=i),
            tenant_id=test_tenant.id,
        )
        db_session.add(message)
        db_session.flush()

        lead = Lead(
            message_id=message.id,
            rule_id=test_rule.id,
            status=LeadStatus.NEW if i < 5 else LeadStatus.CONTACTED,
            score=0.7 + (i * 0.02),
            reasoning=f"Test lead {i}",
            created_at=datetime.utcnow() - timedelta(days=i),
            tenant_id=test_tenant.id,
        )
        db_session.add(lead)
        leads.append(lead)

    db_session.commit()
    return leads


class TestAnalytics:
    """Test analytics endpoints."""

    def test_get_summary(self, authenticated_client: TestClient, analytics_data):
        """Test getting analytics summary."""
        response = authenticated_client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()

        assert "total_leads" in data
        assert "total_messages" in data
        assert "conversion_rate" in data
        assert "avg_lead_score" in data
        assert data["total_leads"] == 10

    def test_get_summary_with_date_range(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting summary with date filters."""
        date_from = (datetime.utcnow() - timedelta(days=5)).isoformat()
        date_to = datetime.utcnow().isoformat()

        response = authenticated_client.get(
            "/api/v1/analytics/summary",
            params={"date_from": date_from, "date_to": date_to},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_leads"] <= 10

    def test_get_leads_time_series(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting leads time series data."""
        response = authenticated_client.get(
            "/api/v1/analytics/leads-time-series",
            params={"granularity": "day"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "data_points" in data
        assert "period_start" in data
        assert "period_end" in data
        assert len(data["data_points"]) > 0

        # Check data point structure
        point = data["data_points"][0]
        assert "timestamp" in point
        assert "date_label" in point
        assert "count" in point

    def test_get_leads_time_series_different_granularity(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test time series with different granularity options."""
        for granularity in ["hour", "day", "week", "month"]:
            response = authenticated_client.get(
                "/api/v1/analytics/leads-time-series",
                params={"granularity": granularity},
            )
            assert response.status_code == 200
            data = response.json()
            assert "data_points" in data

    def test_get_conversion_funnel(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting conversion funnel data."""
        response = authenticated_client.get("/api/v1/analytics/conversion-funnel")
        assert response.status_code == 200
        data = response.json()

        assert "stages" in data
        assert "final_conversion_rate" in data
        assert len(data["stages"]) > 0

        # Check stage structure
        stage = data["stages"][0]
        assert "stage_name" in stage
        assert "count" in stage
        assert "percentage" in stage

    def test_get_source_performance(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting source performance data."""
        response = authenticated_client.get("/api/v1/analytics/source-performance")
        assert response.status_code == 200
        data = response.json()

        assert "sources" in data
        assert len(data["sources"]) > 0

        # Check source structure
        source = data["sources"][0]
        assert "source_id" in source
        assert "source_title" in source
        assert "total_messages" in source
        assert "total_leads" in source
        assert "conversion_rate" in source
        assert "avg_lead_score" in source

    def test_get_rule_performance(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting rule performance data."""
        response = authenticated_client.get("/api/v1/analytics/rule-performance")
        assert response.status_code == 200
        data = response.json()

        assert "rules" in data
        assert len(data["rules"]) > 0

        # Check rule structure
        rule = data["rules"][0]
        assert "rule_id" in rule
        assert "rule_name" in rule
        assert "total_leads" in rule
        assert "leads_last_7d" in rule
        assert "leads_last_30d" in rule
        assert "avg_lead_score" in rule
        assert "is_active" in rule

    def test_get_activity_trends(
        self, authenticated_client: TestClient, analytics_data
    ):
        """Test getting activity trends."""
        response = authenticated_client.get("/api/v1/analytics/activity-trends")
        assert response.status_code == 200
        data = response.json()

        assert "period" in data
        assert "leads_trend" in data
        assert "messages_trend" in data
        assert "conversion_trend" in data

        # Check trend structure
        trend = data["leads_trend"]
        assert "metric_name" in trend
        assert "current_value" in trend
        assert "previous_value" in trend
        assert "change_percentage" in trend
        assert "trend_direction" in trend
        assert trend["trend_direction"] in ["up", "down", "stable"]

    def test_analytics_unauthorized(self, client: TestClient):
        """Test analytics endpoints without authentication."""
        endpoints = [
            "/api/v1/analytics/summary",
            "/api/v1/analytics/leads-time-series",
            "/api/v1/analytics/conversion-funnel",
            "/api/v1/analytics/source-performance",
            "/api/v1/analytics/rule-performance",
            "/api/v1/analytics/activity-trends",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401

    def test_analytics_empty_data(self, authenticated_client: TestClient):
        """Test analytics with no data."""
        response = authenticated_client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_leads"] == 0
        assert data["total_messages"] == 0
