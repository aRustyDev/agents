---
name: Pytest Testing Guide
module_type: guide
scope: temporary
priority: low
triggers: ["pytest", "python testing", "test fixtures", "parameterized tests", "python unit tests"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Pytest Testing Guide

## Purpose
Pytest is a powerful Python testing framework that makes writing and organizing tests simple and scalable. It provides fixtures, parameterization, plugins, and excellent error reporting.

## Installation and Setup
```bash
# Install pytest
pip install pytest
pip install pytest-cov  # Coverage plugin
pip install pytest-mock  # Mocking support
pip install pytest-xdist  # Parallel execution

# Verify installation
pytest --version

# Basic project structure
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── calculator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Shared fixtures
│   ├── test_unit/       # Unit tests
│   └── test_integration/ # Integration tests
└── pytest.ini           # Configuration
```

## Basic Testing

### Simple Test Functions
```python
# test_calculator.py
def test_addition():
    assert 2 + 2 == 4

def test_subtraction():
    result = 10 - 3
    assert result == 7

# Run tests
# pytest test_calculator.py
# pytest -v  # Verbose output
# pytest -k "addition"  # Run tests matching pattern
```

### Testing Exceptions
```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert str(exc_info.value) == "Cannot divide by zero"

def test_divide_normal():
    assert divide(10, 2) == 5.0
```

### Test Classes
```python
class TestUserAuthentication:
    """Group related tests in a class"""
    
    def test_valid_login(self):
        user = User("alice", "secret123")
        assert user.login("alice", "secret123") is True
    
    def test_invalid_password(self):
        user = User("alice", "secret123")
        assert user.login("alice", "wrong") is False
    
    def test_user_not_found(self):
        with pytest.raises(UserNotFoundError):
            User.find("nonexistent")
```

## Fixtures

### Basic Fixtures
```python
# conftest.py - Shared fixtures
import pytest
from myapp.database import Database

@pytest.fixture
def db():
    """Provide a clean database for each test"""
    database = Database(":memory:")
    database.create_tables()
    yield database  # This is where the test runs
    database.close()

@pytest.fixture
def sample_user():
    """Provide a sample user"""
    return {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com"
    }

# test_users.py
def test_create_user(db, sample_user):
    user_id = db.create_user(**sample_user)
    assert user_id == 1
    assert db.get_user(1)["name"] == "Alice"
```

### Fixture Scopes
```python
@pytest.fixture(scope="session")
def app():
    """App instance shared across all tests"""
    application = create_app("testing")
    return application

@pytest.fixture(scope="module")
def client(app):
    """Test client shared within module"""
    return app.test_client()

@pytest.fixture(scope="function")  # Default
def transaction(db):
    """New transaction for each test"""
    trans = db.begin()
    yield trans
    trans.rollback()
```

### Parameterized Fixtures
```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Test with multiple database backends"""
    db = create_database(request.param)
    yield db
    db.cleanup()

def test_query_performance(database):
    # This test runs 3 times, once per database
    result = database.execute("SELECT 1")
    assert result is not None
```

## Parameterized Tests

### Basic Parameterization
```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (-2, 4),
])
def test_square(input, expected):
    assert input ** 2 == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
], ids=["one_plus_one", "two_plus_three", "negative", "zeros"])
def test_addition_cases(a, b, expected):
    assert a + b == expected
```

### Multiple Parameters
```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [3, 4])
def test_multiply(x, y):
    # Runs 4 times: (1,3), (1,4), (2,3), (2,4)
    assert x * y > 0
```

### Complex Parameterization
```python
test_cases = [
    # (username, password, should_succeed, error_type)
    ("alice", "correct123", True, None),
    ("alice", "wrong", False, AuthError),
    ("", "pass", False, ValidationError),
    ("alice", "", False, ValidationError),
    (None, "pass", False, TypeError),
]

@pytest.mark.parametrize("username,password,should_succeed,error_type", test_cases)
def test_login_scenarios(username, password, should_succeed, error_type):
    if should_succeed:
        result = login(username, password)
        assert result.is_authenticated
    else:
        with pytest.raises(error_type):
            login(username, password)
```

## Mocking and Patching

### Using pytest-mock
```python
def test_api_call(mocker):
    # Mock external API
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok"}
    
    mocker.patch("requests.get", return_value=mock_response)
    
    result = fetch_data("https://api.example.com")
    assert result["status"] == "ok"

def test_datetime_now(mocker):
    # Mock datetime
    mock_now = mocker.patch("myapp.utils.datetime")
    mock_now.now.return_value = datetime(2024, 1, 1, 12, 0)
    
    timestamp = get_current_timestamp()
    assert timestamp == "2024-01-01 12:00:00"
```

### Spying and Call Assertions
```python
def test_logging(mocker):
    mock_logger = mocker.patch("myapp.logger")
    
    process_user_action("login", "alice")
    
    # Verify logger was called
    mock_logger.info.assert_called_once_with("User alice performed login")
    
    # Check multiple calls
    mock_logger.debug.assert_has_calls([
        mocker.call("Starting action processing"),
        mocker.call("Action validated"),
        mocker.call("Action completed")
    ])
```

## Markers and Test Organization

### Built-in Markers
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9+")
def test_new_syntax():
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_broken_feature():
    assert False  # This failure is expected

@pytest.mark.timeout(5)  # Requires pytest-timeout
def test_slow_operation():
    perform_operation()
```

### Custom Markers
```python
# pytest.ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    smoke: marks tests as smoke tests

# test_performance.py
@pytest.mark.slow
def test_large_dataset_processing():
    process_million_records()

# Run only smoke tests
# pytest -m smoke
# Run all except slow tests
# pytest -m "not slow"
```

## Advanced Features

### Temporary Directories and Files
```python
def test_file_processing(tmp_path):
    # tmp_path is a Path object to a temporary directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")
    
    result = process_file(test_file)
    assert result == "HELLO, WORLD!"

def test_config_loading(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"debug": true}')
    
    config = load_config(config_file)
    assert config["debug"] is True
```

### Capturing Output
```python
def test_print_output(capsys):
    print("Hello from test")
    print("Error message", file=sys.stderr)
    
    captured = capsys.readouterr()
    assert "Hello from test" in captured.out
    assert "Error message" in captured.err

def test_logging_output(caplog):
    import logging
    logging.info("Processing started")
    logging.error("Something went wrong")
    
    assert "Processing started" in caplog.text
    assert caplog.records[1].levelname == "ERROR"
```

### Monkey Patching
```python
def test_environment_variable(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    
    config = load_config()
    assert config.api_key == "test-key-123"

def test_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "yes")
    
    result = confirm_action()
    assert result is True
```

## Configuration

### pytest.ini
```ini
[tool:pytest]
# Test discovery
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Default options
addopts = 
    -ra
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing:skip-covered

# Test paths
testpaths = tests

# Minimum Python version
minversion = 6.0
```

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=myapp",
    "--cov-branch",
    "--cov-report=html",
    "--cov-report=term-missing",
]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
]
```

## Common Patterns

### Testing Abstract Base Classes
```python
class TestAnimalBehavior:
    """Test all Animal subclasses"""
    
    @pytest.fixture
    def animal(self):
        """Subclasses override this"""
        raise NotImplementedError
    
    def test_make_sound(self, animal):
        sound = animal.make_sound()
        assert isinstance(sound, str)
        assert len(sound) > 0

class TestDog(TestAnimalBehavior):
    @pytest.fixture
    def animal(self):
        return Dog("Buddy")

class TestCat(TestAnimalBehavior):
    @pytest.fixture
    def animal(self):
        return Cat("Whiskers")
```

### Database Testing Pattern
```python
@pytest.fixture
def db_session():
    """Provide a transactional database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_user_creation(db_session):
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.commit()
    
    retrieved = db_session.query(User).filter_by(email="alice@example.com").first()
    assert retrieved.name == "Alice"
```

## Best Practices

### DO
- ✅ Use descriptive test names
- ✅ Keep tests independent
- ✅ Use fixtures for setup/teardown
- ✅ Group related tests
- ✅ Test edge cases

### DON'T
- ❌ Share state between tests
- ❌ Test implementation details
- ❌ Use production credentials
- ❌ Ignore test failures
- ❌ Write overly complex tests

## Debugging Tests

### Useful Pytest Options
```bash
# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Show first failure then stop
pytest -x

# Show last failed
pytest --lf

# Run tests in parallel
pytest -n 4

# Verbose with full diff
pytest -vv

# Show slowest tests
pytest --durations=10
```

### Using breakpoints
```python
def test_complex_logic():
    data = prepare_data()
    
    # Drop into debugger
    import pdb; pdb.set_trace()
    # Or in Python 3.7+
    # breakpoint()
    
    result = process_data(data)
    assert result.is_valid()
```

---
*Pytest makes testing in Python productive and enjoyable with its simple syntax, powerful features, and excellent ecosystem of plugins.*