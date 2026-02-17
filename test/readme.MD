# Initiative Viewer Test Suite

## Overview

This test suite provides comprehensive testing for the Initiative Viewer application, including:
- Web interface endpoints
- PDF generation (regular and wide formats)
- Parameter validation
- Error handling
- Integration tests

## Test Files

- **`test_initiative_viewer.py`** - Main test suite for Initiative Viewer
  - `TestWebInterface` - Tests all web endpoints
  - `TestPDFGeneration` - Tests PDF generation functionality
  - `TestErrorHandling` - Tests error scenarios
  - `TestDataValidation` - Tests data validation
  - `TestIntegration` - Full workflow integration tests

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

Tests all Flask endpoints:
- ✅ Index route loads correctly
- ✅ Analyze endpoint accepts valid data
- ✅ Analyze endpoint rejects invalid data
- ✅ Health check endpoint (if exists)

### 2. PDF Generation Tests (`TestPDFGeneration`)

Tests PDF functionality:
- ✅ PDF generator initialization (all formats: A4, A3, wide)
- ✅ **Duplicate arguments bug prevention** (catches the TypeError)
- ✅ PDF generation produces valid PDF output
- ✅ PDF export endpoints work correctly
- ✅ Wide PDF export works correctly

**Key Test:** `test_pdf_generator_initialization_no_duplicate_args`
- This test specifically prevents the bug where arguments were passed twice
- It verifies that TypeError is raised when duplicate args are provided
- This is the test that would have caught the colleague's error!

### 3. Error Handling Tests (`TestErrorHandling`)

Tests error scenarios:
- ✅ Empty initiatives list
- ✅ Missing session data
- ✅ Invalid analysis keys
- ✅ None/empty jira_url

### 4. Data Validation Tests (`TestDataValidation`)

Tests data integrity:
- ✅ Risk probability values (1-5, None)
- ✅ Completed statuses recognition
- ✅ Data structure validation

### 5. Integration Tests (`TestIntegration`)

Tests complete workflows:
- ✅ Full analysis → PDF export workflow
- ✅ Mocked Jira client interactions

## Understanding Test Results

### Successful Run
```
tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args PASSED [100%]
```

### Failed Test
```
tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args FAILED [100%]
FAILED tests/test_initiative_viewer.py::TestPDFGeneration::test_pdf_generator_initialization_no_duplicate_args - TypeError: __init__() got multiple values for argument 'jira_url'
```

This error would indicate the duplicate arguments bug has been reintroduced.

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

### Template for New Test

```python
def test_my_new_feature(self, client, sample_initiatives):
    """Test description goes here."""
    # Arrange
    # ... setup test data ...
    
    # Act
    result = some_function()
    
    # Assert
    assert result is not None
    assert result.expected_value == expected
```

### Test Fixtures Available

- `client` - Flask test client for HTTP requests
- `sample_initiatives` - Sample initiative data
- `sample_areas` - Sample area/project data

### Mocking Jira Client

```python
@patch('initiative_viewer.JiraClient')
def test_with_jira_mock(self, mock_jira, client):
    mock_client = Mock()
    mock_client.search_issues.return_value = [...]
    mock_jira.return_value = mock_client
    # ... your test ...
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
