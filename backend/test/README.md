# Backend Tests

This directory contains all API tests for the MedPredict AI backend.

## Test Files

- **test_unified_api.py** - Comprehensive API endpoint tests
- **quick_api_test.py** - Quick API functionality tests
- **run_all_tests.py** - Master test runner (runs all tests)

## Running Tests

### Run All Tests
```bash
python backend/test/run_all_tests.py
```

### Run Individual Tests
```bash
# Comprehensive test
python backend/test/test_unified_api.py

# Quick test
python backend/test/quick_api_test.py
```

## Test Coverage

The tests verify:
- ✅ API server health and status
- ✅ All endpoint availability
- ✅ PKL model loading
- ✅ Data fetching from models
- ✅ Response format validation
- ✅ Error handling

## Requirements

- Backend API must be running on port 8000
- All PKL models must be in `backend/models/`
- Training data must be in `media/data/`

## Adding New Tests

1. Create a new test file in this directory
2. Add it to the test_files list in `run_all_tests.py`
3. Run `python backend/test/run_all_tests.py` to verify
