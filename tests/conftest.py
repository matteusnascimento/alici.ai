"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment variables
os.environ["STRIPE_SECRET_KEY"] = "sk_test_123456789"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_123456789"
os.environ["MIXPANEL_TOKEN"] = "test_token_123"


@pytest.fixture(scope="session")
def test_user_id():
    """Test user ID"""
    return "test_user_123"


@pytest.fixture(scope="session")
def test_email():
    """Test user email"""
    return "test@alici.ai"


@pytest.fixture(scope="session")
def test_stripe_customer_id():
    """Test Stripe customer ID"""
    return "cus_test_123456"


@pytest.fixture(scope="session")
def test_subscription_id():
    """Test subscription ID"""
    return "sub_test_123456"


@pytest.fixture
def mock_stripe_env(monkeypatch):
    """Mock Stripe environment variables"""
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_mock")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_mock")


@pytest.fixture
def mock_analytics_env(monkeypatch):
    """Mock Analytics environment variables"""
    monkeypatch.setenv("MIXPANEL_TOKEN", "mock_token")


@pytest.fixture
def test_file_path():
    """Path to test files"""
    return PROJECT_ROOT / "tests" / "fixtures"
