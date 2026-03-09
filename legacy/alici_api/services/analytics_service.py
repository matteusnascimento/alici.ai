"""
Analytics Service for ALICI
Tracks user events, conversion funnels, retention
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json


class EventType(str, Enum):
    """Trackable event types"""
    USER_SIGNUP = "user_signup"
    FIRST_MESSAGE = "first_message"
    PLAN_UPGRADE = "plan_upgrade"
    PLAN_DOWNGRADE = "plan_downgrade"
    API_CALL = "api_call"
    MESSAGE_SENT = "message_sent"
    TRIAL_ENDED = "trial_ended"
    SUBSCRIPTION_CREATED = "subscription_created"


class AnalyticsService:
    """
    Track events and analytics for ALICI.
    Integrates with Mixpanel for production analytics.
    """
    
    def __init__(self):
        """Initialize analytics service"""
        self.token = os.getenv("MIXPANEL_TOKEN")
        self.events_buffer: List[Dict] = []
        self.enabled = bool(self.token)
    
    def track_event(self, user_id: str, event_type: EventType, properties: Dict = None) -> bool:
        """
        Track a user event
        
        Args:
            user_id: ALICI user ID
            event_type: Type of event (from EventType enum)
            properties: Additional properties for the event
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            event_data = {
                "user_id": user_id,
                "event": event_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "properties": properties or {}
            }
            
            self.events_buffer.append(event_data)
            
            # Flush if buffer gets large
            if len(self.events_buffer) >= 100:
                self.flush()
            
            return True
        except Exception as e:
            print(f"Analytics error: {str(e)}")
            return False
    
    def track_signup(self, user_id: str, email: str) -> bool:
        """Track user signup"""
        return self.track_event(
            user_id,
            EventType.USER_SIGNUP,
            {"email": email, "signup_source": "organic"}
        )
    
    def track_first_message(self, user_id: str, content_length: int = 0) -> bool:
        """Track first message sent"""
        return self.track_event(
            user_id,
            EventType.FIRST_MESSAGE,
            {"content_length": content_length}
        )
    
    def track_plan_upgrade(self, user_id: str, from_plan: str, to_plan: str, amount: float = 0) -> bool:
        """Track subscription upgrade"""
        return self.track_event(
            user_id,
            EventType.PLAN_UPGRADE,
            {
                "from_plan": from_plan,
                "to_plan": to_plan,
                "amount": amount
            }
        )
    
    def track_plan_downgrade(self, user_id: str, from_plan: str, to_plan: str) -> bool:
        """Track subscription downgrade"""
        return self.track_event(
            user_id,
            EventType.PLAN_DOWNGRADE,
            {
                "from_plan": from_plan,
                "to_plan": to_plan
            }
        )
    
    def track_api_call(self, user_id: str, endpoint: str, latency_ms: int, status_code: int = 200) -> bool:
        """Track API call"""
        return self.track_event(
            user_id,
            EventType.API_CALL,
            {
                "endpoint": endpoint,
                "latency_ms": latency_ms,
                "status_code": status_code
            }
        )
    
    def track_message(self, user_id: str, message_length: int, response_time_ms: int = 0) -> bool:
        """Track message sent"""
        return self.track_event(
            user_id,
            EventType.MESSAGE_SENT,
            {
                "length": message_length,
                "response_time_ms": response_time_ms
            }
        )
    
    def set_user_properties(self, user_id: str, properties: Dict) -> bool:
        """
        Update user properties (plan, location, etc)
        
        Args:
            user_id: ALICI user ID
            properties: Dict of user properties
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            # In production, would call Mixpanel API
            # mp.people_set(user_id, properties)
            print(f"[ANALYTICS] Updated user properties: {user_id}")
            return True
        except Exception as e:
            print(f"Analytics error: {str(e)}")
            return False
    
    def flush(self) -> bool:
        """
        Send buffered events to Mixpanel
        
        Returns:
            True if successful
        """
        if not self.enabled or not self.events_buffer:
            return False
        
        try:
            # In production, would batch post to Mixpanel API
            # response = requests.post(
            #     "https://api.mixpanel.com/track",
            #     data={"data": base64.b64encode(json.dumps(self.events_buffer))}
            # )
            
            event_count = len(self.events_buffer)
            self.events_buffer = []
            
            print(f"[ANALYTICS] Flushed {event_count} events")
            return True
        except Exception as e:
            print(f"Analytics flush error: {str(e)}")
            return False
    
    def get_user_metrics(self, user_id: str) -> Dict:
        """
        Get metrics for a specific user
        
        Args:
            user_id: ALICI user ID
            
        Returns:
            User metrics dictionary
        """
        # In production, would query Mixpanel API
        return {
            "user_id": user_id,
            "signup_date": None,
            "first_message_date": None,
            "messages_sent": 0,
            "plan": "free",
            "lifetime_value": 0,
            "last_active": None
        }
    
    def get_cohort_metrics(self) -> Dict:
        """
        Get aggregated metrics across all users
        
        Returns:
            Cohort metrics
        """
        return {
            "total_users": 0,
            "active_users_today": 0,
            "active_users_month": 0,
            "mau": 0,  # Monthly Active Users
            "signup_count_today": 0,
            "paid_users": 0,
            "mrr": 0,  # Monthly Recurring Revenue
            "avg_messages_per_user": 0,
            "avg_session_duration_seconds": 0,
            "conversion_rate": 0.0,
            "churn_rate": 0.0,
            "nps_score": None
        }
    
    def calculate_funnel_conversion(self, step1_count: int, step2_count: int) -> float:
        """
        Calculate conversion rate between funnel steps
        
        Args:
            step1_count: Count at step 1
            step2_count: Count at step 2
            
        Returns:
            Conversion rate (0.0-1.0)
        """
        if step1_count == 0:
            return 0.0
        return step2_count / step1_count
    
    def estimate_ltv(self, arpu: float, gross_margin: float, monthly_churn: float) -> float:
        """
        Estimate Lifetime Value (SaaS standard formula)
        
        Based on industry benchmarks for AI/SaaS products.
        Formula: LTV = ARPU × Gross Margin / Monthly Churn Rate
        
        Args:
            arpu: Average Revenue Per User (monthly, in BRL)
            gross_margin: Gross margin percentage (0.0-1.0), typically 70-85% for SaaS
            monthly_churn: Monthly churn rate (0.0-1.0), e.g., 0.05 = 5% monthly churn
            
        Returns:
            Estimated LTV in BRL
        """
        if monthly_churn == 0:
            # Zero churn scenario: assume 1-year payoff period minimum
            # More realistic than infinite months
            return arpu * gross_margin * 12
        
        if monthly_churn >= 1.0:
            return 0
        
        # Standard SaaS LTV formula
        avg_lifetime_months = 1 / monthly_churn
        ltv = (arpu * gross_margin) * avg_lifetime_months
        
        # Cap at reasonable maximum (e.g., 10 year customer)
        max_ltv = arpu * gross_margin * 120
        return min(ltv, max_ltv)
    
    def calculate_cac_payback(self, cac: float, arpu: float, gross_margin: float) -> float:
        """
        Calculate CAC payback period in months
        
        Args:
            cac: Customer Acquisition Cost
            arpu: Average Revenue Per User (monthly)
            gross_margin: Gross margin (0.0-1.0)
            
        Returns:
            Months to recover CAC
        """
        if arpu * gross_margin == 0:
            return float('inf')
        
        return cac / (arpu * gross_margin)
    
    def project_mrr(self, free_users: int, conversion_rate: float, arpu: float, monthly_churn: float) -> Dict:
        """
        Project Monthly Recurring Revenue from free user base
        
        Args:
            free_users: Number of free users
            conversion_rate: Conversion rate from free to paid (0.0-1.0)
            arpu: Average Revenue Per User (monthly)
            monthly_churn: Monthly churn rate (0.0-1.0)
            
        Returns:
            Dict with MRR projections for next 12 months
        """
        projections = {}
        current_paid_users = free_users * conversion_rate
        current_mrr = current_paid_users * arpu
        
        for month in range(1, 13):
            # Apply monthly churn
            current_paid_users = current_paid_users * (1 - monthly_churn)
            current_mrr = current_paid_users * arpu
            
            projections[f"month_{month}"] = {
                "paid_users": round(current_paid_users, 0),
                "mrr": round(current_mrr, 2),
                "churn_rate": monthly_churn
            }
        
        return projections
    
    def calculate_ltv_sensitivity(self, arpu: float, gross_margin: float, churn_rates: List[float]) -> Dict:
        """
        Calculate LTV sensitivity to churn rates
        Useful for pitch deck and investor presentations
        
        Args:
            arpu: Average Revenue Per User (monthly)
            gross_margin: Gross margin percentage (0.0-1.0)
            churn_rates: List of monthly churn rates to test
            
        Returns:
            Dict mapping churn rate to LTV
        """
        sensitivity = {}
        for churn in churn_rates:
            ltv = self.estimate_ltv(arpu, gross_margin, churn)
            sensitivity[f"{churn*100:.0f}%_churn"] = {
                "ltv": round(ltv, 2),
                "ltv_to_cac_ratio": round(ltv / 200, 2) if ltv > 0 else 0,
                "payback_months": round(1 / churn, 1) if churn > 0 else float('inf')
            }
        return sensitivity


# Global analytics instance
analytics = AnalyticsService()
