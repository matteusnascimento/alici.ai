"""
ALICI Financial Model - 18 Month Projection
Exportable to Excel via pandas
"""

import json
from datetime import datetime, timedelta

financial_model = {
    "metadata": {
        "company": "ALICI",
        "model_type": "18-month projections",
        "created_at": "2026-03-04",
        "currency": "BRL",
        "base_scenarios": ["conservative", "base_case", "aggressive"]
    },
    
    "assumptions": {
        "plans": {
            "free": {
                "price_monthly": 0,
                "gross_margin": 0.0,
                "included_in_arpu": False
            },
            "pro": {
                "price_monthly": 49,
                "gross_margin": 0.75,
                "included_in_arpu": True
            },
            "ultra": {
                "price_monthly": 99,
                "gross_margin": 0.75,
                "included_in_arpu": True
            },
            "enterprise": {
                "price_monthly_avg": 750,
                "gross_margin": 0.85,
                "included_in_arpu": True
            }
        },
        
        "acquisition": {
            "cac": {
                "month_1_3": 500,
                "month_4_6": 300,
                "month_7_12": 200,
                "month_13_18": 150
            },
            "organic_monthly_signups": {
                "month_1_3": 50,
                "month_4_6": 75,
                "month_7_12": 100,
                "month_13_18": 150
            },
            "viral_coefficient": {
                "month_1_6": 0,
                "month_7_12": 0.05,
                "month_13_18": 0.1
            },
            "partnerships_contribution": {
                "month_1_6": 0,
                "month_7_12": 0.1,
                "month_13_18": 0.25
            }
        },
        
        "conversion": {
            "free_to_pro": {
                "rate": 0.05,
                "trial_duration_days": 14
            },
            "free_to_ultra": {
                "rate": 0.03,
                "trial_duration_days": 14
            },
            "pro_to_ultra_upsell": {
                "rate": 0.15,
                "timeframe_months": 6
            },
            "saas_to_enterprise": {
                "rate": 0.02,
                "deal_size_monthly": 750
            }
        },
        
        "retention": {
            "pro_monthly_churn": 0.05,
            "ultra_monthly_churn": 0.03,
            "enterprise_monthly_churn": 0.01,
            "cohort_month_1_retention": 0.95,
            "cohort_month_3_retention": 0.85,
            "cohort_month_6_retention": 0.80
        },
        
        "costs": {
            "cogs_percentage": 0.25,
            "payroll": {
                "month_1_3": 25000,
                "month_4_6": 40000,
                "month_7_9": 55000,
                "month_10_12": 70000,
                "month_13_15": 85000,
                "month_16_18": 100000
            },
            "marketing": {
                "month_1_3": 10000,
                "month_4_6": 15000,
                "month_7_9": 20000,
                "month_10_12": 25000,
                "month_13_15": 30000,
                "month_16_18": 40000
            },
            "infrastructure": 5000,
            "tools_and_software": 3000,
            "admin_and_legal": 5000
        }
    },
    
    "monthly_projections": [
        {
            "month": 1,
            "new_signups": 50,
            "total_free_users": 50,
            "free_to_pro_conversions": 2,
            "free_to_ultra_conversions": 1,
            "total_pro_users": 2,
            "total_ultra_users": 1,
            "enterprise_customers": 0,
            "pro_churn": 0,
            "ultra_churn": 0,
            "enterprise_churn": 0,
            "pro_ending_balance": 2,
            "ultra_ending_balance": 1,
            "enterprise_ending_balance": 0,
            "mrr": 197,  # 2*49 + 1*99
            "arr_equivalent": 2364,
            "cogs": 50,
            "gross_profit": 147,
            "payroll_cost": 25000,
            "marketing_cost": 10000,
            "infra_and_tools": 8000,
            "admin_legal": 5000,
            "total_opex": 48000,
            "ebitda": -47853,
            "cumulative_ebitda": -47853
        },
        {
            "month": 2,
            "new_signups": 55,
            "total_free_users": 105,
            "free_to_pro_conversions": 3,
            "free_to_ultra_conversions": 1,
            "total_pro_users": 5,
            "total_ultra_users": 2,
            "enterprise_customers": 0,
            "pro_churn": 0,
            "ultra_churn": 0,
            "enterprise_churn": 0,
            "pro_ending_balance": 5,
            "ultra_ending_balance": 2,
            "enterprise_ending_balance": 0,
            "mrr": 443,  # 5*49 + 2*99
            "arr_equivalent": 5316,
            "cogs": 111,
            "gross_profit": 332,
            "payroll_cost": 25000,
            "marketing_cost": 10000,
            "infra_and_tools": 8000,
            "admin_legal": 5000,
            "total_opex": 48000,
            "ebitda": -47668,
            "cumulative_ebitda": -95521
        }
    ],
    
    "quarterly_summary": {
        "q1": {
            "signups": 160,
            "free_users_ending": 150,
            "pro_users_ending": 10,
            "ultra_users_ending": 4,
            "enterprise_customers": 0,
            "mrr_ending": 1000,
            "arr_equivalent": 12000,
            "total_revenue": 1500,
            "total_cogs": 375,
            "total_gross_profit": 1125,
            "total_opex": 144000,
            "ebitda": -142875,
            "cumulative_ebitda": -142875
        },
        "q2": {
            "signups": 225,
            "free_users_ending": 240,
            "pro_users_ending": 25,
            "ultra_users_ending": 8,
            "enterprise_customers": 0,
            "mrr_ending": 2300,
            "arr_equivalent": 27600,
            "total_revenue": 5000,
            "total_cogs": 1250,
            "total_gross_profit": 3750,
            "total_opex": 115000,
            "ebitda": -111250,
            "cumulative_ebitda": -254125
        },
        "q3": {
            "signups": 300,
            "free_users_ending": 300,
            "pro_users_ending": 50,
            "ultra_users_ending": 20,
            "enterprise_customers": 2,
            "mrr_ending": 5200,
            "arr_equivalent": 62400,
            "total_revenue": 15000,
            "total_cogs": 3750,
            "total_gross_profit": 11250,
            "total_opex": 165000,
            "ebitda": -153750,
            "cumulative_ebitda": -407875
        },
        "h2": {
            "signups": 400,
            "free_users_ending": 400,
            "pro_users_ending": 80,
            "ultra_users_ending": 40,
            "enterprise_customers": 5,
            "mrr_ending": 10000,
            "arr_equivalent": 120000,
            "total_revenue": 50000,
            "total_cogs": 12500,
            "total_gross_profit": 37500,
            "total_opex": 290000,
            "ebitda": -252500,
            "cumulative_ebitda": -660375
        }
    },
    
    "annual_summary": {
        "year_1_h1": {
            "total_signups": 385,
            "ending_free_users": 150,
            "ending_pro_users": 25,
            "ending_ultra_users": 8,
            "ending_enterprise": 0,
            "annual_revenue_run_rate": 27600,
            "gross_margin": 0.75,
            "operating_expenses": 259000,
            "ebitda": -231400,
            "cash_burn_per_month": 38567
        },
        "year_1_h2": {
            "total_signups": 400,
            "ending_free_users": 300,
            "ending_pro_users": 50,
            "ending_ultra_users": 20,
            "ending_enterprise": 5,
            "annual_revenue_run_rate": 120000,
            "gross_margin": 0.78,
            "operating_expenses": 455000,
            "ebitda": -335000,
            "cash_burn_per_month": 27917
        },
        "year_1_full": {
            "total_signups": 785,
            "ending_free_users": 300,
            "ending_pro_users": 50,
            "ending_ultra_users": 20,
            "ending_enterprise": 5,
            "annual_revenue_run_rate": 120000,
            "annual_revenue_actual": 65000,
            "gross_margin": 0.77,
            "operating_expenses": 714000,
            "ebitda": -649000,
            "cash_burn_per_month": 33250,
            "runway_months": "4.5 (without seed)"
        }
    },
    
    "18_month_projection": {
        "month_1": {"mrr": 197, "free_users": 50, "pro": 2, "ultra": 1, "enterprise": 0},
        "month_2": {"mrr": 443, "free_users": 105, "pro": 5, "ultra": 2, "enterprise": 0},
        "month_3": {"mrr": 1000, "free_users": 150, "pro": 10, "ultra": 4, "enterprise": 0},
        "month_4": {"mrr": 1800, "free_users": 180, "pro": 18, "ultra": 6, "enterprise": 0},
        "month_5": {"mrr": 2500, "free_users": 200, "pro": 25, "ultra": 10, "enterprise": 1},
        "month_6": {"mrr": 3500, "free_users": 240, "pro": 35, "ultra": 15, "enterprise": 3},
        "month_7": {"mrr": 5000, "free_users": 280, "pro": 50, "ultra": 20, "enterprise": 4},
        "month_8": {"mrr": 6500, "free_users": 320, "pro": 65, "ultra": 25, "enterprise": 5},
        "month_9": {"mrr": 8000, "free_users": 350, "pro": 80, "ultra": 30, "enterprise": 6},
        "month_10": {"mrr": 10000, "free_users": 400, "pro": 100, "ultra": 40, "enterprise": 8},
        "month_11": {"mrr": 12000, "free_users": 450, "pro": 120, "ultra": 50, "enterprise": 10},
        "month_12": {"mrr": 14000, "free_users": 500, "pro": 140, "ultra": 60, "enterprise": 12},
        "month_13": {"mrr": 16000, "free_users": 550, "pro": 160, "ultra": 70, "enterprise": 15},
        "month_14": {"mrr": 20000, "free_users": 600, "pro": 190, "ultra": 85, "enterprise": 18},
        "month_15": {"mrr": 25000, "free_users": 650, "pro": 220, "ultra": 100, "enterprise": 22},
        "month_16": {"mrr": 30000, "free_users": 700, "pro": 250, "ultra": 120, "enterprise": 25},
        "month_17": {"mrr": 35000, "free_users": 750, "pro": 280, "ultra": 140, "enterprise": 28},
        "month_18": {"mrr": 40000, "free_users": 800, "pro": 310, "ultra": 160, "enterprise": 32}
    },
    
    "key_metrics": {
        "month_6": {
            "signups": 240,
            "paying_customers": 50,
            "mrr": 3500,
            "arr_run_rate": 42000,
            "conversion_rate": 0.10,
            "cac": 300,
            "arpu": 70,
            "ltv_estimate": 1400,
            "ltv_cac_ratio": 4.7,
            "cac_payback_months": 1.4,
            "gross_margin": 0.75,
            "monthly_churn": 0.05,
            "30_day_retention": 0.85,
            "nps_score": 35
        },
        "month_12": {
            "signups": 500,
            "paying_customers": 200,
            "mrr": 14000,
            "arr_run_rate": 168000,
            "conversion_rate": 0.12,
            "cac": 200,
            "arpu": 70,
            "ltv_estimate": 1400,
            "ltv_cac_ratio": 7.0,
            "cac_payback_months": 2.0,
            "gross_margin": 0.78,
            "monthly_churn": 0.04,
            "30_day_retention": 0.88,
            "nps_score": 40
        },
        "month_18": {
            "signups": 800,
            "paying_customers": 490,
            "mrr": 40000,
            "arr_run_rate": 480000,
            "conversion_rate": 0.15,
            "cac": 150,
            "arpu": 82,
            "ltv_estimate": 1640,
            "ltv_cac_ratio": 10.9,
            "cac_payback_months": 1.8,
            "gross_margin": 0.80,
            "monthly_churn": 0.03,
            "30_day_retention": 0.90,
            "nps_score": 45
        }
    },
    
    "scenarios": {
        "conservative": {
            "assumption_adjustments": {
                "organic_signups_reduction": 0.7,
                "conversion_reduction": 0.8,
                "churn_increase": 1.3
            },
            "month_6_mrr": 2000,
            "month_12_mrr": 8000,
            "month_18_mrr": 20000
        },
        "base_case": {
            "assumption_adjustments": {
                "organic_signups_reduction": 1.0,
                "conversion_reduction": 1.0,
                "churn_increase": 1.0
            },
            "month_6_mrr": 3500,
            "month_12_mrr": 14000,
            "month_18_mrr": 40000
        },
        "aggressive": {
            "assumption_adjustments": {
                "organic_signups_reduction": 1.3,
                "conversion_reduction": 1.2,
                "churn_increase": 0.8
            },
            "month_6_mrr": 5000,
            "month_12_mrr": 20000,
            "month_18_mrr": 60000
        }
    },
    
    "funding_impact": {
        "seed_round": {
            "amount_brl": 1500000,
            "amount_usd_equiv": 300000,
            "runway_months": 18,
            "pre_money_valuation": 5000000,
            "post_money_valuation": 6500000,
            "investor_equity": 0.231,
            "founder_equity_post": 0.769
        },
        "series_a_estimate": {
            "expected_month": 18,
            "expected_valuation": 250000000,
            "expected_raise": 30000000,
            "founder_ownership_post_dilution": 0.35,
            "seed_investor_ownership_post_dilution": 0.18
        }
    }
}

# Export to JSON
if __name__ == "__main__":
    with open("financial_model.json", "w", encoding="utf-8") as f:
        json.dump(financial_model, f, ensure_ascii=False, indent=2)
    print("Financial model exported to financial_model.json")
    
    # Example: Print key metrics for month 6
    print("\n=== MONTH 6 KEY METRICS ===")
    for key, value in financial_model["key_metrics"]["month_6"].items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
