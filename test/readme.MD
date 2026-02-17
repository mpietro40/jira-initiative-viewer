# Initiative Viewer Test Suite

## Overview

This test suite provides comprehensive testing for the Initiative Viewer application **without requiring a Jira connection**. All tests use static mocks and stubs that simulate real Jira behavior.

### Key Features:
- ✅ **No Jira connection required** - All tests use mock data
- ✅ **Comprehensive coverage** - Tests all web endpoints and PDF generation
- ✅ **Error simulation** - Tests authentication, permission, and JQL errors
- ✅ **Realistic data** - Mock data mirrors actual Jira structure
- ✅ **Fast execution** - No network calls means quick test runs

## Test Files

- **`test_initiative_viewer.py`** - Main test suite (650+ lines)
  - `TestWebInterface` - Tests all web endpoints  
  - `TestPDFGeneration` - Tests PDF generation functionality
  - `TestErrorHandling` - Tests error scenarios
  - `TestDataValidation` - Tests data validation
  - `TestIntegration` - Full workflow integration tests
  - **`TestWithMockJiraClient`** - Tests using complete mock Jira client
  - **`TestJiraErrorScenarios`** - Tests Jira error handling (401, 403, 400)
  - **`TestFullWorkflowWithMocks`** - End-to-end tests with mock data
  - **`TestMockDataStructure`** - Validates mock data structure
  - **`TestPDFWithVariousScenarios`** - PDF generation edge cases
  - **`TestEndToEndWithoutJira`** - Complete workflows without any Jira

- **`fixtures_initiative_viewer.py`** - Mock data and fixtures (500+ lines)
  - `MockJiraResponses` - Static Jira API response templates
  - `MockJiraClient` - Complete mock Jira client
  - Helper functions for creating test data

## Mock Data System

### MockJiraClient

A complete mock implementation of the Jira client that simulates real behavior:

```python
from fixtures_initiative_viewer import get_mock_jira_client

# Normal operation
mock_client = get_mock_jira_client()
results = mock_client.search_issues('project = PROJ AND type = "Business Initiative"')

# Simulate authentication error
mock_client = get_mock_jira_client(simulate_error='auth')
# This will raise: Exception('401 Unauthorized')

# Simulate permission error
mock_client = get_mock_jira_client(simulate_error='permission')

# Simulate JQL syntax error  
mock_client = get_mock_jira_client(simulate_error='jql')
```

### MockJiraResponses

Static response templates for various Jira issue types:

```python
from fixtures_initiative_viewer import MockJiraResponses

# Get a complete Business Initiative
initiative = MockJiraResponses.valid_business_initiative()

# Get a high-risk initiative
high_risk = MockJiraResponses.initiative_high_risk()

# Get error responses
auth_error = MockJiraResponses.authentication_error()
```

### Complete Hierarchy Data

Realistic test data with full hierarchy:

```python
from fixtures_initiative_viewer import create_mock_hierarchy_data

# Get 3 initiatives with complete Feature → Sub-Feature → Epic structure
hierarchy = create_mock_hierarchy_data()

# Includes:
# - PROJ-1: Customer Portal (3 features, risk=3)
# - PROJ-2: Security Upgrade (1 feature, risk=5)
# - PROJ-3: Q4 Improvements (1 feature, risk=1, status=Done)
```

## Running Tests

### Quick Start

```bash
# From the PerseusLeadTime directory
pytest tests/test_initiative_viewer.py -v
```

### With Coverage

```bash
pytest tests/test_initiative_viewer.py -v --cov=. --cov-report=html
```

### Run Specific Test Classes

```bash
# Test only PDF generation
pytest tests/test_initiative_viewer.py::TestPDFGeneration -v

# Test only web interface
pytest tests/test_initiative_viewer.py::TestWebInterface -v

# Test only error handling
pytest tests/test_initiative_viewer.py::TestErrorHandling -v
```

### Run Specific Tests

```bash
# Test the duplicate args bug fix
pytest tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args -v

# Test PDF export endpoint
pytest tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_export_endpoint -v
```

## Installation

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-flask` - Flask testing utilities
- `pytest-cov` - Code coverage
- `pytest-mock` - Mocking utilities
- `responses` - HTTP mocking
- All production dependencies

## Test Categories

### 1. Web Interface Tests (`TestWebInterface`)

Tests all Flask endpoints using mocks:
- ✅ Index route loads correctly
- ✅ Analyze endpoint with mocked Jira client
- ✅ Analyze endpoint rejects invalid data
- ✅ Health check endpoint (if exists)

### 2. PDF Generation Tests (`TestPDFGeneration`)

Tests PDF functionality with static data:
- ✅ PDF generator initialization (all formats: A4, A3, wide)
- ✅ **Duplicate arguments bug prevention** (catches the TypeError)
- ✅ PDF generation produces valid PDF output
- ✅ PDF export endpoints work correctly
- ✅ Wide PDF export works correctly

**Key Test:** `test_pdf_generator_initialization_no_duplicate_args`
- This test specifically prevents the bug where arguments were passed twice
- It verifies that TypeError is raised when duplicate args are provided
- This is the test that would have caught the colleague's error!

### 3. Mock Jira Client Tests (`TestWithMockJiraClient`) **NEW!**

Tests using complete mock Jira client - no actual Jira needed:
- ✅ Search for initiatives returns mock data
- ✅ Get single issue returns mock data
- ✅ Authentication error simulation (401)
- ✅ Permission error simulation (403)
- ✅ JQL syntax error simulation (400)
- ✅ Empty results handling
- ✅ Filtering by status, fix version

### 4. Jira Error Scenarios (`TestJiraErrorScenarios`) **NEW!**

Tests how application handles various Jira errors:
- ✅ Authentication failure (401 Unauthorized)
- ✅ Permission denied (403 Forbidden)
- ✅ JQL syntax errors (400 Bad Request)
- ✅ Empty result sets
- ✅ Graceful error messages to users

### 5. Full Workflow Tests (`TestFullWorkflowWithMocks`) **NEW!**

Tests complete workflows with mock data:
- ✅ Analysis → PDF export pipeline
- ✅ Data storage and retrieval
- ✅ PDF with complete hierarchy
- ✅ PDF with different risk levels (1-5)
- ✅ PDF with completed initiatives

### 6. Error Handling Tests (`TestErrorHandling`)

Tests error scenarios:
- ✅ Empty initiatives list
- ✅ Missing session data
- ✅ Invalid analysis keys
- ✅ None/empty jira_url

### 7. Data Validation Tests (`TestDataValidation`)

Tests data integrity:
- ✅ Risk probability values (1-5, None)
- ✅ Completed statuses recognition
- ✅ Data structure validation

### 8. Mock Data Structure Tests (`TestMockDataStructure`) **NEW!**

Validates mock data has correct structure:
- ✅ Mock initiatives have all required fields
- ✅ Hierarchy includes all levels (Initiative → Feature → Sub-Feature → Epic)
- ✅ Areas list is valid
- ✅ Empty hierarchy structure

### 9. PDF Scenario Tests (`TestPDFWithVariousScenarios`) **NEW!**

Tests PDF generation with various data scenarios:
- ✅ Single initiative
- ✅ Empty hierarchy
- ✅ Multiple areas (15+)
- ✅ Limited results (with warnings)
- ✅ All page formats (A4, A3, wide)

### 10. End-to-End Tests (`TestEndToEndWithoutJira`) **NEW!**

Complete tests without any Jira dependency:
- ✅ All risk probability values (None, 1-5)
- ✅ All status values (To Do, In Progress, Done, etc.)
- ✅ Complex hierarchies
- ✅ Edge cases

## Understanding Test Results

### Successful Run
```
tests/test_initiative_viewer.py::TestWithMockJiraClient::test_mock_client_authentication_error PASSED
tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args PASSED
tests/test_initiative_viewer.py::TestFullWorkflowWithMocks::test_complete_analysis_to_pdf_workflow PASSED
...
========================= 50+ tests passed in 5.23s =========================
```

### Failed Test Example
```
tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args FAILED
FAILED - TypeError: __init__() got multiple values for argument 'jira_url'
```

This error would indicate the duplicate arguments bug has been reintroduced.

## Error Simulation Details

The mock system simulates real Jira errors:

### Authentication Error (401)
```python
mock_client = get_mock_jira_client(simulate_error='auth')
# Raises: Exception('401 Client Error: Unauthorized. Authentication failed.')
```

**When this happens in real Jira:**
- Invalid API token
- Expired token
- Wrong email address
- Account locked

### Permission Error (403)
```python
mock_client = get_mock_jira_client(simulate_error='permission')
# Raises: Exception('403 Forbidden: You do not have permission.')
```

**When this happens in real Jira:**
- No access to the project
- Insufficient permissions
- Issue-level security restrictions

### JQL Syntax Error (400)
```python
mock_client = get_mock_jira_client(simulate_error='jql')
# Raises: Exception('400 Bad Request: Error in JQL Query')
```

**When this happens in real Jira:**
- Invalid JQL syntax
- Reserved characters not escaped
- Non-existent fields
- Invalid operators

### Testing Without Errors
```python
mock_client = get_mock_jira_client()  # No error simulation
results = mock_client.search_issues('project = PROJ')
# Returns mock data successfully
```

## Mock Data Coverage

The mock system provides:

| Data Type | Count | Risk Levels | Statuses | Features |
|-----------|-------|-------------|----------|----------|
| Initiatives | 3 | 1, 3, 5 | In Progress, Done | ✅ Multi-level |
| Features | 4 | 1-5 | Various | ✅ With Sub-Features |
| Sub-Features | 4 | 1-5 | Various | ✅ With Epics |
| Epics | 6 | - | Various | ✅ Complete |
| Areas | 4 | - | - | ✅ Multiple |

**Coverage:**
- ✅ All risk probability values (None, 1, 2, 3, 4, 5)
- ✅ Multiple statuses (To Do, In Progress, Done, Blocked, etc.)
- ✅ Complete hierarchy (4 levels deep)
- ✅ Multiple assignees
- ✅ Different fix versions
- ✅ Various project areas

## GitHub Actions Integration

Tests run automatically on:
- Every push to main/master/develop branches
- Every pull request
- Manual trigger via GitHub Actions UI

### Workflow Features:
- ✅ Tests on Python 3.8, 3.9, 3.10, 3.11
- ✅ Code coverage reporting
- ✅ Linting with flake8
- ✅ Automatic executable build on main/master
- ✅ Artifact upload (Windows executable)

View workflow: `.github/workflows/test-initiative-viewer.yml`

## Writing New Tests

### Using Mock Jira Client

The easiest way to test without Jira:

```python
from fixtures_initiative_viewer import get_mock_jira_client

def test_my_feature_with_mock():
    """Test a feature using mock Jira client."""
    # Get mock client
    mock_client = get_mock_jira_client()
    
    # Use it like real JiraClient
    results = mock_client.search_issues(
        'project = PROJ AND type = "Business Initiative"'
    )
    
    assert len(results) > 0
    assert results[0]['key'] == 'PROJ-1'
```

### Testing Error Scenarios

Test how your code handles errors:

```python
from fixtures_initiative_viewer import get_mock_jira_client

def test_authentication_error_handling():
    """Test handling of authentication failure."""
    # Mock client that simulates auth error
    mock_client = get_mock_jira_client(simulate_error='auth')
    
    # This will raise exception
    with pytest.raises(Exception, match='401'):
        mock_client.search_issues('project = PROJ')
```

### Using Pre-built Test Data

Use realistic hierarchical data:

```python
from fixtures_initiative_viewer import (
    create_mock_hierarchy_data,
    create_mock_areas
)

def test_pdf_with_realistic_data():
    """Test PDF generation with realistic hierarchy."""
    initiatives = create_mock_hierarchy_data()
    areas = create_mock_areas()
    
    pdf_gen = PDFGen(
        initiatives=initiatives,
        fix_version='v1.0',
        all_areas=areas,
        query='project = PROJ',
        jira_url='https://jira.example.com'
    )
    
    pdf_buffer = pdf_gen.generate()
    assert pdf_buffer is not None
```

### Template for New Test

```python
def test_my_new_feature(self, mock_jira_client):
    """Test description goes here."""
    # Arrange - setup test data using fixtures
    credentials = get_valid_test_credentials()
    
    # Act - perform the action
    result = mock_jira_client.search_issues(credentials['jql'])
    
    # Assert - verify the outcome
    assert result is not None
    assert len(result) > 0
```

### Test Fixtures Available

#### From `conftest.py`:
- `client` - Flask test client for HTTP requests

#### From `test_initiative_viewer.py`:
- `sample_initiatives` - Comprehensive mock hierarchy data
- `sample_areas` - Mock area/project data
- `mock_jira_client` - Mock Jira client (normal operation)
- `mock_jira_client_auth_error` - Mock that simulates 401
- `mock_jira_client_permission_error` - Mock that simulates 403
- `mock_jira_client_jql_error` - Mock that simulates 400
- `valid_credentials` - Valid test credentials

#### From `fixtures_initiative_viewer.py`:
- `MockJiraClient` - Complete mock Jira client class
- `MockJiraResponses` - Static response templates
- `get_mock_jira_client()` - Factory function
- `create_mock_hierarchy_data()` - Complete hierarchy
- `create_mock_empty_hierarchy()` - Empty initiatives
- `create_mock_areas()` - Mock areas list
- `get_valid_test_credentials()` - Test credentials

### Mocking Jira Client in Flask Tests

```python
@patch('initiative_viewer.JiraClient')
def test_with_patched_jira(self, mock_jira_class, client):
    """Test Flask endpoint with mocked Jira."""
    # Replace JiraClient with mock
    mock_jira_class.return_value = get_mock_jira_client()
    
    # Make request
    response = client.post('/analyze', data={
        'jira_url': 'https://jira.example.com',
        'email': 'test@example.com',
        'api_token': 'mock-token',
        'jql': 'project = PROJ',
        'fix_version': 'v1.0'
    })
    
    assert response.status_code in [200, 302]
```

## Continuous Improvement

### Adding Tests for New Bugs

When a bug is discovered:

1. **Write a failing test** that reproduces the bug
2. **Fix the code** to make the test pass
3. **Commit both** test and fix together

Example:
```python
def test_bug_pdf_duplicate_args(self):
    """
    Regression test for bug: PDF generator received duplicate arguments.
    This test ensures the bug doesn't happen again.
    """
    # Test that would have caught the original bug
    with pytest.raises(TypeError, match="multiple values"):
        PDFGen(args, args, jira_url=url)  # Wrong way
```

### Test Coverage Goals

Current coverage targets:
- **Minimum**: 60% code coverage
- **Goal**: 80% code coverage
- **Critical paths**: 100% (PDF generation, web endpoints)

Check coverage:
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Troubleshooting Tests

### Tests fail with "Import Error"

```bash
# Make sure you're in the PerseusLeadTime directory
cd PerseusLeadTime

# Install all dependencies
pip install -r requirements-test.txt
```

### Tests fail with "No module named 'initiative_viewer'"

```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=.  # Linux/Mac
set PYTHONPATH=.     # Windows cmd
$env:PYTHONPATH="."  # Windows PowerShell
```

### Mocked tests don't work

The `@patch` decorators mock external dependencies. If decorators seem ignored:
- Check decorator order (bottom-up execution)
- Verify the patch path is correct
- Use `patch.object` for class methods

### Tests pass locally but fail on GitHub

- Check Python version compatibility
- Verify all dependencies in `requirements-test.txt`
- Check for OS-specific code (Windows vs Linux)

## Best Practices

✅ **DO:**
- Write tests before fixing bugs (TDD)
- Test both success and failure cases
- Use descriptive test names
- Mock external services (Jira API)
- Keep tests independent (no shared state)

❌ **DON'T:**
- Make actual Jira API calls in tests
- Depend on external data
- Create files without cleanup
- Skip error case testing

## Quick Reference

```bash
# Run all tests
pytest tests/test_initiative_viewer.py -v

# Run with coverage
pytest tests/test_initiative_viewer.py --cov=. --cov-report=term

# Run specific test class
pytest tests/test_initiative_viewer.py::TestPDFGeneration -v

# Run tests matching pattern
pytest tests/ -k "pdf" -v

# Show print statements
pytest tests/test_initiative_viewer.py -v -s

# Stop on first failure
pytest tests/test_initiative_viewer.py -x

# Run last failed tests
pytest --lf
```

## Questions?

- Check test output for detailed error messages
- Review `pytest.ini` for configuration
- See `conftest.py` for shared fixtures
- Run `pytest --help` for all options

---

**Remember:** These tests are your safety net. Keep them updated and they'll prevent bugs from reaching production!
