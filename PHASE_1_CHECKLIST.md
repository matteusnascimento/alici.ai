# ✅ PHASE 1 EXECUTION CHECKLIST

**Phase 1 Duration**: Months 1-6  
**Target**: 200 users, 20 paying, R$3.5k MRR  
**Last Updated**: March 4, 2026

---

## WEEK 1: STRIPE SETUP

**Status**: [ ] Not Started

### Prerequisites
- [ ] Stripe account created (stripe.com)
- [ ] API keys generated (Secret + Publishable)
- [ ] API keys saved in `.env` file
  ```
  STRIPE_SECRET_KEY=sk_live_...
  STRIPE_PUBLISHABLE_KEY=pk_live_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  ```
- [ ] Test mode enabled (start with test keys: sk_test_*)

### Backend Implementation
- [ ] Install Stripe Python library: `pip install stripe`
- [ ] Create `alici_api/services/stripe_service.py` ✅ DONE
- [ ] Create `alici_api/routes/billing.py` with webhook handler
- [ ] Add environment variable validation in startup
- [ ] Test locally with Stripe test cards:
  - [ ] Valid card: `4242 4242 4242 4242`
  - [ ] Declined card: `4000 0000 0000 0002`
  - [ ] 3D Secure: `4000 0025 0000 3155`

### Frontend Integration
- [ ] Create upgrade CTA buttons on dashboard
- [ ] Create `static/js/billing.js` with Stripe.js integration
- [ ] Test checkout flow locally
- [ ] Confirm payment success redirects to dashboard

### Testing
- [ ] Create customer endpoint working
- [ ] Create subscription endpoint working
- [ ] Upgrade plan endpoint working
- [ ] Cancel subscription endpoint working
- [ ] Webhook receiver tested (use Stripe CLI locally)
- [ ] Database updates when payment received

### Deployment
- [ ] Push Stripe keys to production `.env`
- [ ] Webhook URL configured in Stripe Dashboard
- [ ] SSL certificate valid (required for webhooks)
- [ ] Monitor webhook delivery in Stripe Dashboard

---

## WEEK 2: ANALYTICS SETUP

**Status**: [ ] Not Started

### Choose Analytics Platform
- [ ] Option 1: Mixpanel (recommended for SaaS)
  - [ ] Create account at mixpanel.com
  - [ ] Create project
  - [ ] Generate API token
  - [ ] Install Python library: `pip install mixpanel`
  
- [ ] Option 2: Segment (event warehouse)
  - [ ] Create account at segment.com
  - [ ] Create source
  - [ ] Connect destinations (Mixpanel, Amplitude, etc)

### Backend Implementation
- [ ] Create `alici_api/services/analytics_service.py` ✅ DONE
- [ ] Integrate with routing:
  - [ ] Track user signups
  - [ ] Track first message (activation)
  - [ ] Track plan upgrades
  - [ ] Track API calls
- [ ] Add analytics to `/auth/register` endpoint
- [ ] Add analytics to `/chat` endpoint
- [ ] Add analytics to `/billing/checkout` endpoint

### Event Tracking
- [ ] User Signup: When account created
- [ ] First Message: When user sends first chat
- [ ] Plan Upgrade: When user upgrades plan
- [ ] Plan Downgrade: When user downgrades
- [ ] Trial Ended: When free trial expires
- [ ] Subscription Created: When paid subscription starts
- [ ] API Call: Track endpoint usage + latency

### Dashboards
- [ ] Create Mixpanel dashboard:
  - [ ] Daily Active Users (DAU)
  - [ ] Monthly Recurring Revenue (MRR)
  - [ ] Conversion funnel (signup → trial → paid)
  - [ ] Retention chart (day 1, 7, 30)
  - [ ] User segmentation
- [ ] Create alerts for:
  - [ ] Churn spike (>10% MoM)
  - [ ] Zero signups in a day
  - [ ] Payment errors (invoice failures)

### Testing
- [ ] Events firing in Mixpanel live view
- [ ] Funnel conversion rates calculated
- [ ] Cohort retention showing in dashboard
- [ ] Export data to CSV for reporting

---

## WEEK 3-4: COLD EMAIL SEQUENCE

**Status**: [ ] Not Started

### Preparation
- [ ] Create target list (~100-200 prospects):
  - [ ] Fintech founders (LinkedIn search)
  - [ ] Marketing agencies (ZoomInfo)
  - [ ] SaaS CTOs (AngelList, Twitter)
- [ ] Research each prospect:
  - [ ] LinkedIn profile review
  - [ ] Company website check
  - [ ] Recent news/funding (personalization angle)
- [ ] Prepare email templates:
  - [ ] Email 1: Cold open (day 0)
  - [ ] Email 2: Social proof (day 3)
  - [ ] Email 3: Case study (day 7)
  - [ ] Email 4: Demo offer (day 10)

### Email Automation Setup
- [ ] Create SendGrid account (or Mailgun, Outreach)
- [ ] Verify sender domain (alici.ai)
- [ ] Create email templates with variables
- [ ] Set up automation sequence:
  - [ ] Segment prospects by type
  - [ ] Schedule emails at optimal times (9am Tuesday-Thursday)
  - [ ] Track opens, clicks, replies

### First Campaign (Batch 1: 50 emails)
- [ ] Send 50 cold opens (day 0)
- [ ] Monitor open rate (target: >40%)
- [ ] Respond to replies manually (high touch)
- [ ] Track demo scheduled (target: 2-3)

### Tools Setup
- [ ] Email authentication (SPF, DKIM, DMARC)
- [ ] Deliverability monitoring
- [ ] Unsubscribe management
- [ ] CRM integration (HubSpot or Airtable)

### Scaling
- [ ] Batch 2: 50 more emails (week 3-4)
- [ ] Batch 3: 100 more emails (month 2)
- [ ] Iterate based on replies and conversions
- [ ] A/B test subject lines

---

## WEEK 4-6: PRODUCT-LED GROWTH

**Status**: [ ] Not Started

### Free Trial Configuration
- [ ] Set trial duration: 14 days
- [ ] Set usage limits:
  - [ ] Messages: 20/day
  - [ ] Storage: 100MB
  - [ ] History: 7 days
- [ ] Create trial expiry notifications:
  - [ ] Email at day 1
  - [ ] Email at day 10
  - [ ] In-app banner at day 13

### Upgrade Prompts
- [ ] When user hits daily message limit
  - [ ] Show modal: "Upgrade to Pro for 100/day"
  - [ ] Direct link to `/billing/checkout?plan=pro`
- [ ] When user storage full
  - [ ] Show modal: "Need more space? Upgrade to Pro (3GB)"
- [ ] When trial ending
  - [ ] Show banner: "3 days left in trial. Upgrade now"

### Landing Page Optimization
- [ ] Clear Free/Pro/Ultra comparison table
- [ ] "Start free" CTA above fold
- [ ] Social proof: Customer logos, testimonials
- [ ] Pricing page: Features per plan

### Referral Program (Optional)
- [ ] Create referral link for each user
- [ ] Offer incentive: "R$10 credit per referral"
- [ ] Track referral clicks + conversions
- [ ] Display referral dashboard in settings

---

## MONTH 1-2: BETA TESTING

**Status**: [ ] Not Started

### Internal Testing
- [ ] QA test all signup flows
- [ ] QA test all payment flows
- [ ] QA test analytics tracking (events firing)
- [ ] Load testing: Ensure dashboard handles 100 concurrent users

### Beta User Recruitment (20-30 users)
- [ ] Invite friends + family
- [ ] Post on Product Hunt (pre-launch)
- [ ] Post on relevant Slack communities
- [ ] Direct outreach to early contacts

### Feedback Collection
- [ ] NPS survey: "How likely to recommend?" (target: 30+)
- [ ] Feature requests survey
- [ ] Bug reports form
- [ ] User interviews (1:1 calls, 5-10 users)

### Metrics Target (Month 2)
- [ ] Signups: 100+
- [ ] Trial starters: 90%
- [ ] Paying customers: 10 (10% conversion)
- [ ] MRR: R$500-750
- [ ] NPS: 25+
- [ ] Churn: <5% (new customers)

### Bug Fixes
- [ ] Payment failures: Resolve immediately
- [ ] Login issues: High priority
- [ ] Analytics gaps: Missing events
- [ ] UI bugs: Polish interface

---

## MONTH 3: TRACTION PHASE

**Status**: [ ] Not Started

### Growth Levers
- [ ] Cold email: Scale to 200 emails (Batches 2-3)
- [ ] ProductHunt: Plan launch for month 3-4
- [ ] SEO: Publish 3-5 blog posts (target keywords)
- [ ] Twitter: Build founder presence (@mateusnascimento)
- [ ] Discord: Launch community server (100+ members target)

### Sales Process
- [ ] Create case study from first customer
  - [ ] Document their use case
  - [ ] Quantify results (time saved, cost reduction)
  - [ ] Get testimonial + permission to use
- [ ] Sales playbook created:
  - [ ] Pitch deck (investor-grade)
  - [ ] Product demo script (10 min)
  - [ ] Objection handling guide
  - [ ] Pricing sheet + custom quotes

### Enterprise Sales
- [ ] Target 1 enterprise customer (R$500-2k/month)
- [ ] Outreach to CTOs / VPs at 10+ person companies
- [ ] Create enterprise proposal template
- [ ] Negotiate SOW (Statement of Work)

### Metrics Target (Month 3)
- [ ] Signups: 150+
- [ ] Paying customers: 15
- [ ] MRR: R$1,000+
- [ ] CAC (from cold email): <R$300
- [ ] Demo scheduled: 5-10/month
- [ ] NPS: 30+
- [ ] Churn: 5-10% MoM (acceptable for early SaaS)

---

## MONTH 4-5: SCALING PHASE

**Status**: [ ] Not Started

### UserTesting & Optimization
- [ ] Session recording setup (Hotjar / LogRocket)
- [ ] Identify drop-off points in funnel
- [ ] A/B test:
  - [ ] CTA button color + text
  - [ ] Pricing page layout
  - [ ] Email subject lines
- [ ] Iterate based on learnings

### Marketing Content
- [ ] Create 3-5 guides:
  - [ ] "How to use AI for marketing"
  - [ ] "Cost comparison: ALICI vs ChatGPT API"
  - [ ] "Privacy with ALICI vs cloud AI"
- [ ] YouTube: 2-3 demo videos (5-10 min)
- [ ] Case studies: 3-5 documented (anonymized)

### Team Expansion Prep
- [ ] Write JD for first engineer hire
- [ ] Create onboarding playbook
- [ ] Identify advisors for technical interviews
- [ ] Budget for hiring (month 4, ~R$12k/month salary)

### Metrics Target (Month 4-5)
- [ ] Signups: 250+
- [ ] Paying customers: 18+
- [ ] MRR: R$2,000+
- [ ] Enterprise deals: 2-3 in progress
- [ ] Blog traffic: 1,000+ monthly
- [ ] Email list: 500+ subscribers

---

## MONTH 6: INVESTOR PREP

**Status**: [ ] Not Started

### Financial Reporting
- [ ] P&L statement (all 6 months)
- [ ] Customer acquisition cost (CAC)
- [ ] Lifetime value (LTV)
- [ ] Burn rate
- [ ] Runway (months)
- [ ] Monthly growth rate

### Customer Interviews (5 customers)
- [ ] Record testimonials (video + written)
- [ ] Document use cases
- [ ] Quantify impact (productivity gains, cost savings)
- [ ] Get permission for case studies

### Pitch Deck Refinement
- [ ] Update with Month 6 metrics
- [ ] Add customer logos + testimonials
- [ ] Add financial projections (18-month)
- [ ] Create investor FAQ (FAQ.md)

### Data Room Setup
- [ ] Prepare cap table
- [ ] Prepare financial model (Excel)
- [ ] Prepare customer list (anonymized)
- [ ] Prepare security documentation
- [ ] Prepare legal documents (incorporation, IP)

### Series Seed Preparation
- [ ] Create list of 50 target investors:
  - [ ] Angel investors (Brazil-focused)
  - [ ] Micro-VCs (500k-2M checks)
  - [ ] Accelerators (Plug and Play, Y Combinator)
- [ ] Research founder + managing partner
- [ ] Personalize outreach email
- [ ] Schedule 50 intro calls (target: 20 meetings, 5 leads, 1-2 sheets)

### Metrics Target (Month 6)
- [ ] Signups: 300
- [ ] Paying customers: 20+
- [ ] MRR: R$3,500 ✅ TARGET
- [ ] ARR: R$42k
- [ ] Churn: <10% MoM
- [ ] NPS: 35+
- [ ] Customer retention: 85% (30-day cohort)
- [ ] LTV:CAC ratio: 7x+

---

## ONGOING (ALL 6 MONTHS)

### Daily Tasks (15-30 min)
- [ ] Check Stripe dashboard (payments, errors)
- [ ] Monitor Mixpanel (DAU, MRR, errors)
- [ ] Reply to emails (support, sales)
- [ ] Post on Twitter (1 thoughtful post)

### Weekly Tasks (2-3 hours)
- [ ] Sync with any team members/advisors
- [ ] Read 3-5 customer support tickets
- [ ] Plan content (blog posts, emails)
- [ ] Check cold email metrics (open rate, replies)

### Bi-weekly Tasks (4-6 hours)
- [ ] Review metrics (growth, churn, CAC)
- [ ] Customer calls (2-3 one-on-ones)
- [ ] Product updates planning
- [ ] Hiring planning (when time)

### Monthly Tasks (1 day)
- [ ] Full financial review
- [ ] Cohort analysis (retention by signup month)
- [ ] Competitor monitoring
- [ ] Roadmap adjustment
- [ ] Investor updates (if raised)

---

## CRITICAL PATH (Don't Skip)

**Week 1**: Stripe live + testing
**Week 2**: Analytics live + tracking
**Week 3**: First cold emails sent
**Week 4**: First customers paying
**Month 2**: 10 paying customers
**Month 3**: 15 paying customers + case study
**Month 6**: 20 paying customers + investor ready

---

## SUCCESS CRITERIA (Month 6)

✅ **Quantitative**
- [ ] 300+ signups
- [ ] 20+ paying customers
- [ ] R$3,500 MRR
- [ ] LTV:CAC > 7x
- [ ] Payback period < 3 months
- [ ] Churn < 10% MoM
- [ ] NPS > 30

✅ **Qualitative**
- [ ] Repeatable sales process (founder-led)
- [ ] Product-market fit validated (retention > 80%)
- [ ] Investor traction (50+ investor conversations)
- [ ] Team ready for growth (hire #1 engineer)
- [ ] Competitive moat emerging (proprietary features)

---

**Phase 1 Owner**: Mateus Nascimento (Founder)  
**Executive Sponsor**: [Investor/Advisor name]  
**Last Updated**: March 4, 2026  

*This checklist is a living document. Update as priorities shift. Review weekly.*
