# 🧪 TESTING GUIDE — ALICI

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_services.py
```

### Run Specific Test Class
```bash
pytest tests/test_services.py::TestStripeService
```

### Run Specific Test
```bash
pytest tests/test_services.py::TestStripeService::test_plan_pricing_brl
```

### Run with Coverage Report
```bash
pytest tests/ --cov=alici_api --cov-report=html
```

---

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── test_services.py      # Services (Stripe, Analytics)
├── test_api.py           # API endpoints
└── fixtures/
    └── sample_data.json
```

---

## Test Categories

### Unit Tests (Fast)
- Individual service methods
- Helper functions
- Data validation

**Run**: `pytest -m unit`

### Integration Tests (Slower)
- Service interactions
- Database operations
- Multi-component flows

**Run**: `pytest -m integration`

### End-to-End Tests (Slowest)
- Full user journeys
- API + Database + Auth flows

**Run**: `pytest -m e2e`

---

## Key Test Files

### `test_services.py`

**StripeService Tests:**
- ✅ test_plan_config_exists
- ✅ test_plan_pricing_brl
- ✅ test_create_customer_success
- ✅ test_create_subscription_pro
- ✅ test_upgrade_subscription
- ✅ test_webhook_payment_succeeded

**AnalyticsService Tests:**
- ✅ test_track_signup
- ✅ test_track_plan_upgrade
- ✅ test_estimate_ltv
- ✅ test_calculate_cac_payback

**Business Metrics Tests:**
- ✅ test_phase1_unit_economics
- ✅ test_mrr_projection_month6

---

## Writing New Tests

### Basic Unit Test Template

```python
import pytest
from alici_api.services.your_service import YourService

class TestYourService:
    @pytest.fixture
    def service(self):
        """Provide service instance"""
        return YourService()
    
    def test_something(self, service):
        """Test description"""
        # Arrange
        input_data = "test"
        
        # Act
        result = service.do_something(input_data)
        
        # Assert
        assert result == expected_value
```

### Mock External Calls

```python
from unittest.mock import patch, Mock

@patch('stripe.Customer.create')
def test_create_customer(mock_stripe, stripe_service):
    mock_customer = Mock()
    mock_customer.id = "cus_test123"
    mock_stripe.return_value = mock_customer
    
    result = stripe_service.create_customer("test@example.com", "Test User", "user_123")
    
    assert result == "cus_test123"
```

### Using Fixtures

```python
@pytest.fixture
def test_user_data():
    return {
        "email": "test@alici.ai",
        "name": "Test User",
        "user_id": "test_user_123"
    }

def test_with_fixture(test_user_data):
    # Use test_user_data here
    assert test_user_data["email"] == "test@alici.ai"
```

---

## Continuous Testing

### Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest tests/ || exit 1
```

### CI/CD (GitHub Actions)

Create `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=alici_api
```

---

## Common Issues

### "Import errors" when running tests

**Solution**: Ensure `PYTHONPATH` includes project root:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/alici.ai"
pytest tests/
```

### "stripe module not found"

**Solution**: Install test dependencies:
```bash
pip install -r requirements.txt
```

### "Mock not patching correctly"

**Solution**: Patch where the object is **used**, not where it's defined:
```python
# WRONG:
@patch('stripe.Customer.create')  # ❌

# CORRECT:
@patch('alici_api.services.stripe_service.stripe.Customer.create')  # ✅
```

---

## Test Coverage

Generate coverage report:
```bash
pytest tests/ --cov=alici_api --cov-report=html
open htmlcov/index.html
```

**Target Coverage**: 80%+

Current coverage (approximate):
- `stripe_service.py`: 85%
- `analytics_service.py`: 90%
- `routes/billing.py`: 70% (needs more tests)

---

## Performance Testing

### Load Test Example

```python
@pytest.mark.slow
def test_api_load():
    """Simulate 100 concurrent requests"""
    import concurrent.futures
    
    def make_request():
        return client.get("/health")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(make_request, range(100)))
    
    assert all(r.status_code == 200 for r in results)
```

Run slow tests:
```bash
pytest -m slow
```

---

## Debugging Tests

### Print Debug Output

```python
def test_with_debug(capsys):
    print("Debug message")
    captured = capsys.readouterr()
    assert "Debug" in captured.out
```

Run with captured output:
```bash
pytest tests/ -s
```

### Use pdb Breakpoint

```python
def test_something():
    result = some_function()
    breakpoint()  # Execution pauses here
    assert result == expected
```

Run and interact:
```bash
pytest tests/ --pdb
```

---

## Best Practices

✅ **DO:**
- Test behavior, not implementation
- Use descriptive test names
- Keep tests small and focused
- Mock external dependencies
- Use fixtures for reusable setup
- Test edge cases and errors
- Maintain >80% coverage

❌ **DON'T:**
- Create brittle tests that break on refactoring
- Test multiple things in one test
- Rely on test execution order
- Create tests that connect to real APIs
- Commit code with failing tests

---

## Test Maintenance

### Weekly
- Run full test suite before merging
- Review coverage reports
- Fix any flaky tests

### Monthly
- Update mock data
- Add tests for new features
- Refactor old tests

### Before Release
- Run full test suite
- Load test critical flows
- Manual QA on staging

---

For questions: See `tests/conftest.py` for fixtures and test setup helpers.
