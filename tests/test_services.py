"""
Test suite for ALICI Stripe and Analytics services
Run with: pytest tests/
"""

import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from alici_api.services.stripe_service import StripeService, PlanType
from alici_api.services.analytics_service import AnalyticsService, EventType


class TestStripeService:
    """Tests for Stripe payment service"""
    
    @pytest.fixture
    def stripe_service(self):
        """Provide StripeService instance"""
        return StripeService()
    
    def test_plan_config_exists(self, stripe_service):
        """Test that all plans are configured"""
        assert "free" in stripe_service.PLANS
        assert "pro" in stripe_service.PLANS
        assert "ultra" in stripe_service.PLANS
        assert "enterprise" in stripe_service.PLANS
    
    def test_plan_pricing_brl(self, stripe_service):
        """Test Brazilian real pricing"""
        pro_plan = stripe_service.get_plan_info("pro")
        assert pro_plan["price_brl"] == 49
        
        ultra_plan = stripe_service.get_plan_info("ultra")
        assert ultra_plan["price_brl"] == 99
    
    def test_plan_features(self, stripe_service):
        """Test that plans have features"""
        free_plan = stripe_service.get_plan_info("free")
        assert len(free_plan["features"]) > 0
        
        pro_plan = stripe_service.get_plan_info("pro")
        assert "100 messages/day" in pro_plan["features"]
        assert "3GB storage" in pro_plan["features"]
    
    def test_invalid_plan(self, stripe_service):
        """Test handling of invalid plan type"""
        result = stripe_service.get_plan_info("invalid_plan")
        assert result == {}
    
    @patch('stripe.Customer.create')
    def test_create_customer_success(self, mock_stripe, stripe_service):
        """Test successful customer creation"""
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        mock_stripe.return_value = mock_customer
        
        customer_id = stripe_service.create_customer(
            user_email="test@example.com",
            user_name="Test User",
            user_id="user_123"
        )
        
        assert customer_id == "cus_test123"
        mock_stripe.assert_called_once()
    
    @patch('stripe.Subscription.create')
    def test_create_subscription_pro(self, mock_stripe, stripe_service):
        """Test subscription creation for Pro plan"""
        mock_subscription = Mock()
        mock_subscription.id = "sub_test123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1234567890
        mock_subscription.client_secret = "secret_test"
        mock_stripe.return_value = mock_subscription
        
        result = stripe_service.create_subscription(
            user_id="user_123",
            stripe_customer_id="cus_test123",
            plan="pro"
        )
        
        assert result["plan"] == "pro"
        assert result["status"] == "active"
        assert result["amount"] == 49
    
    def test_create_subscription_free(self, stripe_service):
        """Test free subscription creation (no Stripe charge)"""
        result = stripe_service.create_subscription(
            user_id="user_123",
            stripe_customer_id="cus_test123",
            plan="free"
        )
        
        assert result["plan"] == "free"
        assert result["amount"] == 0
        assert result["status"] == "active"
    
    def test_invalid_subscription_plan(self, stripe_service):
        """Test subscription with invalid plan"""
        with pytest.raises(ValueError):
            stripe_service.create_subscription(
                user_id="user_123",
                stripe_customer_id="cus_test123",
                plan="invalid"
            )
    
    @patch('stripe.Subscription.retrieve')
    @patch('stripe.Subscription.modify')
    def test_upgrade_subscription(self, mock_modify, mock_retrieve, stripe_service):
        """Test plan upgrade"""
        mock_sub = Mock()
        mock_sub.items.data = [Mock(id="item_123")]
        mock_retrieve.return_value = mock_sub
        
        mock_updated = Mock()
        mock_updated.id = "sub_test123"
        mock_updated.status = "active"
        mock_updated.latest_invoice = "inv_123"
        mock_modify.return_value = mock_updated
        
        result = stripe_service.upgrade_subscription(
            subscription_id="sub_test123",
            new_plan="ultra"
        )
        
        assert result["new_plan"] == "ultra"
        assert result["status"] == "active"
        mock_modify.assert_called_once()
    
    @patch('stripe.Subscription.delete')
    def test_cancel_subscription_immediate(self, mock_delete, stripe_service):
        """Test immediate subscription cancellation"""
        mock_deleted = Mock()
        mock_deleted.canceled_at = datetime.utcnow().timestamp()
        mock_delete.return_value = mock_deleted
        
        result = stripe_service.cancel_subscription(
            subscription_id="sub_test123",
            immediate=True
        )
        
        assert result["status"] == "canceled"
        mock_delete.assert_called_once()
    
    @patch('stripe.Subscription.modify')
    def test_cancel_subscription_at_period_end(self, mock_modify, stripe_service):
        """Test subscription cancellation at period end"""
        mock_modified = Mock()
        mock_modified.status = "active"
        mock_modified.current_period_end = 1234567890
        mock_modify.return_value = mock_modified
        
        result = stripe_service.cancel_subscription(
            subscription_id="sub_test123",
            immediate=False
        )
        
        assert result["status"] == "active"
        mock_modify.assert_called_once()
    
    @patch('stripe.Invoice.list')
    def test_list_invoices(self, mock_list, stripe_service):
        """Test invoice listing"""
        mock_invoice1 = Mock()
        mock_invoice1.id = "inv_123"
        mock_invoice1.total = 4900
        mock_invoice1.created = datetime.utcnow().timestamp()
        mock_invoice1.status = "paid"
        mock_invoice1.invoice_pdf = "https://example.com/inv.pdf"
        
        mock_list.return_value.data = [mock_invoice1]
        
        invoices = stripe_service.list_invoices("cus_test123")
        
        assert len(invoices) == 1
        assert invoices[0]["amount"] == 49.0
        assert invoices[0]["status"] == "paid"
    
    def test_webhook_payment_succeeded(self, stripe_service):
        """Test payment success webhook"""
        event = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "metadata": {"alici_user_id": "user_123"},
                    "amount_paid": 4900
                }
            }
        }
        
        result = stripe_service.handle_webhook(event)
        assert result is True
    
    def test_webhook_subscription_updated(self, stripe_service):
        """Test subscription updated webhook"""
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "metadata": {
                        "alici_user_id": "user_123",
                        "plan": "ultra"
                    }
                }
            }
        }
        
        result = stripe_service.handle_webhook(event)
        assert result is True
    
    def test_webhook_subscription_deleted(self, stripe_service):
        """Test subscription deleted webhook"""
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "metadata": {"alici_user_id": "user_123"}
                }
            }
        }
        
        result = stripe_service.handle_webhook(event)
        assert result is True


class TestAnalyticsService:
    """Tests for Analytics tracking service"""
    
    @pytest.fixture
    def analytics(self):
        """Provide AnalyticsService instance"""
        return AnalyticsService()
    
    def test_analytics_initialization(self, analytics):
        """Test analytics service initializes"""
        assert isinstance(analytics.events_buffer, list)
        assert len(analytics.events_buffer) == 0
    
    def test_track_signup(self, analytics):
        """Test tracking user signup"""
        result = analytics.track_signup("user_123", "test@example.com")
        assert result is True
        assert len(analytics.events_buffer) >= 0
    
    def test_track_first_message(self, analytics):
        """Test tracking first message"""
        result = analytics.track_first_message("user_123", content_length=150)
        assert result is True
    
    def test_track_plan_upgrade(self, analytics):
        """Test tracking plan upgrade"""
        result = analytics.track_plan_upgrade(
            "user_123",
            from_plan="free",
            to_plan="pro",
            amount=49.0
        )
        assert result is True
    
    def test_track_api_call(self, analytics):
        """Test tracking API call"""
        result = analytics.track_api_call(
            "user_123",
            endpoint="/chat",
            latency_ms=245,
            status_code=200
        )
        assert result is True
    
    def test_set_user_properties(self, analytics):
        """Test setting user properties"""
        properties = {
            "plan": "pro",
            "signup_source": "organic",
            "country": "BR"
        }
        result = analytics.set_user_properties("user_123", properties)
        assert result is True
    
    def test_get_user_metrics(self, analytics):
        """Test getting user metrics"""
        metrics = analytics.get_user_metrics("user_123")
        
        assert "user_id" in metrics
        assert "signup_date" in metrics
        assert "messages_sent" in metrics
        assert "plan" in metrics
    
    def test_get_cohort_metrics(self, analytics):
        """Test getting cohort metrics"""
        metrics = analytics.get_cohort_metrics()
        
        assert "total_users" in metrics
        assert "active_users_today" in metrics
        assert "mau" in metrics
        assert "mrr" in metrics
        assert "conversion_rate" in metrics
        assert "churn_rate" in metrics
    
    def test_calculate_funnel_conversion(self, analytics):
        """Test funnel conversion calculation"""
        # 100 signups → 10 conversions
        conversion = analytics.calculate_funnel_conversion(100, 10)
        assert conversion == 0.1
    
    def test_funnel_conversion_division_by_zero(self, analytics):
        """Test funnel conversion with zero step1"""
        conversion = analytics.calculate_funnel_conversion(0, 10)
        assert conversion == 0.0
    
    def test_estimate_ltv(self, analytics):
        """Test LTV calculation"""
        # ARPU: R$49/month, Gross margin: 75%, Monthly churn: 5%
        ltv = analytics.estimate_ltv(arpu=49, gross_margin=0.75, monthly_churn=0.05)
        
        # Expected: (49 * 0.75) / 0.05 = 735
        assert ltv == pytest.approx(735, rel=0.01)
    
    def test_estimate_ltv_zero_churn(self, analytics):
        """Test LTV with zero churn (infinite value)"""
        ltv = analytics.estimate_ltv(arpu=49, gross_margin=0.75, monthly_churn=0.0)
        
        # Should return large number (assume ~100 month lifetime)
        assert ltv > 5000
    
    def test_calculate_cac_payback(self, analytics):
        """Test CAC payback calculation"""
        # CAC: R$200, ARPU: R$49, Gross margin: 75%
        payback = analytics.calculate_cac_payback(cac=200, arpu=49, gross_margin=0.75)
        
        # Expected: 200 / (49 * 0.75) = 5.44 months
        assert payback == pytest.approx(5.44, rel=0.01)
    
    def test_calculate_cac_payback_zero_arpu(self, analytics):
        """Test CAC payback with zero ARPU"""
        payback = analytics.calculate_cac_payback(cac=200, arpu=0, gross_margin=0.75)
        assert payback == float('inf')
    
    def test_flush_events(self, analytics):
        """Test event buffer flush"""
        analytics.track_signup("user_123", "test@example.com")
        
        result = analytics.flush()
        assert result is True
        assert len(analytics.events_buffer) == 0


class TestBusinessMetrics:
    """Integration tests for business metrics"""
    
    def test_phase1_unit_economics(self):
        """Test Phase 1 unit economics"""
        analytics = AnalyticsService()
        
        # Phase 1: 200 free users, 20 paying
        free_users = 200
        paid_users = 20
        conversion_rate = analytics.calculate_funnel_conversion(free_users, paid_users)
        
        assert conversion_rate == 0.1  # 10% conversion
        
        # CAC and LTV
        cac = 200  # R$200 estimated
        arpu = 49  # R$49/month for Pro
        gross_margin = 0.75
        
        ltv = analytics.estimate_ltv(arpu, gross_margin, monthly_churn=0.05)
        cac_payback = analytics.calculate_cac_payback(cac, arpu, gross_margin)
        ltv_to_cac = ltv / cac
        
        assert ltv_to_cac > 3  # Should be healthy
        assert cac_payback < 12  # Payback in < 12 months
    
    def test_mrr_projection_month6(self):
        """Test Phase 1 Month 6 MRR projection"""
        # Target: 300 users, 20+ paying
        pro_users = 15
        ultra_users = 5
        enterprise_contracts = 3
        
        pro_revenue = pro_users * 49
        ultra_revenue = ultra_users * 99
        enterprise_revenue = enterprise_contracts * 500  # Avg R$500/contract
        
        total_mrr = pro_revenue + ultra_revenue + enterprise_revenue
        
        assert total_mrr > 3000  # Target: R$3,500
        assert total_mrr == pytest.approx(3360, abs=100)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
