# 🚀 PHASE 1 EXECUTION — STRIPE + ANALYTICS + SALES

**Duration**: Months 1-6 (immediately post-seed)  
**Goals**: 
- MVP with payments (Stripe live)
- 200 beta users, 20 paying (R$3.5k MRR)
- Operational metrics dashboard
- Repeatable founder-led sales process
- Series A pitch deck ready

---

## 💳 STRIPE INTEGRATION (Weeks 1-3)

### Stripe API Setup

```python
# alici_api/services/stripe_service.py

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    """Manage subscriptions, payments, invoices"""
    
    PLANS = {
        "free": {
            "name": "Free",
            "price_usd": 0,
            "price_brl": 0,
            "stripe_price_id": "price_free",  # Not in Stripe (no charge)
        },
        "pro": {
            "name": "Pro",
            "price_usd": 9,
            "price_brl": 49,
            "stripe_price_id": "price_pro_monthly",
            "features": ["100 messages/day", "3GB storage", "basic analytics"]
        },
        "ultra": {
            "name": "Ultra",
            "price_usd": 19,
            "price_brl": 99,
            "stripe_price_id": "price_ultra_monthly",
            "features": ["Unlimited messages", "100GB storage", "advanced analytics", "API access"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price_usd": "Custom",
            "price_brl": "Custom",
            "stripe_price_id": None,  # Manual handling
            "features": ["Everything in Ultra", "SSO", "SLA", "dedicated support"]
        }
    }
    
    @staticmethod
    def create_customer(user_email: str, user_name: str) -> str:
        """Create Stripe customer linked to ALICI user"""
        customer = stripe.Customer.create(
            email=user_email,
            name=user_name,
            metadata={
                "alici_user_id": user_email.split("@")[0],  # Placeholder
                "created_at": datetime.utcnow().isoformat()
            }
        )
        return customer.id
    
    @staticmethod
    def create_subscription(user_id: str, stripe_customer_id: str, plan: str) -> Dict:
        """Create monthly subscription for user"""
        if plan == "free":
            return {"status": "active", "plan": "free", "amount": 0}
        
        price_id = StripeService.PLANS[plan]["stripe_price_id"]
        
        subscription = stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            collection_method="charge_automatically",
            metadata={
                "alici_user_id": user_id,
                "plan": plan
            }
        )
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "plan": plan,
            "amount": StripeService.PLANS[plan]["price_brl"],
            "next_billing": subscription.current_period_end,
            "client_secret": subscription.client_secret  # For payment confirmation
        }
    
    @staticmethod
    def upgrade_subscription(subscription_id: str, new_plan: str) -> Dict:
        """Upgrade/downgrade user plan (pro → ultra)"""
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        new_price_id = StripeService.PLANS[new_plan]["stripe_price_id"]
        
        # Update the item
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription.items.data[0].id,
                "price": new_price_id
            }],
            proration_behavior="always_invoice"  # Pro-rate costs
        )
        
        return {
            "subscription_id": updated_subscription.id,
            "new_plan": new_plan,
            "status": updated_subscription.status,
            "prorated_charge": updated_subscription.latest_invoice
        }
    
    @staticmethod
    def cancel_subscription(subscription_id: str, immediate: bool = False) -> Dict:
        """Cancel subscription (at end of period or immediately)"""
        if immediate:
            deleted = stripe.Subscription.delete(subscription_id)
            return {"status": "canceled_immediately", "refund": "check email"}
        else:
            cancelled = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return {
                "status": cancelled.status,
                "final_billing": cancelled.current_period_end
            }
    
    @staticmethod
    def list_invoices(stripe_customer_id: str) -> list:
        """Get all invoices for a customer"""
        invoices = stripe.Invoice.list(customer=stripe_customer_id, limit=20)
        return [
            {
                "invoice_id": inv.id,
                "amount": inv.total / 100,  # Convert cents to dollars
                "date": inv.created,
                "status": inv.status,
                "pdf_url": inv.invoice_pdf
            }
            for inv in invoices.data
        ]
    
    @staticmethod
    def handle_webhook(event: Dict) -> None:
        """Process Stripe webhooks (payment, subscription changes)"""
        event_type = event["type"]
        data = event["data"]["object"]
        
        if event_type == "invoice.payment_succeeded":
            # Update user's payment status in DB
            user_id = data["metadata"]["alici_user_id"]
            StripeService._record_payment(user_id, data["amount"] / 100)
        
        elif event_type == "customer.subscription.updated":
            user_id = data["metadata"]["alici_user_id"]
            new_plan = data["metadata"]["plan"]
            StripeService._update_user_plan(user_id, new_plan)
        
        elif event_type == "customer.subscription.deleted":
            user_id = data["metadata"]["alici_user_id"]
            StripeService._downgrade_user_to_free(user_id)
    
    @staticmethod
    def _record_payment(user_id: str, amount: float):
        """Log payment in ALICI database"""
        # Implementation: Update users table, payment_transactions table
        pass
    
    @staticmethod
    def _update_user_plan(user_id: str, plan: str):
        """Update user's plan in ALICI database"""
        # Implementation: Update users.plan
        pass
    
    @staticmethod
    def _downgrade_user_to_free(user_id: str):
        """Downgrade user after subscription cancellation"""
        # Implementation: Update users.plan = 'free'
        pass
```

### Stripe Webhook Handler

```python
# alici_api/routes/billing.py

from fastapi import APIRouter, Request, HTTPException
import stripe
import hmac
import hashlib
import os
from alici_api.services.stripe_service import StripeService

router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks (must be POST)"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Verify webhook authenticity
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle event
    try:
        StripeService.handle_webhook(event)
    except Exception as e:
        print(f"Stripe webhook processing error: {e}")
        # Don't fail, Stripe will retry
    
    return {"status": "received"}

@router.get("/subscription")
async def get_subscription(user_id: str):
    """Get current subscription for user"""
    from alici_api.dependencies import get_current_user
    current_user = await get_current_user(user_id)
    
    # Get from DB
    subscription = {
        "plan": current_user.plan,
        "stripe_subscription_id": current_user.stripe_subscription_id,
        "next_billing": current_user.subscription_end_date
    }
    return subscription

@router.post("/checkout")
async def create_checkout_session(plan: str, user_id: str):
    """Create Stripe Checkout session for upgrade"""
    from alici_api.dependencies import get_current_user
    current_user = await get_current_user(user_id)
    
    # Create session
    session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        line_items=[{
            "price": StripeService.PLANS[plan]["stripe_price_id"],
            "quantity": 1
        }],
        mode="subscription",
        success_url="https://alici.ai/dashboard?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://alici.ai/dashboard"
    )
    
    return {"checkout_url": session.url}
```

### Frontend Stripe Integration

```javascript
// static/js/billing.js

async function upgradeToProPlan() {
    // Call backend to create checkout session
    const response = await fetch('/billing/checkout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plan: 'pro' })
    });
    
    const { checkout_url } = await response.json();
    
    // Redirect to Stripe Checkout (hosted page)
    window.location.href = checkout_url;
}

async function showCurrentPlan() {
    const response = await fetch('/billing/subscription', {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    const { plan, next_billing } = await response.json();
    
    document.getElementById('current-plan').innerText = plan.toUpperCase();
    if (plan !== 'free') {
        document.getElementById('next-billing').innerText = 
            new Date(next_billing * 1000).toLocaleDateString('pt-BR');
    }
}

// Run on dashboard load
showCurrentPlan();
```

---

## 📊 ANALYTICS SETUP (Weeks 2-4)

### Mixpanel Integration

```python
# alici_api/services/analytics_service.py

from mixpanel import Mixpanel
import os

class AnalyticsService:
    """Track events, user properties, funnels"""
    
    def __init__(self):
        self.mp = Mixpanel(os.getenv("MIXPANEL_TOKEN"))
    
    def track_user_signup(self, user_id: str, email: str):
        """User completed registration"""
        self.mp.track(user_id, 'User Signup', {
            'email': email,
            'signup_date': datetime.utcnow().isoformat()
        })
    
    def track_first_message(self, user_id: str):
        """User sent first chat message"""
        self.mp.track(user_id, 'First Message', {
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def track_plan_upgrade(self, user_id: str, from_plan: str, to_plan: str):
        """User upgraded subscription"""
        self.mp.track(user_id, 'Plan Upgrade', {
            'from_plan': from_plan,
            'to_plan': to_plan,
            'upgrade_date': datetime.utcnow().isoformat()
        })
    
    def track_api_call(self, user_id: str, endpoint: str, latency_ms: int):
        """Log API usage for analytics"""
        self.mp.track(user_id, 'API Call', {
            'endpoint': endpoint,
            'latency_ms': latency_ms
        })
    
    def set_user_properties(self, user_id: str, properties: dict):
        """Update user profile in Mixpanel"""
        self.mp.people_set(user_id, properties)
    
    def get_funnel_conversion(self, funnel_name: str) -> dict:
        """Query funnel data from Mixpanel API"""
        # Implementation: Call Mixpanel API
        return {
            "funnel": funnel_name,
            "conversion_rate": 0.10,
            "steps": [...]
        }
```

### Dashboard Analytics

```html
<!-- templates/analytics.html -->

<div class="analytics-container">
    <h2>ALICI Metrics Dashboard</h2>
    
    <div class="metrics-grid">
        <!-- Daily Active Users -->
        <div class="metric-card">
            <h3>Daily Active Users</h3>
            <canvas id="dau-chart"></canvas>
            <p id="dau-value">--</p>
        </div>
        
        <!-- MRR -->
        <div class="metric-card">
            <h3>Monthly Recurring Revenue</h3>
            <canvas id="mrr-chart"></canvas>
            <p id="mrr-value">R$ 0</p>
        </div>
        
        <!-- Conversion Funnel -->
        <div class="metric-card">
            <h3>Signup → Paid Funnel</h3>
            <table>
                <tr><td>Signups</td><td>200</td><td>100%</td></tr>
                <tr><td>Trial Start</td><td>180</td><td>90%</td></tr>
                <tr><td>First Message</td><td>120</td><td>60%</td></tr>
                <tr><td>Conversion</td><td>20</td><td>10%</td></tr>
            </table>
        </div>
        
        <!-- Retention -->
        <div class="metric-card">
            <h3>Monthly Retention</h3>
            <canvas id="retention-chart"></canvas>
            <p>M1: 95%, M2: 85%, M3: 80%</p>
        </div>
    </div>
</div>

<script src="https://cdn.mixpanel.com/mixpanel.js"></script>
<script>
mixpanel.init("YOUR_TOKEN");

// Custom realtime dashboard
async function loadMetrics() {
    const response = await fetch('/analytics/metrics', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    
    const { dau, mrr, users, paying_users } = await response.json();
    
    document.getElementById('dau-value').innerText = dau;
    document.getElementById('mrr-value').innerText = `R$ ${mrr.toLocaleString()}`;
    
    // Render charts
    renderConversionFunnel(users, paying_users);
    renderRetention();
}

loadMetrics();
setInterval(loadMetrics, 60000); // Refresh every minute
</script>
```

---

## 📧 COLD EMAIL SEQUENCE (Month 1-6)

### Target Profiles

```
Segment 1: Fintech Founders (Brazil)
├─ Company size: 10-50 people
├─ Use case: Legal docs analysis, compliance
├─ Pain point: ChatGPT is expensive + no memory
├─ Willingness to pay: R$500-2k/month (enterprise)
└─ Outreach: 100 founders via LinkedIn

Segment 2: Marketing Agencies
├─ Company size: 20-100 people
├─ Use case: Content ideas, copywriting, SEO optimization
├─ Pain point: Time-consuming, needs domain knowledge
├─ Willingness to pay: R$100-300/month
└─ Outreach: 150 agencies via ZoomInfo

Segment 3: SaaS Companies
├─ Company size: 30-200 people
├─ Use case: Customer support, code generation, docs
├─ Pain point: OpenAI API costs mounting, no memory context
├─ Willingness to pay: Custom enterprise
└─ Outreach: 50 CTOs/eng leads via AngelList
```

### Email Sequence Templates

```
EMAIL 1 (Day 0): Personalized Cold Open
──────────────────────────────────────

Subject: [Company name] + better AI memory?

Hi [Name],

I saw that [Company] is using ChatGPT for [use case]. 

Most teams don't realize ChatGPT forgets everything between sessions — so every conversation starts from scratch.

ALICI remembers. We're purpose-built for teams that need:
• Persistent context across conversations
• Affordable pricing (vs OpenAI enterprise)
• Owned by you (no vendor lock-in)

We just closed our Series Seed. 20 early customers are seeing 30% productivity gains.

Want to be our [Industry] reference customer?

Free 14-day trial: [link]

  Mateus  
  Founder, ALICI
  mateus@alici.ai

[No CTA pressure — just opening door]


EMAIL 2 (Day 3): Social Proof + Traction
──────────────────────────────────────

Subject: Re: ALICI + [Company name]

Hi [Name],

Following up — I wanted to share what we're seeing with similar teams:

[Similar company] (marketing agency, ~40 people) tried ALICI and reduced their copywriting time by 25%. They're now on our Pro plan.

The key difference: We save conversation history. So ALICI learns your brand voice, your customer segments, your tone.

Available for a quick 15-min call next Tuesday?

  Mateus  
  Founder, ALICI


EMAIL 3 (Day 7): Case Study + Specificity
──────────────────────────────────────

Subject: Case study: [Similar company] saves R$5k/month

Hi [Name],

Attached is a case study from [similar company].

In 30 days, they:
• Reduced chat messages needed (because ALICI remembers context)
• Cut ChatGPT API spend by 40% (switched to ALICI Pro)
• Gave team back 10 hours/week

Does this resonate with [Company]'s workflow?

Happy to show you how ALICI would work for [specific use case].

  Mateus


EMAIL 4 (Day 10): Demo Offer
──────────────────────────────

Subject: 5-min ALICI demo for [Company]

Hi [Name],

Want to see ALICI in action?

5-minute walkthrough:
1. Chat about [your use case]
2. Show how memory solves [their pain]
3. Answer questions

Calendly: [link]

(No pressure — just want to see if this fits)

  Mateus
```

### Email Cadence

```
Week 1: Email 1 (cold open)
Week 2: Email 2 (social proof) if no reply
Week 3: Email 3 (case study) if no reply
Week 4: EMAIL 4 (demo) if no reply
Week 5: STOP if no engagement

Success metrics:
├─ Open rate: 40%+ (personalized = better)
├─ Reply rate: 5-10%
├─ Demo scheduled: 2-3%
├─ Customer closed: 0.5-1% (1 of 50-100)
```

### Email Automation Setup (SendGrid)

```python
# alici_api/services/email_service.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    
    def send_cold_email_sequence(self, prospect_email: str, prospect_name: str, company: str):
        """Queue cold email sequence emails"""
        # Email 1 (Day 0)
        self._schedule_email(
            to_email=prospect_email,
            subject=f"{company} + better AI memory?",
            template_name="cold_open",
            variables={"name": prospect_name, "company": company},
            send_at=datetime.utcnow()
        )
        
        # Email 2 (Day 3)
        self._schedule_email(
            to_email=prospect_email,
            subject="Re: ALICI + " + company,
            template_name="social_proof",
            variables={"name": prospect_name},
            send_at=datetime.utcnow() + timedelta(days=3)
        )
        
        # Email 3 (Day 7)
        self._schedule_email(
            to_email=prospect_email,
            subject="Case study: [Similar company] saves R$5k/month",
            template_name="case_study",
            variables={"name": prospect_name},
            send_at=datetime.utcnow() + timedelta(days=7)
        )
        
        # Email 4 (Day 10)
        self._schedule_email(
            to_email=prospect_email,
            subject=f"5-min ALICI demo for {company}",
            template_name="demo_offer",
            variables={"name": prospect_name},
            send_at=datetime.utcnow() + timedelta(days=10)
        )
    
    def _schedule_email(self, to_email, subject, template_name, variables, send_at):
        """Use SendGrid template system"""
        message = Mail(
            from_email="mateus@alici.ai",
            to_emails=to_email,
            subject=subject
        )
        
        # Set template + personalizations
        message.template_id = os.getenv(f"SENDGRID_TEMPLATE_{template_name.upper()}")
        message.dynamic_template_data = variables
        
        # Queue send
        self.sg.send(message)
```

---

## 📱 PRODUCT-LED GROWTH (Months 1-6)

### Free Trial Funnel

```
Sign up (landing page CTA)
    ↓
Verify email (automated)
    ↓
Create account (dashboard redirect)
    ↓
Send first message (guided demo)
    ↓
See memory in action (key feature reveal)
    ↓
Offer upgrade to Pro (after 10 free messages)
```

### Free Trial Configuration

```python
# alici_api/services/trial_service.py

class TrialService:
    """Manage free trial limits and upsell"""
    
    TRIAL_LIMITS = {
        "free": {
            "messages_per_day": 20,
            "storage_mb": 100,
            "history_retention_days": 7,
            "api_calls": 0,
            "trial_duration_days": 14
        },
        "pro": {
            "messages_per_day": 100,
            "storage_mb": 3000,
            "history_retention_days": 365,
            "api_calls": 1000,
            "trial_duration_days": 0  # No trial for paid
        }
    }
    
    def check_trial_expired(self, user_id: str) -> bool:
        """Check if user's free trial ended"""
        user = get_user(user_id)
        if user.plan != "free":
            return False
        
        days_since_signup = (datetime.utcnow() - user.created_at).days
        return days_since_signup > 14
    
    def show_upsell_prompt(self, user_id: str, reason: str) -> str:
        """Show upgrade prompt when user hits limit"""
        
        upsell_messages = {
            "daily_limit_hit": "You've reached your 20 daily messages (Free plan limit). Upgrade to Pro for 100/day.",
            "trial_ending": "Your 14-day free trial ends tomorrow. Upgrade to Pro (R$49/mês) for unlimited messages.",
            "storage_full": "You've used all 100MB of storage. Pro includes 3GB.",
            "no_api_access": "Need API access? Upgrade to Pro or Ultra."
        }
        
        return upsell_messages.get(reason, "Upgrade to Pro for more features.")
```

### In-App Notifications

```javascript
// static/js/upsell.js

function checkTrialStatus() {
    fetch('/trial/status', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.days_left === 3) {
            showTrialEndingBanner(data.days_left);
        } else if (data.limit_hit) {
            showUpgradeModal(data.limit_type);
        }
    });
}

function showUpgradeModal(limitType) {
    const modal = document.getElementById('upgrade-modal');
    const message = {
        'daily_limit': 'You\'ve reached your daily message limit',
        'storage': 'You need more storage for these documents',
        'api_limit': 'API access requires Pro or Ultra'
    }[limitType];
    
    modal.querySelector('p').innerText = message;
    modal.style.display = 'flex';
    
    // CTA button
    modal.querySelector('button').onclick = () => {
        window.location.href = '/billing/checkout?plan=pro';
    };
}

// Run every 5 minutes
setInterval(checkTrialStatus, 5 * 60 * 1000);
```

---

## 📊 PHASE 1 SUCCESS METRICS

```
Month 1: Launch
├─ 50 signups (organic + founder networks)
├─ 3 paying customers (R$147/month MRR)
├─ Stripe live + secure
├─ Mixpanel tracking active
└─ First 5 cold emails sent

Month 2: Growth
├─ 100 signups
├─ 10 paying (R$500 MRR)
├─ Cold email sequence generating 2-3 demos/week
├─ First enterprise customer inquiry
└─ NPS: 30+ (target: 25+)

Month 3: Scaling
├─ 150 signups
├─ 15 paying (R$750 MRR)
├─ 1 enterprise customer ($2k-5k deal)
├─ Referral loop showing signs (10% of signups)
└─ Retention: 85% MoM

Month 4-6: Consolidation
├─ 300 signups (M6)
├─ 20+ paying (R$1k+ MRR)
├─ 3-5 enterprise customers ($120k MRR total)
├─ Launch ProductHunt (generate buzz)
├─ Community discord (100+ members)
└─ Preparation for Series A pitch

Target M6 MRR: R$3,500
└─ Free users: 300
└─ Pro: 15 × R$49 = R$735
└─ Ultra: 5 × R$99 = R$495
└─ Enterprise: 3-5 × R$500-2000 = R$2,500
```

---

## ✅ PHASE 1 LAUNCH CHECKLIST

Weeks 1-3 (Stripe):
- [ ] Stripe account created + keys in `.env`
- [ ] Billing page designed (upgrade CTA)
- [ ] Webhook receiver tested locally
- [ ] Pro/Ultra prices configured in Stripe dashboard
- [ ] Test credit card flows (Stripe test mode)
- [ ] Invoice generation working
- [ ] Cancel/refund policy documented

Weeks 2-4 (Analytics):
- [ ] Mixpanel account created
- [ ] Analytics service integrated
- [ ] Key events tracked (signup, first message, upgrade)
- [ ] Dashboard built (metrics visible)
- [ ] Funnel analysis set up
- [ ] UTM parameters configured (source tracking)

Weeks 4-6 (Sales):
- [ ] Cold email templates written + approved
- [ ] Prospect list prepared (100+ emails)
- [ ] SendGrid account + templates configured
- [ ] Calendly / Demo scheduling link ready
- [ ] Case study content prepared
- [ ] Cold email sequence testing in staging

Ongoing (Month 1-6):
- [ ] Daily review: signups, MRR, retention
- [ ] Weekly: Cold email metrics (open, reply, demo scheduled)
- [ ] Bi-weekly: One-on-one customer calls (learning)
- [ ] Monthly: Full metrics review + roadmap adjustment

---

**Phase 1 Focus**: Founder-led sales + product retention  
*At end of M6, have: recurring revenue, repeatable sales process, clear product-market fit signals.*

