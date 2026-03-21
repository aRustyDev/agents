"""Tests for the SafeExecutor class.

Tests cover:
- Basic code execution
- Input handling
- Exception handling
- Timeout handling
- Output comparison
"""

from __future__ import annotations

from ir_roundtrip.executor import ExecutionResult, SafeExecutor


class TestExecutionResult:
    """Tests for ExecutionResult class."""

    def test_timeout_factory(self) -> None:
        """Test timeout factory method."""
        result = ExecutionResult.timeout()

        assert not result.success
        assert result.timed_out
        assert result.exception_type == "TimeoutError"

    def test_error_factory(self) -> None:
        """Test error factory method."""
        result = ExecutionResult.error("ValueError", "Invalid input")

        assert not result.success
        assert result.exception_type == "ValueError"
        assert result.exception_message == "Invalid input"

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        result = ExecutionResult(
            success=True,
            return_value=42,
            execution_time_ms=10.5,
        )
        d = result.to_dict()

        assert d["success"] is True
        assert "42" in d["return_value"]  # repr(42)
        assert d["execution_time_ms"] == 10.5


class TestSafeExecutor:
    """Tests for SafeExecutor class."""

    def test_simple_function_execution(self) -> None:
        """Test executing a simple function."""
        executor = SafeExecutor()
        code = "def add(a, b): return a + b"

        result = executor.execute(code, {"a": 2, "b": 3}, func_name="add")

        assert result.success
        assert "5" in result.return_value

    def test_function_with_no_args(self) -> None:
        """Test executing a function with no arguments."""
        executor = SafeExecutor()
        code = "def get_value(): return 42"

        result = executor.execute(code, {}, func_name="get_value")

        assert result.success
        assert "42" in result.return_value

    def test_function_with_list_input(self) -> None:
        """Test executing a function with list input."""
        executor = SafeExecutor()
        code = "def sum_list(numbers): return sum(numbers)"

        result = executor.execute(
            code, {"numbers": [1, 2, 3, 4, 5]}, func_name="sum_list"
        )

        assert result.success
        assert "15" in result.return_value

    def test_function_that_raises(self) -> None:
        """Test executing a function that raises an exception."""
        executor = SafeExecutor()
        code = """def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
"""

        result = executor.execute(code, {"a": 10, "b": 0}, func_name="divide")

        assert not result.success
        assert result.exception_type == "ValueError"
        assert "Division by zero" in result.exception_message

    def test_syntax_error_handling(self) -> None:
        """Test handling of syntax errors in code."""
        executor = SafeExecutor()
        code = "def add(a, b) return a + b"  # Missing colon

        result = executor.execute(code, {"a": 1, "b": 2}, func_name="add")

        assert not result.success
        assert result.exception_type is not None

    def test_timeout_handling(self) -> None:
        """Test timeout handling for long-running code."""
        executor = SafeExecutor(timeout=0.5)
        code = """def infinite():
    while True:
        pass
    return 1
"""

        result = executor.execute(code, {}, func_name="infinite")

        assert not result.success
        assert result.timed_out

    def test_return_none(self) -> None:
        """Test function that returns None."""
        executor = SafeExecutor()
        code = "def do_nothing(): pass"

        result = executor.execute(code, {}, func_name="do_nothing")

        assert result.success
        assert "None" in result.return_value

    def test_return_complex_value(self) -> None:
        """Test function that returns complex value."""
        executor = SafeExecutor()
        code = "def get_dict(): return {'a': 1, 'b': [2, 3]}"

        result = executor.execute(code, {}, func_name="get_dict")

        assert result.success
        # Should contain repr of dict
        assert "a" in result.return_value


class TestOutputComparison:
    """Tests for output comparison logic."""

    def test_equal_integers(self) -> None:
        """Test comparing equal integers."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=42)
        result2 = ExecutionResult(success=True, return_value=42)

        assert executor.compare_outputs(result1, result2)

    def test_equal_floats_within_tolerance(self) -> None:
        """Test comparing floats within tolerance."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=1.0)
        result2 = ExecutionResult(success=True, return_value=1.0 + 1e-10)

        assert executor.compare_outputs(result1, result2)

    def test_unequal_values(self) -> None:
        """Test comparing unequal values."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=42)
        result2 = ExecutionResult(success=True, return_value=43)

        assert not executor.compare_outputs(result1, result2)

    def test_success_vs_failure(self) -> None:
        """Test comparing success vs failure."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=42)
        result2 = ExecutionResult(success=False, exception_type="ValueError")

        assert not executor.compare_outputs(result1, result2)

    def test_same_exception_type(self) -> None:
        """Test comparing same exception types."""
        executor = SafeExecutor()

        result1 = ExecutionResult(
            success=False, exception_type="ValueError", exception_message="Error 1"
        )
        result2 = ExecutionResult(
            success=False, exception_type="ValueError", exception_message="Error 2"
        )

        assert executor.compare_outputs(result1, result2)

    def test_different_exception_types(self) -> None:
        """Test comparing different exception types."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=False, exception_type="ValueError")
        result2 = ExecutionResult(success=False, exception_type="TypeError")

        assert not executor.compare_outputs(result1, result2)

    def test_equal_lists(self) -> None:
        """Test comparing equal lists."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=[1, 2, 3])
        result2 = ExecutionResult(success=True, return_value=[1, 2, 3])

        assert executor.compare_outputs(result1, result2)

    def test_unequal_lists(self) -> None:
        """Test comparing unequal lists."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=[1, 2, 3])
        result2 = ExecutionResult(success=True, return_value=[1, 2, 4])

        assert not executor.compare_outputs(result1, result2)

    def test_equal_dicts(self) -> None:
        """Test comparing equal dicts."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value={"a": 1, "b": 2})
        result2 = ExecutionResult(success=True, return_value={"a": 1, "b": 2})

        assert executor.compare_outputs(result1, result2)

    def test_none_values(self) -> None:
        """Test comparing None values."""
        executor = SafeExecutor()

        result1 = ExecutionResult(success=True, return_value=None)
        result2 = ExecutionResult(success=True, return_value=None)

        assert executor.compare_outputs(result1, result2)


class TestValuesEqual:
    """Tests for the _values_equal method."""

    def test_nested_structures(self) -> None:
        """Test comparing nested structures."""
        executor = SafeExecutor()

        val1 = {"a": [1, 2, {"b": 3}]}
        val2 = {"a": [1, 2, {"b": 3}]}

        assert executor._values_equal(val1, val2)

    def test_float_zero_comparison(self) -> None:
        """Test comparing zeros with floats."""
        executor = SafeExecutor()

        assert executor._values_equal(0.0, 0.0)

    def test_set_comparison(self) -> None:
        """Test comparing sets."""
        executor = SafeExecutor()

        assert executor._values_equal({1, 2, 3}, {3, 2, 1})
        assert not executor._values_equal({1, 2}, {1, 2, 3})

    def test_tuple_vs_list(self) -> None:
        """Test comparing tuple vs list (should be equal)."""
        executor = SafeExecutor()

        # Lists and tuples are compared element-wise
        assert executor._values_equal([1, 2], [1, 2])
        assert executor._values_equal((1, 2), (1, 2))
        # But tuple != list
        assert executor._values_equal([1, 2], (1, 2))
